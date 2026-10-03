# Proyecto final del framework Lumina Implementation Plan

Estado de ejecución: implementación y entregables comprobados el 2 de octubre de 2026. Registro autoritativo de lo ejecutado y las adaptaciones: `docs/evidencia_final/execution_log.md` y `verification_summary.json`. Los checkboxes siguientes conservan el plan original; no son un tablero activo. La entrega usa una repo independiente por solicitud posterior del estudiante y conserva el Avance 2 como referencia. La fixture de integración usa 32 semanas para respetar los espacios temporales. La revisión del Word se realizó con Microsoft Word al faltar el renderer de LibreOffice.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convertir el framework conceptual existente en un prototipo reproducible que genere el escenario acordado, ejecute el flujo completo de regresión temporal, compare tres enfoques y produzca la evidencia técnica y académica de la actividad final.

**Architecture:** Se conservarán los paquetes actuales y se ampliarán mediante composición. La fuente controlada se generará de forma independiente; el pipeline cargará una copia con anomalías, limpiará sin mutar la entrada, construirá características históricas, separará periodos con espacios de cuatro semanas, entrenará candidatos mediante pipelines de scikit-learn y entregará resultados tipados a visualización y reportes.

**Tech Stack:** Python 3.11, pandas, NumPy, scikit-learn, Matplotlib, Seaborn, PyYAML, joblib, pytest y python-docx mediante el runtime de documentos de Codex.

**Spec:** `docs/superpowers/specs/2026-10-02-proyecto-final-framework-design.md`

## Global Constraints

- Conservar compatibilidad con el diagnóstico conceptual y las 28 pruebas existentes.
- Usar semilla `42`, 20 productos, 5 sucursales, 104 semanas y fecha inicial `2024-01-01`.
- Cada fila representa producto-sucursal-semana; el target es la suma de ventas de las cuatro semanas posteriores.
- Tratar ventas como aproximación de demanda observada y declarar la limitación por desabasto.
- Ajustar imputación, codificación, escalado y modelos únicamente con entrenamiento; después de seleccionar configuración, reajustar con entrenamiento más validación antes de prueba.
- Mantener espacios temporales de cuatro semanas entre orígenes de entrenamiento, validación y prueba.
- Generar figuras exclusivamente con Matplotlib y Seaborn.
- No añadir base de datos, API, frontend, dashboard, aprendizaje no supervisado ni dependencias externas innecesarias.
- No presentar resultados del escenario como información real de Lumina o Red Comercial Boreal.
- Implementar mediante TDD y realizar commits pequeños por tarea.

## Review Focus

- Un CSV con fecha inválida debe limpiarse de forma trazable sin impedir que las fechas válidas continúen; lo comprobará `test_business_cleaner_drops_unrecoverable_dates_and_logs_change` en la Tarea 3.
- Una categoría no vista en entrenamiento debe transformarse sin error; lo comprobará `test_experiment_handles_unseen_category_in_test` en la Tarea 6.
- Ninguna característica histórica puede incluir la semana actual o futura; lo comprobará `test_feature_engineer_uses_strictly_previous_weeks` en la Tarea 4.
- WAPE debe devolver `None` cuando el volumen real total es cero; lo comprobará `test_metrics_return_none_wape_for_zero_volume` en la Tarea 5.
- Todas las combinaciones de una misma semana deben quedar en el mismo periodo; lo comprobará `test_temporal_split_never_divides_a_week_across_sets` en la Tarea 4.

---

## File Structure

### Files to create

- `config/project_final.yaml`: contrato confirmado, parámetros del escenario y cortes del experimento.
- `src/lumina_framework/data/synthetic.py`: generación reproducible y anomalías controladas.
- `src/lumina_framework/preprocessing/features.py`: rezagos, agregados históricos y target futuro.
- `src/lumina_framework/preprocessing/temporal.py`: partición semanal con espacios por horizonte.
- `src/lumina_framework/modeling/baseline.py`: referencia de las cuatro semanas anteriores.
- `src/lumina_framework/modeling/experiment.py`: selección de configuraciones y evaluación final.
- `src/lumina_framework/visualization/business.py`: exploración del escenario.
- `src/lumina_framework/visualization/diagnostics.py`: comparación, errores e interpretación.
- `src/lumina_framework/reporting/inventory.py`: señales orientativas para revisión de inventario.
- `scripts/run_final_project.py`: punto de entrada del proyecto final, sin lógica de negocio interna.
- `tests/test_final_configuration.py`
- `tests/test_synthetic_business_data.py`
- `tests/test_business_quality_pipeline.py`
- `tests/test_feature_engineering_and_temporal_split.py`
- `tests/test_regression_metrics.py`
- `tests/test_model_experiment.py`
- `tests/test_business_visualizations.py`
- `tests/test_final_reporting.py`
- `tests/test_final_pipeline.py`
- `docs/proyecto_final.md`: explicación técnica alineada con los 12 puntos.

