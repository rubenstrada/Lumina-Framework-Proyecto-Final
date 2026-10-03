"""Selección en validación y evaluación temporal final de tres enfoques."""
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.inspection import permutation_importance

from lumina_framework.preprocessing.preprocessor import DataPreprocessor
from lumina_framework.modeling.baseline import NaiveFourWeekBaseline
from lumina_framework.modeling.evaluator import ModelEvaluator


@dataclass
class ExperimentResult:
    validation_metrics: pd.DataFrame
    test_metrics: pd.DataFrame
    predictions: pd.DataFrame
    selected_model_name: str
    selected_pipeline: object
    importance: pd.DataFrame
    coefficients: pd.DataFrame
    validation_pipelines: dict
    refit_rows: int
    uncertainty: object
    selection_reason: str


class ModelExperimentRunner:
    def run(self, split, contract, config):
        """Elegir antes de consultar prueba evita optimizar sobre el resultado final."""
        evaluator = ModelEvaluator()
        features = list(contract.numeric_features+contract.categorical_features)
        target = contract.target_column
        transformer = DataPreprocessor.build_transformer(contract.numeric_features,contract.categorical_features)
        records = []
        val_models = {}
        baseline = NaiveFourWeekBaseline()
        naive_val = baseline.predict(split.validation)
        records.append(dict(modelo='Ingenuo',configuracion='4 semanas anteriores',
            **asdict(evaluator.calculate_regression_metrics(split.validation[target],naive_val))))
        candidates = [('Ridge',f'alpha={alpha}',Ridge(alpha=alpha,solver='lsqr')) for alpha in (.1,1.,10.)]
        candidates += [('Random Forest',f'depth={depth}; leaf={leaf}',
            RandomForestRegressor(n_estimators=config.forest_trees,max_depth=depth,
                min_samples_leaf=leaf,random_state=config.seed,n_jobs=1))
            for depth in (8,None) for leaf in (2,5)]
        best = {}
        for name, params, estimator in candidates:
            pipeline = Pipeline([('preprocessor',clone(transformer)),('model',estimator)])
            pipeline.fit(split.train[features],split.train[target])
            prediction = np.maximum(pipeline.predict(split.validation[features]),0)
            metrics = evaluator.calculate_regression_metrics(split.validation[target],prediction)
            records.append(dict(modelo=name,configuracion=params,**asdict(metrics)))
            if name not in best or metrics.mae < best[name][0]:
                best[name] = (metrics.mae,params,pipeline)
        validation = pd.DataFrame(records)
        baseline_mae = records[0]['mae']
        ridge_mae, forest_mae = best['Ridge'][0],best['Random Forest'][0]
        selected = 'Ingenuo'
        if min(ridge_mae,forest_mae) < baseline_mae:
            selected = 'Ridge' if ridge_mae <= forest_mae*1.02 and ridge_mae < baseline_mae else 'Random Forest'
        reason = ('Selección por MAE de validación; tolerancia de 2 % favorece Ridge por sencillez. '
                  'Prueba no participa en selección ni ajuste.')
        prediction_frame = split.test.copy()
        prediction_frame['Ingenuo'] = baseline.predict(split.test)
        metrics_rows = []
        refit = pd.concat([split.train,split.validation],ignore_index=True)
        fitted = {'Ingenuo':baseline}
        coefficients = pd.DataFrame(columns=['variable','coeficiente'])
        for name, (_,params,val_pipeline) in best.items():
            val_models[name] = val_pipeline
            model = clone(val_pipeline).fit(refit[features],refit[target])
            prediction_frame[name] = np.maximum(model.predict(split.test[features]),0)
            fitted[name] = model
            if name == 'Ridge':
                coefficients = pd.DataFrame({'variable':model.named_steps['preprocessor'].get_feature_names_out(),
                                             'coeficiente':model.named_steps['model'].coef_})
        for name in ('Ingenuo','Ridge','Random Forest'):
            metrics_rows.append(dict(modelo=name,**asdict(evaluator.calculate_regression_metrics(split.test[target],prediction_frame[name]))))
        test_metrics = pd.DataFrame(metrics_rows)
        baseline_test_mae = test_metrics.iloc[0].mae
        test_metrics['mejora_mae_pct'] = 100*(baseline_test_mae-test_metrics.mae)/baseline_test_mae if baseline_test_mae else np.nan
        importance = pd.DataFrame(columns=['variable','importancia','desviacion'])
        if selected != 'Ingenuo':
            pi = permutation_importance(fitted[selected],split.test[features],split.test[target],
                    scoring='neg_mean_absolute_error',n_repeats=5,random_state=config.seed,n_jobs=1)
            importance = pd.DataFrame({'variable':features,'importancia':pi.importances_mean,
                'desviacion':pi.importances_std}).sort_values('importancia',ascending=False)
        uncertainty = evaluator.bootstrap_mae_difference(prediction_frame,target,selected,'Ingenuo',
            contract.date_column,config.bootstrap_iterations,config.seed)
        return ExperimentResult(validation,test_metrics,prediction_frame,selected,fitted[selected],
                                importance,coefficients,val_models,len(refit),uncertainty,reason)
