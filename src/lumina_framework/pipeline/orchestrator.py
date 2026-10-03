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

