"""Señales de revisión, no órdenes de compra ni estimaciones de demanda perdida."""
import numpy as np


class InventorySignalGenerator:
    def generate(self,predictions,prediction_column):
        """Compara horizonte futuro con stock al cierre de la misma fecha de corte."""
        latest=predictions.loc[predictions.semana.eq(predictions.semana.max())].copy()
        columns=['semana','sucursal_id','producto_id','inventario_inicial','inventario_cierre']
        signals=latest[columns].copy()
        signals['venta_prevista_4_semanas']=np.maximum(latest[prediction_column],0)
        signals['brecha_estimada']=(signals.venta_prevista_4_semanas-signals.inventario_cierre).clip(lower=0)
        signals['requiere_revision']=(signals.brecha_estimada>0) | signals.inventario_cierre.isna()
        signals['estado']=np.where(signals.inventario_cierre.isna(),'inventario_no_disponible',
                                   np.where(signals.requiere_revision,'revisar_cobertura','sin_brecha_estimada'))
        return signals.reset_index(drop=True)
