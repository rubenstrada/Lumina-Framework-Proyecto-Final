# Resultados del framework Lumina

El caso no proporciona una fuente operativa; se construyó un escenario reproducible para probar la viabilidad técnica. Los resultados corresponden a sus reglas y no son evidencia empresarial real.

## Calidad de datos

Entrada: 10431 filas. Después de limpiar: 10369.
Las ventas corruptas no se imputan para crear etiquetas. Se excluyen ventanas con semanas ausentes; los predictores faltantes se imputan dentro del pipeline.

## Evaluación

| Modelo | MAE unidades | RMSE unidades | WAPE | R² | Mejora MAE |
|---|---:|---:|---:|---:|---:|
| Ingenuo | 51.296 | 76.559 | 26.50% | 0.464 | 0.00% |
| Ridge | 42.035 | 60.040 | 21.72% | 0.671 | 18.05% |
| Random Forest | 38.985 | 58.289 | 20.14% | 0.689 | 24.00% |

Modelo elegido en validación: **Random Forest**.
Selección por MAE de validación; tolerancia de 2 % favorece Ridge por sencillez. Prueba no participa en selección ni ajuste.
En prueba su MAE fue 38.985 unidades frente a 51.296 de la referencia. Diferencia de MAE candidato menos referencia, intervalo orientativo del 95 %: [-14.709, -10.274].
El remuestreo usa bloques de cuatro semanas. Hay pocos bloques independientes: no demuestra una mejora económica ni elimina la incertidumbre de generalización.

## Interpretación y recomendaciones

96 combinaciones requieren revisar cobertura según stock al cierre y ventas previstas. No son órdenes de compra: faltan pedidos en tránsito, plazos y costos.
Cobertura del último corte: 96 de 100 combinaciones. Inventarios no disponibles: 2; requieren revisión de calidad, no se consideran sin riesgo.
Priorizar revisión de errores por categoría y sucursal; contrastar promociones dentro de grupos equivalentes. Una asociación entre promoción y ventas no demuestra causalidad.
Mantener revisión manual en episodios de agotamiento. Las ventas observadas están limitadas por stock y no miden demanda perdida.
Si el modelo elegido no supera la referencia en prueba, conservar una política sencilla y obtener más historial antes de decidir su adopción.

## Limitaciones y mejoras

Solo dos años, un escenario y doce semanas de prueba. Se pronostica venta acumulada observada, condicionada a una política de reposición. No se conocen futuras promociones ni futuros precios; no se usan como características.
Las ventanas futuras superpuestas hacen que sus volúmenes no puedan sumarse como ventas anuales. No se calcularán ahorros multiplicando MAE por semanas.
Antes de uso operativo: contrato de datos real, costos de exceso y faltante, pedidos pendientes, validación en más periodos y seguimiento del error.
