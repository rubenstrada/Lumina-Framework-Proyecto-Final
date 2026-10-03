"""Cortes por semanas completas y embargo correspondiente al horizonte."""
from dataclasses import dataclass
import pandas as pd
from lumina_framework.core.exceptions import InsufficientDataError


@dataclass(frozen=True)
class TemporalSplitResult:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame
    boundaries: dict[str, str]


class TemporalDataSplitter:
    def split(self, data, date_column, config):
        dates = pd.to_datetime(data[date_column])
        week = ((dates-pd.Timestamp(config.start_date)).dt.days//7)+1
        frames, boundaries = [], {}
        for name in ('train','validation','test'):
            a,b = getattr(config,name+'_start_week'),getattr(config,name+'_end_week')
            part = data.loc[week.between(a,b)].sort_values(date_column).reset_index(drop=True)
            if part.empty:
                raise InsufficientDataError('No hay datos en el periodo '+name)
            boundaries[name+'_start'] = str(part[date_column].min().date())
            boundaries[name+'_end'] = str(part[date_column].max().date())
            frames.append(part)
        return TemporalSplitResult(*frames,boundaries)
