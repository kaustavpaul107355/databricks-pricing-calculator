"""Unit tests for scenarios.py."""

import pytest

from scenarios import (
    calculate_pt_vs_ppt_breakeven,
    compare_models,
    estimate_batch_pipeline_scenario,
    estimate_multi_agent_scenario,
    estimate_rag_scenario,
)
from pricing_data import AI_PARSE_DBU_PER_1K_PAGES


def test_rag_scenario_positive_total():
    cx = "Medium (text + tables + images, e.g. 10-Ks)"
    assert cx in AI_PARSE_DBU_PER_1K_PAGES
    r = estimate_rag_scenario(
        num_docs=1000,
        avg_pages_per_doc=5,
        avg_chunks_per_doc=20,
        queries_per_day=100,
        embedding_model="GTE",
        llm_model="Llama 3.1 8B",
        parse_complexity=cx,
        cloud="AWS",
        region="us-east-1",
    )
    assert r.total_monthly_usd > 0
    assert len(r.line_items) >= 3


def test_multi_agent_vector_search_toggle():
    with_vs = estimate_multi_agent_scenario(
        requests_per_day=500,
        avg_steps_per_request=3,
        tools_per_step=2,
        orchestrator_model="Llama 3.1 8B",
        worker_model="Llama 3.1 8B",
        include_vector_search=True,
    )
    without_vs = estimate_multi_agent_scenario(
        requests_per_day=500,
        avg_steps_per_request=3,
        tools_per_step=2,
        orchestrator_model="Llama 3.1 8B",
        worker_model="Llama 3.1 8B",
        include_vector_search=False,
    )
    assert with_vs.total_monthly_usd > without_vs.total_monthly_usd


def test_breakeven_llama_33_70b():
    r = calculate_pt_vs_ppt_breakeven(
        "Llama 3.3 70B", 2000, 500, queries_per_min=5.0, uptime_hours_per_day=12,
        cloud="AWS", region="us-east-1",
    )
    assert r.ppt_monthly > 0
    assert r.pt_monthly > 0
    assert r.break_even_qpm > 0
    assert len(r.data_points) == 51


def test_compare_models_requires_known_models():
    r = compare_models(
        ["Llama 3.3 70B", "GPT 5 mini"],
        input_millions=10,
        output_millions=2,
    )
    assert len(r.models) == 2
    assert all(c > 0 for c in r.costs)


def test_compare_unknown_model_raises():
    with pytest.raises(ValueError):
        compare_models(["Not A Real Model"], input_millions=1, output_millions=1)


def test_batch_pipeline_parse_only():
    r = estimate_batch_pipeline_scenario(
        num_docs=1000,
        pages_per_doc=5,
        parse_complexity="Low (simple text, e.g. receipts, W2s)",
        frequency_per_month=2,
        output_model="Llama 3.1 8B",
    )
    services = [li.service for li in r.line_items]
    assert any("AI Parse" in s for s in services)
    assert not any("AI Extract" in s for s in services)


def test_batch_pipeline_with_extract_increases_cost():
    base = estimate_batch_pipeline_scenario(
        num_docs=1000,
        pages_per_doc=5,
        parse_complexity="Low (simple text, e.g. receipts, W2s)",
        frequency_per_month=2,
        output_model="Llama 3.1 8B",
    )
    with_extract = estimate_batch_pipeline_scenario(
        num_docs=1000,
        pages_per_doc=5,
        parse_complexity="Low (simple text, e.g. receipts, W2s)",
        frequency_per_month=2,
        output_model="Llama 3.1 8B",
        include_extract=True,
        extract_workload="Invoices (~1 page)",
    )
    assert with_extract.total_monthly_usd > base.total_monthly_usd
    assert any("AI Extract" in li.service for li in with_extract.line_items)
