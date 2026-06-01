# Pricing fitment check

This document is the **operational fitment guide** for the GenAI TCO Estimator (`pricing_data.py` + `calculator.py`). It records what was verified against official sources, known gaps, and how to refresh data before pricing drifts again.

**Last fitment pass:** 2026-05-30  
**Previous full audit:** 2026-05-04 (see [PRICING_SOURCES.md](../PRICING_SOURCES.md))

---

## Scope

| In scope | Out of scope (document only) |
|----------|------------------------------|
| GenAI tiles in Dash app (FM, proprietary FM, GPU, Vector Search, AI Parse, Agent Eval, Training, Gateway, ImageAI) | Classic cluster / job DBU pricing (compute tab placeholders) |
| DBU **consumption** rates (DBU/hr, DBU/1M tokens, multipliers) | Committed-use discounts, enterprise agreements |
| Model catalog vs supported-models doc | Lakeflow Connect $/DBU (JS-only page) |
| Promotional windows (AI Parse 50%, Gemini 20%) | Authoritative per-customer $/DBU (use `system.billing.list_prices`) |

---

## Canonical source URLs

Use these in order on every refresh. **Authoritative for DBU tables:** Azure Learn when dated recently; **authoritative for proprietary/cache/batch and newest models:** databricks.com proprietary page.

### Tier 1 — refresh every fitment pass

| # | Source | URL | What to verify |
|---|--------|-----|----------------|
| 1 | Azure Databricks serverless pricing | https://learn.microsoft.com/en-us/azure/databricks/resources/pricing | GPU serving, Vector Search, AI Parse tiers, open FM table, Anthropic table, Agent Eval, AI Gateway, SQL warehouse, Lakebase, training estimates |
| 2 | Foundation Model Serving | https://www.databricks.com/product/pricing/foundation-model-serving | Open FM PPT + PT entry/scaling DBU/hr |
| 3 | Proprietary Foundation Model Serving | https://www.databricks.com/product/pricing/proprietary-foundation-model-serving | OpenAI / Anthropic / Google tiers, cache, batch |
| 4 | AI Parse | https://www.databricks.com/product/pricing/ai-parse | Complexity tiers, 50% promo end date |
| 5 | Supported models | https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/supported-models | New endpoints, retirements, preview status |

### Tier 2 — confirm on major releases or when a tile breaks

| # | Source | URL | Calculator tile |
|---|--------|-----|-----------------|
| 6 | Model Serving (GPU) | https://www.databricks.com/product/pricing/model-serving | GPU |
| 7 | Vector Search | https://www.databricks.com/product/pricing/vector-search | Vector Search |
| 8 | Model Training | https://www.databricks.com/product/pricing/mosaic-foundation-model-training | Training |
| 9 | Agent Evaluation | https://www.databricks.com/product/pricing/agent-evaluation | Agent Eval (often JS-only; use #1) |
| 10 | Mosaic AI Gateway | https://www.databricks.com/product/pricing/mosaic-ai-gateway | Gateway (often JS-only; use #1) |
| 11 | Shutterstock ImageAI | https://www.databricks.com/product/pricing/mosaic-imageai-serving | ImageAI |
| 12 | Official GenAI calculator | https://www.databricks.com/product/pricing/genai-pricing-calculator | Cross-check scenarios manually |

### Tier 3 — regions, SKUs, billing

| # | Source | URL |
|---|--------|-----|
| 13 | Feature region support | https://docs.databricks.com/en/resources/feature-region-support.html |
| 14 | AWS regions | https://docs.databricks.com/aws/en/resources/supported-regions |
| 15 | Azure regions | https://learn.microsoft.com/en-us/azure/databricks/resources/supported-regions |
| 16 | GCP regions | https://docs.databricks.com/gcp/en/resources/supported-regions.html |
| 17 | Billing system tables | https://docs.databricks.com/en/admin/system-tables/billing.html |
| 18 | List prices table | https://docs.databricks.com/en/admin/system-tables/pricing.html |

Full page index (including non-GenAI categories) lives in `pricing_data.PRICING_PAGES` and [PRICING_SOURCES.md](../PRICING_SOURCES.md).

---

## Fitment matrix (2026-05-30)

| Calculator feature | Data module | Primary source(s) | Fitment status |
|--------------------|-------------|-------------------|----------------|
| Open FM (PPT / PT) | `FOUNDATION_MODEL_DBU_PER_MILLION` | #1, #2 | **Match** — Llama 4 Maverick, Qwen 3 Next 80B, Qwen 0.6B embedding, GPT OSS, Gemma 3 12B align with pricing page table |
| Proprietary FM | `PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION` | #3, #1 | **Updated 2026-05-30** — Gemini family corrected; added Opus 4.8, Gemini 3.5 Flash, 2.5 Flash Lite |
| Gemini 20% promo | `GEMINI_FM_PROMO_*` + `apply_gemini_promo` | #3 | **Modeled** — list rates in data; optional 20% through 2026-06-30 in UI |
| AI Parse | `AI_PARSE_DBU_PER_1K_PAGES` | #4, #1 | **Match** — midpoints 12.5 / 22.5 / 62.5 / 87.5; 50% promo through 2026-06-30 |
| AI Extract | `AI_EXTRACT_DBU_PER_1K_INPUTS` | #4 | **Match** — invoice 45, financial 67.5 DBU/1k inputs (midpoints) |
| AI Classify | `AI_CLASSIFY_DBU_PER_1K_DOCUMENTS` | #4 | **Match** — short text 4.5, rental 50 DBU/1k docs (midpoints) |
| Vector Search | `VECTOR_SEARCH_DBU_PER_HOUR` | #7, #1 | **Match** — Standard 4.0, Storage Optimized 18.29 DBU/hr |
| GPU serving | `MODEL_SERVING_GPU_DBU_PER_HOUR` | #6, #1 | **Match** — XLarge/2XL/4XL via Azure Learn; Medium/Large variants via model-serving page |
| Agent Evaluation | `AGENT_EVALUATION_DBU` | #1 | **Match** — LLM judge + synthetic data (page JS-only) |
| AI Gateway | `GATEWAY_*` | #1 | **Match** |
| Model Training | `MODEL_TRAINING_DBU_ESTIMATES` | #8, #1 | **Match** |
| ImageAI | `SHUTTERSTOCK_DBU_PER_IMAGE` | #1 | **Match** |
| $/DBU by region | `get_price_per_dbu*` | databricks.com (JS) | **Unverified** — use workspace `system.billing.list_prices` for customer truth |

