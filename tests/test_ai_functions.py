"""Tests for AI Parse, Extract, and Classify estimates."""

import datetime

import pytest

from calculator import estimate_ai_extract, estimate_ai_classify
from pricing_data import AI_FUNCTIONS_PROMO_EXPIRY


def test_ai_extract_invoice_workload():
    r = estimate_ai_extract(10, "Invoices (~1 page)", apply_promo=False)
    assert r.dbu_total == 450.0
    assert r.cost_usd > 0


def test_ai_classify_short_text():
    r = estimate_ai_classify(5, "Short text (e.g. news brief)", apply_promo=False)
    assert r.dbu_total == 22.5
    assert r.cost_usd > 0


def test_ai_extract_promo_when_active():
    without = estimate_ai_extract(1, "Invoices (~1 page)", apply_promo=False)
    with_promo = estimate_ai_extract(1, "Invoices (~1 page)", apply_promo=True)
    expiry = datetime.date.fromisoformat(AI_FUNCTIONS_PROMO_EXPIRY)
    if datetime.date.today() <= expiry:
        assert with_promo.cost_usd <= without.cost_usd
        assert "promo" in (with_promo.description or "").lower()
    else:
        assert with_promo.cost_usd == without.cost_usd
