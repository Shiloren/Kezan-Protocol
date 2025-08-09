# Bot de históricos en la nube — Especificación

## Objetivo
Recoger snapshots horarios de subastas de Blizzard y almacenarlos comprimidos para su consulta por el Cliente PC.

## Endpoints Blizzard
- `/data/wow/connected-realm/{id}/auctions`
- `/data/wow/auctions/commodities` (opcional)

## Autenticación
- OAuth2 Client Credentials contra Battle.net.
- Variables:
  - `BLIZZARD_CLIENT_ID`
  - `BLIZZARD_CLIENT_SECRET`
  - `REGION` (ej: `eu`, `us`)

## Clave de almacenamiento
```
region:realm:YYYY-MM-DDTHH.json.gz
```

## Plataforma
- Cloudflare Workers / Pages Functions
- GitHub Actions (schedule) + Cloud storage (KV, R2, S3 compatible)

## Retención y compresión
- Gzip o zstd según plataforma.
- Retención recomendada: 12 meses en Premium; 7 días en plan gratuito.

## Límites y buenas prácticas
- Respetar rate limits de Blizzard.
- Cache local entre ejecuciones para evitar duplicados.
