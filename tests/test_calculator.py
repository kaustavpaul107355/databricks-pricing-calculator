"""Unit tests for calculator.py."""

import datetime

import pytest

from calculator import (
    estimate_ai_parse,
    estimate_foundation_model_tokens,
    estimate_proprietary_foundation_model,
    estimate_vector_search,
    get_price_per_dbu,
)
from pricing_data import AI_PARSE_PROMO_EXPIRY, GEMINI_FM_PROMO_EXPIRY, get_proprietary_model_rates


def test_vector_search_standard_one_unit():
    r = estimate_vector_search("Standard", units=1, hours_per_month=720, cloud="AWS", region="us-east-1")
    assert r.cost_usd > 0
    assert r.dbu_total == 4.0 * 720


def test_foundation_model_ppt_tokens():
    r = estimate_foundation_model_tokens(
        "Llama 3.3 70B",
        input_millions=10,
        output_millions=2,
        cloud="AWS",
        region="us-east-1",
    )
    assert r.cost_usd > 0
    assert "input" in (r.details or "").lower()


def test_proprietary_model_in_geo_tier():
    r = estimate_proprietary_foundation_model(
        "GPT 5 mini",
        input_millions=1,
        output_millions=0.5,
        tier="in_geo",
        cloud="AWS",
        region="us-east-1",
    )
    r_global = estimate_proprietary_foundation_model(
        "GPT 5 mini",
        input_millions=1,
        output_millions=0.5,
        tier="global",
        cloud="AWS",
        region="us-east-1",
    )
    assert r.cost_usd >= r_global.cost_usd


def test_ai_parse_promo_discount_when_active():
    """When promo window is active, apply_promo=True must not exceed apply_promo=False."""
    without = estimate_ai_parse(10, "Low (simple text, e.g. receipts, W2s)", apply_promo=False)
    with_promo = estimate_ai_parse(10, "Low (simple text, e.g. receipts, W2s)", apply_promo=True)
    expiry = datetime.date.fromisoformat(AI_PARSE_PROMO_EXPIRY)
    if datetime.date.today() <= expiry:
        assert with_promo.cost_usd == pytest.approx(without.cost_usd * 0.5, rel=0.01)
        assert "promo" in (with_promo.description or "").lower()
    else:
        assert with_promo.cost_usd == without.cost_usd


def test_azure_region_price():
    aws = get_price_per_dbu("AWS", "us-east-1")
    azure = get_price_per_dbu("Azure", "eastus")
    assert aws > 0 and azure > 0


def test_gemini_31_flash_lite_rates_match_2026_05_page():
    rates = get_proprietary_model_rates("Gemini 3.1 Flash Lite", "global")
    assert rates["input"] == 4.464
    assert rates["output"] == 26.786


def test_gemini_promo_discount_when_active():
    without = estimate_proprietary_foundation_model(
        "Gemini 2.5 Flash", input_millions=1, apply_gemini_promo=False
    )
    with_promo = estimate_proprietary_foundation_model(
        "Gemini 2.5 Flash", input_millions=1, apply_gemini_promo=True
    )
    expiry = datetime.date.fromisoformat(GEMINI_FM_PROMO_EXPIRY)
    if datetime.date.today() <= expiry:
        assert with_promo.cost_usd <= without.cost_usd
        assert with_promo.cost_usd == pytest.approx(without.cost_usd * 0.8, abs=0.02)
        assert "promo" in (with_promo.description or "").lower()
    else:
        assert with_promo.cost_usd == without.cost_usd
