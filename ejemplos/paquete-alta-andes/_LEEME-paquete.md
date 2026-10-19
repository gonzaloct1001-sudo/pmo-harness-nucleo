# Paquete de prueba para el alta (FICTICIO)

Documentos en bruto del Programa Andes Digital, todos inventados, para probar la skill `alta-proyecto`.

Cómo usarlo:
1. Ejecuta `instalar` (o `alta-proyecto`) con un proyecto de prueba, por ejemplo "Prueba Andes".
2. Copia las subcarpetas 01 a 08 de esta carpeta dentro de `proyectos/prueba-andes/_entrada/` (este archivo no hace falta
   copiarlo; si se copia, el harness lo ignora).
3. Escribe **listo**.
4. Compara el resultado con `ejemplos/demo-andes/`, que es cómo debería quedar aproximadamente.

Lo que el alta debería resolver sola (con las reglas de decisión):
- Término vigente 30-04-2027 y monto 895 MM: la enmienda prevalece sobre el contrato y la propuesta.
- Fecha del piloto: la carta Gantt (15-01-2027) prevalece sobre "fines de enero" del informe semanal.
- Ignorar la conversación de ChatGPT que no es del proyecto.
- Tratar lo que sugirió la IA como riesgo candidato, no como hecho.

Lo que debería preguntar o marcar para revisión:
- Quién aprueba cambios: el contrato dice Comité de Dirección, pero un correo posterior de la Gerente General delega los cambios menores en el Jefe de TI.
- La tarea de cierre termina después del plazo contractual vigente.
- El PEP de agosto informa 45% de avance en la app, más de lo que respalda la carta Gantt.
