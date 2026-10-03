# Diseño del proyecto final del framework Lumina

## Propósito

Transformar la arquitectura preliminar del Avance 2 en un prototipo funcional y reproducible que cargue, valide, limpie, transforme, explore, modele, evalúe e interprete datos tabulares. El prototipo debe responder la actividad final punto por punto y mantener una separación clara entre la explicación académica del documento y la evidencia técnica de GitHub.

El proyecto evaluará si un modelo supervisado mejora una referencia sencilla para estimar ventas futuras. No asumirá desde el inicio que machine learning es necesario ni afirmará que los resultados simulados representan el comportamiento real de Red Comercial Boreal.

## Problema y decisión apoyada

- **Unidad de observación:** un producto en una sucursal durante una semana.
- **Resultado medible:** ventas acumuladas durante las cuatro semanas posteriores a la fecha de corte.
- **Interpretación:** las ventas futuras funcionan como aproximación de la demanda observada.
- **Decisión apoyada:** identificar combinaciones producto-sucursal que requieren revisión de inventario para cubrir las siguientes cuatro semanas.
- **Límite:** las ventas pueden subestimar la demanda cuando existe desabasto; el prototipo no automatizará órdenes de compra.

## Alcance y exclusiones

### Incluido

- Generación reproducible de un escenario empresarial controlado.
- Archivo CSV con aproximadamente 10,400 observaciones.
- Problemas de calidad introducidos de forma controlada y documentada.
- Flujo completo desde la carga hasta la generación de reportes.
- Comparación temporal entre una línea base, Ridge y Random Forest.
- Métricas globales y segmentadas.
- Visualizaciones exploratorias y de desempeño generadas con código.
- Modelo y preprocesamiento persistidos como un único pipeline.
- README, bitácora, evidencias, reporte académico y paquete final.

### Excluido

- Datos personales de clientes.
- Base de datos, API, frontend o dashboard interactivo.
- Redes neuronales, microservicios o infraestructura productiva.
- Segmentación no supervisada sin una pregunta de negocio que la justifique.
- Afirmaciones de rentabilidad o recomendaciones operativas reales sin costos y datos empresariales.

## Datos del escenario

La fuente tendrá 20 productos, 5 sucursales y 104 semanas. La semilla aleatoria será fija para que cada ejecución produzca el mismo resultado.

### Columnas originales

| Columna | Rol |
|---|---|
| `semana` | Fecha de inicio de la semana |
| `sucursal_id` | Dimensión operativa |
| `producto_id` | Dimensión comercial |
| `categoria` | Familia del producto |
| `precio` | Precio vigente |
| `promocion` | Indicador conocido para la semana |
| `inventario_inicial` | Existencia disponible al inicio |
| `unidades_vendidas` | Medida observada |

### Comportamiento generado

La simulación combinará demanda base por producto, efecto de sucursal, categoría, estacionalidad, tendencia, promociones, variación de precio, reposición periódica, retrasos ocasionales, límite por inventario, agotamientos, picos plausibles y ruido. La complejidad adicional vivirá principalmente en el generador y no aumentará innecesariamente el contrato público del dataset.

Después de generar una tabla coherente se creará una versión de entrada con faltantes, duplicados, diferencias de mayúsculas o espacios, fechas inválidas, valores imposibles y atípicos controlados. El código conservará las cantidades introducidas para verificar que el pipeline las detecta.

## Calidad, limpieza y preprocesamiento

La limpieza será conservadora y trazable:

1. Preservar la fuente original.
2. Validar columnas, tipos, llave producto-sucursal-semana y cobertura temporal.
3. Eliminar duplicados exactos y registrar el número de filas afectadas.
4. Normalizar categorías mediante reglas explícitas.
5. Convertir fechas y reportar valores inválidos.
6. Marcar valores físicamente imposibles antes de corregirlos o excluirlos.
7. Imputar faltantes mediante transformadores ajustados únicamente con entrenamiento.
8. Detectar atípicos, conservar picos plausibles y limitar solo valores claramente corruptos.
9. Registrar cada transformación en un reporte de calidad.

