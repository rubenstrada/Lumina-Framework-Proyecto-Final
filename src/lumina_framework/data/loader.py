"""Carga de fuentes sin aplicar transformaciones implícitas."""

from pathlib import Path

import pandas as pd

from lumina_framework.core.exceptions import DataSourceError


class DataLoader:
    """Lee una fuente CSV y conserva su estructura original."""

    def load(self, path: Path) -> pd.DataFrame:
        """Carga un CSV o explica por qué la fuente no puede utilizarse."""
        if not path.exists():
            raise DataSourceError(f"La fuente no existe: {path}")
        if path.suffix.lower() != ".csv":
            raise DataSourceError(f"Extensión no soportada: {path.suffix}")
        try:
            return pd.read_csv(path)
        except (OSError, UnicodeError, pd.errors.ParserError) as exc:
            raise DataSourceError(
                f"No fue posible leer {path.name}: {exc}"
            ) from exc