### Files to modify

- `src/lumina_framework/core/config.py`: configuración extendida y cargador del proyecto final.
- `src/lumina_framework/core/contracts.py`: roles semánticos y resultados tipados nuevos.
- `src/lumina_framework/data/validator.py`: reglas de calidad empresarial.
- `src/lumina_framework/data/cleaner.py`: limpieza conservadora y bitácora.
- `src/lumina_framework/preprocessing/preprocessor.py`: transformador reutilizable para tres periodos.
- `src/lumina_framework/modeling/evaluator.py`: R², segmentación e incertidumbre.
- `src/lumina_framework/reporting/generator.py`: artefactos del experimento y reporte Markdown.
- `src/lumina_framework/pipeline/orchestrator.py`: ejecución de extremo a extremo.
- `src/lumina_framework/cli.py`: modo de ejecución final conservando el diagnóstico.
- `README.md`: estado funcional, mapa de la actividad y comandos.
- `artifacts/development_log.md`: decisiones, errores y ajustes de esta etapa.
- `pyproject.toml`: descripción final sin cambiar el conjunto mínimo de dependencias.

### Generated outputs

- `data/raw/lumina_operaciones.csv`
- `data/raw/generation_metadata.json`
- `artifacts/project_final/` con perfiles, limpieza, métricas, predicciones, señales, figuras, modelo y manifiesto.
- `C:/Users/rayor/Downloads/Programación para la inteligencia artificial Proyecto final.docx`
- `C:/Users/rayor/Downloads/lumina_proyecto_final_codigo.zip`

---

### Task 1: Final project contracts and configuration

**Files:**
- Modify: `src/lumina_framework/core/contracts.py`
- Modify: `src/lumina_framework/core/config.py`
- Create: `config/project_final.yaml`
- Create: `tests/test_final_configuration.py`

**Interfaces:**
- Produces: `SyntheticScenarioConfig(seed, product_count, branch_count, week_count, start_date)`.
- Produces: `ExperimentConfig(train_start_week, train_end_week, validation_start_week, validation_end_week, test_start_week, test_end_week, horizon_weeks)`.
- Produces: semantic fields on `DatasetContract`: `category_column`, `price_column`, `promotion_column`, `inventory_column`, `sales_column`.
- Produces: `load_project_configuration(path: Path) -> tuple[FrameworkConfig, DatasetContract, SyntheticScenarioConfig, ExperimentConfig]`.
- Preserves: `load_yaml_configuration(path)` and existing defaults.

- [ ] **Step 1: Write failing configuration tests**

Add tests asserting that `config/project_final.yaml` loads seed `42`, counts `20/5/104`, start date `2024-01-01`, the eight exact source columns, identifier columns `producto_id/sucursal_id/semana`, target `ventas_proximas_4_semanas`, horizon `4 semanas`, and cutoffs `5-68`, `73-84`, `89-100`.

- [ ] **Step 2: Run the tests and confirm the missing interfaces fail**

Run: `python -m pytest tests/test_final_configuration.py -v`

Expected: FAIL because the new configuration types and loader do not exist.

- [ ] **Step 3: Implement typed configuration while preserving the old loader**

Add the exact interfaces above. Reject nonpositive counts, a horizon other than four, overlapping ranges and a start date that cannot be parsed with `SchemaConfigurationError`.

- [ ] **Step 4: Run configuration and legacy tests**

Run: `python -m pytest tests/test_final_configuration.py tests/test_config_and_readiness.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add config/project_final.yaml src/lumina_framework/core tests/test_final_configuration.py
git commit -m "feat: definir configuración del proyecto final"
```

### Task 2: Reproducible business dataset generator

