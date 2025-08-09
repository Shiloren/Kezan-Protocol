# Addon Kezan Protocol (WoW) — Especificación

## Objetivo
Escanear la Casa de Subastas, capturar estadísticas de crafteo del personaje y guardar todo en SavedVariables para su consumo por el Cliente PC.

## SavedVariables: Estructura propuesta
```lua
KezanAHDB = {
  lastScan = 1723202123,
  realm = "Sanguino",
  faction = "Alliance",
  items = {
    [19019] = { price = 123456, qty = 2, seller = "Goblin", ts = 1723202123 },
    -- ... más items
  },
  playerStats = {
    multicraft = 0.27,
    resourcefulness = 0.12,
    inspiration = 0.18,
    craftingSpeed = 0.22,
    skill = 211
  }
}
```

## Eventos y flujo
- Al abrir AH: lanzar escaneo selectivo (por categorías) o full scan con throttling.
- Hook de resultados: actualizar `items` con precio mínimo por `itemID`, cantidad y timestamp.
- Captura de stats: leer buffs, equipo, y talentos que afectan crafteo; persistir en `playerStats`.

## Serialización y rendimiento
- Usar claves numéricas para `items`.
- Minimizar strings repetidas.
- Limitar `items` a último precio mínimo y conteo por item.

## Seguridad y cumplimiento
- Solo lectura/asesoría; no automatizar pujas/ventas.
- No interferir con la UI por defecto más de lo necesario.