---

## 2026-05-30 findings (applied vs backlog)

### Applied in `pricing_data.py`

| Model / area | Was (stale) | Now (per proprietary page) |
|--------------|-------------|----------------------------|
| Gemini 3.1 Flash Lite (global in/out) | 3.571 / 21.429 | 4.464 / 26.786 (+ in_geo tier) |
| Gemini 2.5 Pro (short in/out) | 17.857 / 142.857 | 22.321 / 178.571 (+ cache fields) |
| Gemini 2.5 Pro (long in/out) | 35.714 / 214.286 | 44.643 / 267.857 |
| Gemini 2.5 Flash | 4.286 / 35.714 | 5.357 / 44.643 (+ cache) |
| Gemini 3.1 Pro batch | 230.357 | 230.429 |
| **New** Gemini 3.5 Flash | — | Full global + in_geo table |
| **New** Gemini 2.5 Flash Lite | — | 1.786 / 7.143 |
| **New** Claude Opus 4.8 | — | Same list as Opus 4.5–4.7; batch `None` (coming soon on page) |
| **New** AI Extract workloads | — | Invoices 45 / Financial 67.5 DBU per 1k inputs |
| **New** AI Classify workloads | — | Short text 4.5 / Rental 50 DBU per 1k documents |
| **Retirement UI** | — | Codex + Llama 3.1 405B notices in dropdowns and alerts |

### Ongoing maintenance

| Item | Source note | Suggested action |
|------|-------------|------------------|
| **GPT 5.x Codex** retirement | **2026-07-16** per supported-models | UI hints in place; drop catalog rows when pricing page removes them |
| **Llama 3.1 405B** | PT retired **2026-05-15** | Kept as `(deprecated)` for historical estimates |
| **Committed use / list $/DBU** | Not in Learn doc | Use `system.billing.list_prices` for customer-specific dollars |

---

## Refresh procedure

Run this checklist quarterly or when Databricks announces pricing/model changes.

1. **Record pass date** in this file and add a row to [PRICING_SOURCES.md](../PRICING_SOURCES.md) audit history.
2. **Fetch Tier 1 URLs** (browser or `WebFetch`). Note each page’s “Last updated” / footer date.
3. **Diff proprietary Gemini + Anthropic tables** against `PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION` (highest churn).
4. **Diff open FM table** on foundation-model-serving vs `FOUNDATION_MODEL_DBU_PER_MILLION`.
5. **Scan supported-models** (#5) for new headings and “Retired on …” banners; update model dropdowns and deprecation notes.
6. **Promotions:** Confirm AI Parse 50% and Gemini 20% end dates on #3 and #4; update `AI_PARSE_PROMO_EXPIRY` / `GEMINI_FM_PROMO_EXPIRY` if extended.
7. **Run local fitment script:**
   ```bash
   cd Databricks/databricks-pricing-calculator
   python scripts/pricing_fitment_check.py
   ```
8. **Run tests:** `pytest tests/ -q`
9. **Update** [CALCULATION_COVERAGE.md](../CALCULATION_COVERAGE.md) if tiles or formulas change.
10. **Workspace spot-check (optional):** Query `system.billing.list_prices` for `sku_name LIKE '%Model Serving%'` or GenAI SKUs to validate $/DBU, not DBU multipliers.

---

## How list price vs promo works in this app

| Product | Stored rates | Promo handling |
|---------|--------------|----------------|
| AI Parse | Midpoint of each complexity band | `apply_promo` → 50% off USD through `AI_PARSE_PROMO_EXPIRY` |
| Gemini proprietary | List DBU rates from pricing page | `apply_gemini_promo` → 20% off USD through `GEMINI_FM_PROMO_EXPIRY` |
| Other proprietary | List rates | No automatic promo |

Promo applies to **USD cost** only; DBU totals in results stay at list consumption (matches how customers reconcile usage vs discounted invoices).

---

## Related docs

- [PRICING_SOURCES.md](../PRICING_SOURCES.md) — per-source verification notes and audit log  
- [CALCULATION_COVERAGE.md](../CALCULATION_COVERAGE.md) — tile ↔ formula mapping  
- [DESIGN.md](./DESIGN.md) — architecture and extension points  
