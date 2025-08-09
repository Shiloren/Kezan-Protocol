# AGENTS: Política de iteración y conducta

Este archivo define reglas operativas para agentes y contribuciones automatizadas/humanas.

Propósito: los agentes deben aportar activamente al contenido y a la creación de la aplicación (código, tests, documentación, guías), siguiendo directrices ajustadas a los Términos de Servicio (ToS) de Blizzard y alineadas con la visión/objetivo descritos en el Prompt Maestro (`docs/kezan_protocol_master_prompt.md`).

## Principios
- Seguridad: no exfiltrar secretos ni claves; no llamadas de red en tests.
- Enfoque Windows-friendly: comandos PowerShell en docs y scripts.
- Cambios trazables: cada cambio de código debe reflejarse en CHANGELOG.md.
- Docs vivas: nuevas features o cambios de uso requieren README y/o docs actualizados.
- Pruebas primero: mantener cobertura objetivo ≥95% sin flakiness; tests deterministas.
- Compatibilidad: evitar cambios breaking sin plan/documentación.

## Reglas de contribución
- Si cambias código en `kezan/`, `frontend/`, `templates/` o `installer/`:
  - Actualiza `CHANGELOG.md` con versión/fecha y bullets (feat/fix/perf/docs/tests/chore).
- Si agregas features o cambias comandos/uso:
  - Actualiza `README.md` y `docs/`.
- Ejecuta tests y cobertura antes de abrir PR.

Directrices: todas las acciones y propuestas deben cumplir el ToS de Blizzard (modo asesoría, sin automatizar el cliente) y mantener la alineación con los objetivos y principios del Prompt Maestro.

## Cumplimiento (CI)
- Workflow `agents-policy.yml` en `.github/workflows/` verifica:
  - Que `CHANGELOG.md` se haya modificado cuando hay cambios en código.
  - Que `AGENTS.md` exista.

## Notas
- `market_optimizer` usa import perezoso de NumPy; las pruebas pueden saltar si `numpy` no está instalado.
- Dos tests están skippeados intencionalmente (ver README/CONTRIBUTING) para evitar redundancia/dependencia dura.
