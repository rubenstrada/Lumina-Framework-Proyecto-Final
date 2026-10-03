"""Referencia sencilla reproducible sin ajuste estadístico."""
from sklearn.base import BaseEstimator, RegressorMixin


class NaiveFourWeekBaseline(RegressorMixin, BaseEstimator):
    def fit(self, X, y=None):
        return self

    def predict(self, data):
        return data['baseline_4_semanas'].to_numpy(dtype=float)
