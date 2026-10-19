# Checklist de despliegue (ajustar al equipo)

## Antes
- [ ] Cambios revisados y aprobados; pruebas automatizadas en verde.
- [ ] Migraciones de datos probadas en un ambiente igual al productivo y con plan de reversa.
- [ ] Banderas de funcionalidad (feature flags) definidas para lo riesgoso.
- [ ] Plan de reversa (rollback) escrito y criterio para activarlo.
- [ ] Comunicación a usuarios o soporte si hay impacto visible.
- [ ] Ventana de despliegue acordada y responsables disponibles.

## Durante
- [ ] Monitoreo de errores, latencia y métricas de negocio abierto.
- [ ] Verificación de humo (smoke test) tras el despliegue.

## Después
- [ ] Registrar el despliegue en `ingenieria/despliegues.csv` (resultado, tiempo de entrega).
- [ ] Si hubo incidente: registrar recuperación y abrir postmortem.
