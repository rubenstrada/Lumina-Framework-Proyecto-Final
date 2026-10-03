from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def test_generator_creates_the_three_documented_pngs(tmp_path: Path) -> None:
    """Detecta si falta el script o deja de producir alguno de los visuales."""

    project_root = Path(__file__).resolve().parents[1]
    script = project_root / "scripts" / "generate_visuals.py"

    result = subprocess.run(
        [sys.executable, str(script), "--output-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    expected_names = {
        "arquitectura_framework.png",
        "mapa_clases.png",
        "visualizaciones_propuestas.png",
    }
    assert {path.name for path in tmp_path.glob("*.png")} == expected_names

    for name in expected_names:
        image = tmp_path / name
        assert image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        assert image.stat().st_size > 10_000
