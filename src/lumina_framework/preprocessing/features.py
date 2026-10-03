"""Variables históricas y etiqueta futura con calendario explícito."""
import numpy as np
import pandas as pd
from lumina_framework.core.exceptions import InsufficientDataError, DataValidationError


class FeatureEngineer:
    def build(self, data, contract, calendar_start=None):
        """Usa solamente semanas anteriores en rezagos y exige etiquetas observadas."""
        date, sales = contract.date_column, contract.sales_column
        keys = [k for k in contract.identifier_columns if k != date]
        if data.empty:
            raise InsufficientDataError('No existen grupos disponibles.')
        try:
            dates = pd.to_datetime(data[date], errors='coerce')
            if dates.isna().any() or not dates.eq(dates.dt.normalize()).all():
                raise DataValidationError('Las semanas requieren fechas válidas sin componente horario.')
            anchor = dates.min() if calendar_start is None else pd.Timestamp(calendar_start)
            if pd.isna(anchor) or anchor != anchor.normalize():
                raise DataValidationError('El inicio del calendario requiere una fecha válida sin componente horario.')
            offsets = (dates - anchor).dt.days
        except (ValueError, TypeError, AttributeError) as exc:
            raise DataValidationError('Las fechas no son compatibles con el calendario semanal.') from exc
        if offsets.mod(7).ne(0).any():
            raise DataValidationError('Hay fechas fuera del calendario semanal declarado.')
        prepared = data.copy(deep=True)
        prepared[date] = dates
        results = []
        for _, group in prepared.groupby(keys, sort=True):
            g = group.copy().set_index(date).sort_index()
            if len(g) < 9:
                raise InsufficientDataError('Se requieren nueve semanas por grupo.')
            if g.index.duplicated().any():
                raise DataValidationError('Llave temporal repetida.')
            calendar = pd.date_range(g.index.min(), g.index.max(), freq='7D')
            g = g.reindex(calendar)
            s = g[sales]
            past = s.shift(1)
            for lag, name in [(1,'ventas_semana_anterior'),(2,'ventas_hace_2_semanas'),(4,'ventas_hace_4_semanas')]:
                g[name] = s.shift(lag)
            rolling = past.rolling(4, min_periods=4)
            g['promedio_ventas_4_semanas'] = rolling.mean()
            g['variabilidad_4_semanas'] = rolling.std()
            g['baseline_4_semanas'] = rolling.sum()
            g['tendencia_reciente'] = past - s.shift(4)
            g['mes'] = g.index.month
            g['semana_anio'] = g.index.isocalendar().week.to_numpy(dtype=int)
            g['inventario_sobre_promedio'] = g[contract.inventory_column] / g.promedio_ventas_4_semanas.replace(0,np.nan)
            # No sumamos si falta cualquiera de las cuatro semanas futuras.
            future = pd.concat([s.shift(-i) for i in range(1,5)],axis=1)
            g[contract.target_column] = future.sum(axis=1,min_count=4)
            g['inventario_cierre'] = g[contract.inventory_column] - s
            g['posible_agotamiento'] = s.eq(g[contract.inventory_column]).astype(int)
            g[date] = g.index
            g = g.dropna(subset=['baseline_4_semanas',contract.target_column,sales,*keys])
            results.append(g.reset_index(drop=True))
        if not results:
            raise InsufficientDataError('No existen grupos disponibles.')
        return pd.concat(results,ignore_index=True)
