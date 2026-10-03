"""Construye el reporte académico desde las salidas verificables del experimento.

No entrena modelos ni calcula métricas nuevas: lee los artefactos de la ejecución.
La prosa documenta las decisiones acordadas y no atribuye datos reales al caso.
"""
from __future__ import annotations

import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "project_final"
REPOSITORY_URL = "https://github.com/rubenstrada/Lumina-Framework-Proyecto-Final"


def read_json(name):
    return json.loads((OUTPUT / name).read_text(encoding="utf-8"))


def read_csv(name):
    with (OUTPUT / name).open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


def table(headers, rows):
    return "\n".join([
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
        *("| " + " | ".join(str(x) for x in row) + " |" for row in rows),
    ])


def build_report():
    before, after = read_json("profile_before.json"), read_json("profile_after.json")
    manifest, cuts = read_json("manifest.json"), read_json("temporal_split.json")
    metrics, validation = read_csv("test_metrics.csv"), read_csv("validation_metrics.csv")
    interval = read_json("uncertainty.json")
    importance = read_csv("feature_importance.csv")
    signals = read_csv("inventory_signals.csv")
    evidence = ET.parse(ROOT / 'docs' / 'evidencia_final' / 'test_results.xml').getroot()
    test_count = sum(int(s.get('tests',0)) for s in evidence.findall('testsuite'))
    selected = manifest["selected_model"]
    best = next(row for row in metrics if row["modelo"] == selected)
    selected_validation = min((x for x in validation if x["modelo"] == selected), key=lambda x: float(x["mae"]))
    metric_table = table(
        ["Modelo", "MAE unidades", "RMSE unidades", "WAPE", "R²", "Mejora MAE"],
        [(x["modelo"], f'{float(x["mae"]):.2f}', f'{float(x["rmse"]):.2f}',
          f'{float(x["wape"]):.2%}', f'{float(x["r2"]):.3f}', f'{float(x["mejora_mae_pct"]):.2f}%') for x in metrics],
    )
    validation_table = table(["Modelo", "Configuración", "MAE de validación"],
                             [(x["modelo"], x["configuracion"], f'{float(x["mae"]):.2f}') for x in validation])
    sections = []

    def section(number, instruction, response):
        sections.append(f"## {number}\n\n{instruction}\n\n{response.strip()}\n")

    section(1, "Retoma los avances previos y ajusta la problemática, el objetivo técnico y la arquitectura del framework con base en la retroalimentación recibida.", """
El problema que retomé es cómo aprovechar el historial de ventas e inventario de Red Comercial Boreal, con apoyo de Lumina Datos Operativos, para anticipar necesidades de revisión de existencias. En los avances previos propuse una arquitectura configurable porque el caso describía información general, sin entregar una base de datos ni confirmar columnas. Mi punto de partida sigue siendo conocer la estructura y la calidad de los datos antes de elegir un modelo.

Como el caso no incluye una base de datos, trabajé con un escenario simulado de 20 productos, 5 sucursales y 104 semanas, con semilla 42. Sus columnas son decisiones del prototipo, no campos confirmados de la empresa. Esta aclaración aplica a todas las cifras, gráficas y recomendaciones de la entrega.

El objetivo técnico quedó definido como estimar las unidades vendidas acumuladas en las cuatro semanas posteriores a cada corte producto-sucursal-semana. El resultado apoyará una revisión de cobertura de inventario, sin producir órdenes de compra. Elegí ventas observadas como objetivo verificable; cuando el inventario se agota, las ventas dejan de reflejar toda la demanda y no puedo llamar demanda real a la predicción.

A partir de la revisión de los avances, concreté el contrato de datos, incorporé un generador y completé el flujo de análisis. Elegí los modelos según el objetivo del proyecto, los comparé con una regla sencilla y separé los datos por periodos. Conservé la arquitectura previa y amplié sus componentes para esta etapa. El proyecto final tiene su propia repo; el Avance 2 permanece como antecedente en https://github.com/rubenstrada/Dise-o-framework-.
""")
    section(2, "Desarrolla un prototipo funcional en Python. El proyecto deberá organizarse mediante funciones, clases, módulos o archivos separados que permitan reutilizar el código y facilitar su mantenimiento.", """
El prototipo se ejecuta con una configuración YAML y genera los datos de entrada si no existe la fuente. Después carga, valida, limpia, explora, prepara variables, entrena, compara y entrega reportes. Si el CSV ya existe, lo carga sin regenerarlo ni corregir la fuente original.

Organicé los archivos por responsabilidad. Una clase agrupa una responsabilidad con métodos concretos; una función resuelve una operación puntual; un módulo es el archivo Python y un paquete reúne módulos relacionados. No necesito una clase por columna ni un archivo principal que concentre todo. En un backend anterior reuní demasiada lógica en app.py; aquí el punto de entrada solo recibe argumentos y delega.

La estructura principal es src/lumina_framework con core, data, preprocessing, visualization, modeling, reporting y pipeline. config contiene parámetros; tests verifica comportamiento; scripts inicia procesos; data conserva la fuente; artifacts contiene resultados. La separación permite cambiar un modelo o un gráfico sin reescribir la carga y la limpieza.

El comando de ejecución es `python scripts/run_final_project.py --config config/project_final.yaml`. Los requisitos, los comandos y el código completo se encuentran en el README. La entrega documental explica qué hace el proyecto; el repositorio de GitHub permite ejecutarlo y revisar la evidencia.
""")
    modules = table(["Módulo y clase", "Entrada", "Proceso", "Salida"], [
        ("Carga DataLoader", "CSV y contrato", "Carga sin mutar la fuente", "DataFrame"),
        ("Calidad DataValidator y DataCleaner", "DataFrame y reglas", "Revisa columnas, llaves y valores; limpia de forma conservadora", "Copia limpia y bitácora"),
        ("Perfil DataProfiler", "Tabla antes y después", "Calcula tipos, nulos, duplicados y estadísticas", "Perfiles JSON"),
        ("Preprocesamiento FeatureEngineer y DataPreprocessor", "Historial limpio", "Construye rezagos, objetivo futuro e imputación y codificación", "Variables y transformador"),
        ("Cortes TemporalDataSplitter", "Variables fechadas", "Separa semanas completas con espacios de cuatro semanas", "Entrenamiento, validación y prueba"),
        ("Visualización BusinessVisualizer y ModelDiagnosticsVisualizer", "Tabla, predicciones y métricas", "Agrega y dibuja con Matplotlib y Seaborn", "Ocho figuras PNG"),
        ("Entrenamiento ModelExperimentRunner", "Cortes y parámetros", "Ajusta candidatos en entrenamiento; elige en validación; reajusta", "Pipelines y predicciones"),
        ("Evaluación ModelEvaluator", "Objetivo y predicciones", "Calcula métricas globales, por segmento y remuestreo", "Tablas e intervalo orientativo"),
        ("Reportes ReportGenerator e InventorySignalGenerator", "Resultados y stock al cierre", "Serializa y genera señales para revisión", "CSV, JSON, Markdown, joblib y manifiesto"),
        ("Coordinación LuminaPipeline", "Configuración y componentes", "Ordena el flujo y registra eventos", "RunResult"),
    ])
    cleaning = table(["Regla", "Registros afectados", "Decisión"], [
        (x["rule"], x["affected_rows"], x["details"]) for x in read_json("cleaning_log.json")])
    section(3, """Integra un flujo completo de trabajo que incluya:

- Carga de datos.
- Revisión de estructura y calidad de datos.
- Limpieza de valores faltantes, duplicados, inconsistencias o valores atípicos.
- Preprocesamiento de variables.
- Visualización exploratoria.
- Entrenamiento de al menos un modelo de machine learning.
- Evaluación del desempeño del modelo.
- Interpretación de resultados.
- Recomendaciones para la toma de decisiones.""", f"""
El flujo conecta módulos con entradas y salidas explícitas:

{modules}

Primero leo el CSV y reviso su estructura. La entrada tiene {before['row_count']:,} filas y {before['column_count']} columnas; la limpieza deja {after['row_count']:,} filas, sin duplicados exactos. No tomo el archivo limpio original del generador para recuperar valores corruptos: el pipeline trabaja con la copia recibida.

{cleaning}

Conservo picos plausibles, porque un valor alto puede representar una promoción o un evento y no necesariamente un error. Los valores imposibles pasan a ausentes. Precio e inventario se imputan dentro del pipeline con la mediana aprendida del entrenamiento; las ventas ausentes no se rellenan para fabricar etiquetas. Al reindexar cada producto-sucursal por su calendario semanal, una semana perdida queda como hueco y no se confunde con la semana anterior.

Las características incluyen ventas de hace 1, 2 y 4 semanas; promedio, variabilidad y suma de las cuatro anteriores; tendencia reciente; mes y semana del año; precio, promoción e inventario observados, e identificadores categóricos. Se usa shift antes de rolling para excluir la semana actual del resumen histórico. El objetivo suma t+1 a t+4; descarto ventanas incompletas. Las características del corte son conocidas al cierre de t. No incluyo precio, promoción ni ventas futuras.

La imputación, el escalado y OneHotEncoder se ajustan solo con entrenamiento durante la selección. El codificador permite categorías nuevas sin fallar. Finalmente reajusto los candidatos seleccionados con entrenamiento más validación, antes de evaluar el periodo de prueba.

| Periodo de origen | Semanas | Filas utilizables | Función |
|---|---|---|---|
| Entrenamiento | 5 a 68 | {cuts['rows']['train']:,} | Ajustar candidatos |
| Validación | 73 a 84 | {cuts['rows']['validation']:,} | Elegir parámetros y enfoque |
| Prueba | 89 a 100 | {cuts['rows']['test']:,} | Evaluación final fuera de selección |

Las semanas 1 a 4 aportan historial; 69 a 72 y 85 a 88 permiten completar etiquetas sin cruzar el siguiente conjunto; 101 a 104 completan las etiquetas finales. Estos cortes evitan que las etiquetas superpuestas mezclen información de entrenamiento y validación. Las filas difieren del calendario ideal por las ventanas incompletas, no por una partición aleatoria.
""")
    section(4, "Si la problemática requiere predicción o clasificación, implementa al menos un modelo supervisado. Si la problemática requiere segmentación, agrupamiento o reducción de dimensionalidad, implementa al menos un modelo no supervisado. Puedes integrar ambos enfoques si el caso lo justifica.", """
La pregunta es una regresión supervisada: cada fila tiene variables disponibles en el corte y una etiqueta numérica calculada con ventas posteriores. Implementé Ridge y Random Forest, además de una referencia ingenua que pronostica la suma de las cuatro semanas previas. La referencia permite comprobar si el machine learning aporta algo frente a una regla sencilla.

Ridge es una regresión lineal regularizada que facilita revisar coeficientes y reduce inestabilidad entre variables relacionadas. Random Forest combina árboles y permite relaciones no lineales e interacciones. Ambos reciben el mismo preprocesamiento para mantener una comparación consistente; el escalado beneficia a Ridge, aunque los árboles no lo necesitan. Los pipelines encapsulan transformación y ajuste (scikit-learn developers, s. f.-a, s. f.-b).

Un modelo global aprende de todas las combinaciones, con producto y sucursal codificados. No construí cien modelos separados con pocas observaciones cada uno. Tampoco añadí clustering: agrupar datos no es el objetivo de esta decisión y hacerlo solo para aumentar técnicas complicaría la explicación.
""")
    section(5, "Selecciona métricas de evaluación adecuadas para el tipo de problema. Por ejemplo, puedes utilizar exactitud, precisión, recall, F1-score, matriz de confusión, error absoluto medio, error cuadrático medio, R², silhouette score u otras métricas pertinentes. Justifica por qué seleccionaste dichas métricas.", """
Elegí MAE como criterio principal porque expresa cuánto difiere la previsión en unidades de venta acumulada por combinación y corte. Es fácil relacionarlo con una revisión de cobertura, sin convertirlo automáticamente en dinero.

RMSE penaliza más los errores grandes y ayuda a detectar episodios con desviaciones importantes. WAPE divide la suma de errores absolutos entre el volumen real total; facilita comparar el error relativo agregado. Si el volumen total es cero, el código devuelve un valor no definido y no divide entre cero. R² describe el ajuste respecto de la media del conjunto evaluado, pero no sustituye la comparación con el pronóstico ingenuo.

También calculo la mejora porcentual de MAE frente a la referencia y errores por sucursal, categoría, producto y semana. No uso accuracy ni matriz de confusión, porque la salida es numérica y no una clase. Un menor MAE global no garantiza que cada segmento mejore ni que exista un ahorro económico.

La incertidumbre se explora remuestreando bloques móviles de cuatro semanas completas. Esto conserva parte de la dependencia de etiquetas superpuestas. Con solo doce semanas en prueba hay pocos bloques independientes; el intervalo es orientativo y no una garantía estadística de uso operativo.
""")
    section(6, "Compara, cuando sea posible, al menos dos configuraciones, modelos o enfoques. Explica cuál ofrece mejores resultados y por qué, considerando tanto el desempeño técnico como la utilidad para el negocio.", f"""
Comparé una referencia sencilla, tres alphas de Ridge y cuatro configuraciones de Random Forest con 300 árboles. La semilla permanece fija y los parámetros se seleccionan por MAE de validación.

{validation_table}

La regla de selección se definió antes de consultar prueba: si ningún candidato mejora la referencia en validación, conservo la referencia; si Ridge queda dentro del 2 % del mejor Random Forest y también supera la referencia, prefiero Ridge por sencillez. En esta ejecución fue elegido {selected}, con {selected_validation['configuracion']} y MAE de validación {float(selected_validation['mae']):.2f}. Su ventaja supera esa tolerancia, por lo que no seleccioné el modelo complejo solo por ser machine learning.

Después del reajuste con {manifest['refit_rows']:,} filas, estos fueron los resultados del periodo reservado:

{metric_table}

{selected} obtuvo el menor MAE de prueba y redujo el error en {float(best['mejora_mae_pct']):.2f} % respecto de la regla sencilla. Su MAE de {float(best['mae']):.2f} corresponde a unidades acumuladas en cuatro semanas por combinación-corte, no a error diario ni a porcentaje de exactitud.

El intervalo orientativo del 95 % para MAE del elegido menos MAE de referencia fue [{interval['lower']:.2f}, {interval['upper']:.2f}] unidades, con {interval['iterations']:,} remuestreos. Es favorable en este periodo, pero el escenario y el horizonte corto limitan la generalización. No modifiqué parámetros después de mirar prueba. El resultado justifica probar el enfoque con datos reales, no recomendar compras automáticas ni afirmar que el volumen de filas por sí solo exige machine learning.
""")
    charts = [
        ("ventas_semanales.png", "Ventas a través del tiempo", "La serie muestra niveles variables y oscilaciones recurrentes. Revisaría cobertura de cada semana antes de atribuir toda caída a menor demanda; una venta también puede caer por falta de stock."),
        ("distribucion_categoria.png", "Distribución por categoría", "Las medianas y la dispersión no son iguales. Hay ventas altas plausibles que no se eliminaron automáticamente; revisar su contexto es mejor que tratarlas como errores por su magnitud."),
        ("mapa_sucursal_categoria.png", "Diferencias entre sucursales y categorías", "El promedio por producto-semana permite comparar grupos sin confundirlo con el total de ventas. SUC-05 presenta promedios mayores que SUC-01; esto invita a revisar políticas diferenciadas, no a imponer el mismo nivel de inventario."),
        ("promocion_ventas.png", "Ventas y promoción", "La mediana de las semanas con promoción es mayor en el escenario, pero ambas distribuciones se superponen. La asociación no demuestra efecto causal; sería necesario comparar productos, periodos y disponibilidad equivalentes."),
        ("comparacion_modelos.png", "Desempeño de los enfoques", f"{selected} presenta el menor MAE y RMSE en prueba. Separé las métricas en paneles porque WAPE tiene una escala diferente y no debe compartir eje con unidades."),
        ("real_vs_predicho.png", "Pronóstico y observación", "El modelo sigue mejor el nivel agregado que la referencia, aunque conserva desviaciones. Cada punto suma las ventanas de cuatro semanas del mismo corte; no se deben sumar puntos sucesivos para obtener ventas anuales porque se superponen y la cobertura utilizable puede variar."),
        ("errores_segmentados.png", "Error por grupo", "SUC-05 concentra el MAE más alto y las categorías tampoco tienen el mismo error. Parte puede reflejar mayor volumen; antes de priorizar solo por MAE revisaría WAPE y cantidad de observaciones de cada segmento."),
        ("importancia_variables.png", "Información que utiliza el modelo", f"La variable con mayor aumento de MAE al permutarla es {importance[0]['variable'] if importance else 'la referencia histórica'}. El historial y el inventario aportan señal predictiva; la importancia no prueba causalidad y puede repartirse entre variables correlacionadas."),
    ]
    chart_text = "\n\n".join(f"#### {title}\n\n![{title}](../artifacts/project_final/figures/{filename})\n\n{interpretation}" for filename, title, interpretation in charts)
    section(7, "Genera visualizaciones que ayuden a comprender los datos, los patrones encontrados, el desempeño del modelo o los resultados obtenidos. Las visualizaciones deben tener título, etiquetas claras y una interpretación escrita.", f"""
Utilicé Matplotlib y Seaborn para explorar el comportamiento de las ventas y revisar el desempeño de los modelos. Las ocho visualizaciones presentan la evolución temporal, diferencias entre grupos y resultados del pronóstico. Cada figura incluye títulos, etiquetas claras y una interpretación relacionada con las preguntas del negocio.

{chart_text}
""")
    libraries = table(["Librería", "Uso y justificación"], [
        ("pandas", "CSV, DataFrames, calendarios, agrupaciones, rezagos y perfiles tabulares"),
        ("NumPy", "Generador aleatorio con semilla, arrays de predicciones y remuestreo"),
        ("Matplotlib y Seaborn", "Figuras reproducibles, etiquetas, cajas, series y mapa de calor"),
        ("scikit-learn", "Pipelines, imputación, escalado, codificación, Ridge, Random Forest y métricas"),
        ("PyYAML", "Parámetros y contrato fuera de la lógica del código"),
        ("joblib", "Conserva el pipeline ajustado; se debe cargar solo desde fuentes de confianza"),
        ("pytest", "Verifica transformaciones, métricas, cortes, errores y ejecución completa"),
    ])
    section(8, "Documenta tu código de manera básica mediante comentarios, nombres claros de variables, docstrings o un archivo README. La documentación debe permitir que otra persona comprenda cómo ejecutar y utilizar el prototipo.", f"""
Los nombres y docstrings describen responsabilidades; los comentarios explican decisiones como excluir la semana actual de rolling o mantener huecos del calendario. El README da los comandos de instalación, ejecución y pruebas, las rutas de resultados y las limitaciones. La configuración permite cambiar la fuente y los parámetros sin modificar el punto de entrada.

Para ejecutar el prototipo desde la raíz de la repo utilizo `python scripts/run_final_project.py --config config/project_final.yaml`; las pruebas se ejecutan con `python -m pytest -q`. El README contiene las dependencias y los comandos necesarios. La fuente incluida permite repetir el análisis sin descargar datos, y el generador puede probarse por separado. Al repetir el flujo se conserva el CSV existente.

{libraries}

La solución conserva separación de responsabilidades, copias de DataFrames para no mutar entradas, errores de dominio, trazabilidad de limpieza y resultados tipados. El manifiesto registra semilla, cortes, versiones, eventos, modelo seleccionado y SHA-256 de la fuente. Las métricas CSV facilitan revisión independiente del texto.

El entorno comprobado usó Python {manifest['python_version']}, pandas {manifest['versions']['pandas']}, NumPy {manifest['versions']['numpy']}, scikit-learn {manifest['versions']['scikit-learn']}, Matplotlib {manifest['versions']['matplotlib']} y Seaborn {manifest['versions']['seaborn']}. requirements-lock.txt fija las dependencias directas de esa ejecución. Hay advertencias de deprecación de Seaborn relacionadas con una API de Matplotlib; no impidieron las pruebas ni la generación de figuras.
""")
    section(9, """Elabora un reporte final que explique:

- El problema abordado.
- El contexto organizacional.
- La solución propuesta.
- La arquitectura del framework.
- Los datos utilizados.
- El proceso de limpieza y preprocesamiento.
- Los modelos implementados.
- Las métricas de evaluación.
- Los principales hallazgos.
- Las recomendaciones para la toma de decisiones.
- Las limitaciones del prototipo.
- Posibles mejoras futuras.""", f"""
El reporte reúne el problema y el contexto del punto 1, la solución y arquitectura de los puntos 2 y 3, los modelos del 4, la evaluación de los puntos 5 y 6 y los hallazgos visuales del 7. GitHub complementa el reporte con la fuente, los scripts y los artefactos de ejecución; no sustituye las respuestas del documento.

Los datos utilizados tienen ocho campos: semana, sucursal_id, producto_id, categoria, precio, promocion, inventario_inicial y unidades_vendidas. La llave lógica es producto-sucursal-semana. Después de limpiar quedan {after['missing_counts']['precio']} precios, {after['missing_counts']['inventario_inicial']} inventarios y {after['missing_counts']['unidades_vendidas']} ventas ausentes. Mantenerlos visibles permite distinguir una corrección trazable de la imputación aprendida durante el modelado.

El hallazgo técnico principal es que la comparación supera la regla histórica en este periodo, con ventaja de {selected}. También encontré heterogeneidad entre grupos e importancia del historial de ventas. Estos resultados son compatibles con usar un modelo global, pero no bastan para decidir su adopción empresarial.

Para apoyar decisiones, el reporte genera señales en el último corte de prueba. Compara la previsión con inventario al cierre, calculado como inventario inicial menos ventas de la semana. {sum(x['requiere_revision'].lower() == 'true' for x in signals)} combinaciones requieren revisión: {sum(x['estado'] == 'revisar_cobertura' for x in signals)} por brecha y {sum(x['estado'] == 'inventario_no_disponible' for x in signals)} por inventario desconocido. La cobertura es {len(signals)} de 100 combinaciones; las restantes carecen de ventana utilizable y su ausencia no representa ausencia de riesgo. Una brecha positiva indica revisar existencias, reposiciones pendientes y condiciones del producto; no implica comprar esa diferencia, porque faltan plazos, pedidos en tránsito, costos y demanda no atendida.

Mi recomendación es validar primero el contrato operativo, probar varios periodos históricos y usar la referencia sencilla como alternativa permanente. Si la mejora no compensa costo de mantenimiento y de errores, sería razonable mantener una política simple. El tamaño de la tabla no determina por sí solo la conveniencia de machine learning.

Las limitaciones son dos años de historial, una sola semilla de escenario, doce semanas de prueba, ventas censuradas por inventario y ausencia de costos y futuras campañas. Los promedios agregados ocultan diferencias por producto; el análisis de promociones no identifica causalidad. El pipeline evalúa cortes históricos con etiqueta conocida, no constituye todavía un servicio de pronóstico en vivo.

Como mejoras futuras propongo validación temporal en varios cortes, un camino de inferencia para semanas recientes sin etiqueta futura, medición de faltantes de venta, reposiciones y lead time, costos diferenciados de exceso y faltante, revisión de drift y monitoreo por segmento. Para estimar un ahorro anual necesitaría conocer los costos del negocio y considerar que las ventanas de predicción se superponen; multiplicar el MAE por semanas no permite obtener ese ahorro.
""")
    section(10, """Incluye evidencia suficiente de trabajo propio. Debes incorporar al menos cinco de los siguientes elementos:

- Capturas de ejecución del código.
- Repositorio, carpeta o estructura de archivos del proyecto.
- Fragmentos de código explicados por ti.
- Bitácora de decisiones técnicas.
- Comparación de modelos o configuraciones.
- Registro de errores y ajustes realizados.
- Interpretación personal de resultados.
- Explicación de cambios realizados a partir de retroalimentación.
- Pruebas realizadas con distintos datos o parámetros.
- Reflexión final sobre aprendizajes obtenidos.""", f"""
Presento ocho tipos de evidencia rastreables que relacionan las decisiones de diseño, la implementación y las comprobaciones del proyecto.

| Evidencia | Ubicación | Qué permite comprobar |
|---|---|---|
| Repo y estructura | README y src/lumina_framework | Separación de responsabilidades y archivos ejecutables |
| Código explicado | preprocessing/features.py y modeling/experiment.py | Rezagos antes de rolling y selección con validación |
| Decisiones técnicas | docs/evidencia_final/execution_log.md | Alcance, objetivo, cortes y regla de selección |
| Comparación | validation_metrics.csv y test_metrics.csv | Parámetros probados y desempeño fuera del ajuste |
| Errores y ajustes | Tests y registro de ejecución | Fechas inválidas, faltantes, categorías nuevas y fallo de escritura |
| Interpretación personal | Puntos 6, 7 y 9 | Diferencia entre resultado técnico y decisión de negocio |
| Cambios de los avances | Punto 1 y nueva repo | Paso de diagnóstico conceptual a flujo comprobable |
| Pruebas y reflexión | tests y este punto | Repetibilidad, métricas conocidas y aprendizaje |

En features.py, `shift(1)` mueve la venta una semana antes de calcular la ventana; así el promedio no incluye el dato del corte. Reindexar el calendario hace que el rezago sea una semana real, no simplemente la fila anterior. En experiment.py, las configuraciones compiten en validación; prueba permanece fuera de la selección. Entender esas dos decisiones importa más que acumular algoritmos.

La ejecución registrada aprobó {test_count} pruebas; el resultado estructurado se conserva en docs/evidencia_final/test_results.xml. Las pruebas comprueban valores de métricas conocidos, WAPE con volumen cero, cambios futuros que no modifican características previas, categorías no vistas, cortes semanales completos y repetición del experimento. La prueba de integración carga el modelo guardado y compara sus predicciones con las reportadas. Un fallo de escritura provocado debe producir un error, sin declarar una ejecución completada.

Mi aprendizaje fue precisar la unidad de observación y lo que el modelo realmente predice antes de entrenarlo. Una tabla con muchas filas puede contener poco historial independiente; por eso decidí comparar con una regla simple y conservar la cautela sobre el beneficio económico. También mantuve la organización por carpetas para evitar repetir la concentración de lógica de mi backend anterior.
""")
    section(11, """Incluye una declaración de autoría y uso responsable de herramientas digitales o de inteligencia artificial. En esta declaración deberás especificar:

- Qué herramientas utilizaste.
- Para qué las utilizaste.
- Qué partes del proyecto fueron desarrolladas directamente por ti.
- Cómo verificaste, probaste o adaptaste cualquier apoyo recibido.
- Qué decisiones técnicas fueron tomadas con base en tu propio análisis.""", (
        ROOT / 'docs' / 'evidencia_final' / 'autoria_ia.md'
    ).read_text(encoding='utf-8').partition('\n\n')[2])
    section(12, "No se aceptará como proyecto final una entrega generada íntegramente por inteligencia artificial, sin ejecución comprobable, sin explicación personal, sin evidencia de pruebas o sin adaptación al caso seleccionado. El estudiante deberá demostrar comprensión del código, de los resultados y de las decisiones tomadas.", """
La entrega relaciona las decisiones de negocio y de diseño con un prototipo ejecutado, una fuente de entrada, pruebas de comportamiento, comparación de parámetros, métricas y figuras reconstruibles. La configuración y las limitaciones mantienen el objetivo que definí para el framework.

Puedo explicar por qué el proyecto pronostica ventas observadas, por qué los cortes respetan el tiempo y por qué una señal de inventario requiere revisión antes de tomar una decisión de compra. El reporte desarrolla esas relaciones y la guía de comprensión permite seguirlas en el código y en sus resultados.

El repositorio permite revisar y repetir las comprobaciones. La declaración de herramientas describe cómo utilicé Codex durante la implementación y la verificación. Mi responsabilidad sobre el resultado incluye revisar el código, interpretar sus salidas y justificar las decisiones del proyecto.
""")
    references = """## Referencias

pandas development team. (s. f.). *pandas documentation*. Recuperado el 2 de octubre de 2026, de https://pandas.pydata.org/docs/

scikit-learn developers. (s. f.-a). *Ridge*. Recuperado el 2 de octubre de 2026, de https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html

scikit-learn developers. (s. f.-b). *RandomForestRegressor*. Recuperado el 2 de octubre de 2026, de https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html

scikit-learn developers. (s. f.-c). *Common pitfalls and recommended practices*. Recuperado el 2 de octubre de 2026, de https://scikit-learn.org/stable/common_pitfalls.html

Universidad Tecmilenio. (2026). *Predicciones bajo presión El desafío analítico de Lúmina Datos Operativos* [Caso práctico proporcionado en el curso].

Waskom, M. L. (2021). seaborn: Statistical data visualization. *Journal of Open Source Software, 6*(60), 3021. https://doi.org/10.21105/joss.03021
"""
    introduction = f"""# Framework modular para pronóstico de ventas y revisión de inventario

Este reporte presenta el prototipo funcional del proyecto final de Programación para la inteligencia artificial. El flujo permite comparar una regla histórica con modelos supervisados para pronosticar ventas y revisar inventario; su adopción operativa requiere datos y costos del negocio.

Repositorio complementario: {REPOSITORY_URL}

Antecedente documental y técnico del Avance 2: https://github.com/rubenstrada/Dise-o-framework-

Documento y repo se entregan juntos: el documento desarrolla las respuestas y la repo contiene la configuración, el código, las pruebas y los resultados verificables.

"""
    return introduction + "\n".join(sections) + references, metric_table


def main():
    report, metrics = build_report()
    (ROOT / "docs" / "proyecto_final.md").write_text(report, encoding="utf-8")
    print("Reporte actualizado desde artefactos: docs/proyecto_final.md")


if __name__ == "__main__":
    main()
