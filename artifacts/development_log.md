# Bitácora técnica de desarrollo

## Task 1 Núcleo y preparación

- Se creó el entorno virtual local para no modificar el Python global.
- Incidencia: la primera ejecución no encontró `pytest`; se instaló dentro de `.venv` y se repitió la prueba.
- Verificación RED: la prueba falló con `ModuleNotFoundError: lumina_framework` antes de crear las clases.
- Verificación GREEN: `2 passed in 0.02s` al ejecutar `python -m pytest tests/test_config_and_readiness.py -v`.
- Resultado: `FrameworkConfig`, `DatasetContract`, `ReadinessChecker`, `RunContext` y excepciones de dominio disponibles.

## Task 2 Carga

- Verificación RED: `ModuleNotFoundError: lumina_framework.data` antes de crear `DataLoader`.
- Verificación GREEN: `3 passed in 0.40s` al ejecutar `python -m pytest tests/test_loader.py -v`.
- Resultado: el cargador rechaza rutas ausentes y extensiones no admitidas, y conserva los encabezados originales del CSV.

## Task 3 Validación limpieza y perfilado

- Verificación RED: `ModuleNotFoundError: lumina_framework.data.cleaner` antes de crear los tres componentes.
- Verificación GREEN enfocada: `5 passed in 0.36s`.
- Regresión completa: `10 passed in 0.42s`.
- Resultado: la validación no modifica datos; la limpieza solo aplica reglas explícitas y devuelve una bitácora; el perfilado describe cualquier tabla sin exigir una etiqueta.

## Task 4 Preprocesamiento y visualización

- Verificación RED: faltaban los paquetes `preprocessing` y `visualization`.
- Verificación GREEN enfocada: `5 passed in 4.74s`.
- Regresión completa: `15 passed in 1.79s`.
- Resultado: el preprocesador exige etiqueta y predictores configurados, respeta el orden temporal y deja el transformador sin ajustar; el visualizador valida roles, genera tres tipos de figura y no modifica la entrada.
- Nota: las figuras creadas durante las pruebas usan un fixture técnico mínimo y no representan datos de Lumina.

## Task 5 Modelado y evaluación

- Verificación RED: faltaba el paquete `lumina_framework.modeling`.
- Verificación GREEN enfocada: `4 passed in 1.40s`.
- Regresión completa: `19 passed in 3.39s`.
- Resultado: `ModelTrainer` recibe un estimador externo y ajusta preprocesamiento solo con entrenamiento; `ModelEvaluator` rechaza entradas inválidas y nunca recomienda un candidato con MAE peor que la línea base.
- Limitación conservada: no se eligió algoritmo ni se entrenó un modelo atribuido a Lumina.

## Task 6 Reporte orquestación y CLI

- Verificación RED: faltaban `load_yaml_configuration` y el paquete `pipeline`.
- Verificación GREEN enfocada: `5 passed in 0.44s`.
- Regresión completa: `22 passed in 2.92s`.
- Resultado: `assess()` informa preparación sin abrir archivos; `run_profile()` ejecuta únicamente carga, validación, limpieza explícita y perfilado; el resultado se serializa y los reportes conservan un manifiesto.

## Task 7 Integración y documentación técnica

- Se instaló el paquete local en modo editable para comprobar que la estructura declarada en `pyproject.toml` puede importarse como un proyecto real.
- Se ejecutó la CLI con la configuración de ejemplo todavía vacía. Terminó correctamente con estado `blocked` y los códigos `missing_source`, `missing_columns`, `missing_target` y `missing_prediction_horizon`; este bloqueo es intencional porque no se recibieron datos, esquema, variable objetivo ni horizonte confirmado.
- Se revisó la correspondencia entre las clases implementadas, el árbol de carpetas, el README, la arquitectura y los requisitos mínimos de datos.
- Decisión académica: no se creó un CSV atribuido a Lumina ni se reportaron resultados predictivos empresariales. Los DataFrames pequeños de las pruebas son fixtures técnicos y están aislados en `tests/`.

## Incidencia de consistencia detectada antes del entregable

- Hallazgo: el diagrama indicaba que el modelado requería un horizonte confirmado, pero la primera versión de `ReadinessChecker` solo comprobaba fuente, columnas y variable objetivo.
- Prueba RED: `4 failed, 2 passed` al añadir la expectativa `missing_prediction_horizon`.
- Corrección: se agregó `prediction_horizon` al contrato, al YAML y a la comprobación de preparación.
- Prueba GREEN enfocada: `6 passed in 0.43s`.

