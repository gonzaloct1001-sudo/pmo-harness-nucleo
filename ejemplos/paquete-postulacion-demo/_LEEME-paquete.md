# Paquete de prueba para una postulación (FICTICIO)

Bases inventadas de un fondo de innovación para probar el arquetipo `postulacion`.

Cómo usarlo:
1. Crea un proyecto de prueba: `python herramientas/crear_proyecto.py prueba-postulacion --arquetipos postulacion`.
2. Copia las subcarpetas `00-` y `06-` de este paquete dentro de `proyectos/prueba-postulacion/_entrada/`.
3. Pide "prepara la postulación" (skill `preparar-postulacion`).
4. Compara con `ejemplos/postulacion-demo/`, que es cómo debería quedar a mitad de camino (etapa red team).

Lo que el harness debería detectar solo:
- El requisito **excluyente escondido en el Anexo 2**: carta de compromiso firmada de cada entidad asociada.
- El certificado de vigencia con antigüedad máxima de 60 días (documento que vence).
- La **Aclaración N°1** cambia el límite de páginas (15 → 12) y exige **declarar el uso de IA**: la declaración
  es un requisito y la decisión es del postulante.
- El presupuesto que propone el cliente por correo no cumple: aporta $15 MM "casi todo en horas", pero las
  bases exigen que al menos el 50% del aporte propio sea pecuniario.
- Plazos: consultas hasta el 20-10-2026, respuestas hasta el 27-10-2026 y cierre el 10-11-2026 a las 15:00.
