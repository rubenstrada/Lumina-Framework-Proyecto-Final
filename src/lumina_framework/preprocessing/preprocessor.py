"""Separación y transformaciones previas al modelado supervisado."""

from math import ceil

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from lumina_framework.core.contracts import DatasetContract, PreprocessingResult
from lumina_framework.core.exceptions import (
    DataValidationError,
    InsufficientDataError,
    SchemaConfigurationError,
    TargetNotConfiguredError,
)


class DataPreprocessor:
    """Prepara una partición sin ajustar transformaciones con el futuro."""

    def __init__(self, test_fraction: float = 0.20) -> None:
        self.test_fraction = test_fraction

    def prepare(
        self,
        data: pd.DataFrame,
        contract: DatasetContract,
    ) -> PreprocessingResult:
        """Separa cronológicamente y construye un transformador no ajustado."""
        if contract.target_column is None:
            raise TargetNotConfiguredError(
                "No se configuró una variable objetivo validada por Boreal."
            )

        features = contract.numeric_features + contract.categorical_features
        if not features:
            raise SchemaConfigurationError(
                "Falta declarar las columnas predictoras."
            )

        required = set(features) | {contract.target_column}
        if contract.date_column:
            required.add(contract.date_column)
        missing = sorted(required - set(data.columns))
        if missing:
            raise SchemaConfigurationError(
                "Faltan columnas configuradas: " + ", ".join(missing)
            )
        if len(data) < 2:
            raise InsufficientDataError(
                "Se requieren al menos dos observaciones para separar periodos."
            )

        prepared = data.copy(deep=True)
        train_dates: pd.Series | None = None
        test_dates: pd.Series | None = None
        if contract.date_column:
            parsed = pd.to_datetime(prepared[contract.date_column], errors="coerce")
            if parsed.isna().any():
                raise DataValidationError(
                    "La columna temporal contiene valores no convertibles."
                )
            prepared[contract.date_column] = parsed
            prepared = prepared.sort_values(contract.date_column).reset_index(drop=True)

        test_count = max(1, ceil(len(prepared) * self.test_fraction))
        split_index = len(prepared) - test_count
        if split_index < 1:
            raise InsufficientDataError(
                "La fracción de prueba no deja observaciones para entrenamiento."
            )

        train = prepared.iloc[:split_index]
        test = prepared.iloc[split_index:]
        if contract.date_column:
            train_dates = train[contract.date_column].copy()
            test_dates = test[contract.date_column].copy()

        transformers: list[tuple[str, Pipeline, list[str]]] = []
        if contract.numeric_features:
            numeric_pipeline = Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]
            )
            transformers.append(
                ("numeric", numeric_pipeline, list(contract.numeric_features))
            )
        if contract.categorical_features:
            categorical_pipeline = Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("encoder", OneHotEncoder(handle_unknown="ignore")),
                ]
            )
            transformers.append(
                (
                    "categorical",
                    categorical_pipeline,
                    list(contract.categorical_features),
                )
            )

        transformer = ColumnTransformer(transformers=transformers)
        return PreprocessingResult(
            X_train=train.loc[:, list(features)].copy(),
            X_test=test.loc[:, list(features)].copy(),
            y_train=train.loc[:, contract.target_column].copy(),
            y_test=test.loc[:, contract.target_column].copy(),
            transformer=transformer,
            train_dates=train_dates,
            test_dates=test_dates,
        )