**Files:**
- Create: `src/lumina_framework/data/synthetic.py`
- Modify: `src/lumina_framework/data/__init__.py`
- Create: `tests/test_synthetic_business_data.py`

**Interfaces:**
- Consumes: `SyntheticScenarioConfig` from Task 1.
- Produces: `GeneratedDataset(clean_data: pd.DataFrame, raw_data: pd.DataFrame, issue_counts: dict[str, int])`.
- Produces: `SyntheticRetailDataGenerator.generate(config: SyntheticScenarioConfig) -> GeneratedDataset`.
- Produces: `SyntheticRetailDataGenerator.write(result: GeneratedDataset, csv_path: Path, metadata_path: Path) -> tuple[Path, Path]`.

- [ ] **Step 1: Write failing determinism and shape tests**

Assert two calls with the same config produce identical frames; `clean_data` contains exactly 10,400 rows and the eight configured columns; every clean sale is nonnegative and no greater than starting inventory; product, branch and week cardinalities are 20, 5 and 104.

- [ ] **Step 2: Write failing scenario behavior tests**

Assert the controlled process produces variation by product and branch, at least one promotional week, at least one stockout-limited observation and metadata for exact duplicates, missing values, inconsistent categories, invalid dates, impossible values and corrupted outliers.

- [ ] **Step 3: Run tests and confirm failure**

Run: `python -m pytest tests/test_synthetic_business_data.py -v`

Expected: FAIL with missing generator module.

- [ ] **Step 4: Implement the generator**

Use a local `numpy.random.Generator`; do not call global `np.random.seed`. Build demand from product base, branch factor, category seasonality, product trend, promotion uplift, price effect and noise. Run a simple inventory/replenishment process, then inject anomalies into a deep copy using deterministic sampled indices.

- [ ] **Step 5: Verify tests and write round-trip**

Run: `python -m pytest tests/test_synthetic_business_data.py -v`

Expected: PASS and a temporary CSV reload equals `raw_data` after normalized dtypes.

- [ ] **Step 6: Commit**

```bash
git add src/lumina_framework/data tests/test_synthetic_business_data.py
git commit -m "feat: generar escenario empresarial reproducible"
```

### Task 3: Business validation and conservative cleaning

**Files:**
- Modify: `src/lumina_framework/core/contracts.py`
- Modify: `src/lumina_framework/data/validator.py`
- Modify: `src/lumina_framework/data/cleaner.py`
- Create: `tests/test_business_quality_pipeline.py`
- Modify: `tests/test_validation_and_cleaning.py`

**Interfaces:**
- Produces: additional `ValidationResult` fields `missing_by_column`, `negative_by_column`, `sales_above_inventory`, `inconsistent_categories` with backward-compatible defaults.
- Produces: `DataValidator.validate_business_rules(data: pd.DataFrame, contract: DatasetContract) -> ValidationResult`.
- Produces: `DataCleaner.clean_business_data(data: pd.DataFrame, contract: DatasetContract) -> CleaningResult`.

- [ ] **Step 1: Write failing validation tests**

Assert the validator counts every injected issue without mutating the raw frame and raises `SchemaConfigurationError` when semantic roles are absent.

- [ ] **Step 2: Write failing conservative-cleaning tests**

Include `test_business_cleaner_drops_unrecoverable_dates_and_logs_change`. Assert exact duplicates are removed, known category variants normalize, invalid dates drop, negative numeric values become missing for later train-only imputation, sales above available inventory are capped, plausible promotional spikes remain and every action has a `CleaningChange`.

- [ ] **Step 3: Run tests and confirm failure**

Run: `python -m pytest tests/test_business_quality_pipeline.py -v`

Expected: FAIL because the business methods do not exist.

- [ ] **Step 4: Implement validation and cleaning**

Use only contract roles and explicit rules. Preserve the existing generic `validate()` and `clean()` APIs. Return a deep-copied frame and deterministic change ordering.

- [ ] **Step 5: Run business and legacy quality tests**

Run: `python -m pytest tests/test_business_quality_pipeline.py tests/test_validation_and_cleaning.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/lumina_framework/core/contracts.py src/lumina_framework/data tests/test_business_quality_pipeline.py tests/test_validation_and_cleaning.py
git commit -m "feat: limpiar datos empresariales con trazabilidad"
```

### Task 4: Leakage-safe feature engineering and temporal split

