import pandas as pd
from lumina_framework.reporting.inventory import InventorySignalGenerator


def test_inventory_signals_use_stock_at_forecast_cutoff_and_latest_week():
    f = pd.DataFrame({'semana':pd.to_datetime(['2024-01-01','2024-01-08','2024-01-08']),
        'sucursal_id':['S','S','S'],'producto_id':['A','A','B'],
        'inventario_inicial':[100,80,50],'unidades_vendidas':[30,20,10],
        'inventario_cierre':[70,60,40],'Ridge':[90,100,-5]})
    r = InventorySignalGenerator().generate(f,'Ridge')
    assert len(r) == 2
    assert r.brecha_estimada.tolist() == [40,0]
    assert r.requiere_revision.tolist() == [True,False]
    assert (r.venta_prevista_4_semanas >= 0).all()


def test_unknown_inventory_requires_quality_review():
    f=pd.DataFrame({'semana':pd.to_datetime(['2024-01-08']),
        'sucursal_id':['S'],'producto_id':['A'],'inventario_inicial':[None],
        'unidades_vendidas':[10],'inventario_cierre':[None],'Ridge':[100]})
    r=InventorySignalGenerator().generate(f,'Ridge')
    assert r.requiere_revision.iloc[0]
    assert r.estado.iloc[0] == 'inventario_no_disponible'
