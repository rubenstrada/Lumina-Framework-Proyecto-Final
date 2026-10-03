# Registro de ejecución del proyecto final

Plan de implementación: docs/superpowers/plans/2026-10-02-proyecto-final-framework.md

La implementación y las comprobaciones se realizaron localmente en Windows el 2 de octubre de 2026, con asistencia de Codex.

El desarrollo comenzó en una rama separada. Decidí entregar el proyecto final en un repositorio independiente llamado Lumina-Framework-Proyecto-Final. El repositorio del Avance 2 y su rama main se conservan como referencia.

Revisión inicial: configuración -> generador -> validación y limpieza -> variables y cortes -> métricas -> experimento -> visualización -> reportes -> orquestador. Se estableció este orden para implementar las interfaces.

Decisión: el periodo de prueba se reserva para evaluar el desempeño final; la selección y el ajuste de los modelos se hacen con validación. Una tolerancia predefinida de 2 % en MAE permite preferir Ridge cuando queda cerca de Random Forest.

Avance 1: configuración y pruebas previas. Se aprobaron 30 pruebas, incluidas las 28 previas. Se resolvieron permisos temporales ejecutando pytest con acceso local.
Avance 2: generador determinista y serialización. Se aprobaron 4 pruebas de configuración y datos.
Cambio de repositorio: la entrega pasó a lumina_proyecto_final. El Avance 2 se conserva en main; la implementación reutilizada se reconoce como antecedente.
Decisión: las ventas superiores al inventario se marcan ausentes, en lugar de sustituirlas por el máximo. Se excluyen ventanas incompletas del objetivo para evitar etiquetas inventadas; los faltantes de predictores se imputan solamente con entrenamiento.

Avance 3: limpieza conservadora y pruebas anteriores. Se aprobaron 34 pruebas.
Avance 4: se verificaron los rezagos, el calendario con huecos y los cortes por semanas completas.
Avance 5: métricas conocidas y bootstrap móvil de cuatro semanas. Se aprobaron 40 pruebas en total.
Decisión: se agrega inventario_cierre como metadato, calculado con datos observados al cierre, para comparar una previsión futura con existencia disponible en el mismo momento. Usar inventario inicial sin descontar ventas sobreestimaría cobertura.
Decisión: con solo doce semanas en prueba, el intervalo bootstrap se presenta como orientativo y conserva bloques de cuatro semanas debido a etiquetas superpuestas.

Avance 6: se compararon ocho configuraciones en validación y tres enfoques en prueba; se comprobaron la imputación solo con entrenamiento y las categorías nuevas.
Avance 7: se produjeron e inspeccionaron ocho gráficas con Matplotlib y Seaborn.
Avance 8: se generaron perfiles, limpieza, métricas, predicciones, señales, modelo, reporte y manifiesto.
Avance 9: ejecución inicial y repetida sobre 10,431 filas; 10,369 después de limpiar. Cortes utilizables: 6,017 entrenamiento, 1,159 validación, 1,139 prueba.

Revisión del flujo temporal: se inspeccionó el proceso y se reprodujeron casos límite. Las pruebas nuevas fallaron antes de las correcciones:

- Ridge extrapolaba a valores negativos mientras la evaluación recortaba fuera del pipeline. La regla ahora pertenece al pipeline persistido; la recarga se verifica sin recortar otra vez.
- Una repetición fallida conservaba un manifiesto de éxito previo. Ahora se escribe running al iniciar y failed al fallar.
- Un WAPE no definido provocaba error al escribir el reporte. Se presenta No disponible.
- Dos inventarios desconocidos se marcaban sin revisión. Ahora requieren revisión de calidad; se distingue de brecha de cobertura.
- Una fecha fuera del calendario podía desaparecer al reindexar. Se rechaza explícitamente antes de crear ventanas.
- Texto numérico inválido pasaba a ausente sin contarse. La bitácora registra la transformación sin volver a contar ausentes originales.

El corte final tiene 96 de las 100 combinaciones: 94 con brecha y 2 con inventario desconocido. Las cuatro sin ventana utilizable no se consideran sin riesgo.

Random Forest seleccionado con validación (300 árboles, profundidad sin límite, cinco muestras mínimas por hoja). Prueba: MAE 38.984577, referencia 51.295874; mejora 24.000558 %. No se modificaron parámetros al consultar prueba.

El entorno local produjo advertencias de deprecación de Seaborn/Matplotlib, sin impedir las pruebas o las figuras. Las restricciones de permisos de los temporales de pytest se resolvieron mediante ejecución local, sin cambiar la lógica del proyecto.

Avance 10: documento, documentación y paquete terminados. Word de 16 páginas con 12 instrucciones, 12 respuestas y 8 figuras. Se conservaron geometría, estilos, numeración, fuentes y tema de la referencia; el archivo original permanece inalterado. Al no estar disponible LibreOffice, se exportó una copia con Microsoft Word y se revisaron todas sus páginas.

Verificación final: 58 pruebas aprobadas, 0 fallos; evidencia XML versionada. El ZIP se extrajo en un directorio temporal independiente, se construyó e instaló el paquete, se repitieron las 58 pruebas y la ejecución completa produjo las mismas métricas. La primera comprobación de instalación sin aislamiento falló porque el entorno no tenía setuptools; se utilizó el backend aislado declarado en pyproject, sin modificar el entorno anterior.

Publicación: https://github.com/rubenstrada/Lumina-Framework-Proyecto-Final. El repositorio del avance anterior se conserva como antecedente.

Revisión de la nota metodológica: expliqué mi experiencia previa con modelos, por qué busqué comprender el negocio y explorar los datos antes de modelar, y cómo mi experiencia con un backend de ERP influyó en la organización del framework. La nota se redactó en primera persona para reflejar las decisiones que tomé y el apoyo de Codex en escritura, implementación y comprobaciones.

La misma nota se integra en el reporte y en la declaración de herramientas; README y guía de comprensión mantienen ese enfoque. Las instrucciones, tablas, figuras, estilos y demás partes del Word se conservaron. El documento revisado tiene 17 páginas y se inspeccionaron todas. El código del framework, los datos, los parámetros y los resultados permanecieron iguales. La verificación posterior confirmó 58 pruebas aprobadas, con las 14 advertencias de deprecación ya conocidas.

Revisión de presentación: se retiraron los doce rótulos «Respuesta» para dejar la explicación directamente después de cada indicación. También se simplificaron la guía de ejecución y algunas frases del reporte y la bitácora. El Word conserva las doce indicaciones originales, ocho tablas y ocho figuras; se revisaron sus 17 páginas. Las comprobaciones del generador y del documento confirmaron que los cambios afectan solo la presentación y que la declaración de autoría permanece intacta.
