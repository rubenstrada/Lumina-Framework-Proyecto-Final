"""Escenario reproducible de ventas e inventario; sus reglas son supuestos."""

from dataclasses import dataclass, asdict
from pathlib import Path
import json

import numpy as np
import pandas as pd

from lumina_framework.core.config import SyntheticScenarioConfig


@dataclass(frozen=True)
class GeneratedDataset:
    clean_data: pd.DataFrame
    raw_data: pd.DataFrame
    issue_counts: dict[str, int]


class SyntheticRetailDataGenerator:
    """Comparte patrones entre entidades, sin favorecer un algoritmo específico."""

    def generate(self, config: SyntheticScenarioConfig) -> GeneratedDataset:
        rng = np.random.default_rng(config.seed)
        dates = pd.date_range(config.start_date, periods=config.week_count, freq='7D')
        categories = ['Iluminación', 'Accesorios', 'Decoración', 'Herramientas']
        rows = []
        for product in range(config.product_count):
            category = categories[product % len(categories)]
            base = rng.uniform(12, 75)
            base_price = rng.uniform(80, 650)
            trend = rng.uniform(-0.0008, 0.002)
            phase = product % 4 * np.pi / 5
            for branch in range(config.branch_count):
                volume = 0.65 + 0.15 * branch
                stock = int(base * volume * 4)
                demand_memory = base * volume
                for week, date in enumerate(dates):
                    promo = int(rng.random() < 0.18)
                    price = round(base_price * (0.86 if promo else 1) * rng.uniform(.97, 1.03), 2)
                    season = 1 + .28 * np.sin(2*np.pi*week/52 + phase)
                    expected = base * volume * season * (1+trend*week) * (1+.32*promo) * (base_price/price)**.7
                    demand_memory = .6 * demand_memory + .4 * expected
                    wanted = max(0, int(rng.normal(demand_memory, max(2, expected*.18))))
                    if rng.random() < .012:
                        wanted = int(wanted * 1.8)  # pico plausible, conservado por limpieza
                    if week % 3 == 0 and rng.random() >= .12:
                        stock = int(expected * rng.uniform(2.5, 4.2))
                    initial = max(stock, 0)
                    sold = min(wanted, initial)
                    rows.append((date, f'SUC-{branch+1:02d}', f'PROD-{product+1:03d}', category,
                                 price, promo, initial, sold))
                    stock = initial - sold
        columns = ['semana','sucursal_id','producto_id','categoria','precio',
                   'promocion','inventario_inicial','unidades_vendidas']
        clean = pd.DataFrame(rows, columns=columns)
        raw = clean.copy(deep=True)
        raw['semana'] = raw.semana.dt.strftime('%Y-%m-%d')
        count = max(1, int(len(raw)*.003))
        chosen = rng.choice(len(raw), size=count*7, replace=False).reshape(7, count)
        raw.loc[chosen[0], 'precio'] = np.nan
        raw.loc[chosen[1], 'inventario_inicial'] = np.nan
        raw.loc[chosen[2], 'categoria'] = raw.loc[chosen[2], 'categoria'].str.upper().radd(' ').add(' ')
        raw.loc[chosen[3], 'semana'] = 'fecha-invalida'
        raw.loc[chosen[4], 'precio'] = -10
        raw.loc[chosen[5], 'inventario_inicial'] = -5
        raw.loc[chosen[6], 'unidades_vendidas'] = 999999
        duplicates = clean.iloc[rng.choice(len(clean), size=count, replace=False)].copy()
        duplicates['semana'] = duplicates.semana.dt.strftime('%Y-%m-%d')
        # Duplicar después de alterar evita introducir llaves contradictorias.
        raw = pd.concat([raw, raw.iloc[rng.choice(len(raw), size=count, replace=False)]], ignore_index=True)
        issues = dict(duplicados=count, faltantes_precio=count, faltantes_inventario=count,
                      categorias_inconsistentes=count, fechas_invalidas=count,
                      precios_imposibles=count, inventarios_imposibles=count,
                      ventas_corruptas=count)
        return GeneratedDataset(clean, raw, issues)

    def write(self, result: GeneratedDataset, csv_path: Path, metadata_path: Path):
        """Guarda solo la fuente de entrada; la tabla perfecta no se usa para limpiar."""
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        result.raw_data.to_csv(csv_path, index=False)
        metadata_path.write_text(json.dumps({'original_rows':len(result.clean_data),
            'raw_rows':len(result.raw_data), 'injected_issues':result.issue_counts},
            ensure_ascii=False, indent=2), encoding='utf-8')
        return csv_path, metadata_path