**Files:**
- Create: `src/lumina_framework/preprocessing/features.py`
- Create: `src/lumina_framework/preprocessing/temporal.py`
- Modify: `src/lumina_framework/preprocessing/__init__.py`
- Modify: `src/lumina_framework/core/contracts.py`
- Create: `tests/test_feature_engineering_and_temporal_split.py`

**Interfaces:**
- Produces: `FeatureEngineer.build(data: pd.DataFrame, contract: DatasetContract) -> pd.DataFrame`.
- Produces: columns `ventas_semana_anterior`, `ventas_hace_2_semanas`, `ventas_hace_4_semanas`, `promedio_ventas_4_semanas`, `variabilidad_4_semanas`, `tendencia_reciente`, `mes`, `semana_anio`, `inventario_sobre_promedio`, `ventas_proximas_4_semanas` and `baseline_4_semanas`.
- Produces: `TemporalSplitResult(train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame, boundaries: dict[str, str])`.
- Produces: `TemporalDataSplitter.split(data: pd.DataFrame, date_column: str, config: ExperimentConfig) -> TemporalSplitResult`.

- [ ] **Step 1: Write failing feature calculations**

Use a single group with known values `1..10`. Assert the first valid row uses only the four preceding values, `baseline_4_semanas` is their sum and the target is the sum of the next four values.

- [ ] **Step 2: Add leakage and completeness tests**

Add `test_feature_engineer_uses_strictly_previous_weeks`; mutate a future sale and assert past features do not change. Assert the full clean scenario yields 9,600 feature rows before temporal embargoes.

- [ ] **Step 3: Write failing split tests**

Add `test_temporal_split_never_divides_a_week_across_sets`. Assert week-number ranges are exactly 5-68, 73-84 and 89-100 and no set shares a week or logical key.

- [ ] **Step 4: Run tests and confirm failure**

Run: `python -m pytest tests/test_feature_engineering_and_temporal_split.py -v`

Expected: FAIL with missing modules.

- [ ] **Step 5: Implement features and split**

Sort by product, branch and week. Reindex each product-sucursal group to the expected weekly calendar before calculating variables so a missing week cannot masquerade as the immediately preceding week. Use grouped `shift` and rolling windows shifted by one period, discard any feature or target window that crosses a missing observation, keep the date and identifiers as metadata and raise `InsufficientDataError` when a group lacks nine consecutive weeks.

- [ ] **Step 6: Run tests**

Run: `python -m pytest tests/test_feature_engineering_and_temporal_split.py -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/lumina_framework/core/contracts.py src/lumina_framework/preprocessing tests/test_feature_engineering_and_temporal_split.py
git commit -m "feat: crear variables y cortes temporales sin fuga"
```

### Task 5: Regression metrics, baseline and uncertainty

**Files:**
- Create: `src/lumina_framework/modeling/baseline.py`
- Modify: `src/lumina_framework/modeling/evaluator.py`
- Modify: `src/lumina_framework/modeling/__init__.py`
- Modify: `src/lumina_framework/core/contracts.py`
- Create: `tests/test_regression_metrics.py`
- Modify: `tests/test_modeling_and_evaluation.py`

**Interfaces:**
- Produces: `EvaluationMetrics(mae: float, rmse: float, wape: float | None, r2: float)`.
- Produces: `NaiveFourWeekBaseline.predict(data: pd.DataFrame) -> pd.Series` using `baseline_4_semanas`.
- Produces: `ModelEvaluator.calculate_regression_metrics(y_true, predictions) -> EvaluationMetrics`.
- Produces: `ModelEvaluator.segmented_metrics(frame, y_column, prediction_column, segments) -> pd.DataFrame`.
- Produces: `ModelEvaluator.bootstrap_mae_difference(frame, y_column, candidate_column, baseline_column, week_column, iterations=1000, seed=42) -> ConfidenceInterval`.

- [ ] **Step 1: Write failing known-value metric tests**

Assert MAE, RMSE, WAPE and R² against hand-computed arrays and add `test_metrics_return_none_wape_for_zero_volume`.

- [ ] **Step 2: Write failing baseline, segmentation and bootstrap tests**

Assert the baseline returns the exact stored sum; segmented output includes global, branch, category and product records; bootstrap is deterministic, returns ordered bounds and resamples complete weeks.

