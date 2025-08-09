## Resumen
- [ ] IA asesoría-only (Blizzard-safe): guardarraíles + DSL
- [ ] Conectores LLM (Ollama/OpenAI-style)
- [ ] Nuevas pruebas (llm_interface, ai_controller)
- [ ] Docs/README actualizados

## Cambios principales
-

## Cómo probar
```
pytest -q --disable-warnings --cov=kezan --cov-report=term-missing
```

## Requisitos del sistema
Consulta `docs/llm_y_requisitos.md`.

## Checklist
- [ ] Cobertura >= 80%
- [ ] Docs enlazados desde docs/index.html
- [ ] Cumplimiento DSL asesoría (sanitize/preamble)## Resumen
Describe brevemente el cambio y su motivación.

## Checklist de alineación (Kezan Protocol)
- [ ] He revisado `docs/kezan_protocol_master_prompt.md` y este cambio está alineado con la visión y filosofía.
- [ ] Si hay información nueva (arquitectura, flujos, requisitos de IA/simulación), he actualizado `docs/kezan_protocol_master_prompt.md` y la documentación relevante.
- [ ] Mantiene el enfoque plug & play (instalación sencilla, entorno de simulación integrado, solo requiere API key de Blizzard).
- [ ] Cumple los Términos de Servicio de Blizzard (procesamiento fuera del cliente de WoW).
- [ ] Si aplica, he añadido/actualizado pruebas y documentación.

## Impacto
- Backend / Frontend / Addon / Infra / Docs

## Notas adicionales
