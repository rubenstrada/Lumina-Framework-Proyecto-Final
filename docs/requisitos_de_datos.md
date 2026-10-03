# Requisitos de datos antes de modelar

## Motivo

El caso no proporciona tablas, columnas ni registros. Esta ausencia no se corrige inventando un dataset. Se convierte en una lista de información que Lumina debe solicitar y validar con Red Comercial Boreal.

## Inventario de fuentes

Por cada archivo, tabla o consulta se requiere:

- nombre y ubicación de la fuente;
- sistema que la genera;
- responsable funcional y técnico;
- frecuencia y hora de actualización;
- cobertura histórica;
- formato, codificación y zona horaria;
- reglas de acceso y retención.

## Diccionario de datos

Cada campo debe documentar:

- nombre exacto;
- significado de negocio;
- tipo físico y tipo lógico;
- unidad de medida y moneda;
- valores permitidos;
- significado de cero y de valor faltante;
- fecha desde la que es confiable;
- momento en que está disponible para decidir.

## Unidad de observación y llave

Se debe confirmar qué representa una fila. Producto por sucursal por semana es una hipótesis procedente del Avance 1, no una definición confirmada. También debe acordarse la llave que hace única cada observación y el tratamiento de correcciones tardías.

## Tiempo

La organización debe identificar la fecha del evento, la fecha de registro, la zona horaria y la frecuencia real. El tiempo de reabasto y la frecuencia de pedido determinan el horizonte. Cuatro semanas permanece como hipótesis y no debe fijarse antes de consultar la operación.

## Ventas demanda e inventario

Venta observada no siempre equivale a demanda. Si una sucursal agotó un producto, una venta baja puede significar falta de disponibilidad. Se requieren señales de inventario inicial, movimientos, devoluciones, ajustes, quiebres de stock y demanda no atendida para decidir qué objetivo es defendible.

## Promociones precios y disponibilidad futura

Solo pueden utilizarse como predictores los precios y promociones conocidos en el momento real de la decisión. Una campaña registrada después de la fecha de corte produciría fuga de información.

## Objetivo y decisión

Antes de entrenar debe contestarse:

1. ¿Qué decisión cambiará con la predicción?
2. ¿Quién toma esa decisión?
3. ¿Qué entidad recibe una predicción?
4. ¿Qué periodo futuro se desea anticipar?
5. ¿Cómo se observará después el resultado real?
6. ¿Cuánto cuesta un faltante frente a un sobrante?
7. ¿Cuál es la regla simple que actuará como línea base?

El contrato de configuración conserva `prediction_horizon: null` hasta que
este periodo se confirme; el modelado permanece bloqueado mientras siga vacío.

## Plan de exploración

La exploración se ejecutará en dos niveles. El primero es técnico y no requiere conocer el significado de las columnas; el segundo requiere un diccionario aprobado.

### Nivel 1 perfilado físico genérico

| Revisión | Operación principal | Salida |
|---|---|---|
| Forma | `DataFrame.shape` | Número de filas y columnas |
| Inventario | `columns` y `dtypes` | Nombres y tipos inferidos |
| Faltantes | `isna().sum()` | Conteo por columna |
| Duplicados | `duplicated().sum()` | Filas repetidas exactamente |
| Cardinalidad | `nunique()` | Valores distintos por campo |
| Numéricos | `select_dtypes()` y `describe()` | Conteo, media, dispersión, cuartiles y extremos |
| Tamaño en memoria | `memory_usage(deep=True)` | Base para decidir si la carga en memoria sigue siendo adecuada |

Pandas conserva la estructura tabular y los nombres. Cuando se requieran operaciones vectorizadas sobre un bloque numérico, este puede convertirse explícitamente con `to_numpy()`. La conversión no se aplica a toda la tabla porque podría mezclar texto, fechas, identificadores y medidas.

### Nivel 2 validación semántica

Después de recibir el diccionario se revisarán la llave de observación, fechas válidas, unidades, categorías permitidas, valores imposibles, cobertura temporal, relación entre fuentes, censura por desabasto y disponibilidad real de cada predictor.

Solo después de definir una posible variable objetivo se evaluarán su tasa base, estabilidad, horizonte y riesgo de fuga. El detalle técnico se encuentra en [`exploracion_generica.md`](exploracion_generica.md).

## Visualizaciones previstas

| Gráfica | Campos lógicos | Pregunta de negocio |
|---|---|---|
| Serie temporal | Fecha, entidad y medida | ¿Existen tendencia, estacionalidad o rupturas? |
| Mapa de calor | Dos dimensiones y medida | ¿Dónde se concentra la disponibilidad o el riesgo? |
| Histograma y caja | Medida y segmento | ¿Hay asimetrías o valores atípicos por grupo? |
| Real contra pronóstico | Fecha, real y predicción | ¿El modelo mejora el baseline y dónde falla? |

Estas visualizaciones son propuestas. No se generarán resultados empresariales hasta que existan las columnas y observaciones requeridas.

## Criterio de aceptación

El análisis puede comenzar cuando la fuente abre de forma reproducible, el diccionario cubre los campos críticos, la llave no es ambigua, el tiempo está ordenado y la diferencia entre venta y demanda está documentada. El modelado requiere además objetivo, horizonte, fecha de corte, baseline y métrica acordados.