- [ ] **Step 3: Run tests and confirm failure**

Run: `python -m pytest tests/test_regression_metrics.py tests/test_modeling_and_evaluation.py -v`

Expected: FAIL for the new interfaces.

- [ ] **Step 4: Implement the evaluator extensions**

Retain `evaluate_regression()` as the backward-compatible baseline comparison. Guard against empty, nonfinite and unequal arrays.

- [ ] **Step 5: Run tests**

Run: `python -m pytest tests/test_regression_metrics.py tests/test_modeling_and_evaluation.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/lumina_framework/core/contracts.py src/lumina_framework/modeling tests/test_regression_metrics.py tests/test_modeling_and_evaluation.py
git commit -m "feat: evaluar regresión con referencia e incertidumbre"
```

### Task 6: Ridge and Random Forest experiment runner

**Files:**
- Modify: `src/lumina_framework/preprocessing/preprocessor.py`
- Create: `src/lumina_framework/modeling/experiment.py`
- Modify: `src/lumina_framework/core/contracts.py`
- Create: `tests/test_model_experiment.py`
- Modify: `tests/test_preprocessing.py`

**Interfaces:**
- Consumes: `TemporalSplitResult`, `DatasetContract`, `ExperimentConfig`, `ModelEvaluator` and `NaiveFourWeekBaseline`.
- Produces: `DataPreprocessor.build_transformer(numeric_features, categorical_features) -> ColumnTransformer`.
- Produces: `ModelExperimentRunner.run(split: TemporalSplitResult, contract: DatasetContract, config: ExperimentConfig) -> ExperimentResult`.
- Produces: validation rows for baseline, Ridge alphas `0.1`, `1.0`, `10.0` and Random Forest combinations `max_depth in (8, None)`, `min_samples_leaf in (2, 5)`, `n_estimators=300`, `random_state=42`.
- Produces: test predictions and metrics for baseline, best Ridge and best Random Forest; `selected_model_name` is chosen from validation MAE before test inspection.

- [ ] **Step 1: Write failing experiment-selection test**

Use a small deterministic fixture and assert every configured candidate appears in validation results, selection uses validation MAE and the final test table contains exactly baseline, Ridge and Random Forest.

- [ ] **Step 2: Add preprocessing isolation tests**

Assert imputer statistics are learned from training only, the final selected pipeline is refit on train plus validation and add `test_experiment_handles_unseen_category_in_test`.

- [ ] **Step 3: Add repeatability and interpretation-data tests**

Run the experiment twice and assert equal predictions. Assert transformed feature names are available for coefficient or permutation interpretation.

- [ ] **Step 4: Run tests and confirm failure**

Run: `python -m pytest tests/test_model_experiment.py tests/test_preprocessing.py -v`

Expected: FAIL with missing experiment runner.

- [ ] **Step 5: Implement the runner**

Use cloned transformers per candidate, `OneHotEncoder(handle_unknown="ignore")`, Ridge with scaled numeric values and `solver="lsqr"` for stable sparse-matrix support, Random Forest with the shared preprocessor, and nonnegative clipped predictions. Do not tune on the test set.

- [ ] **Step 6: Run experiment and legacy model tests**

Run: `python -m pytest tests/test_model_experiment.py tests/test_preprocessing.py tests/test_modeling_and_evaluation.py -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/lumina_framework/core/contracts.py src/lumina_framework/preprocessing src/lumina_framework/modeling/experiment.py tests/test_model_experiment.py tests/test_preprocessing.py
git commit -m "feat: comparar ridge y random forest temporalmente"
```

### Task 7: Business and model visualizations

**Files:**
- Create: `src/lumina_framework/visualization/business.py`
- Create: `src/lumina_framework/visualization/diagnostics.py`
- Modify: `src/lumina_framework/visualization/__init__.py`
- Create: `tests/test_business_visualizations.py`

**Interfaces:**
- Produces: `BusinessVisualizer.generate(data: pd.DataFrame, output_dir: Path) -> tuple[Path, ...]` with four exact filenames: `ventas_semanales.png`, `distribucion_categoria.png`, `mapa_sucursal_categoria.png`, `promocion_ventas.png`.
- Produces: `ModelDiagnosticsVisualizer.generate(predictions: pd.DataFrame, metrics: pd.DataFrame, importance: pd.DataFrame, output_dir: Path) -> tuple[Path, ...]` with `comparacion_modelos.png`, `real_vs_predicho.png`, `errores_segmentados.png`, `importancia_variables.png`.

