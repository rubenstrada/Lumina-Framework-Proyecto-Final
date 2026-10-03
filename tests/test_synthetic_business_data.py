import pandas as pd
from lumina_framework.core.config import SyntheticScenarioConfig
from lumina_framework.data.synthetic import SyntheticRetailDataGenerator


def test_generator_is_deterministic_and_respects_inventory():
    config = SyntheticScenarioConfig()
    a = SyntheticRetailDataGenerator().generate(config)
    b = SyntheticRetailDataGenerator().generate(config)
    pd.testing.assert_frame_equal(a.raw_data, b.raw_data)
    assert a.clean_data.shape == (10400, 8)
    assert (a.clean_data.unidades_vendidas <= a.clean_data.inventario_inicial).all()
    assert (a.clean_data.unidades_vendidas >= 0).all()
    assert a.clean_data.producto_id.nunique() == 20
    assert a.clean_data.sucursal_id.nunique() == 5
    assert a.clean_data.semana.nunique() == 104
    assert len(a.raw_data) > len(a.clean_data)
    assert all(count > 0 for count in a.issue_counts.values())


def test_generator_includes_stockouts_and_serializes_source(tmp_path):
    g = SyntheticRetailDataGenerator()
    a = g.generate(SyntheticScenarioConfig(product_count=3, branch_count=2, week_count=24))
    assert a.clean_data.promocion.sum() > 0
    assert (a.clean_data.unidades_vendidas == a.clean_data.inventario_inicial).any()
    assert a.clean_data.groupby('producto_id').unidades_vendidas.mean().nunique() > 1
    paths = g.write(a, tmp_path/'source.csv', tmp_path/'metadata.json')
    assert all(p.exists() for p in paths)
    assert len(pd.read_csv(paths[0])) == len(a.raw_data)
