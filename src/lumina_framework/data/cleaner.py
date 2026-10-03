"""Limpieza controlada por reglas explícitas."""

from collections.abc import Mapping

import pandas as pd

from lumina_framework.core.contracts import CleaningChange, CleaningResult
from lumina_framework.core.exceptions import SchemaConfigurationError
from lumina_framework.core.exceptions import DataValidationError


class DataCleaner:
    """Aplica únicamente transformaciones solicitadas por configuración."""

    def clean(
        self,
        data: pd.DataFrame,
        *,
        remove_exact_duplicates: bool = False,
        rename_columns: Mapping[str, str] | None = None,
    ) -> CleaningResult:
        """Devuelve una copia y una bitácora de cada cambio aplicado."""
        cleaned = data.copy(deep=True)
        changes: list[CleaningChange] = []

        if rename_columns:
            absent = sorted(set(rename_columns) - set(cleaned.columns))
            if absent:
                raise SchemaConfigurationError(
                    "Las columnas de origen no existen: " + ", ".join(absent)
                )
            cleaned = cleaned.rename(columns=dict(rename_columns))
            changes.append(
                CleaningChange(
                    rule="rename_columns",
                    affected_rows=len(cleaned),
                    details=f"Se renombraron {len(rename_columns)} columnas.",
                )
            )

        if remove_exact_duplicates:
            before = len(cleaned)
            cleaned = cleaned.drop_duplicates().reset_index(drop=True)
            removed = before - len(cleaned)
            changes.append(
                CleaningChange(
                    rule="remove_exact_duplicates",
                    affected_rows=removed,
                    details="Se eliminaron únicamente duplicados exactos.",
                )
            )

        return CleaningResult(data=cleaned, changes=tuple(changes))

    def clean_business_data(self, data, contract):
        """Aplica restricciones físicas sin consultar la tabla perfecta del generador."""
        required = set(contract.columns)
        if required - set(data.columns):
            raise SchemaConfigurationError('Faltan columnas del contrato.')
        cleaned = data.copy(deep=True)
        changes = []

        def record(rule, affected, details):
            changes.append(CleaningChange(rule, int(affected), details))

        before = len(cleaned)
        cleaned = cleaned.drop_duplicates().copy()
        record('remove_exact_duplicates', before-len(cleaned), 'Duplicados exactos.')
        date = contract.date_column
        dates = pd.to_datetime(cleaned[date], errors='coerce')
        record('drop_invalid_dates', dates.isna().sum(), 'La fecha no se inventa ni se recupera usando el generador.')
        cleaned[date] = dates
        cleaned = cleaned.loc[dates.notna()].copy()
        cat = contract.category_column
        normalized = cleaned[cat].astype('string').str.strip().str.title()
        record('normalize_categories', (cleaned[cat] != normalized).sum(), 'Espacios y mayúsculas.')
        cleaned[cat] = normalized
        for c in (contract.price_column, contract.inventory_column, contract.sales_column):
            values = pd.to_numeric(cleaned[c], errors='coerce')
            newly_missing = cleaned[c].notna() & values.isna()
            bad = (values < 0) | (values.abs() == float('inf'))
            if c == contract.price_column:
                bad |= values == 0
            record('invalidate_'+c, (bad | newly_missing).sum(), 'Valores imposibles o no numéricos a faltantes; imputación del predictor se ajusta con entrenamiento.')
            cleaned[c] = values.mask(bad)
        sales, inventory = contract.sales_column, contract.inventory_column
        corrupt = cleaned[sales] > cleaned[inventory]
        # No se reconstruyen etiquetas corruptas: podrían introducir objetivos falsos.
        cleaned.loc[corrupt, sales] = float('nan')
        record('invalidate_sales_above_inventory', corrupt.sum(), 'Ventas corruptas pasan a ausentes; se excluyen ventanas de etiqueta incompletas.')
        record('preserve_plausible_outliers', 0, 'Picos dentro del inventario se conservan; no se usa un umbral aprendido del futuro.')
        keys = list(contract.identifier_columns)
        if cleaned.duplicated(keys).any():
            raise DataValidationError('Hay llaves repetidas con valores contradictorios.')
        return CleaningResult(cleaned.sort_values(keys).reset_index(drop=True), tuple(changes))
