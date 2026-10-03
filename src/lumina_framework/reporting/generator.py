"""Persistencia de perfiles y manifiestos sin conclusiones inventadas."""

from dataclasses import asdict
import json
from pathlib import Path

from lumina_framework.core.context import RunContext
from lumina_framework.core.contracts import ProfileResult


class ReportGenerator:
    """Convierte resultados estructurados en salidas auditables."""

    def write_run_status(self, context, output_dir):
        """Invalida el estado previo antes de reemplazar salidas de una corrida."""
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / 'manifest.json').write_text(
            json.dumps(context.to_manifest(), ensure_ascii=False, indent=2), encoding='utf-8')

    def generate_project_reports(self, *, output_dir, context, profiles, validation,
                                 cleaning, split, experiment, signals, figures,
                                 scenario, experiment_config, source_path, contract):
        """Serializa resultados calculados y conserva procedencia y configuración."""
        import hashlib
        import importlib.metadata
        import platform
        import joblib
        import pandas as pd
        from lumina_framework.modeling.evaluator import ModelEvaluator
        output_dir.mkdir(parents=True,exist_ok=True)
        paths=[]

        def json_file(name,obj):
            path=output_dir/name
            # pandas normaliza NaN a null en el intercambio JSON.
            payload=json.loads(pd.Series([obj]).to_json(orient='values',force_ascii=False))[0]
            path.write_text(json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
            paths.append(path)
            return path

        def csv_file(name,data):
            path=output_dir/name
            data.to_csv(path,index=False)
            paths.append(path)

        for name,profile in profiles.items():
            json_file('profile_'+name+'.json',asdict(profile))
        json_file('validation.json',asdict(validation))
        json_file('cleaning_log.json',[asdict(c) for c in cleaning.changes])
        csv_file('cleaned_data.csv',cleaning.data)
        json_file('temporal_split.json',dict(boundaries=split.boundaries,
            rows={k:len(getattr(split,k)) for k in ('train','validation','test')}))
        csv_file('validation_metrics.csv',experiment.validation_metrics)
        csv_file('test_metrics.csv',experiment.test_metrics)
        json_file('test_metrics.json',experiment.test_metrics.to_dict(orient='records'))
        csv_file('predictions.csv',experiment.predictions)
        evaluator=ModelEvaluator()
        segmented=evaluator.segmented_metrics(experiment.predictions,contract.target_column,
            experiment.selected_model_name,['sucursal_id','categoria','producto_id','semana'])
        csv_file('segmented_metrics.csv',segmented)
        csv_file('inventory_signals.csv',signals)
        csv_file('feature_importance.csv',experiment.importance)
        csv_file('ridge_coefficients.csv',experiment.coefficients)
        json_file('uncertainty.json',asdict(experiment.uncertainty))
        model_path=output_dir/'model.joblib'
        joblib.dump(experiment.selected_pipeline,model_path,compress=3)
        paths.append(model_path)
        paths.extend(figures)
        report=output_dir/'technical_report.md'
        chosen=experiment.test_metrics.set_index('modelo').loc[experiment.selected_model_name]
        baseline=experiment.test_metrics.set_index('modelo').loc['Ingenuo']
        interval=experiment.uncertainty
        lines=['# Resultados del framework Lumina','',
            'El caso no proporciona una fuente operativa; se construyó un escenario reproducible para probar la viabilidad técnica. Los resultados corresponden a sus reglas y no son evidencia empresarial real.','',
            '## Calidad de datos','',
            f'Entrada: {profiles["before"].row_count} filas. Después de limpiar: {profiles["after"].row_count}.',
            'Las ventas corruptas no se imputan para crear etiquetas. Se excluyen ventanas con semanas ausentes; los predictores faltantes se imputan dentro del pipeline.','',
            '## Evaluación','',
            '| Modelo | MAE unidades | RMSE unidades | WAPE | R² | Mejora MAE |',
            '|---|---:|---:|---:|---:|---:|']
        for _,r in experiment.test_metrics.iterrows():
            wape='No disponible' if pd.isna(r.wape) else f'{r.wape:.2%}'
            improvement='No disponible' if pd.isna(r.mejora_mae_pct) else f'{r.mejora_mae_pct:.2f}%'
            lines.append(f'| {r.modelo} | {r.mae:.3f} | {r.rmse:.3f} | {wape} | {r.r2:.3f} | {improvement} |')
        lines += ['',f'Modelo elegido en validación: **{experiment.selected_model_name}**.',experiment.selection_reason,
            f'En prueba su MAE fue {chosen.mae:.3f} unidades frente a {baseline.mae:.3f} de la referencia. Diferencia de MAE candidato menos referencia, intervalo orientativo del 95 %: [{interval.lower:.3f}, {interval.upper:.3f}].',
            'El remuestreo usa bloques de cuatro semanas. Hay pocos bloques independientes: no demuestra una mejora económica ni elimina la incertidumbre de generalización.','',
            '## Interpretación y recomendaciones','',
            f'{int(signals.requiere_revision.sum())} combinaciones requieren revisar cobertura según stock al cierre y ventas previstas. No son órdenes de compra: faltan pedidos en tránsito, plazos y costos.',
            f'Cobertura del último corte: {len(signals)} de {len(cleaning.data[["sucursal_id","producto_id"]].drop_duplicates())} combinaciones. Inventarios no disponibles: {int(signals.inventario_cierre.isna().sum())}; requieren revisión de calidad, no se consideran sin riesgo.',
            'Priorizar revisión de errores por categoría y sucursal; contrastar promociones dentro de grupos equivalentes. Una asociación entre promoción y ventas no demuestra causalidad.',
            'Mantener revisión manual en episodios de agotamiento. Las ventas observadas están limitadas por stock y no miden demanda perdida.',
            'Si el modelo elegido no supera la referencia en prueba, conservar una política sencilla y obtener más historial antes de decidir su adopción.','',
            '## Limitaciones y mejoras','',
            'Solo dos años, un escenario y doce semanas de prueba. Se pronostica venta acumulada observada, condicionada a una política de reposición. No se conocen futuras promociones ni futuros precios; no se usan como características.',
            'Las ventanas futuras superpuestas hacen que sus volúmenes no puedan sumarse como ventas anuales. No se calcularán ahorros multiplicando MAE por semanas.',
            'Antes de uso operativo: contrato de datos real, costos de exceso y faltante, pedidos pendientes, validación en más periodos y seguimiento del error.']
        report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        paths.append(report)
        for p in paths:
            context.record_artifact(p.stem,str(p.relative_to(output_dir)).replace('\\','/'))
        context.status='completed'
        manifest=context.to_manifest()
        manifest.update(seed=scenario.seed,scenario=asdict(scenario),experiment=asdict(experiment_config),
            source_generation_metadata=(json.loads((source_path.parent/'generation_metadata.json').read_text(encoding='utf-8'))
                if (source_path.parent/'generation_metadata.json').exists() else None),
            scenario_parameters_are_source_proof=False,
            selected_model=experiment.selected_model_name,selection_reason=experiment.selection_reason,
            refit_rows=experiment.refit_rows,source_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),
            versions={k:importlib.metadata.version(k) for k in ('pandas','numpy','scikit-learn','matplotlib','seaborn','joblib')},
            python_version=platform.python_version())
        json_file('manifest.json',manifest)
        return tuple(paths)

    def generate_profile_reports(
        self,
        profile: ProfileResult,
        context: RunContext,
        output_dir: Path,
    ) -> tuple[Path, Path]:
        """Escribe un perfil JSON y un manifiesto JSON de la corrida."""
        output_dir.mkdir(parents=True, exist_ok=True)
        profile_path = output_dir / "profile.json"
        manifest_path = output_dir / "manifest.json"

        profile_path.write_text(
            json.dumps(asdict(profile), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        context.record_artifact("profile", profile_path.name)
        manifest_path.write_text(
            json.dumps(context.to_manifest(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return profile_path, manifest_path
