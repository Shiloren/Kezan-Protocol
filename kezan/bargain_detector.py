"""Bargain detector (ganga) for Blizzard auction snapshots (advisory-only).

Implements the normalization, candidate filtering, simple rule-based score (placeholder for ML),
final recommendation fields, and compliance with advisory-only UX.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Protocol


@dataclass
class Stats:
    P50_7d: float
    P50_30d: float
    MAD_7d: float
    vol_7d: float
    rot: float


class History(Protocol):
    def get_stats(self, key: tuple) -> Optional[Stats]:
        ...


@dataclass
class Config:
    discount_p50_30d: float = 0.75
    discount_p50_7d: float = 0.85
    z_threshold: float = -1.5
    min_vol_commodity: int = 200
    min_vol_noncommodity: int = 40
    bargain_score_min: float = 0.6
    max_alloc_fraction: float = 0.12
    max_units_cap: int = 200
    eta_h_default: int = 48


@dataclass
class Lot:
    item_id: int
    quantity: int
    scope: str  # region or connected_realm_id
    is_commodity: bool
    price_u: Optional[float]  # normalized per-unit price
    time_left: Optional[str] = None
    quality: Optional[int] = None
    listings: Optional[int] = None
    spread_proxy: Optional[float] = None


def normalize_commodity_lot(region: str, lot: Dict) -> Lot:
    return Lot(
        item_id=int(lot.get("item", {}).get("id", 0)),
        quantity=int(lot.get("quantity", 0)),
        scope=region,
        is_commodity=True,
        price_u=float(lot.get("unit_price")) if lot.get("unit_price") is not None else None,
    )


def normalize_noncommodity_lot(realm_id: int, lot: Dict) -> Optional[Lot]:
    q = max(int(lot.get("quantity", 0)), 1)
    buyout = lot.get("buyout")
    if buyout is None:
        return None
    return Lot(
        item_id=int(lot.get("item", {}).get("id", 0)),
        quantity=q,
        scope=str(realm_id),
        is_commodity=False,
        price_u=float(buyout) / float(q) if q > 0 else None,
        time_left=lot.get("time_left"),
        listings=None,
    )


def zscore(price_u: float, P50_7d: float, MAD_7d: float) -> float:
    eps = 1e-6
    denom = 1.4826 * max(MAD_7d, eps)
    return (price_u - P50_7d) / denom


def rule_score(features: Dict) -> float:
    # Simple heuristic: stronger discount and better rot → higher score
    rel7 = features.get("rel_7d", 1.0)
    rel30 = features.get("rel_30d", 1.0)
    rot = features.get("rot", 0.0)
    base = 0.0
    # Stronger weight to 7d/30d discounts
    base += max(0.0, (1.0 - rel7)) * 0.5
    base += max(0.0, (1.0 - rel30)) * 0.35
    # Rotation helps but capped
    base += min(1.0, rot / 1.0) * 0.15
    return max(0.0, min(1.0, base))


def build_features(lot: Lot, price_u: float, stats: Stats) -> Dict:
    features = {
        "rel_7d": price_u / max(stats.P50_7d, 1e-6),
        "rel_30d": price_u / max(stats.P50_30d, 1e-6),
        "zscore_7d": zscore(price_u, stats.P50_7d, stats.MAD_7d),
        "MAD_7d": stats.MAD_7d,
        "vol_7d": stats.vol_7d,
        "rot": stats.rot,
        "is_commodity": lot.is_commodity,
    }
    return features


def compute_target(stats: Stats, features: Dict, pred_72h: Optional[float] = None) -> float:
    p50_7d = stats.P50_7d
    if pred_72h is not None and pred_72h > 0:
        return min(pred_72h * 0.99, p50_7d * 1.01)
    return p50_7d * 0.99


def estimate_eta(stats: Stats) -> int:
    # Coarse heuristic: faster rotation → lower eta
    if stats.rot >= 1.0:
        return 36
    if stats.rot >= 0.6:
        return 48
    return 72


def detect_bargains(snapshot: Iterable[Lot], history: History, capital: float, cfg: Config) -> List[Dict]:
    recs: List[Dict] = []
    for lot in snapshot:
        price_u = lot.price_u
        if price_u is None:
            continue
        stats = history.get_stats((lot.scope, lot.item_id, lot.quality))
        if not stats:
            continue

        discount_flag = (price_u <= cfg.discount_p50_30d * stats.P50_30d) and (
            price_u <= cfg.discount_p50_7d * stats.P50_7d
        )
        z = zscore(price_u, stats.P50_7d, stats.MAD_7d)
        anomaly_flag = z <= cfg.z_threshold
        candidate = discount_flag or anomaly_flag

        if lot.is_commodity:
            liquidity_ok = stats.vol_7d >= cfg.min_vol_commodity
        else:
            liquidity_ok = stats.vol_7d >= cfg.min_vol_noncommodity

        if not (candidate and liquidity_ok):
            continue

        features = build_features(lot, price_u, stats)
        score = rule_score(features)
        # If anomaly very strong (z <= -2.0), boost score
        if features.get("zscore_7d", 0) <= -2.0:
            score = max(score, 0.7)
        if score < cfg.bargain_score_min:
            continue

        # qty suggestion (advisory-only)
        qty = min(int((capital * cfg.max_alloc_fraction) // max(price_u, 1)), cfg.max_units_cap)
        if qty <= 0:
            continue

        target_sell = compute_target(stats, features)
        eta_h = estimate_eta(stats)
        reason = f"Descuento/anomalía; z={z:.2f}, vol_7d={stats.vol_7d}, rot={stats.rot}"

        recs.append(
            {
                "item_id": lot.item_id,
                "realm_or_region": lot.scope,
                "is_commodity": lot.is_commodity,
                "price_u": price_u,
                "p50_7d": stats.P50_7d,
                "p50_30d": stats.P50_30d,
                "zscore_7d": round(z, 2),
                "vol_7d": stats.vol_7d,
                "rot": stats.rot,
                "bargain_score": round(score, 3),
                "recommendation_type": "RECOMMEND_BUY",
                "qty_sugerida": qty,
                "target_sell": target_sell,
                "eta_h": eta_h,
                "reason": reason,
            }
        )

    return sorted(recs, key=lambda r: r["bargain_score"], reverse=True)
