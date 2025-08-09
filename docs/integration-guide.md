# Guía de integración — Kezan Protocol

## Flujo de datos
1. Addon guarda `KezanAHDB` en SavedVariables.
2. Cliente PC parsea SavedVariables (Lua → JSON) e integra con histórico remoto.
3. Se procesan oportunidades (heurísticas + ML ligero) y se consultan a la IA (modo asesoría) para validación.

## Control de acceso Premium
- API Key por cuenta.
- Endpoint `/premium-check` devuelve `{"active": true|false, "plan": "premium|free"}`.
- Límite de descargas diarias de snapshots según plan.

## Versionado y compatibilidad
- Versionar el formato SavedVariables.
- Documentar breaking changes en CHANGELOG.