- [ ] **Step 1: Write failing artifact tests**

Assert eight files exist, are nonempty PNGs, close all Matplotlib figures, contain configured title and axis text, and neither visualizer mutates its input.

- [ ] **Step 2: Run tests and confirm failure**

Run: `python -m pytest tests/test_business_visualizations.py -v`

Expected: FAIL with missing visualizers.

- [ ] **Step 3: Implement business visuals**

Aggregate before plotting to keep figures legible. Use business titles, Spanish labels, consistent palette and no word `simulado` in individual chart titles.

- [ ] **Step 4: Implement diagnostics visuals**

Use small multiples for metrics with different scales, weekly aggregation for real versus predicted, MAE by branch/category for errors and permutation importance for the selected candidate.

- [ ] **Step 5: Run visualization tests**

Run: `python -m pytest tests/test_business_visualizations.py tests/test_profiler_and_visualization.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/lumina_framework/visualization tests/test_business_visualizations.py
git commit -m "feat: generar visualizaciones analíticas del proyecto"
```

### Task 8: Inventory signals and final reports

**Files:**
- Create: `src/lumina_framework/reporting/inventory.py`
- Modify: `src/lumina_framework/reporting/generator.py`
- Modify: `src/lumina_framework/reporting/__init__.py`
- Create: `tests/test_final_reporting.py`

**Interfaces:**
- Produces: `InventorySignalGenerator.generate(predictions: pd.DataFrame, prediction_column: str) -> pd.DataFrame` for the latest test week with `venta_prevista_4_semanas`, `inventario_inicial`, `brecha_estimada` and `requiere_revision`.
- Produces: `ReportGenerator.generate_project_reports(...) -> tuple[Path, ...]` writing profiles, cleaning log, split manifest, metrics CSV/JSON, segmented metrics, predictions, inventory signals, feature importance, technical Markdown, joblib pipeline and final manifest.

- [ ] **Step 1: Write failing signal tests**

Assert only the latest week appears, `brecha_estimada=max(predicción-inventario,0)`, negative model outputs cannot create negative demand and signals are labeled as review rather than purchase orders.

- [ ] **Step 2: Write failing report-contract tests**

Assert every required artifact exists, JSON files parse, CSV schemas are stable, the joblib file reloads and predicts, the manifest records seed, cuts, package versions and relative artifact paths.

- [ ] **Step 3: Run tests and confirm failure**

Run: `python -m pytest tests/test_final_reporting.py -v`

Expected: FAIL with missing reporting interfaces.

- [ ] **Step 4: Implement signals and reports**

Build the Markdown report from computed values only. Separate facts, interpretation, recommendations and limitations; never hardcode winning-model metrics.

- [ ] **Step 5: Run reporting tests**

Run: `python -m pytest tests/test_final_reporting.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/lumina_framework/reporting tests/test_final_reporting.py
git commit -m "feat: producir señales y reportes interpretables"
```

### Task 9: End-to-end pipeline, CLI and generated evidence

