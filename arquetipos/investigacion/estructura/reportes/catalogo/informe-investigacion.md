---
tipo: informe-investigacion
nombre: Informe de investigación
formato: docx
modo: generar
plantilla: ""
cadencia: a pedido
periodo_archivo: mes
destinatarios: []
fuentes:
  - investigaciones/
---

# Secciones
Se genera desde `investigaciones/<id>/E6_entregable.md` de la investigación cerrada que se indique:
1. **Respuesta** — la respuesta a la pregunta de decisión, primero.
2. **Fundamento** — cada afirmación con su marca (H, D, T, I, S, V) y su cita.
3. **Conclusiones y condición de revisión** — «Alta confianza. Cambiaría si aparece X.»
4. **Lo que no se sabe** — los vacíos; es parte del resultado, no un anexo.
5. **Límite de cobertura** — qué no se pudo verificar y con qué fuente se habría verificado.
6. **Anexo: fuentes** — desde `expediente.csv` (solo las citadas; nunca N6).

# Validaciones
- `python herramientas/investigacion.py <proyecto> --instancia <id> --revisar` sin errores antes de generar.
- En el Word, los ID internos (E-01, C-02) pueden reemplazarse por notas al pie con la fuente; la marca se conserva.
- Autoría limpia: `verificar_autoria.py` en OK.
