"""Pruebas de validación, limpieza explícita y perfilado genérico."""

import pandas as pd
import pytest

from lumina_framework.core.contracts import DatasetContract
from lumina_framework.core.exceptions import SchemaConfigurationError
from lumina_framework.data.cleaner import DataCleaner
from lumina_framework.data.profiler import DataProfiler
from lumina_framework.data.validator import DataValidator


def test_validator_reports_missing_declared_columns_without_mutation() -> None:
    """Detecta un esquema incompleto sin alterar la tabla recibida."""
    frame = pd.DataFrame({"campo_a": [1]})
    original = frame.copy(deep=True)
    contract = DatasetContract(columns=("campo_a", "campo_b"))

    result = DataValidator().validate(frame, contract)

    assert result.valid is False
    assert result.missing_columns == ("campo_b",)
    pd.testing.assert_frame_equal(frame, original)


def test_validator_counts_key_duplicates_and_invalid_dates() -> None:
    """Protege la llave lógica y la convertibilidad de la fecha declarada."""
    frame = pd.DataFrame(
        {
            "id": [1, 1, 2],
            "fecha": ["2026-01-01", "2026-01-01", "fecha-invalida"],
        }
    )
    contract = DatasetContract(
        columns=("id", "fecha"),
        identifier_columns=("id", "fecha"),
        date_column="fecha",
    )

    result = DataValidator().validate(frame, contract)

    assert result.exact_duplicates == 1
    assert result.key_duplicates == 1
    assert result.invalid_dates == 1
    assert result.valid is False


def test_cleaner_removes_only_exact_duplicates_and_records_count() -> None:
    """Exige trazabilidad cuando una limpieza elimina registros."""
    frame = pd.DataFrame({"campo": [1, 1, 2]})

    result = DataCleaner().clean(frame, remove_exact_duplicates=True)

    assert result.data["campo"].tolist() == [1, 2]
    assert result.changes[0].rule == "remove_exact_duplicates"
    assert result.changes[0].affected_rows == 1
    assert frame["campo"].tolist() == [1, 1, 2]


def test_cleaner_rejects_rename_for_absent_source_column() -> None:
    """Impide que un mapeo mal configurado falle silenciosamente."""
    frame = pd.DataFrame({"campo": [1]})

    with pytest.raises(SchemaConfigurationError, match="no existen"):
        DataCleaner().clean(frame, rename_columns={"ausente": "nuevo"})


def test_profiler_describes_available_structure_without_contract() -> None:
    """Permite un perfil inicial aun cuando el cliente no definió etiqueta."""
    frame = pd.DataFrame({"numero": [1.0, None], "grupo": ["a", "b"]})

    profile = DataProfiler().profile(frame)

    assert profile.row_count == 2
    assert profile.column_count == 2
    assert profile.missing_counts["numero"] == 1
    assert profile.dtypes["grupo"] == "string"
    assert profile.unique_counts == {"numero": 1, "grupo": 2}
