"""Excepciones de dominio con mensajes accionables."""


class LuminaFrameworkError(Exception):
    """Error base controlado por el framework."""


class DataSourceError(LuminaFrameworkError):
    """La fuente no existe, no es compatible o no puede leerse."""


class SchemaConfigurationError(LuminaFrameworkError):
    """El contrato no define la estructura necesaria para la operación."""


class DataValidationError(LuminaFrameworkError):
    """Los datos no satisfacen una regla crítica del contrato."""


class TargetNotConfiguredError(SchemaConfigurationError):
    """No se configuró una variable objetivo para modelado supervisado."""


class InsufficientDataError(LuminaFrameworkError):
    """La cantidad o calidad de observaciones no permite continuar."""

