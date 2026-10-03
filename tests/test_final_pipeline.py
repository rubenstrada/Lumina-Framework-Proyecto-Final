from pathlib import Path
from dataclasses import replace
import json
import joblib
import numpy as np
import pandas as pd
import pytest
from lumina_framework.core.config import load_project_configuration, ExperimentConfig
from lumina_framework.pipeline.orchestrator import LuminaPipeline
from lumina_framework.core.exceptions import LuminaFrameworkError


def small_config(tmp_path):
    config,c,s,e = load_project_configuration(Path('config/project_final.yaml'))
    config=replace(config,source_path=tmp_path/'data'/'input.csv',output_dir=tmp_path/'results')
    s=replace(s,product_count=3,branch_count=2,week_count=32)
    e=ExperimentConfig(train_end_week=16,validation_start_week=21,validation_end_week=22,
        test_start_week=27,test_end_week=28,forest_trees=12,bootstrap_iterations=30)
    return config,c,s,e


def test_final_pipeline_generates_artifacts_and_saved_model_predicts(tmp_path):
    config,c,s,e=small_config(tmp_path)
    r=LuminaPipeline().run_project(config,c,s,e)
    assert r.status == 'completed'
    assert len(r.artifact_paths) >= 20
    assert all(p.exists() for p in r.artifact_paths)
    manifest=json.loads((config.output_dir/'manifest.json').read_text(encoding='utf-8'))
    assert manifest['seed'] == 42 and manifest['status'] == 'completed'
    pred=pd.read_csv(config.output_dir/'predictions.csv')
    model=joblib.load(config.output_dir/'model.joblib')
    np.testing.assert_allclose(model.predict(pred),pred[manifest['selected_model']],rtol=1e-6)
    again=LuminaPipeline().run_project(config,c,s,e)
    pd.testing.assert_frame_equal(pred,pd.read_csv(config.output_dir/'predictions.csv'))
    assert again.status == 'completed'


def test_output_failure_does_not_claim_completion(tmp_path,monkeypatch):
    config,c,s,e=small_config(tmp_path)
    # El fallo real ocurre al escribir una salida; el resto del flujo permanece real.
    from lumina_framework.reporting.generator import ReportGenerator
    def denied(*args,**kwargs):
        raise PermissionError('denied')
    monkeypatch.setattr(ReportGenerator,'generate_project_reports',denied)
    with pytest.raises(LuminaFrameworkError):
        LuminaPipeline().run_project(config,c,s,e)
    assert json.loads((config.output_dir/'manifest.json').read_text())['status'] == 'failed'


def test_failed_rerun_cannot_leave_previous_completed_manifest(tmp_path,monkeypatch):
    config,c,s,e=small_config(tmp_path)
    LuminaPipeline().run_project(config,c,s,e)
    previous=json.loads((config.output_dir/'manifest.json').read_text())['run_id']
    def denied(*args,**kwargs):
        raise PermissionError('denied during rerun')
    monkeypatch.setattr('lumina_framework.reporting.generator.ReportGenerator.generate_project_reports',denied)
    with pytest.raises(LuminaFrameworkError):
        LuminaPipeline().run_project(config,c,s,e)
    manifest=json.loads((config.output_dir/'manifest.json').read_text())
    assert manifest['status'] == 'failed'
    assert manifest['run_id'] != previous


def test_final_report_handles_zero_observed_volume(tmp_path):
    config,c,s,e=small_config(tmp_path)
    from lumina_framework.data.synthetic import SyntheticRetailDataGenerator
    generated=SyntheticRetailDataGenerator().generate(s)
    generated.clean_data.loc[:,'unidades_vendidas']=0
    config.source_path.parent.mkdir(parents=True)
    generated.clean_data.to_csv(config.source_path,index=False)
    result=LuminaPipeline().run_project(config,c,s,e)
    assert result.status == 'completed'
    assert 'No disponible' in (config.output_dir/'technical_report.md').read_text(encoding='utf-8')