## Task 8 Verificación y preparación del entregable

- Regresión del proyecto antes de publicar el generador visual: `23 passed`.
- `compileall` terminó sin errores de sintaxis en `src/`.
- La CLI conservó el estado `blocked` con los cuatro prerrequisitos faltantes.
- Se generaron tres visuales propios y se corrigió la legibilidad del diagrama principal después de inspeccionarlo.
- El contenido se integró en la plantilla académica final y se revisó visualmente página por página.
- GitHub quedó establecido como medio de entrega del desarrollo técnico; el repositorio excluye `.venv`, cachés, archivos compilados y datos operativos.

## Task 9 Visuales reproducibles y evidencia en GitHub

- Prueba RED: el test del generador falló porque `scripts/generate_visuals.py` todavía no existía.
- Implementación: se añadió un script comentado con Matplotlib y `matplotlib.patches` que genera arquitectura, mapa de clases y bocetos exploratorios.
- Prueba GREEN: el generador creó los tres PNG en una carpeta temporal y validó firma y tamaño de cada archivo.
- GitHub: `docs/arquitectura.md` incorpora diagramas Mermaid cuyo código fuente puede revisarse junto con el resultado renderizado.
- Presentación final: el README usa Mermaid directamente y los PNG generados se mantienen fuera del control de versiones para que la evidencia principal sea el código reproducible.
- Alcance conservado: los bocetos no contienen observaciones, escalas ni resultados atribuidos a Lumina.
- Regresión final: `24 passed`.

## Task 10 Exploración genérica sin esquema confirmado

- Se separó el perfilado físico de la interpretación semántica: el primero puede describir cualquier `DataFrame` autorizado; la segunda requiere el diccionario de datos.
- El README documenta el recorrido `CSV → DataLoader → DataFrame → DataProfiler → ProfileResult → JSON` y muestra el uso directo del perfilador sin definir target.
- Se explicó por qué Pandas conserva la tabla durante el descubrimiento y por qué NumPy se reserva para bloques numéricos y cálculos vectorizados.
- No se declaró soporte para grandes volúmenes: la implementación actual trabaja en memoria y solo evolucionará si una prueba real excede la memoria o el tiempo acordado.
- El informe final sustituyó las imágenes por tablas explicativas. Mermaid y el generador Matplotlib quedan en GitHub como material técnico complementario.

## Task 11 Alineación con el documento académico final

- El README se organizó para mostrar la correspondencia directa con los once puntos de la actividad.
- Se añadió la cuarta visualización propuesta en el documento: comparación de valor real, candidato y baseline.
- GitHub se documentó como medio de entrega del desarrollo técnico y no solo como enlace complementario.
- La nota de inteligencia artificial se amplió con la misma narrativa del documento: experiencia previa con un backend de ERP, relación con procesos reales de extracción y limpieza, decisiones técnicas personales, trabajo iterativo con Codex y responsabilidad final del estudiante.
- No se modificó el código del framework ni se agregaron supuestos sobre datos, columnas, target, horizonte o volumen.

## Task 12 Exploración EDA reproducible

- Motivo: la rúbrica avanzada solicita ejecutar estadísticas descriptivas y representaciones con Matplotlib y Seaborn. El recorrido permite revisar los datos antes de elegir transformaciones o plantear un objetivo predictivo.
- Prueba RED: el generador reproducible ya cumplía con la estructura esperada, pero la prueba de integración falló porque todavía no se escribían `resumen_demo.json`, `resumen_demo.md` ni las tres visualizaciones.
- Implementación: `scripts/run_synthetic_eda_demo.py` crea en memoria 74 filas con semilla `20260916`, cinco campos terminados en `_demo`, faltantes controlados y dos duplicados exactos.
- Reutilización: la tabla se entrega directamente a `DataProfiler` y `EDAVisualizer`. No se creó un CSV temporal artificial para forzar `DataLoader`, que ya cuenta con pruebas independientes.
- Evidencia: se generaron una serie temporal, una distribución y un mapa de calor con títulos que comunican el contenido. Los resultados también se conservan en JSON y Markdown.
- Trazabilidad en GitHub: `docs/exploracion_sintetica.md` muestra las importaciones, el perfilado, las llamadas al visualizador y las funciones `lineplot`, `histplot`, `heatmap` y `savefig` junto a sus salidas.
- Alcance conservado: el esquema, target, horizonte y modelo empresarial permanecen pendientes hasta recibir la fuente autorizada.
- Prueba GREEN enfocada final: `6 passed in 4.72s`.
- Regresión final: `28 passed`.
