# Resultados de la exploración preliminar

## Ejecución

- Semilla fija: `20260916`.
- Estructura: 74 filas y 5 columnas.
- Duplicados exactos detectados: 2.
- La tabla se genera en memoria y se entrega directamente a `DataProfiler` y
  `EDAVisualizer`. No se crea un CSV artificial solo para forzar el uso de
  `DataLoader`; ese componente se valida por separado en las pruebas del framework.

## Estructura y valores faltantes

| Campo analizado | Tipo observado | Faltantes | Porcentaje |
|---|---:|---:|---:|
| `fecha_demo` | `datetime64[us]` | 0 | 0.00% |
| `entidad_demo` | `string` | 0 | 0.00% |
| `categoria_demo` | `string` | 3 | 4.05% |
| `valor_demo` | `float64` | 4 | 5.41% |
| `promocion_demo` | `bool` | 0 | 0.00% |

## Estadística descriptiva de `valor_demo`

| Estadístico | Resultado |
|---|---:|
| count | 70.0 |
| mean | 56.843857 |
| std | 5.462105 |
| min | 45.78 |
| 25% | 52.3675 |
| 50% | 57.51 |
| 75% | 60.2775 |
| max | 68.18 |

El perfil permite revisar estructura, calidad básica y distribución antes de definir
transformaciones o un posible objetivo predictivo.

## Visualizaciones generadas con el framework

- [`serie_temporal_demo.png`](serie_temporal_demo.png)
- [`distribucion_demo.png`](distribucion_demo.png)
- [`mapa_calor_demo.png`](mapa_calor_demo.png)

- La serie temporal presenta el cambio de la medida a lo largo de las fechas.
- La distribución permite revisar frecuencia, dispersión y grupos.
- El mapa de calor resume el promedio entre dos dimensiones.

Las preguntas reales de negocio, el esquema fuente, la variable objetivo y el
horizonte predictivo permanecen pendientes hasta recibir datos y definiciones reales.
