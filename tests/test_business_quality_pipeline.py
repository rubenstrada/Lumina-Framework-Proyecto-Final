from pathlib import Path
import pandas as pd
import pytest
from lumina_framework.core.config import load_project_configuration, SyntheticScenarioConfig
from lumina_framework.data.synthetic import SyntheticRetailDataGenerator
from lumina_framework.data.cleaner import DataCleaner
from lumina_framework.data.validator import DataValidator
from lumina_framework.core.exceptions import SchemaConfigurationError


def contract():
    return load_project_configuration(Path('config/project_final.yaml'))[1]


def test_business_validation_and_cleaning_preserve_original():
    raw = SyntheticRetailDataGenerator().generate(SyntheticScenarioConfig()).raw_data
    original = raw.copy(deep=True)
    v = DataValidator().validate_business_rules(raw, contract())
    assert v.invalid_dates > 0 and v.negative_by_column['precio'] > 0
    assert v.sales_above_inventory > 0
    result = DataCleaner().clean_business_data(raw, contract())
    assert not result.data.duplicated().any()
    assert pd.to_datetime(result.data.semana).notna().all()
    assert result.data.precio.min() > 0
    assert set(result.data.categoria) == {'Iluminación','Accesorios','Decoración','Herramientas'}
    assert result.data.unidades_vendidas.max() < 999999
    assert len(result.changes) >= 6
    pd.testing.assert_frame_equal(raw, original)


def test_business_cleaner_drops_unrecoverable_dates_and_logs_change():
    data = pd.DataFrame([['2024-01-01','S','P','Iluminación',10,1,100,90],
                         ['bad','S','P','Iluminación',10,0,100,5]], columns=contract().columns)
    r = DataCleaner().clean_business_data(data, contract())
    assert len(r.data) == 1
    assert r.data.unidades_vendidas.iloc[0] == 90  # raro pero posible
    assert any(c.rule == 'drop_invalid_dates' and c.affected_rows == 1 for c in r.changes)
