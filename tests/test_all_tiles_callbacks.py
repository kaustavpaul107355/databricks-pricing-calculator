"""
Verify every calculator surface (GenAI tiles + other tabs) with Dash-like string inputs.

Dash often passes type=number values as strings; regressions show up as store=0 with no error.
"""

from __future__ import annotations

from app import (
    _open_models,
    _train_models,
    calc_ab,
    calc_breakeven,
    calc_classify,
    calc_comparison,
    calc_eval,
    calc_extract,
    calc_fm,
    calc_gw,
    calc_parse,
    calc_prop,
    calc_quick,
    calc_reranker,
    calc_scenario,
    calc_serv,
    calc_train,
    calc_vs,
    genai_total,
    update_prop_tiers,
    update_qe_sizes,
    update_train_scales,
)
from pricing_data import (
    AI_CLASSIFY_WORKLOAD_LABELS,
    AI_EXTRACT_WORKLOAD_LABELS,
    AI_PARSE_DBU_PER_1K_PAGES,
    AI_PARSE_DOCUMENT_TYPE_LABELS,
    MODEL_TRAINING_DBU_ESTIMATES,
    PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION,
    get_all_models_with_pt,
)
from ui_helpers import GENAI_STORE_KEYS
from scenarios import embedding_model_names, inference_model_names
from ui_helpers import coerce_store_amount

CLOUD, REGION = "AWS", "us-east-1"

_N_RAG, _N_MA, _N_BATCH, _N_FT = 8, 6, 9, 6


def _scenario_call(
    scn: str,
    rag: tuple = (),
    ma: tuple = (),
    batch: tuple = (),
    ft: tuple = (),
    cloud: str = CLOUD,
    region: str = REGION,
):
    """Build calc_scenario args: pad each section to match callback arity."""
    rag_a = (list(rag) + [None] * _N_RAG)[:_N_RAG]
    ma_a = (list(ma) + [None] * _N_MA)[:_N_MA]
    batch_a = (list(batch) + [None] * _N_BATCH)[:_N_BATCH]
    ft_a = (list(ft) + [None] * _N_FT)[:_N_FT]
    return calc_scenario(scn, *rag_a, *ma_a, *batch_a, *ft_a, cloud, region)


def _assert_positive_store(store, label: str):
    amt = coerce_store_amount(store)
    assert amt > 0, f"{label}: expected positive store, got {store!r} ({amt})"


def _assert_cost_result(children, store, label: str):
    _assert_positive_store(store, label)
    assert children is not None, f"{label}: missing result UI"


# --- GenAI Calculator tab (12 monthly tiles + training + total) ---


class TestGenAITilesWithStringInputs:
    def test_vector_search(self):
        children, store = calc_vs("Standard", "2", "720", CLOUD, REGION)
        _assert_cost_result(children, store, "Vector Search")

    def test_reranker(self):
        children, store = calc_reranker("50", CLOUD, REGION)
        _assert_cost_result(children, store, "Reranker")

    def test_agent_bricks_cpu(self):
        children, store, *_ = calc_ab(
            "Knowledge Assistant", "CPU (typical)", "720", "Small", "100", CLOUD, REGION
        )
        _assert_cost_result(children, store, "Agent Bricks CPU")

    def test_agent_bricks_gpu(self):
        children, store, *_ = calc_ab(
            "Supervisor Agent", "GPU", "0", "Medium", "200", CLOUD, REGION
        )
        _assert_cost_result(children, store, "Agent Bricks GPU")

    def test_gateway_inference_tables(self):
        children, store = calc_gw(["inf"], "10", CLOUD, REGION)
        _assert_cost_result(children, store, "Mosaic AI Gateway")

    def test_model_serving_cpu(self):
        children, store, *_ = calc_serv("CPU", "720", "Small", "100", CLOUD, REGION)
        _assert_cost_result(children, store, "Model Serving CPU")

    def test_model_serving_gpu(self):
        children, store, *_ = calc_serv("GPU", "0", "Small", "150", CLOUD, REGION)
        _assert_cost_result(children, store, "Model Serving GPU")

    def test_foundation_model_open(self):
        model = _open_models[0]
        children, store = calc_fm(model, "10", "2", "0", CLOUD, REGION)
        _assert_cost_result(children, store, "Foundation Model")

    def test_proprietary_model(self):
        model = next(iter(PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION))
        _, tier = update_prop_tiers(model)
        children, store = calc_prop(model, tier, "5", "1", "0", "0", "0", [], CLOUD, REGION)
        _assert_cost_result(children, store, "Proprietary Model")

    def test_ai_parse(self):
        _, key = AI_PARSE_DOCUMENT_TYPE_LABELS[0]
        children, store = calc_parse(key, "100", [], CLOUD, REGION)
        _assert_cost_result(children, store, "AI Parse")

    def test_ai_extract(self):
        _, key = AI_EXTRACT_WORKLOAD_LABELS[0]
        children, store = calc_extract(key, "50", [], CLOUD, REGION)
        _assert_cost_result(children, store, "AI Extract")

    def test_ai_classify(self):
        _, key = AI_CLASSIFY_WORKLOAD_LABELS[0]
        children, store = calc_classify(key, "25", [], CLOUD, REGION)
        _assert_cost_result(children, store, "AI Classify")

    def test_agent_evaluation_llm_judge(self):
        children, store = calc_eval("LLM Judge", "1", "0.5", "0", CLOUD, REGION)
        _assert_cost_result(children, store, "Agent Evaluation")

    def test_model_training(self):
        model = _train_models[0]
        _, scale = update_train_scales(model)
        children, store = calc_train(model, scale, CLOUD, REGION)
        _assert_positive_store(store, "Model Training")
        assert children is not None

    def test_genai_total_with_string_stores(self):
        stores = ["100.5", "0", "50", "0", "200"] + ["0"] * (len(GENAI_STORE_KEYS) - 5) + ["25"]
        assert len(stores) == len(GENAI_STORE_KEYS) + 1
        monthly, train, lines = genai_total(*stores)
        assert monthly is not None
        assert "$" in str(monthly)
        assert lines is not None


