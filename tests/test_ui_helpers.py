"""Unit tests for ui_helpers.py (dropdown / coercion logic)."""

from ui_helpers import (
    ai_classify_workload_options,
    ai_extract_workload_options,
    coerce_input,
    coerce_store_amount,
    checklist_enabled,
    parse_complexity_options,
    resolve_proprietary_tier,
    resolve_training_scale,
)
from pricing_data import (
    AI_CLASSIFY_DBU_PER_1K_DOCUMENTS,
    AI_EXTRACT_DBU_PER_1K_INPUTS,
    AI_PARSE_DBU_PER_1K_PAGES,
    MODEL_TRAINING_DBU_ESTIMATES,
)


def test_parse_options_use_pricing_keys():
    opts = parse_complexity_options()
    values = [o["value"] for o in opts if o["value"] != "__none__"]
    assert values
    assert all(v in AI_PARSE_DBU_PER_1K_PAGES for v in values)


def test_resolve_proprietary_tier_stale_tier():
    # GPT 5 mini has global + in_geo; stale long_context should reset to global
    assert resolve_proprietary_tier("GPT 5 mini", "long_context") == "global"
    assert resolve_proprietary_tier("GPT 5 mini", "in_geo") == "in_geo"


def test_resolve_training_scale():
    model = next(iter(MODEL_TRAINING_DBU_ESTIMATES))
    scales = list(MODEL_TRAINING_DBU_ESTIMATES[model].keys())
    assert resolve_training_scale(model, "invalid-scale") == scales[0]
    assert resolve_training_scale(model, scales[0]) == scales[0]


def test_coerce_input_string_from_dash():
    assert coerce_input("720") == 720.0
    assert coerce_input("") == 0.0
    assert coerce_input(None) == 0.0


def test_coerce_store_amount():
    assert coerce_store_amount(None) == 0.0
    assert coerce_store_amount("12.5") == 12.5
    assert coerce_store_amount(-3) == 0.0


def test_checklist_enabled():
    assert checklist_enabled(["yes"]) is True
    assert checklist_enabled([]) is False
    assert checklist_enabled(None) is False


def test_extract_workload_options_keys():
    values = [o["value"] for o in ai_extract_workload_options() if o["value"] != "__none__"]
    assert all(v in AI_EXTRACT_DBU_PER_1K_INPUTS for v in values)


def test_classify_workload_options_keys():
    values = [o["value"] for o in ai_classify_workload_options() if o["value"] != "__none__"]
    assert all(v in AI_CLASSIFY_DBU_PER_1K_DOCUMENTS for v in values)