**Files:**
- Modify: `src/lumina_framework/pipeline/orchestrator.py`
- Modify: `src/lumina_framework/cli.py`
- Create: `scripts/run_final_project.py`
- Create: `tests/test_final_pipeline.py`
- Modify: `tests/test_orchestrator.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Produces: `LuminaPipeline.run_project(config, contract, scenario_config, experiment_config) -> RunResult`.
- Produces: CLI `--mode assess|run`, default `assess`, preserving the existing `--config` argument.
- Produces: command `python scripts/run_final_project.py --config config/project_final.yaml` that generates the source and executes the entire project.

- [ ] **Step 1: Write failing end-to-end test**

Use a reduced 6-product, 3-branch, 24-week test config with proportional nonoverlapping cuts. Assert status `completed`, raw data and every required artifact exist, event order is correct and a second run with the same seed produces equal metrics and predictions apart from run identity/timestamps.

- [ ] **Step 2: Add failure-path tests**

Assert missing semantic roles, insufficient weeks and an output-write failure simulated with `monkeypatch` fail with a domain exception and do not leave a false completed manifest.

- [ ] **Step 3: Run tests and confirm failure**

Run: `python -m pytest tests/test_final_pipeline.py tests/test_orchestrator.py -v`

Expected: FAIL because `run_project` and CLI mode are missing.

- [ ] **Step 4: Implement orchestration and thin entry points**

Record load, validation, profile-before, cleaning, profile-after, features, split, experiment, visuals, signals and reports in `RunContext`. Keep computation in component classes, not in the CLI or script.

- [ ] **Step 5: Run focused and complete tests**

Run: `python -m pytest tests/test_final_pipeline.py tests/test_orchestrator.py -v`

Expected: PASS.

Run: `python -m pytest -v`

Expected: all legacy and final tests PASS.

- [ ] **Step 6: Execute the full project**

Run: `python scripts/run_final_project.py --config config/project_final.yaml`

Expected: `data/raw/lumina_operaciones.csv`, generation metadata and all `artifacts/project_final` outputs are regenerated successfully.

- [ ] **Step 7: Inspect generated evidence**

Open all eight PNG files at original detail, inspect CSV/JSON schemas, reload the joblib pipeline and reproduce its test predictions.

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml src/lumina_framework/pipeline src/lumina_framework/cli.py scripts/run_final_project.py tests/test_final_pipeline.py tests/test_orchestrator.py data/raw artifacts/project_final
git commit -m "feat: ejecutar proyecto final de extremo a extremo"
```

### Task 10: README, authorship evidence, Word report and submission package

**Files:**
- Modify: `README.md`
- Create: `docs/proyecto_final.md`
- Modify: `artifacts/development_log.md`
- Create or update: relevant evidence files under `docs/evidencia_final/`
- Create: `C:/Users/rayor/Downloads/Programación para la inteligencia artificial Proyecto final.docx`
- Create: `C:/Users/rayor/Downloads/lumina_proyecto_final_codigo.zip`

**Interfaces:**
- Consumes: verified outputs from Task 9 and the retained Avance 2 DOCX as the visual template.
- Produces: README and technical narrative mapped to all 12 instructions.
- Produces: final DOCX whose 12 original instructions are each immediately followed by their response.
- Produces: ZIP containing source, configuration, tests, dataset, README, figures, metrics, evidence and AI declaration; exclude `.venv`, caches, temporary renders and Git internals.

- [ ] **Step 1: Update README and technical documentation**

Replace the preliminary-state language with observed results. Include the 12-point mapping, architecture Mermaid, exact commands, artifact map, model comparison, limitations and relationship with the Word document.

- [ ] **Step 2: Complete authorship evidence**

Record decisions made in this design conversation, TDD cycles, errors encountered, parameter comparisons, changes from Avance 2, interpretation in the student's voice and a final learning reflection. Include at least eight distinct evidence types.

- [ ] **Step 3: Verify claims against artifacts**

Every row count, anomaly count, metric, selected model, image name and test count in Markdown must be read from the latest generated output or test run; no placeholder or estimated number may remain.

- [ ] **Step 4: Create the Word report from the retained template**

Use the documents skill, preserve the prior cover and table style, update the title and date to `02/10/2026`, reproduce each instruction before its response, insert only code-generated figures and selected result tables, include the GitHub URL, APA references and the full AI declaration.

- [ ] **Step 5: Render and inspect the DOCX**

Use the packaged document renderer when available, inspect every page at 100% zoom, repair clipping, table wrapping, page breaks and figure captions, then rerender. If the packaged renderer remains unavailable, preserve the DOCX and report that visual compilation could not be independently verified rather than claiming success.

- [ ] **Step 6: Build and inspect the ZIP**

List the archive contents, extract it into a temporary directory, install the package from the extracted copy and run the documented smoke command plus tests.

- [ ] **Step 7: Run final verification**

Run: `python -m pytest -v`

Run: `python scripts/run_final_project.py --config config/project_final.yaml`

Run: `git status --short`

Expected: tests pass, project execution succeeds, tracked outputs match the latest run and only intentional final files are modified.

- [ ] **Step 8: Commit documentation and evidence**

```bash
git add README.md docs artifacts/development_log.md
git commit -m "docs: presentar resultados del proyecto final"
```

- [ ] **Step 9: Push the completed Git history**

Run: `git push origin main`

Expected: the remote repository contains all committed technical evidence; the DOCX and ZIP remain available as separate submission deliverables.
