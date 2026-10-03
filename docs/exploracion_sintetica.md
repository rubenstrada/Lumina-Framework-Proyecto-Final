# Exploración preliminar ejecutada con Python

Antes de plantear transformaciones o modelos es necesario conocer la estructura,
calidad y comportamiento de los datos disponibles. Esta página muestra en GitHub la
secuencia completa entre la tabla analizada, el código y los resultados visuales.

Las figuras son salidas nativas de Matplotlib y Seaborn guardadas por Python como
archivos PNG. De esta manera se pueden revisar tanto el código que las construye como
el resultado de su ejecución.

## Reproducir la exploración

Desde la raíz del repositorio:

```powershell
python scripts/run_synthetic_eda_demo.py
```

El script completo está en
[`scripts/run_synthetic_eda_demo.py`](../scripts/run_synthetic_eda_demo.py) y la
implementación del visualizador en
[`src/lumina_framework/visualization/eda.py`](../src/lumina_framework/visualization/eda.py).

## 1. Preparación de la tabla

La semilla fija permite repetir la exploración con la misma estructura, faltantes y
duplicados:

```python
from scripts.run_synthetic_eda_demo import build_synthetic_dataset

data = build_synthetic_dataset(seed=20260916)
print(data.shape)
print(data.columns.tolist())
print(data.dtypes)
```

Pandas conserva los nombres y tipos dentro del `DataFrame`. NumPy se utiliza para los
cálculos numéricos reproducibles sin eliminar las etiquetas de la tabla.

## 2. Perfilado

La tabla se entrega directamente al componente del framework:

```python
from lumina_framework.data import DataProfiler

profile = DataProfiler().profile(data)

print(profile.row_count, profile.column_count)
print(profile.dtypes)
print(profile.missing_counts)
print(profile.exact_duplicates)
print(profile.unique_counts)
print(profile.numeric_statistics)
```

Los resultados calculados se guardan automáticamente en:

- [`resumen_demo.json`](evidencia_sintetica/resumen_demo.json), con la estructura
  completa en formato procesable.
- [`resumen_demo.md`](evidencia_sintetica/resumen_demo.md), con las tablas de
  faltantes, duplicados y estadísticos descriptivos.

## 3. Matplotlib y Seaborn

`EDAVisualizer` utiliza explícitamente ambas librerías:

```python
import matplotlib.pyplot as plt
import seaborn as sns
```

La exploración ejecuta sus tres métodos sobre el mismo `DataFrame` perfilado:

```python
from pathlib import Path

from lumina_framework.visualization import EDAVisualizer

output_dir = Path("docs/evidencia_sintetica")
visualizer = EDAVisualizer(output_dir)

visualizer.plot_time_series(data, "fecha_demo", "valor_demo")
visualizer.plot_distribution(data, "valor_demo", "categoria_demo")
visualizer.plot_heatmap(
    data,
    row_column="entidad_demo",
    column_column="categoria_demo",
    value_column="valor_demo",
)
```

Seaborn construye las representaciones estadísticas y Matplotlib controla la figura,
los títulos y la exportación:

```python
sns.lineplot(data=plot_data, x=date_column, y=value_column, marker="o")
sns.histplot(data=plot_data, x=value_column, hue=group_column, kde=True)
sns.heatmap(matrix, annot=True, fmt=".2f", cmap="YlGnBu")

plt.title("Evolución temporal de la variable")
plt.title("Distribución de la variable por categoría")
plt.title("Promedio de la variable por entidad y categoría")
plt.savefig(path, dpi=160, bbox_inches="tight")
```

| Componente | Uso dentro de la exploración |
|---|---|
| Pandas | Mantiene la tabla, fechas, categorías, faltantes y duplicados. |
| NumPy | Realiza los cálculos reproducibles. |
| `DataProfiler` | Calcula estructura, calidad básica y estadísticos. |
| Seaborn | Construye la serie, la distribución y el mapa de calor. |
| Matplotlib | Configura, titula y guarda cada figura. |

## 4. Resultados visuales

### Evolución temporal de la variable

![Evolución temporal de la variable](evidencia_sintetica/serie_temporal_demo.png)

La serie permite observar el comportamiento de la medida a lo largo del tiempo.

### Distribución de la variable por categoría

![Distribución de la variable por categoría](evidencia_sintetica/distribucion_demo.png)

El histograma permite revisar frecuencia, dispersión y diferencias entre grupos.

### Promedio de la variable por entidad y categoría

![Promedio de la variable por entidad y categoría](evidencia_sintetica/mapa_calor_demo.png)

El mapa de calor resume la medida mediante una agregación entre dos dimensiones.

## Trazabilidad

```text
Semilla fija
    ↓
Pandas DataFrame
    ├─→ DataProfiler → JSON y Markdown
    └─→ EDAVisualizer → Seaborn + Matplotlib → tres PNG
```

Esta etapa permite conocer los datos antes de decidir reglas de limpieza,
transformaciones o un posible objetivo. La validación del problema de negocio sigue
requiriendo la fuente autorizada, su diccionario y la definición del horizonte.
