# Guía de comprensión del prototipo

Esta guía sirve para revisar el trabajo y preparar la defensa. Leer respuestas no prueba por sí solo dominio del código: conviene ejecutar y modificar una copia, revisar los resultados y explicarlos con palabras propias.

1. ¿Qué representa una fila? Un producto en una sucursal durante una semana; los cortes posteriores son horizontes, no nuevas empresas.
2. ¿Qué se predice? La suma de ventas observadas de las cuatro semanas siguientes; no demanda que habría existido sin límites de inventario.
3. ¿Por qué se explora primero? Para revisar tipos, llaves, calendario, faltantes y disponibilidad de etiquetas antes de fijar transformaciones.
4. ¿Qué hace shift antes de rolling? Excluye la semana del corte del resumen de cuatro semanas anteriores; reindexar impide que un hueco cambie la duración del rezago.
5. ¿Por qué no se divide aleatoriamente? El caso pregunta por el futuro; los grupos de la misma semana deben quedar juntos y las etiquetas de cuatro semanas necesitan espacios entre periodos.
6. ¿Qué distingue validación y prueba? Validación elige parámetros y modelo. Prueba mide desempeño después de decidir; no se retoca el modelo al ver su resultado.
7. ¿Por qué comparar con una regla ingenua? Una solución compleja debe aportar frente a una alternativa mantenible. Si no mejora, el runner conserva la regla histórica.
8. ¿Qué significa MAE 38.98? Un promedio de error absoluto de aproximadamente 39 unidades en la venta acumulada de cuatro semanas por combinación-corte, no 39 por día ni una tasa de exactitud.
9. ¿Qué hace una señal? Compara previsión y stock al cierre para revisión. No incorpora reposiciones pendientes, plazos ni costos. Inventario desconocido requiere revisión de calidad.
10. ¿Por qué no sumar ventanas para calcular ventas anuales? Horizontes sucesivos comparten semanas; sumarlos contaría ventas varias veces.
11. ¿Qué demuestra el resultado? Que el flujo se ejecuta y mejora una referencia en el escenario y periodo evaluados. No demuestra causalidad, generalización a una empresa ni rentabilidad.
12. ¿Quién hizo qué? El estudiante delimitó, cuestionó y decidió aspectos del proyecto; Codex apoyó implementación y comprobaciones. Esa asistencia se declara, y la defensa de decisiones corresponde al estudiante.

Para comprobar entendimiento, localizar la configuración, cambiar un parámetro en una copia, predecir qué debería variar y contrastarlo con la ejecución. No cambiar parámetros después de observar prueba para presentar una mejora como evaluación independiente.
