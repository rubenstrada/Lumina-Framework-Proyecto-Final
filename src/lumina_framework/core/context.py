"""Trazabilidad mínima de una ejecución del framework."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class RunContext:
    """Registra identidad, estado y artefactos de una corrida."""

    run_id: str
    started_at: datetime
    status: str = "created"
    events: list[str] = field(default_factory=list)
    artifacts: dict[str, str] = field(default_factory=dict)

    @classmethod
    def start(cls) -> "RunContext":
        """Crea un contexto identificable con tiempo UTC."""
        return cls(run_id=str(uuid4()), started_at=datetime.now(timezone.utc))

    def record_event(self, event: str) -> None:
        """Agrega un evento legible en orden de ejecución."""
        self.events.append(event)

    def record_artifact(self, name: str, path: str) -> None:
        """Relaciona un resultado lógico con su ruta relativa."""
        self.artifacts[name] = path

    def to_manifest(self) -> dict[str, object]:
        """Devuelve una representación serializable de la corrida."""
        return {
            "run_id": self.run_id,
            "started_at": self.started_at.isoformat(),
            "status": self.status,
            "events": list(self.events),
            "artifacts": dict(self.artifacts),
        }