# --- PT vs PPT Break-Even tab ---


class TestBreakEvenTab:
    def test_breakeven_with_string_inputs(self):
        model = get_all_models_with_pt()[0]
        metrics, chart = calc_breakeven(model, "2000", "500", "5", "12", CLOUD, REGION)
        assert metrics is not None
        assert chart is not None


# --- Model Comparison tab ---


class TestModelComparisonTab:
    def test_comparison_with_string_token_volumes(self):
        models = inference_model_names()[:2]
        result = calc_comparison(models, "10", "2", CLOUD, REGION)
        assert result is not None
        assert "cheaper" in str(result).lower() or "$" in str(result)


# --- Scenario Templates tab ---


class TestScenarioTemplatesTab:
    def test_rag_scenario_strings(self):
        emb = embedding_model_names()[0]
        llm = inference_model_names()[0]
        cx = list(AI_PARSE_DBU_PER_1K_PAGES.keys())[2]
        result = _scenario_call(
            "RAG Application",
            rag=("10000", "5", "20", "500", emb, llm, cx, "1"),
        )
        assert result is not None
        assert "$" in str(result)

    def test_multi_agent_scenario_strings(self):
        models = inference_model_names()
        result = _scenario_call(
            "Multi-Agent System",
            ma=("500", "5", "2", models[0], models[1], ["yes"]),
        )
        assert result is not None
        assert "$" in str(result)

    def test_batch_scenario_strings(self):
        models = inference_model_names()
        _, ext_key = AI_EXTRACT_WORKLOAD_LABELS[0]
        _, cls_key = AI_CLASSIFY_WORKLOAD_LABELS[0]
        cx = list(AI_PARSE_DBU_PER_1K_PAGES.keys())[2]
        result = _scenario_call(
            "Batch AI Pipeline",
            batch=(
                "10000", "5", cx, "4", models[0],
                ["yes"], ext_key, ["yes"], cls_key,
            ),
        )
        assert result is not None
        assert "$" in str(result)

    def test_fine_tune_scenario_strings(self):
        model = _train_models[0]
        scale = list(MODEL_TRAINING_DBU_ESTIMATES[model].keys())[0]
        result = _scenario_call(
            "Fine-Tuned Model",
            ft=(model, scale, "12", "3", "2", "100"),
        )
        assert result is not None
        assert "$" in str(result)


# --- Quick Estimate tab ---


class TestQuickEstimateTab:
    def test_all_preset_types(self):
        for qe_type in ("RAG", "Multi-Agent", "Batch AI", "Fine-Tune"):
            opts, size = update_qe_sizes(qe_type)
            assert opts, f"No presets for {qe_type}"
            result = calc_quick(qe_type, size, CLOUD, REGION)
            assert result is not None, f"{qe_type}/{size} returned None"
            assert "$" in str(result), f"{qe_type}/{size} missing cost"
