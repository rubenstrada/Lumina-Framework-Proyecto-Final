# Cómo comprendí el problema y utilicé la inteligencia artificial

Mi punto de partida fue comprender la lógica del negocio y definir qué problema debía resolver el framework antes de escribir código. Ya había trabajado con modelos, por lo que primero necesitaba establecer qué información analizar, qué resultado obtener y cómo podría utilizarse para tomar decisiones.

En este caso, relacioné el historial de ventas con la revisión del inventario por producto y sucursal. Comprendí que las ventas registradas no representan necesariamente toda la demanda: si se agota el inventario, pueden existir necesidades de compra que no quedan reflejadas en las ventas. Por eso delimité el objetivo como pronosticar ventas observadas y generar señales de revisión, sin presentar las predicciones como órdenes automáticas de compra.

Antes de evaluar modelos necesitaba explorar los datos y comprender su comportamiento. Revisar columnas, tipos, frecuencia temporal, faltantes, duplicados y diferencias entre grupos permite identificar qué información es utilizable y qué transformaciones requiere. También consideré que un valor alto puede corresponder a un comportamiento válido del negocio, por lo que no debía eliminarse automáticamente por parecer atípico.

Codex me ayudó a explorar alternativas y discutir horizontes de predicción. Las decisiones finales las tomé después de relacionar esas alternativas con el objetivo del proyecto. Definí un horizonte de cuatro semanas para obtener una salida concreta y comparable. También consideré necesario comparar los modelos con una regla histórica sencilla: tener muchas filas o utilizar machine learning no demuestra, por sí solo, que la solución aporte valor.

La organización del framework surgió de experiencias anteriores. En un backend de ERP había concentrado demasiada lógica en archivos como app.py, lo que dificultaba localizar responsabilidades y modificar componentes. Esa experiencia influyó en mi decisión de separar carga, validación, limpieza, preprocesamiento, visualización, modelado, evaluación y reportes. Tenía claro cómo quería organizar la solución y qué responsabilidad debían tener sus componentes, métodos y funciones.

Utilicé Codex para acelerar la escritura del código, desarrollar las definiciones que fui estableciendo y apoyar la revisión y las comprobaciones de la implementación. El trabajo fue iterativo: discutí alternativas, indiqué los comportamientos esperados y solicité ajustes para mantener la organización y el alcance que buscaba. Codex también apoyó la ejecución de pruebas automatizadas y la preparación de la documentación.

El apoyo se adaptó al contrato de datos, al objetivo de cuatro semanas y a la comparación con una referencia sencilla. La implementación se comprobó mediante ejecución nativa, pruebas, recarga del pipeline guardado y revisión de figuras y artefactos. La bitácora conserva decisiones y ajustes; las comprobaciones se realizaron con asistencia de Codex.

Las pruebas y los resultados permiten comprobar el funcionamiento técnico. Mi responsabilidad es comprender y explicar cómo se construyen las variables, por qué se respeta el orden temporal, cómo se comparan los modelos y qué limitaciones tienen sus resultados. La IA fue una herramienta de apoyo dentro de ese proceso; las decisiones finales sobre el problema, el alcance y la organización permanecieron bajo mi criterio.

Para desarrollar y verificar el prototipo utilicé Python, pandas, NumPy, scikit-learn, Matplotlib, Seaborn, PyYAML, joblib y pytest. Git y GitHub conservan y presentan la evidencia; Microsoft Word se utilizó para el documento. Las figuras son salidas de Matplotlib y Seaborn ejecutadas sobre los datos del proyecto.
