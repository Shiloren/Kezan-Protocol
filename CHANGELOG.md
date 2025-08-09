## 1.3.0 - 2025-08-08 05:22:17
Initial release of changelog system.

## 1.3.1 - 2025-08-08 05:36:21
- Docstrings traducidos al español y nuevos tests de Fase 14.

## 1.7.0 - 2025-08-08 08:35:44
- Auditoría de dependencias y fijado de versiones.
- Nuevas pruebas para credenciales faltantes, archivos bloqueados y CSV corruptos.
- Manejo de errores mejorado en exportación y carga de contexto.

## 1.7.1 - 2025-08-09 00:00:00
- Fix: corregido error de indentación en `AIController._validate_file_access` que podía causar `SyntaxError` al importar.
- Perf: `market_optimizer` ahora importa NumPy de forma perezosa para reducir el overhead cuando no se usa.
- Tests: colección estabilizada bajo `tests/` con `pytest.ini`; dos tests están marcados como skip intencionalmente (ver README y CONTRIBUTING para detalles).
- Docs: README actualizado con política de changelog y versión; se añadieron plantillas y guía de contribución.

## 1.7.2 - 2025-08-09 00:00:00
- Docs: AGENTS.md actualizado con propósito explícito (aportar al contenido), cumplimiento de ToS de Blizzard y alineación con Prompt Maestro.
- Docs: Prompt Maestro ampliado con sección de Roadmap y marcas de estado [ ], [~], [x] para seguimiento de features.

## 1.7.3 - 2025-08-09 00:00:00
- Docs: añadido `docs/ROADMAP.md` como fuente de verdad y enlazado desde README; snapshot resumido se mantiene en Prompt Maestro.
- Docs: creada carpeta `docs/temp_flow/` para borradores de trabajo (no fuente de verdad) con README de normas.
- CI/Plantillas: PR template actualizado para exigir ROADMAP; workflow ajustado para requerir actualización de ROADMAP en cambios relevantes e ignorar edits sólo en temp_flow.

## 1.8.0 - 2025-08-09 00:00:00
- Feature: endpoint `/api/simulate` (POST) para backtests mínimos del simulador v1 (placeholder).
- Feature: endpoint `/api/premium-check` (GET) para control de plan básico (Free/Pro, placeholder).
- Core: módulo `kezan/simulator.py` creado con `run_backtest` y métricas prototipo.
- Roadmap: actualizado con tareas de API y T2 embeddings.

