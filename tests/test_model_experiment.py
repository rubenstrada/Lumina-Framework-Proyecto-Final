from pathlib import Path
from dataclasses import replace
import numpy as np
import pandas as pd
from lumina_framework.core.config import load_project_configuration, ExperimentConfig
from lumina_framework.data.synthetic import SyntheticRetailDataGenerator
from lumina_framework.preprocessing.features import FeatureEngineer
from lumina_framework.preprocessing.temporal import TemporalDataSplitter
from lumina_framework.modeling.experiment import ModelExperimentRunner


def experiment_fixture():
    _, c,s,e = load_project_configuration(Path('config/project_final.yaml'))
    s = replace(s,product_count=3,branch_count=2,week_count=32)
    e = ExperimentConfig(train_end_week=16,validation_start_week=21,validation_end_week=22,
                         test_start_week=27,test_end_week=28,forest_trees=12,bootstrap_iterations=20)
    f = FeatureEngineer().build(SyntheticRetailDataGenerator().generate(s).clean_data,c)
    return c,e,TemporalDataSplitter().split(f,'semana',e)


def test_experiment_compares_candidates_and_is_reproducible():
    c,e,split = experiment_fixture()
    a = ModelExperimentRunner().run(split,c,e)
    b = ModelExperimentRunner().run(split,c,e)
    assert len(a.validation_metrics) == 8  # 1 referencia + 3 Ridge + 4 bosque
    assert set(a.test_metrics.modelo) == {'Ingenuo','Ridge','Random Forest'}
    pd.testing.assert_frame_equal(a.predictions,b.predictions)
    assert a.selected_model_name in {'Ingenuo','Ridge','Random Forest'}
    assert set(a.importance.columns) >= {'variable','importancia'}


def test_experiment_handles_unseen_category_in_test():
    c,e,split = experiment_fixture()
    split.test.loc[:,'categoria'] = 'Nueva familia'
    split.test.loc[:,'precio'] = 9999
    a = ModelExperimentRunner().run(split,c,e)
    assert np.isfinite(a.predictions[['Ridge','Random Forest']]).all().all()
    statistics = a.validation_pipelines['Ridge'].named_steps['preprocessor'].named_transformers_['numeric'].named_steps['imputer'].statistics_
    expected = split.train.loc[:,list(c.numeric_features)].median().to_numpy()
    np.testing.assert_allclose(statistics,expected)
    assert a.refit_rows == len(split.train)+len(split.validation)


def test_persisted_prediction_rule_is_nonnegative_even_when_ridge_extrapolates():
    c,e,split = experiment_fixture()
    split.test.loc[:,'precio'] = 999999
    result = ModelExperimentRunner().run(split,c,e)
    ridge = result.validation_pipelines['Ridge']
    assert (ridge.predict(split.test[list(c.numeric_features+c.categorical_features)]) >= 0).all()
