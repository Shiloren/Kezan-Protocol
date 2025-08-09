## Resumen
Tipo de cambio: (bugfix, feature, docs, perf, tests, chore)

## Cambios principales
- 

## Cómo probar
```
pytest -q --disable-warnings --cov=kezan --cov-report=term-missing
```

## Checklist de calidad
- [ ] CHANGELOG.md actualizado
- [ ] README.md / Docs actualizados si hay nuevas features o cambios de uso
- [ ] CONTRIBUTING.md sigue vigente (pasos, versiones, políticas)
- [ ] docs/ROADMAP.md actualizado si cambia alcance/prioridades/fechas
- [ ] Si este PR añade contenido en docs/temp_flow, está marcado con estado ([ ], [~], [x]) y no se referencia públicamente
- [ ] Cobertura sin regresiones (objetivo ≥95%)
- [ ] Cumplimiento DSL asesoría (sanitize/preamble)

## Alineación Kezan Protocol
- [ ] Alineado con `docs/kezan_protocol_master_prompt.md`
- [ ] Si hay nueva arquitectura/flujo/IA, docs actualizados

## Áreas impactadas
- Backend / Frontend / Addon / Infra / Docs
