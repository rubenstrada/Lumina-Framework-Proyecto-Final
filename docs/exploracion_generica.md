# Exploración genérica de una fuente desconocida

## Propósito

Este documento define cómo revisar una fuente tabular autorizada cuando todavía no se conocen sus columnas, su volumen ni su función de negocio. La salida es un diagnóstico técnico, no una conclusión sobre Lumina o Red Comercial Boreal.

## Principio de trabajo

La exploración separa lo observable de lo que debe confirmar una persona responsable del dato:

- **Observable automáticamente:** forma, encabezados, tipos físicos, faltantes, duplicados, valores distintos y estadísticos numéricos.
- **Requiere contexto:** significado de una fila, identificadores, fechas oficiales, unidades, valores válidos, variable objetivo y horizonte.

Un tipo físico no determina por sí solo el tipo de negocio. Un entero puede ser un identificador, una cantidad o un código categórico. Por ello, el framework perfila primero y valida el significado después.

## Representaciones utilizadas

### Pandas DataFrame

El `DataFrame` es la representación principal porque conserva:

- nombres y orden de las columnas;
- tipos diferentes dentro de una misma tabla;
- índices y alineación entre filas;
- operaciones por columna para faltantes, duplicados y cardinalidad;
- selección explícita de subconjuntos numéricos, de texto o fecha.

### Arreglos de NumPy

NumPy se usa cuando la operación es puramente numérica y vectorizada. Un bloque puede obtenerse con `data.select_dtypes(include="number").to_numpy()`. Esta conversión debe realizarse después de seleccionar columnas; convertir toda la tabla al principio perdería etiquetas y podría forzar tipos incompatibles.

En etapas posteriores, las predicciones y valores reales también se manejan como arreglos para calcular MAE, RMSE y WAPE.

## Secuencia técnica

| Etapa | Entrada | Operación | Salida |
|---|---|---|---|
| 1. Carga | Ruta autorizada | `DataLoader.load()` y `pd.read_csv()` | `DataFrame` sin limpieza |
| 2. Estructura | `DataFrame` | `shape`, `columns`, `dtypes` | Inventario físico |
| 3. Calidad básica | `DataFrame` | `isna()`, `duplicated()`, `nunique()` | Conteos verificables |
| 4. Numéricos | Columnas numéricas | `select_dtypes()` y `describe()` | Distribución resumida |
| 5. Texto y categorías | Columnas no numéricas | Frecuencias y cardinalidad | Niveles por revisar |
| 6. Fechas | Candidata confirmada | `pd.to_datetime(errors="coerce")` | Fechas inválidas y cobertura |
| 7. Contrato | Diccionario aprobado | `DataValidator.validate()` | Cumplimiento estructural |
| 8. Reporte | `ProfileResult` | `ReportGenerator` | `profile.json` y manifiesto |

## Uso del perfilador existente

```python
from pathlib import Path

from lumina_framework.data import DataLoader, DataProfiler

source = Path("ruta_a_fuente_autorizada.csv")
data = DataLoader().load(source)
profile = DataProfiler().profile(data)

print(profile.row_count)
print(profile.column_count)
print(profile.dtypes)
print(profile.missing_counts)
print(profile.exact_duplicates)
print(profile.unique_counts)
print(profile.numeric_statistics)
```

El ejemplo no fija nombres de columnas y no requiere target. La ruta es un marcador que debe reemplazarse únicamente cuando exista una fuente autorizada.

## Qué no debe automatizarse todavía

Sin diccionario no deben asumirse:

- la llave única;
- la unidad de observación;
- qué columnas son medidas o identificadores;
- cuál fecha representa el evento o la disponibilidad;
- qué valor debe predecirse;
- qué horizonte es útil;
- qué valores extremos son errores.

El framework puede señalar candidatos y problemas técnicos, pero una regla de limpieza o una interpretación de negocio requiere aprobación explícita.

## Volumen y evolución

La versión preliminar usa un `DataFrame` en memoria. Es suficiente para verificar el diseño, pero no demuestra capacidad para archivos de cualquier tamaño.

Antes de cambiar de tecnología se medirá el tamaño del archivo, la memoria máxima durante la carga y el tiempo del perfilado. Si la fuente no cabe en la memoria disponible o rebasa el tiempo acordado, se evaluará en este orden:

1. declarar tipos y cargar solo columnas necesarias;
2. usar `read_csv(chunksize=...)` para métricas acumulables;
3. consultar la fuente mediante SQL sin extraerla completa;
4. incorporar otro motor solo si las mediciones lo justifican.

No se selecciona Dask, Spark, una base analítica ni infraestructura adicional mientras el volumen siga siendo desconocido.

## Criterio de avance

El perfilado técnico puede comenzar cuando exista una fuente autorizada y reproducible. La exploración empresarial requiere además un diccionario y una persona responsable de validar hallazgos. El modelado permanece bloqueado hasta confirmar objetivo, horizonte, fecha de corte, baseline y costo del error.
