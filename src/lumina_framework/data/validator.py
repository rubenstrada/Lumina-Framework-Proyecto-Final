"""Validación de datos contra un contrato confirmado."""

import pandas as pd

from lumina_framework.core.contracts import DatasetContract, ValidationResult
from lumina_framework.core.exceptions import SchemaConfigurationError
from dataclasses import replace


class DataValidator:
    """Observa incumplimientos estructurales sin corregirlos."""

    def validate(
        self,
        data: pd.DataFrame,
        contract: DatasetContract,
    ) -> ValidationResult:
        """Compara columnas, llave y fecha con el contrato declarado."""
        available = set(data.columns)
        missing = tuple(column for column in contract.columns if column not in available)
        exact_duplicates = int(data.duplicated().sum())

        key_duplicates: int | None = None
        if contract.identifier_columns and all(
            column in available for column in contract.identifier_columns
        ):
            key_duplicates = int(
                data.duplicated(subset=list(contract.identifier_columns)).sum()
            )

        invalid_dates: int | None = None
        if contract.date_column and contract.date_column in available:
            converted = pd.to_datetime(data[contract.date_column], errors="coerce")
            invalid_dates = int(converted.isna().sum())

        valid = not missing and (invalid_dates in (None, 0))
        return ValidationResult(
            valid=valid,
            missing_columns=missing,
            exact_duplicates=exact_duplicates,
            key_duplicates=key_duplicates,
            invalid_dates=invalid_dates,
        )

    def validate_business_rules(self, data, contract):
        """Observa reglas físicas; los hallazgos corregibles no son bloqueos de esquema."""
        roles = [contract.price_column, contract.inventory_column, contract.sales_column,
                 contract.category_column, contract.date_column]
        if any(role is None for role in roles):
            raise SchemaConfigurationError('Faltan roles semánticos de negocio.')
        result = self.validate(data, contract)
        if result.missing_columns:
            return result
        nums = {c: pd.to_numeric(data[c], errors='coerce') for c in roles[:3]}
        cat = data[contract.category_column].astype('string')
        return replace(result,
            missing_by_column={c:int(data[c].isna().sum()) for c in data},
            negative_by_column={c:int((s < 0).sum()) for c,s in nums.items()},
            sales_above_inventory=int((nums[contract.sales_column] > nums[contract.inventory_column]).sum()),
            inconsistent_categories=int((cat != cat.str.strip().str.title()).sum()))
