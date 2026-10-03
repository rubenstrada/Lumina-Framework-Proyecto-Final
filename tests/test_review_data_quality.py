"""Regresiones de calendario semanal y trazabilidad de valores numéricos."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lumina_framework.core.config import load_project_configuration
from lumina_framework.core.exceptions import DataValidationError
from lumina_framework.data.cleaner import DataCleaner
from lumina_framework.preprocessing.features import FeatureEngineer


def contract():
    return load_project_configuration(Path('config/project_final.yaml'))[1]


def weekly_data(start='2024-01-01', branch='S'):
    return pd.DataFrame({
        'semana': pd.date_range(start, periods=12, freq='7D'),
        'producto_id': 'P', 'sucursal_id': branch, 'categoria': 'Iluminación',
        'precio': 10., 'promocion': 0, 'inventario_inicial': 100.,
        'unidades_vendidas': np.arange(1, 13),
    })


def test_feature_engineer_rejects_a_date_outside_inferred_weekly_grid():
    data = weekly_data()
    data.loc[5, 'semana'] += pd.Timedelta(days=1)

    with pytest.raises(DataValidationError):
        FeatureEngineer().build(data, contract())


def test_feature_engineer_uses_one_inferred_grid_for_all_groups():
    data = pd.concat([
        weekly_data(branch='S1'),
        weekly_data(start='2024-01-02', branch='S2'),
    ], ignore_index=True)

    with pytest.raises(DataValidationError):
        FeatureEngineer().build(data, contract())


def test_feature_engineer_rejects_dates_with_a_time_component():
    data = weekly_data()
    data['semana'] += pd.Timedelta(hours=12)

    with pytest.raises(DataValidationError):
        FeatureEngineer().build(data, contract())


def test_feature_engineer_rejects_a_grid_not_aligned_to_declared_start():
    data = weekly_data(start='2024-01-02')

    with pytest.raises(DataValidationError):
        FeatureEngineer().build(data, contract(), calendar_start='2024-01-01')


def test_feature_engineer_accepts_the_declared_grid_without_mutating_source():
    data = weekly_data(start='2024-01-02')
    original = data.copy(deep=True)

    features = FeatureEngineer().build(data, contract(), calendar_start='2024-01-02')

    assert len(features) == 4
    assert features.iloc[0].semana == pd.Timestamp('2024-01-30')
    assert features.iloc[0].baseline_4_semanas == 10
    assert features.iloc[0].ventas_proximas_4_semanas == 30
    pd.testing.assert_frame_equal(data, original)


@pytest.mark.parametrize('column', ['precio', 'inventario_inicial', 'unidades_vendidas'])
def test_cleaner_logs_new_numeric_missing_values_without_counting_original_missing(column):
    data = weekly_data()
    data[column] = data[column].astype(object)
    data.loc[:4, column] = ['texto-invalido', None, -1, np.inf, '10']
    original = data.copy(deep=True)

    result = DataCleaner().clean_business_data(data, contract())

    change = next(c for c in result.changes if c.rule == 'invalidate_' + column)
    assert change.affected_rows == 3
    assert result.data.loc[:3, column].isna().all()
    assert result.data.loc[4, column] == 10
    pd.testing.assert_frame_equal(data, original)
