# Status & Coverage — GenAI TCO Estimator (Dash)

**Last updated:** 2026-05-30

## Where we are

- **UI:** Dash app (`app.py`) with five tabs: GenAI Calculator (tile grid), PT vs PPT Break-Even, Model Comparison, Scenario Templates, Quick Estimate.
- **Deploy:** `python app.py` on port `8000` (or `PORT` env); Databricks Apps via `app.yaml`.
- **Logic:** `calculator.py` (atomic estimates), `scenarios.py` (composites), `pricing_data.py` (rates), `ui_helpers.py` (dropdown coercion).
- **CLI:** Broader surface (SQL, storage, compute, etc.) — not all exposed in the Dash UI.
- **Tests:** `pytest tests/` (52 tests as of 2026-05-30).
- **Legacy:** `index.html` deprecated; do not use for current model catalog.

---

## GenAI Calculator tab (per-service)

| Service | UI tile | Calculator function | Confidence |
|---------|---------|---------------------|------------|
| Vector Search | Yes | `estimate_vector_search` | High |
| Vector Search Reranker | Yes | `estimate_vector_search_reranker` | High |
| Agent Bricks | Yes | `estimate_model_serving_cpu` / `_gpu` | High (same as Model Serving) |
| Mosaic AI Gateway | Yes | `estimate_gateway_payload` | High (payload GB); guardrails = info only |
| Model Serving | Yes | CPU / GPU serving | High |
| Foundation Model (open) | Yes | `estimate_foundation_model_tokens` | High |
| Proprietary FM | Yes | `estimate_proprietary_foundation_model` | High (tiers, cache, batch) |
| AI Parse | Yes | `estimate_ai_parse` (+ 50% promo to 2026-06-30) | High |
| AI Extract | Yes | `estimate_ai_extract` (+ shared 50% promo) | High |
| AI Classify | Yes | `estimate_ai_classify` (+ shared 50% promo) | High |
| Model retirement hints | Yes | `MODEL_RETIREMENT_NOTICES` + UI alerts | Medium (doc-driven dates) |
| Agent Evaluation | Yes | `estimate_agent_evaluation` | High |
| Model Training | Yes | `estimate_model_training` (one-time) | High |

**Ballpark total:** Sums monthly `dcc.Store` line items + one-time training.

---

## Other tabs

| Tab | Functions | Confidence |
|-----|-----------|------------|
| PT vs PPT Break-Even | `calculate_pt_vs_ppt_breakeven` | High (open models with PT rates only) |
| Model Comparison | `compare_models` | High |
| Scenario Templates | RAG, multi-agent, batch (+ optional Extract/Classify), fine-tune | Medium (heuristic architecture assumptions) |
| Quick Estimate | Same scenarios via `presets.py` | Medium |

---

## In `pricing_data.py` but not in Dash UI

These remain available via **CLI** and data reference:

- SQL Serverless, generic Compute (DBU-hours), Storage (DSU), Shutterstock ImageAI
- Full SKU catalog (`list skus`)
- Lakeflow / Lakebase workload $/DBU examples

---

## Not replicated (by design)

| Area | Reason |
|------|--------|
| [Instance-type calculator](https://www.databricks.com/product/pricing/product-pricing/instance-types) | External tool; link in sidebar |
| [Official GenAI calculator](https://www.databricks.com/product/pricing/genai-pricing-calculator) | External tool; link in sidebar |
| Data Transfer & Connectivity | No public per-GB formula |
| Platform add-ons, Managed Services | Plan-specific |
| Contract / negotiated $/DBU | Use `system.billing.list_prices` |

---

## Confidence summary

| Area | Level | Notes |
|------|-------|-------|
| Formulas (DBU × $/DBU) | High | Matches public documentation model |
| Published DBU rates | Medium–High | See `PRICING_SOURCES.md`; last major refresh 2026-05-04 |
| Region $/DBU | Medium | Illustrative list prices |
| Scenario TCO | Medium | Heuristic token/chunk/payload assumptions documented in `docs/DESIGN.md` |

---

## Related docs

- [CALCULATION_COVERAGE.md](./CALCULATION_COVERAGE.md) — checklist when adding pricing pages
- [PRICING_SOURCES.md](./PRICING_SOURCES.md) — source verification log
- [docs/REQUIREMENTS.md](./docs/REQUIREMENTS.md) — product requirements
- [docs/DEV_LOG.md](./docs/DEV_LOG.md) — build log
