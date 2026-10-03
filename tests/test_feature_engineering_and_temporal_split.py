from pathlib import Path
import numpy as np
import pandas as pd
from lumina_framework.core.config import load_project_configuration
from lumina_framework.data.synthetic import SyntheticRetailDataGenerator
from lumina_framework.preprocessing.features import FeatureEngineer
from lumina_framework.preprocessing.temporal import TemporalDataSplitter


def configuration():
    return load_project_configuration(Path('config/project_final.yaml'))


def fixture():
    _, c, _, _ = configuration()
    return pd.DataFrame({'semana':pd.date_range('2024-01-01',periods=10,freq='7D'),
        'producto_id':'P','sucursal_id':'S','categoria':'Iluminación','precio':10.,
        'promocion':0,'inventario_inicial':100.,'unidades_vendidas':np.arange(1,11)})


def test_feature_engineer_uses_strictly_previous_weeks():
    _, c, _, _ = configuration()
    f = fixture()
    a = FeatureEngineer().build(f,c)
    assert a.iloc[0].baseline_4_semanas == 10
    assert a.iloc[0].ventas_proximas_4_semanas == 30
    assert a.iloc[0].ventas_semana_anterior == 4
    f.loc[8,'unidades_vendidas'] = 90
    b = FeatureEngineer().build(f,c)
    assert b.iloc[0].promedio_ventas_4_semanas == a.iloc[0].promedio_ventas_4_semanas
    assert b.iloc[0].ventas_proximas_4_semanas != a.iloc[0].ventas_proximas_4_semanas


def test_missing_week_does_not_shift_calendar_lags():
    _, c, _, _ = configuration()
    f = fixture().drop(index=2)
    assert FeatureEngineer().build(f,c).empty


def test_temporal_split_never_divides_a_week_across_sets():
    _, c, s, e = configuration()
    f = FeatureEngineer().build(SyntheticRetailDataGenerator().generate(s).clean_data,c)
    assert len(f) == 9600
    r = TemporalDataSplitter().split(f,'semana',e)
    assert (len(r.train),len(r.validation),len(r.test)) == (6400,1200,1200)
    assert r.train.semana.max() + pd.Timedelta(weeks=4) < r.validation.semana.min()
    assert r.validation.semana.max() + pd.Timedelta(weeks=4) < r.test.semana.min()
    assert set(r.train.semana).isdisjoint(r.test.semana)
