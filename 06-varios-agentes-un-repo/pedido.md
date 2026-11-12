# Pedido de producto · TraveLens, sprint de noviembre

Tres cambios que el equipo de producto quiere para la próxima versión. Están escritos como los escribiría una persona de producto, sin decir cómo se implementan.

1. **Duración a elección.** Hoy todo plan dura tres días. La persona que viaja debe poder pedir de 2 a 7 días. Si no dice nada, siguen siendo 3. Un plan que no trae exactamente los días pedidos no se muestra.

2. **Presupuesto por día.** Cada día del plan trae un costo estimado en dólares (entero, sin centavos, mayor o igual a cero) y el plan trae el total. El total que ve la persona tiene que ser la suma de los días, aunque el modelo se equivoque al sumar.

3. **Descargar el itinerario.** Un botón en el panel del plan descarga el itinerario como un archivo Markdown, con el destino como título, un encabezado por día y sus actividades en lista. El nombre del archivo sale del destino, sin espacios ni acentos (por ejemplo `antigua-guatemala.md`).

Restricciones del equipo: no se agregan dependencias nuevas, el juez del tema anterior (`juez/ai-plan.juez.test.ts`) sigue en verde y `npm run check` también.