### Ingeniería de características

Por cada producto y sucursal se crearán, sin utilizar el futuro:

- ventas con rezagos de 1, 2 y 4 semanas;
- promedio y variabilidad de las cuatro semanas anteriores;
- tendencia reciente;
- mes y semana del año;
- relación entre inventario actual y venta promedio reciente;
- objetivo igual a la suma de ventas de las cuatro semanas posteriores.

Los identificadores se tratarán como categorías, no como números continuos. El ajuste de imputación, codificación y escalado ocurrirá dentro de pipelines de scikit-learn entrenados solo con el pasado.

## Separación temporal

Las filas no se dividirán aleatoriamente. Para cada combinación producto-sucursal se respetará esta secuencia:

| Semanas | Uso |
|---|---|
| 1 a 4 | Historial inicial para rezagos |
| 5 a 68 | Entrenamiento |
| 69 a 72 | Separación correspondiente al horizonte futuro |
| 73 a 84 | Validación |
| 85 a 88 | Segunda separación temporal |
| 89 a 100 | Prueba final |
| 101 a 104 | Horizonte futuro de las últimas observaciones de prueba |

La prueba final se consultará una sola vez después de seleccionar configuración con entrenamiento y validación.

## Modelos y comparación

Se entrenará un modelo global que comparta patrones entre productos y sucursales.

1. **Referencia ingenua:** usar como pronóstico la suma de las cuatro semanas anteriores.
2. **Ridge:** candidato lineal, regularizado e interpretable.
3. **Random Forest:** candidato no lineal para interacciones entre producto, sucursal, calendario, precio y promoción.

El proyecto no presupone que Random Forest debe ganar. Si Ridge obtiene desempeño equivalente se preferirá por sencillez. Si ninguno mejora la referencia, la recomendación será conservar el método simple.

## Evaluación

- **MAE:** métrica primaria en unidades.
- **RMSE:** sensibilidad a errores grandes.
- **WAPE:** error total relativo al volumen, robusto frente a semanas con cero ventas.
- **R²:** variación explicada como referencia complementaria.
- **Mejora porcentual contra la línea base:** contexto para la utilidad incremental.

Se reportarán métricas generales y por sucursal, categoría, producto y semana de prueba. Un remuestreo por bloques semanales estimará la incertidumbre de la diferencia de MAE sin tratar observaciones de una misma semana como independientes.

## Visualizaciones

Todas las figuras se generarán con Matplotlib y Seaborn, tendrán títulos de negocio, ejes, unidades, leyendas cuando correspondan e interpretación escrita.

### Exploración

1. Evolución semanal de ventas.
2. Distribución y valores atípicos por categoría.
3. Mapa de calor de ventas por sucursal y categoría.
4. Comparación de ventas con y sin promoción.

### Desempeño

5. Comparación de MAE, RMSE y WAPE por enfoque.
6. Valores reales y predichos durante el periodo de prueba.
7. Distribución y segmentación de errores.
8. Importancia por permutación y, para Ridge, coeficientes transformados.

Las imágenes serán salidas reproducibles del código, no gráficos creados por inteligencia artificial.

## Arquitectura y evolución del repositorio

Se conservará la organización por capacidades del Avance 2. Se ampliarán componentes existentes y se agregarán solo límites que representen una responsabilidad nueva.

```text
src/lumina_framework/
├── core/              contratos, configuración, contexto y errores
├── data/              generación, carga, validación, limpieza y perfilado
├── preprocessing/     características, particiones y transformadores
├── visualization/     exploración y diagnóstico de modelos
├── modeling/          referencia, entrenamiento, comparación y evaluación
├── reporting/         métricas, manifiestos y reporte técnico
├── pipeline/          coordinación de extremo a extremo
└── cli.py             argumentos y punto de entrada
```

