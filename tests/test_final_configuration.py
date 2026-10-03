from pathlib import Path

import pytest

from lumina_framework.core.config import load_project_configuration, SyntheticScenarioConfig, ExperimentConfig
from lumina_framework.core.exceptions import SchemaConfigurationError


def test_final_configuration_loads_source_contract_and_periods():
    config, contract, scenario, experiment = load_project_configuration(Path('config/project_final.yaml'))
    assert (scenario.seed, scenario.product_count, scenario.branch_count, scenario.week_count) == (42, 20, 5, 104)
    assert scenario.start_date == '2024-01-01'
    assert len(contract.columns) == 8
    assert contract.target_column == 'ventas_proximas_4_semanas'
    assert experiment.train_end_week == 68
    assert experiment.test_start_week == 89
    assert config.source_path.name == 'lumina_operaciones.csv'


def test_configuration_rejects_invalid_counts_and_overlapping_windows():
    with pytest.raises(SchemaConfigurationError):
        SyntheticScenarioConfig(product_count=0)
    with pytest.raises(SchemaConfigurationError):
        ExperimentConfig(validation_start_week=68)
