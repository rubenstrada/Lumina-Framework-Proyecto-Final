# Registro de ejecución del proyecto final

Plan: docs/superpowers/plans/2026-10-02-proyecto-final-framework.md

Modalidad nativa aprobada por el estudiante el 2 de octubre de 2026.

Se trabaja en la rama proyecto-final dentro del checkout existente. Se conserva main como referencia del Avance 2.

Preflight: configuración -> generador -> validación y limpieza -> variables y cortes -> métricas -> experimento -> visualización -> reportes -> orquestador. Las interfaces se implementan en ese orden.

Ruling: el plan pide resultados y reportes en Downloads; se crearán primero dentro del workspace permitido y se entregarán allí si la copia externa no está disponible. No cambia el contenido académico.

Ruling: se usará registro Markdown en lugar de scripts bash de bookkeeping para mantener la ejecución compatible con Windows.

Ruling: la prueba temporal final es la base para conocer desempeño; la selección y ajuste de modelos se hace con validación. Una tolerancia predefinida de 2 % en MAE permite preferir Ridge cuando queda cerca de Random Forest.

Task 1: complete. Configuración y 28 pruebas previas: 30 aprobadas. Se resolvieron permisos temporales ejecutando pytest con acceso local.
Task 2: complete. Generador determinista y serialización: 4 pruebas de configuración y datos aprobadas.
Cambio solicitado: repositorio nuevo lumina_proyecto_final. Avance 2 se conserva en main; la implementación reutilizada se reconoce como antecedente.
Ruling: ventas superiores al inventario se marcan ausentes, en lugar de sustituirlas por el máximo. Se excluyen ventanas incompletas del objetivo para evitar etiquetas inventadas; los faltantes de predictores se imputan solamente con entrenamiento.
