"""Interfaz pequeña para diagnosticar preparación desde consola."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from lumina_framework.core.config import load_yaml_configuration
from lumina_framework.pipeline.orchestrator import LuminaPipeline


def build_parser() -> argparse.ArgumentParser:
    """Define únicamente los argumentos de entrada de la consola."""
    parser = argparse.ArgumentParser(
        description="Diagnostica la preparación del framework conceptual de Lumina."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Ruta al archivo YAML de configuración y contrato.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Carga configuración y muestra el diagnóstico sin inventar datos."""
    args = build_parser().parse_args(argv)
    config, contract = load_yaml_configuration(Path(args.config))
    result = LuminaPipeline().assess(config, contract)
    print(result.to_json())
    return 0 if result.status != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
