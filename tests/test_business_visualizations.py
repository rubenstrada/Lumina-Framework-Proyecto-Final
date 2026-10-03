from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from lumina_framework.visualization.business import BusinessVisualizer
from lumina_framework.visualization.diagnostics import ModelDiagnosticsVisualizer


def test_visualizers_produce_readable_pngs_without_mutating_data(tmp_path):
    dates = pd.date_range('2024-01-01',periods=12,freq='7D')
    data = pd.DataFrame({'semana':dates,'categoria':['A','B']*6,'sucursal_id':['S1','S2']*6,
        'unidades_vendidas':range(12),'promocion':[0,1]*6,
        'ventas_proximas_4_semanas':range(20,32),'Ingenuo':range(22,34),'Ridge':range(21,33),'Random Forest':range(20,32)})
    original = data.copy(deep=True)
    metrics = pd.DataFrame({'modelo':['Ingenuo','Ridge','Random Forest'],'mae':[2,1,0],'rmse':[2,1,0],'wape':[.2,.1,0]})
    importance = pd.DataFrame({'variable':['precio','promocion'],'importancia':[1.,.5]})
    a = BusinessVisualizer().generate(data,tmp_path)
    b = ModelDiagnosticsVisualizer().generate(data,metrics,importance,tmp_path)
    assert len(a+b) == 8
    for p in a+b:
        assert p.stat().st_size > 5000
        pixels = plt.imread(p)
        assert pixels.shape[0] > 400 and pixels.shape[1] > 800
    assert not plt.get_fignums()
    pd.testing.assert_frame_equal(data,original)
