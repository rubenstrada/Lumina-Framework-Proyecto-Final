import pandas as pd
import pytest
from lumina_framework.modeling.evaluator import ModelEvaluator
from lumina_framework.modeling.baseline import NaiveFourWeekBaseline


def test_metrics_return_none_wape_for_zero_volume():
    r = ModelEvaluator().calculate_regression_metrics([0,0],[1,1])
    assert r.wape is None
    assert r.mae == 1


def test_metrics_match_hand_calculation():
    r = ModelEvaluator().calculate_regression_metrics([1,2,3],[1,2,2])
    assert r.mae == pytest.approx(1/3)
    assert r.rmse == pytest.approx((1/3)**.5)
    assert r.wape == pytest.approx(1/6)
    assert r.r2 == pytest.approx(.5)


def test_baseline_returns_past_window_and_block_bootstrap_is_deterministic():
    f = pd.DataFrame({'baseline_4_semanas':[5,6,7,8], 'real':[6,7,8,9],
                      'pred':[6,7,8,9], 'semana':pd.date_range('2024-01-01',periods=4,freq='7D')})
    assert NaiveFourWeekBaseline().predict(f).tolist() == [5,6,7,8]
    ev = ModelEvaluator()
    a = ev.bootstrap_mae_difference(f,'real','pred','baseline_4_semanas','semana',100,42)
    b = ev.bootstrap_mae_difference(f,'real','pred','baseline_4_semanas','semana',100,42)
    assert a == b and a.lower <= a.upper
    assert a.lower == -1