El orquestador coordinará el flujo, pero no contendrá reglas específicas de limpieza, gráficos o modelos. Los resultados continuarán representándose mediante objetos tipados y errores de dominio.

## Flujo de ejecución

```text
Configuración
    -> generación o recepción del CSV
    -> carga inmutable
    -> validación y perfil inicial
    -> limpieza trazable
    -> creación de características y target
    -> partición temporal
    -> ajuste de preprocesamiento y modelos
    -> evaluación comparativa
    -> interpretación y visualizaciones
    -> alertas orientativas de inventario
    -> manifiesto, métricas y reporte
```

Un comando reproducible deberá ejecutar el recorrido completo y guardar todos los artefactos con una identidad de corrida.

## Salidas

- CSV original y versión limpia.
- Perfil antes y después de limpieza.
- Bitácora de transformaciones.
- Particiones o manifiesto de fechas de corte.
- Tabla CSV y JSON de métricas.
- Métricas segmentadas.
- Figuras PNG.
- Pipeline ganador en formato joblib.
- Predicciones de prueba.
- Lista de combinaciones que requieren revisión de inventario.
- Reporte técnico Markdown.
- Manifiesto con configuración, semilla, versiones y rutas.

Las alertas compararán ventas previstas con inventario disponible y se presentarán como señales de revisión, no como órdenes automáticas.

## Manejo de errores y trazabilidad

- Fallar con mensajes accionables ante archivos inaccesibles, columnas ausentes o fechas sin cobertura.
- Diferenciar advertencias de calidad, filas corregibles y errores que bloquean.
- No modificar silenciosamente la fuente.
- Registrar configuración, semilla, cortes temporales, transformaciones, modelos y métricas.
- Evitar secretos, rutas personales y dependencias del equipo del autor.

## Pruebas y criterios de aceptación

Se verificarán al menos:

- determinismo del generador;
- cantidad y tipo de anomalías introducidas;
- detección y limpieza sin mutar la fuente;
- características históricas sin fuga del futuro;
- objetivo de cuatro semanas calculado correctamente;
- límites temporales sin superposición;
- preprocesamiento ajustado solo con entrenamiento;
- cálculo conocido de métricas;
- comparación de modelos;
- generación de figuras y reportes;
- ejecución integral desde CLI.

El proyecto se considerará completo cuando una instalación limpia pueda ejecutar pruebas y producir todos los artefactos mediante comandos documentados.

## Documento académico y evidencia

El Word conservará el estilo del Avance 2: cada una de las 12 indicaciones aparecerá seguida inmediatamente por su respuesta. La exposición combinará voz técnica con reflexión personal y enlazará la evidencia completa en GitHub.

El README mapeará los mismos 12 puntos y explicará instalación, ejecución, resultados, limitaciones y relación con el documento. Se incorporarán más de cinco evidencias: estructura, fragmentos explicados, bitácora, comparación, errores corregidos, pruebas, interpretación personal, cambios desde el avance anterior y reflexión final.

La declaración de IA especificará herramientas, usos, decisiones del estudiante, revisión, adaptación, pruebas y responsabilidad. No se atribuirán a Red Comercial Boreal observaciones ni resultados del escenario controlado.

## Riesgos y controles

| Riesgo | Control |
|---|---|
| Confundir ventas con demanda real | Declarar el uso como aproximación y documentar el efecto del desabasto |
| Diseñar datos para favorecer un algoritmo | Definir reglas antes de entrenar y comparar siempre contra una referencia |
| Fuga temporal | Rezagos estrictos, horizonte futuro y espacios de cuatro semanas |
| Sobreinterpretar datos simulados | Limitar conclusiones a la viabilidad técnica |
| Sobreajuste | Validación temporal, prueba final y parámetros controlados |
| Proyecto sobredimensionado | Sin frontend, base de datos, API ni modelos no relacionados |
| Evidencia de IA sin autoría | Bitácora, pruebas, historial, explicación y reflexión personal |

