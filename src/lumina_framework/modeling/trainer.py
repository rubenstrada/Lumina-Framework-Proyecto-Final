"""Entrenamiento de un estimador proporcionado externamente."""

from typing import Any

from sklearn.pipeline import Pipeline

from lumina_framework.core.contracts import PreprocessingResult, TrainingResult


class ModelTrainer:
    """Ajusta preprocesamiento y modelo únicamente con entrenamiento."""

    def train(
        self,
        split: PreprocessingResult,
        estimator: Any,
    ) -> TrainingResult:
        """Construye un pipeline reproducible y predice ambos periodos."""
        pipeline = Pipeline(
            [
                ("preprocessor", split.transformer),
                ("model", estimator),
            ]
        )
        pipeline.fit(split.X_train, split.y_train)
        return TrainingResult(
            pipeline=pipeline,
            train_predictions=pipeline.predict(split.X_train),
            test_predictions=pipeline.predict(split.X_test),
        )

