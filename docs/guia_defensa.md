# Guía breve para explicar el Avance 2

## Idea central en 30 segundos

El framework está organizado por responsabilidades. Cada módulo recibe una
entrada clara, hace una sola parte del proceso y devuelve un resultado tipado.
Como el caso no incluye datos, columnas, target ni horizonte, la configuración
de ejemplo conserva esos campos vacíos y el sistema responde `blocked`. Esto
evita aparentar resultados y deja preparado el flujo para cuando llegue la
fuente real.

## Clase, objeto, atributo y método

- Una **clase** define una responsabilidad. Ejemplo: `DataLoader` define cómo
  cargar una fuente.
- Un **objeto** es una instancia de esa clase utilizada durante una corrida.
- Un **atributo** conserva estado o configuración. Ejemplo: `source_path`.
- Un **método** realiza una acción. Ejemplo: `load()`, `validate()` o `clean()`.

## Por qué se exploran los datos antes de modelar

Los PDF solo mencionan tipos generales de información. No confirman nombres de
tablas, columnas, unidad de observación, target ni horizonte. Por eso el primer
objetivo es revisar estructura, faltantes, duplicados, tipos y distribuciones.
Solo después de conocer esa información se puede definir responsablemente un
problema predictivo y sus variables.

## Diferencia entre los módulos

- `DataLoader`: abre la fuente y no la corrige.
- `DataValidator`: observa problemas y no modifica la tabla.
- `DataCleaner`: aplica únicamente reglas autorizadas y registra cambios.
- `DataProfiler`: resume estructura, faltantes, duplicados y estadísticos.
- `EDAVisualizer`: genera gráficos solo con roles configurados.
- `DataPreprocessor`: divide por tiempo y construye transformaciones.
- `ModelTrainer`: recibe un estimador externo y lo ajusta con entrenamiento.
- `ModelEvaluator`: compara el candidato con una línea base.
- `ReportGenerator`: convierte resultados en archivos interpretables.
- `LuminaPipeline`: coordina el orden sin absorber la lógica de los demás.

## Tres decisiones que conviene poder defender

1. Se usó configuración YAML para no fijar nombres de columnas en el código.
2. Se separa pasado y futuro antes de ajustar transformaciones para evitar fuga
   de información.
3. Un modelo no se recomienda si no supera una línea base bajo las mismas
   observaciones.

## Evidencia real

- Hay 28 pruebas automatizadas aprobadas que cubren el framework, la exploración reproducible, los títulos y la trazabilidad en GitHub.
- Se detectó una inconsistencia entre el diagrama y el contrato respecto al
  horizonte. Primero se añadió una prueba que falló y después se corrigió el
  contrato, el YAML y el `ReadinessChecker`.
- El informe final explica la arquitectura, las clases y las visualizaciones
  propuestas con tablas. GitHub agrega los diagramas Mermaid, el generador
  Matplotlib y tres gráficas con títulos orientados a su contenido.
- `docs/exploracion_sintetica.md` muestra el código de Pandas, Matplotlib y
  Seaborn junto a los PNG producidos por el programa.
- `DataProfiler` puede describir un `DataFrame` autorizado sin exigir target;
  el significado de las columnas se valida después con el diccionario.

## Preguntas probables

**¿Por qué no entrenaste un modelo?**  Porque no hay target, horizonte ni
observaciones. Entrenar requeriría inventar la definición del problema.

**¿Entonces sí hay código funcional?**  Sí. Los contratos, carga, validación,
limpieza, perfilado, visualización configurable, preprocesamiento, entrenamiento,
evaluación, reportes y orquestación tienen una primera implementación y pruebas.

**¿Qué se necesita para continuar?**  Fuente autorizada, diccionario, llave,
unidad de observación, fechas, target, horizonte, baseline y costo del error.

## Cómo explicar mi participación y el uso de IA

La organización del framework parte de una decisión personal anterior a la
implementación. En un backend de ERP concentré demasiada lógica en pocos
archivos, especialmente en `app.py`, y después resultó difícil localizar
responsabilidades y modificar una parte sin revisar muchas otras. Por eso en
este proyecto separé carga, validación, limpieza, perfilado, visualización,
preprocesamiento, modelado y reportes.

La misma decisión se relaciona con una situación que he observado en mi
trabajo: existen scripts separados para extracción, preparación y limpieza de
información, y localizar procesos o reutilizar soluciones puede consumir mucho
tiempo. El proyecto me permitió conectar clases, métodos, modularidad y manejo
de excepciones con un problema que también aparece fuera del curso.

Codex se utilizó para explorar alternativas, convertir estas decisiones en una
implementación, generar pruebas y revisar consistencia. Yo definí las
responsabilidades, los comportamientos que no debían permitirse y las
condiciones para avanzar. Por ejemplo, decidí que el framework no debía
inventar columnas, target, horizonte ni resultados, y que una posible
predicción temporal debía separar pasado y futuro antes del ajuste.

El proceso fue iterativo. La inconsistencia del horizonte se convirtió primero
en una prueba fallida y después en una corrección del contrato, el YAML y el
verificador. Esta evidencia permite explicar que la IA funcionó como apoyo
técnico bajo revisión, no como sustituto de las decisiones ni de la
responsabilidad del estudiante.

La idea que debo poder defender es sencilla: no basta con que el código
funcione. Debo explicar por qué existe cada clase, qué recibe cada método, qué
devuelve y cómo se relaciona con el resto del framework.
