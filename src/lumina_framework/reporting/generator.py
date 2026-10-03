"""Persistencia de perfiles y manifiestos sin conclusiones inventadas."""

from dataclasses import asdict
import json
from pathlib import Path

from lumina_framework.core.context import RunContext
from lumina_framework.core.contracts import ProfileResult


class ReportGenerator:
    """Convierte resultados estructurados en salidas auditables."""

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

