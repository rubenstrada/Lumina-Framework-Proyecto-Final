"""Pruebas de la frontera de entrada de datos."""

from pathlib import Path

import pytest

from lumina_framework.core.exceptions import DataSourceError
from lumina_framework.data.loader import DataLoader


def test_loader_rejects_missing_path(tmp_path: Path) -> None:
    """Evita continuar cuando la fuente configurada no existe."""
    with pytest.raises(DataSourceError, match="no existe"):
        DataLoader().load(tmp_path / "ausente.csv")


def test_loader_rejects_unsupported_extension(tmp_path: Path) -> None:
    """Evita interpretar silenciosamente formatos no admitidos."""
    source = tmp_path / "datos.txt"
    source.write_text("a|b", encoding="utf-8")

    with pytest.raises(DataSourceError, match="Extensión"):
        DataLoader().load(source)


def test_loader_returns_columns_unchanged(tmp_path: Path) -> None:
    """Protege la separación entre carga y limpieza de encabezados."""
    source = tmp_path / "fixture_tecnico.csv"
    source.write_text("Campo A,Campo B\n1,x\n", encoding="utf-8")

    frame = DataLoader().load(source)

    assert frame.columns.tolist() == ["Campo A", "Campo B"]
    assert frame.to_dict(orient="records") == [{"Campo A": 1, "Campo B": "x"}]
