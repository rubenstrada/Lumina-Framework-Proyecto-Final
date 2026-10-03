# Registro de ejecución del proyecto final

Plan: docs/superpowers/plans/2026-10-02-proyecto-final-framework.md

Modalidad nativa aprobada por el estudiante el 2 de octubre de 2026.

Se inició en una rama separada del checkout anterior. Por solicitud del estudiante, la entrega final se migró a una repo independiente llamada Lumina-Framework-Proyecto-Final. La repo del Avance 2 y su rama main se conservan como referencia; los cambios intermedios locales se guardaron de forma recuperable.

Preflight: configuración -> generador -> validación y limpieza -> variables y cortes -> métricas -> experimento -> visualización -> reportes -> orquestador. Las interfaces se implementan en ese orden.

Ruling: el plan pide resultados y reportes en Downloads; se crearán primero dentro del workspace permitido y se entregarán allí si la copia externa no está disponible. No cambia el contenido académico.

Ruling: se usará registro Markdown en lugar de scripts bash de bookkeeping para mantener la ejecución compatible con Windows.

Ruling: la prueba temporal final es la base para conocer desempeño; la selección y ajuste de modelos se hace con validación. Una tolerancia predefinida de 2 % en MAE permite preferir Ridge cuando queda cerca de Random Forest.

Task 1: complete. Configuración y 28 pruebas previas: 30 aprobadas. Se resolvieron permisos temporales ejecutando pytest con acceso local.
Task 2: complete. Generador determinista y serialización: 4 pruebas de configuración y datos aprobadas.
Cambio solicitado: repositorio nuevo lumina_proyecto_final. Avance 2 se conserva en main; la implementación reutilizada se reconoce como antecedente.
Ruling: ventas superiores al inventario se marcan ausentes, en lugar de sustituirlas por el máximo. Se excluyen ventanas incompletas del objetivo para evitar etiquetas inventadas; los faltantes de predictores se imputan solamente con entrenamiento.

Task 3: complete. Limpieza conservadora y pruebas anteriores: 34 aprobadas.
Task 4: complete. Rezagos, calendario con huecos y cortes por semanas completas verificados.
Task 5: complete. Métricas conocidas y bootstrap móvil de cuatro semanas: suite total 40 aprobadas.
Ruling: se agrega inventario_cierre como metadato, calculado con datos observados al cierre, para comparar una previsión futura con existencia disponible en el mismo momento. Usar inventario inicial sin descontar ventas sobreestimaría cobertura.
Ruling: con solo doce semanas en prueba, el intervalo bootstrap se presenta como orientativo y conserva bloques de cuatro semanas debido a etiquetas superpuestas.

Task 6: complete. Ocho configuraciones de validación, tres enfoques en prueba, imputación solo con entrenamiento y categorías nuevas comprobadas.
Task 7: complete. Ocho gráficas producidas por Matplotlib y Seaborn e inspeccionadas.
Task 8: complete. Perfiles, limpieza, métricas, predicciones, señales, modelo, reporte y manifiesto generados.
Task 9: complete. Ejecución inicial y repetida sobre 10,431 filas; 10,369 después de limpiar. Cortes utilizables: 6,017 entrenamiento, 1,159 validación, 1,139 prueba.

Revisión independiente: se inspeccionó el flujo temporal y se reprodujeron casos límite. Las pruebas nuevas fallaron antes de las correcciones:

- Ridge extrapolaba a valores negativos mientras la evaluación recortaba fuera del pipeline. La regla ahora pertenece al pipeline persistido; la recarga se verifica sin recortar otra vez.
- Una repetición fallida conservaba un manifiesto de éxito previo. Ahora se escribe running al iniciar y failed al fallar.
- Un WAPE no definido provocaba error al escribir el reporte. Se presenta No disponible.
- Dos inventarios desconocidos se marcaban sin revisión. Ahora requieren revisión de calidad; se distingue de brecha de cobertura.
- Una fecha fuera del calendario podía desaparecer al reindexar. Se rechaza explícitamente antes de crear ventanas.
- Texto numérico inválido pasaba a ausente sin contarse. La bitácora registra la transformación sin volver a contar ausentes originales.

El corte final tiene 96 de las 100 combinaciones: 94 con brecha y 2 con inventario desconocido. Las cuatro sin ventana utilizable no se consideran sin riesgo.

Random Forest seleccionado con validación (300 árboles, profundidad sin límite, cinco muestras mínimas por hoja). Prueba: MAE 38.984577, referencia 51.295874; mejora 24.000558 %. No se modificaron parámetros al consultar prueba.

El entorno local produjo advertencias de deprecación de Seaborn/Matplotlib, sin impedir las pruebas o las figuras. Los permisos de temporales de pytest se resolvieron con acceso local aprobado; no se cambió la lógica para ocultar una restricción de entorno.

Task 10: documento, documentación y paquete terminados. Word de 16 páginas con 12 instrucciones, 12 respuestas y 8 figuras. Se conservaron geometría, estilos, numeración, fuentes y tema de la referencia; el archivo original permanece inalterado. Al no estar disponible LibreOffice, se exportó una copia con Microsoft Word y se inspeccionó el render completo de sus páginas.

Verificación final: 58 pruebas aprobadas, 0 fallos; evidencia XML versionada. El ZIP se extrajo en un directorio temporal independiente, se construyó e instaló el paquete, se repitieron las 58 pruebas y la ejecución completa produjo las mismas métricas. La primera comprobación de instalación sin aislamiento falló porque el entorno no tenía setuptools; se utilizó el backend aislado declarado en pyproject, sin modificar el entorno anterior.

Publicación autorizada en repo independiente: https://github.com/rubenstrada/Lumina-Framework-Proyecto-Final. No se fusiona ni se sobrescribe la repo del avance anterior.

Revisión de la nota metodológica: el estudiante explicó su experiencia previa con modelos, la prioridad de comprender el negocio y explorar los datos, y cómo la experiencia del backend de ERP influyó en la organización del framework. Se adaptó y aprobó una narrativa en primera persona que mantiene las decisiones finales bajo su criterio y declara el apoyo de Codex en escritura, implementación y comprobaciones.

La misma nota se integra en el reporte y en la declaración de herramientas; README y guía de comprensión mantienen ese enfoque. Las instrucciones, tablas, figuras, estilos y demás partes del Word permanecen conservados. El documento revisado tiene 17 páginas y se inspeccionaron todas. No se modificaron código del framework, datos, parámetros ni resultados. La verificación posterior volvió a aprobar 58 pruebas, con las 14 advertencias de deprecación ya conocidas.
