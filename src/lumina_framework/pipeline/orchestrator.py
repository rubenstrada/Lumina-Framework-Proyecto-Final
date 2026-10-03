"""Coordinación de componentes sin concentrar su lógica interna."""

from collections.abc import Mapping

from lumina_framework.core.config import FrameworkConfig, ReadinessChecker
from lumina_framework.core.context import RunContext
from lumina_framework.core.contracts import DatasetContract, RunResult
from lumina_framework.core.exceptions import DataValidationError
from lumina_framework.data.cleaner import DataCleaner
from lumina_framework.data.loader import DataLoader
from lumina_framework.data.profiler import DataProfiler
from lumina_framework.data.validator import DataValidator
from lumina_framework.reporting.generator import ReportGenerator


class LuminaPipeline:
    """Compone las etapas y respeta sus límites de responsabilidad."""

    def run_project(self,config,contract,scenario_config,experiment_config):
        """Compone el flujo completo y deja cada regla dentro de su componente."""
        from lumina_framework.data.synthetic import SyntheticRetailDataGenerator
        from lumina_framework.preprocessing.features import FeatureEngineer
        from lumina_framework.preprocessing.temporal import TemporalDataSplitter
        from lumina_framework.modeling.experiment import ModelExperimentRunner
        from lumina_framework.visualization.business import BusinessVisualizer
        from lumina_framework.visualization.diagnostics import ModelDiagnosticsVisualizer
        from lumina_framework.reporting.inventory import InventorySignalGenerator
        from lumina_framework.core.exceptions import DataSourceError, SchemaConfigurationError
        context=RunContext.start()
        if config.source_path is None:
            raise SchemaConfigurationError('Falta fuente de datos.')
        try:
            context.status='running'
            self.reporter.write_run_status(context,config.output_dir)
            if not config.source_path.exists():
                generator=SyntheticRetailDataGenerator()
                generated=generator.generate(scenario_config)
                generator.write(generated,config.source_path,config.source_path.parent/'generation_metadata.json')
                context.record_event('scenario_generated')
            data=self.loader.load(config.source_path)
            context.record_event('source_loaded')
            validation=self.validator.validate_business_rules(data,contract)
            if validation.missing_columns:
                raise SchemaConfigurationError('Faltan columnas: '+', '.join(validation.missing_columns))
            context.record_event('source_validated')
            before=self.profiler.profile(data)
            cleaning=self.cleaner.clean_business_data(data,contract)
            after=self.profiler.profile(cleaning.data)
            context.record_event('cleaning_completed')
            features=FeatureEngineer().build(cleaning.data,contract,calendar_start=experiment_config.start_date)
            split=TemporalDataSplitter().split(features,contract.date_column,experiment_config)
            context.record_event('temporal_split_completed')
            experiment=ModelExperimentRunner().run(split,contract,experiment_config)
            context.record_event('model_experiment_completed')
            figure_dir=config.output_dir/'figures'
            figures=BusinessVisualizer().generate(cleaning.data,figure_dir)
            figures+=ModelDiagnosticsVisualizer().generate(experiment.predictions,experiment.test_metrics,
                experiment.importance,figure_dir,experiment.selected_model_name)
            context.record_event('visualizations_generated')
            signals=InventorySignalGenerator().generate(experiment.predictions,experiment.selected_model_name)
            context.record_event('interpretation_completed')
            paths=self.reporter.generate_project_reports(output_dir=config.output_dir,context=context,
                profiles={'before':before,'after':after},validation=validation,cleaning=cleaning,
                split=split,experiment=experiment,signals=signals,figures=figures,
                scenario=scenario_config,experiment_config=experiment_config,
                source_path=config.source_path,contract=contract)
            return RunResult('completed',(),len(data),paths)
        except Exception as exc:
            context.status='failed'
            context.record_event('run_failed: '+type(exc).__name__)
            try:
                self.reporter.write_run_status(context,config.output_dir)
            except OSError:
                pass  # Si se perdió acceso, el manifiesto previo ya indica running.
            if isinstance(exc,OSError):
                raise DataSourceError('No se pudo leer o guardar una salida: '+str(exc)) from exc
            raise

    def __init__(
        self,
        *,
        readiness_checker: ReadinessChecker | None = None,
        loader: DataLoader | None = None,
        validator: DataValidator | None = None,
        cleaner: DataCleaner | None = None,
        profiler: DataProfiler | None = None,
        reporter: ReportGenerator | None = None,
    ) -> None:
        self.readiness_checker = readiness_checker or ReadinessChecker()
        self.loader = loader or DataLoader()
        self.validator = validator or DataValidator()
        self.cleaner = cleaner or DataCleaner()
        self.profiler = profiler or DataProfiler()
        self.reporter = reporter or ReportGenerator()

    def assess(
        self,
        config: FrameworkConfig,
        contract: DatasetContract,
    ) -> RunResult:
        """Informa preparación sin leer archivos ni ejecutar análisis."""
        readiness = self.readiness_checker.check(config, contract)
        if readiness.ready_for_modeling:
            status = "ready_for_modeling"
        elif readiness.ready_for_profiling:
            status = "ready_for_profiling"
        else:
            status = "blocked"
        return RunResult(
            status=status,
            blocker_codes=tuple(issue.code for issue in readiness.blockers),
        )

    def run_profile(
        self,
        config: FrameworkConfig,
        contract: DatasetContract,
        *,
        remove_exact_duplicates: bool = False,
        rename_columns: Mapping[str, str] | None = None,
    ) -> RunResult:
        """Carga, valida, limpia explícitamente y perfila una fuente."""
        readiness = self.readiness_checker.check(config, contract)
        if not readiness.ready_for_profiling:
            return self.assess(config, contract)

        if config.source_path is None:
            return self.assess(config, contract)

        context = RunContext.start()
        context.record_event("source_loading_started")
        data = self.loader.load(config.source_path)
        context.record_event("source_loaded")

        validation = self.validator.validate(data, contract)
        context.record_event("source_validated")
        if not validation.valid:
            context.status = "failed"
            raise DataValidationError(
                "La fuente no satisface el contrato confirmado."
            )

        cleaning = self.cleaner.clean(
            data,
            remove_exact_duplicates=remove_exact_duplicates,
            rename_columns=rename_columns,
        )
        context.record_event("explicit_cleaning_completed")
        profile = self.profiler.profile(cleaning.data)
        context.record_event("profile_completed")
        context.status = "profiled"
        paths = self.reporter.generate_profile_reports(
            profile,
            context,
            config.output_dir,
        )
        return RunResult(
            status="profiled",
            blocker_codes=tuple(issue.code for issue in readiness.blockers),
            loaded_rows=profile.row_count,
            artifact_paths=paths,
        )
