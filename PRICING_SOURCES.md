# Pricing Data Sources & Verification Status

This document tracks every source used to populate `pricing_data.py`, the verification status of each data point, and when the data was last refreshed.

**Last comprehensive refresh:** 2026-05-04
**Previous refresh:** 2026-04-07

---

## Primary Official Sources

### 1. Azure Databricks Pricing — Serverless DBU Consumption by SKU
- **URL:** https://learn.microsoft.com/en-us/azure/databricks/resources/pricing
- **Last published:** 2026-04-21 (per page metadata)
- **What it provides:** DBU multipliers for all serverless SKUs, GPU instance DBU/hr rates, Vector Search DBU rates, Lakebase multipliers, Agent Evaluation rates, AI Gateway rates, Storage DSU multipliers, AI Parse complexity tiers, Model Training estimates, Anthropic model rates
- **Verification status:** CONFIRMED — most authoritative public source for DBU consumption data
- **Data points confirmed from this source:**
  - GPU Serving: Small 10.48, XLarge 78.6, 2XLarge 157.2, 4XLarge 314.4 DBU/hr
  - Vector Search: Standard 4.0, Storage Optimized 18.29 DBU/hr
  - Vector Search Reranker: 28.571 DBU/1K requests
  - Lakebase Autoscaling Compute: 0.213X multiplier
  - Lakebase Storage: 15X, PITR 8.7X, Snapshots 3.91X DSU
  - AI Gateway Inference Tables: 7.143 DBU/GB
  - AI Gateway Usage Tracking: 1.429 DBU/GB
  - Agent Evaluation LLM Judge: 2.14/8.57 DBU/1M tokens (input/output)
  - Agent Evaluation Synthetic Data: 5.0 DBU/question
  - SQL Warehouse sizes: 2X-Small (4) through 4X-Large (528) DBU/hr
  - Shutterstock ImageAI: 0.857 DBU/image
  - Model Forecasting: 4.0X multiplier
  - All serverless DBU multipliers (Automated, Interactive, Database)
  - AI Parse: 10-15 / 20-25 / 60-65 / 85-90 DBU/1k pages with 50% promo until 2026-06-30
  - Open FM Llama family + GPT OSS + Gemma 3 12B + GTE/BGE Large rates
  - Anthropic full rate table (Opus 4.5, Opus 4/4.1, Sonnet 4.5, Sonnet 4/4.1, Haiku 4.5)

### 2. Databricks Foundation Model Serving Pricing
- **URL:** https://www.databricks.com/product/pricing/foundation-model-serving
- **What it provides:** Per-model DBU rates for open foundation models (pay-per-token and provisioned throughput, both entry and scaling capacity)
- **Note:** Page is JS-rendered; data extracted via WebFetch + Azure Learn cross-reference
- **Data points sourced (2026-05-04 refresh):**
  - All FOUNDATION_MODEL_DBU_PER_MILLION entries: Llama 4 Maverick, 3.3 70B, 3.2 3B/1B, 3.1 8B; GPT OSS 120B/20B; Gemma 3 12B; GTE; BGE Large
  - **Added:** Qwen 3 Next 80B A3B (PPT 2.143/17.143, PT entry 78.571 = scaling); Qwen 3 0.6B Embedding (PPT 0.286, PT 25.0 = scaling)
  - **Fixed:** scaling_capacity_per_hour now populated for all open models that have it (= entry capacity for Maverick/GPT OSS/Gemma/Qwen/GTE/BGE; > entry for Llama 3.3 70B and 3.1 8B)
  - **Removed from page:** Llama 3.1 405B PPT (kept as deprecated entry; PT retiring 2026-05-15)

### 3. Databricks Proprietary Foundation Model Serving Pricing
- **URL:** https://www.databricks.com/product/pricing/proprietary-foundation-model-serving
- **What it provides:** Per-model DBU rates for OpenAI, Anthropic, Google models; Global/In-geo/Long Context tiers; cache write/read rates; batch inference rates
- **Note:** Page is JS-rendered; data extracted via WebFetch on 2026-05-04
- **Data points sourced (2026-05-04 refresh):**
  - **Added:** GPT 5.5, GPT 5.4/5.5 Pro (4 tiers), GPT 5.4 mini, GPT 5.4 nano
  - **Added:** in_geo tier for GPT 5 mini, GPT 5 nano, GPT 5.1 Codex Max, GPT 5.1 Codex Mini
  - **Added:** long_context tier for GPT 5.4 (Global + In-geo), Gemini 3.1 Flash Lite
  - **Fixed:** Gemini 3.1 Flash Lite rates (3.571/21.429/3.571/0.357/71.429 — was estimated 4.286/35.714)
  - **Fixed:** Claude Haiku 4.5 batch (Global 114.286, In-geo 125.714 — was None; Azure Learn shows n/a but pricing page authoritative for this rate)
  - **Renamed:** "Claude Opus 4.5" + "Claude Opus 4.6" → consolidated into "Claude Opus 4.5/4.6/4.7" (matches page grouping; supported-models lists endpoints separately but pricing is shared)
  - **Renamed:** "Claude Sonnet 3.7/4/4.1" → "Claude Sonnet 4/4.1" (Sonnet 3.7 retired 2026-04-12)
  - **Removed:** fabricated long_context + in_geo_long_context tiers from Claude Sonnet 4.5/4.6 (page does not list them)
  - **Removed:** fabricated long_context tier from former Claude Opus 4.6 entry (combined Opus 4.5/4.6/4.7 has no long_context per page)
  - All other proprietary FM rates verified unchanged.

### 4. Databricks AI Parse Pricing
- **URL:** https://www.databricks.com/product/pricing/ai-parse
- **What it provides:** DBU per 1K pages by complexity tier, promotional discount
- **Verification (2026-05-04):** All four tiers and 50% promo through 2026-06-30 confirmed against page and Azure Learn doc.

### 5. Databricks Model Training Pricing
- **URL:** https://www.databricks.com/product/pricing/mosaic-foundation-model-training
- **What it provides:** Training DBU estimates by model and data scale
- **Verification (2026-05-04):** All MODEL_TRAINING_DBU_ESTIMATES match page; $0.65/DBU US East confirmed; supported models unchanged (Llama 3.3 70B, 3.1 70B, 3.1 8B, 3.2 3B, 3.2 1B).

### 6. Databricks Model Serving Pricing
- **URL:** https://www.databricks.com/product/pricing/model-serving
- **What it provides:** GPU instance sizes and DBU/hr rates, CPU serving rate
- **Verification (2026-05-04):** Small (10.48), Medium (20.00), Medium 4X (112.00), Medium 8x (290.80), Large 8X 40GB (538.40), Large 8X 80GB (628.00) confirmed via page. XLarge/2XLarge/4XLarge (78.6/157.2/314.4) confirmed only via Azure Learn — page no longer lists these instance sizes explicitly but Azure Learn page does.

### 7. Databricks Vector Search Pricing
- **URL:** https://www.databricks.com/product/pricing/vector-search
- **Verification (2026-05-04):** Standard 4.0 DBU/hr, Storage Optimized 18.29 DBU/hr; vector capacity per unit (2M / 64M) confirmed. Reranker 28.571 DBU/1k requests confirmed via Azure Learn.

### 8. Databricks Agent Evaluation Pricing
- **URL:** https://www.databricks.com/product/pricing/agent-evaluation
- **Verification (2026-05-04):** Page is JS-rendered (returned "Loading..."); rates confirmed via Azure Learn doc only — LLM Judge 2.14/8.57, Synthetic Data 5.0/question.

### 9. Databricks AI Gateway Pricing
- **URL:** https://www.databricks.com/product/pricing/mosaic-ai-gateway
- **Verification (2026-05-04):** Page is JS-rendered (returned "Loading..."); rates confirmed via Azure Learn doc only — 7.143 + 1.429 DBU/GB.

### 10. Databricks GenAI Pricing Calculator (Official)
- **URL:** https://www.databricks.com/product/pricing/genai-pricing-calculator
- **Verification (2026-05-04):** Page is JS-rendered (no static pricing data); cannot extract via WebFetch.

---

## Secondary Official Sources

### 11. Databricks Foundation Model Supported Models
- **URL:** https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/supported-models
- **What it provides:** Authoritative list of model names, endpoint identifiers, status (Active/Public Preview/Retired), context length, modalities, retirement dates
- **Used in 2026-05-04 refresh to confirm:**
  - Qwen3-Embedding-0.6B and Qwen3-Next 80B A3B status (Public Preview; Qwen3-Next limited to us-west-2 + ap-northeast-1)
  - Llama 3.1 405B retirement (PPT 2026-02-15, PT 2026-05-15)
  - Gemini 3 Pro retirement 2026-03-26 (redirects to Gemini 3.1 Pro at identical pricing through 2026-06-07)
  - Claude Opus 4.5, 4.6, 4.7 are separate endpoints (combined pricing entry is intentional)
  - GPT 5.5 Pro and GPT 5.5 confirmed as separate models from GPT 5.4 family

### 12. AWS Databricks Docs — Create Serving Endpoints
- **URL:** https://docs.databricks.com/en/machine-learning/model-serving/create-manage-serving-endpoints.html
- **Confirms:** AWS GPU types: GPU_SMALL (T4), GPU_MEDIUM (A10G x1), MULTIGPU_MEDIUM (A10G x4), GPU_MEDIUM_8 (A10G x8)

### 13. Azure Databricks Docs — Create Serving Endpoints
- **URL:** https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/create-manage-serving-endpoints
- **Confirms:** Azure GPU types: GPU_SMALL (T4), GPU_LARGE (A100 x1), GPU_LARGE_2 (A100 x2)
- **Key finding:** A10G instances are AWS-only; A100 instances are on both AWS and Azure

### 14. Databricks Feature Regional Availability
- **URL:** https://docs.databricks.com/en/resources/feature-region-support.html
- **Used for:** GENAI_FEATURE_AVAILABILITY cloud/region mapping

### 15. Databricks Billing System Tables
- **URL:** https://docs.databricks.com/en/admin/system-tables/billing.html
- **URL:** https://docs.databricks.com/en/admin/system-tables/pricing.html
- **Used for:** billing_origin_product → SKU category mapping, system.billing.list_prices schema

### 16. Databricks SKU Groups
- **URL:** https://www.databricks.com/product/sku-groups
- **Used for:** FULL_SKU_CATALOG — every SKU name by cloud and category

### 17. Databricks Supported Regions
- **AWS:** https://docs.databricks.com/aws/en/resources/supported-regions (last updated 2026-03-24)
- **Azure:** https://learn.microsoft.com/en-us/azure/databricks/resources/supported-regions
- **GCP:** https://docs.databricks.com/gcp/en/resources/supported-regions.html
- **Used for:** REGIONS_BY_CLOUD region lists
- **2026-05-04 finding:** AWS page lists `us-gov-west-1` (GovCloud) which is not in `REGIONS_BY_CLOUD["AWS"]` — intentionally excluded due to special pricing/availability handling.

---

## Verification Status Summary

| Data Category | Status | Primary Source |
|---|---|---|
| Foundation Model DBU rates (open) | Confirmed (Azure Learn 2026-04-21 + pricing page 2026-05-04) | Sources 1, 2 |
| Open FM scaling capacity rates | Confirmed via pricing page (added in 2026-05-04 refresh) | Source 2 |
| Qwen3 family rates | Confirmed via pricing page (corrected estimated values to actuals) | Sources 2, 11 |
| Proprietary Model DBU rates | Confirmed via pricing page; Anthropic cross-confirmed via Azure Learn | Sources 1, 3 |
| Cache write/read rates | From pricing page (not in Azure Learn for OpenAI/Google) | Source 3 |
| Batch inference rates | From pricing page (not in Azure Learn for OpenAI/Google) | Source 3 |
| GPT 5.4/5.5/5.5 Pro family | Confirmed via pricing page 2026-05-04 (newly added) | Source 3 |
| Claude Haiku 4.5 batch | From pricing page (Azure Learn shows n/a — page is more current) | Source 3 |
| Gemini 3.1 Flash Lite rates | Confirmed via pricing page (corrected from estimate) | Source 3 |
| GPU instance DBU/hr (Small, XLarge, 2XL, 4XL) | Confirmed | Source 1 |
| GPU instance DBU/hr (Medium, Medium 4X, Medium 8x, Large 8X) | Confirmed via pricing page (not in Azure Learn) | Source 6 |
| GPU cloud availability | Confirmed (AWS/Azure docs) | Sources 12, 13 |
| Vector Search rates | Confirmed | Sources 1, 7 |
| Lakebase multipliers | Confirmed | Source 1 |
| AI Gateway rates | Confirmed via Azure Learn (databricks.com page is JS-rendered) | Source 1 |
| Agent Evaluation rates | Confirmed via Azure Learn (databricks.com page is JS-rendered) | Source 1 |
| AI Parse DBU rates + 50% promo | Confirmed | Sources 1, 4 |
| Model Training estimates | Confirmed | Sources 1, 5 |
| SQL Warehouse DBU/hr | Confirmed | Source 1 |
| Storage DSU multipliers | Confirmed | Source 1 |
| Shutterstock ImageAI 0.857 DBU/image | Confirmed | Source 1 |
| $/DBU by workload (per-cloud) | UNCONFIRMED — JS-rendered pricing pages cannot be scraped | Sources 1, 6 |
| Lakeflow Connect $0.35/DBU | UNCONFIRMED — source page JS-rendered | Source 6 |
| Regional $/DBU rates | From databricks.com pricing pages (JS-rendered, unconfirmed) | Sources 2-9 |

---

## Known Limitations

1. **JS-rendered pricing pages:** Many `databricks.com/product/pricing/*` pages render pricing tables via JavaScript. As of 2026-05-04, the open FM, proprietary FM, AI Parse, Vector Search, Model Serving, and Model Training pages return enough static markup to extract rates. AI Gateway, Agent Evaluation, ImageAI, and the official GenAI calculator return only `"Loading..."` and require Azure Learn for verification.

2. **$/DBU rates are not in docs:** The Azure Learn docs page publishes DBU *consumption* rates (DBU/hr, DBU/1M tokens, multipliers) but NOT the $/DBU dollar rates. The $/DBU rates are published on `azure.microsoft.com/pricing/details/databricks/` (Azure) and `databricks.com/product/pricing` (AWS/GCP), both of which are JS-rendered and not currently scrapable. Use `system.billing.list_prices` for authoritative per-customer rates.

3. **Committed-use discounts not modeled:** Actual customer rates can be 20-40% below list. Use `system.billing.list_prices` for contract rates.

4. **Deprecated and retiring models (as of 2026-05-04):**
   - Llama 3.1 405B: PPT retired 2026-02-15; PT retiring 2026-05-15 (~11 days from refresh date). Kept as `(deprecated)` entry for historical comparisons.
   - Claude Sonnet 3.7: retired 2026-04-12; removed from `Claude Sonnet 4/4.1` group label.
   - Gemini 3 Pro: retired 2026-03-26; calls redirect to Gemini 3.1 Pro at identical pricing through 2026-06-07. Not modeled as a separate entry.

5. **GCP feature gaps:** Many GenAI features are "limited" or "preview" on GCP. The calculator does not block estimates for unavailable cloud/feature combinations.

6. **GovCloud excluded:** AWS `us-gov-west-1` is supported per Databricks docs but is not modeled in `REGIONS_BY_CLOUD` due to special pricing and feature availability rules.

7. **Public Preview models with estimated rates:** None as of 2026-05-04 refresh — Qwen3 family rates are now authoritative per the pricing page.

---

## Audit history

| Date | Scope | Highlights |
|---|---|---|
| 2026-04-07 | Initial comprehensive | Established `pricing_data.py` from 17 sources; flagged JS-rendered pages as unverified |
| 2026-04-08 | Targeted refresh | Added Qwen3-Embedding-0.6B, Qwen3-Next 80B A3B (estimated rates), Gemini 3.1 Flash Lite (estimated rates); fixed Claude Opus/Haiku 4.5 batch to None per Azure pricing table; renamed Claude Sonnet 4/4.1 → 3.7/4/4.1 |
| 2026-05-04 | Full audit | Cross-verified all FM rates against pricing page + Azure Learn; replaced estimated Qwen3/Gemini Flash Lite rates with actuals; added GPT 5.5, GPT 5.4/5.5 Pro, GPT 5.4 mini, GPT 5.4 nano; added in_geo tiers for GPT 5 mini/nano + 5.1 Codex Max/Mini; consolidated Claude Opus 4.5/4.6/4.7 into single entry; renamed Sonnet 3.7/4/4.1 → 4/4.1 (3.7 retired); removed fabricated long_context tiers from Sonnet 4.5/4.6 + Opus 4.5/4.6/4.7; populated scaling_capacity_per_hour for all open FMs; fixed Claude Haiku 4.5 batch rates |

---

## How to Refresh

1. **Quick refresh:** Query `system.billing.list_prices` in your workspace for current per-SKU rates.
2. **Full refresh:** Re-fetch each page in the Primary Sources list (1–10), prioritizing 1, 2, 3, 11. Cross-reference Azure Learn (Source 1, dated header) against the databricks.com pricing pages — Azure Learn lags slightly but is the most reliable for static extraction.
3. **Model availability:** Check `docs.databricks.com/aws/en/machine-learning/foundation-model-apis/supported-models` for additions/retirements. Retirement dates here precede pricing-page removal by weeks.
4. **Region drift:** Re-fetch the three supported-regions pages (Source 17) when adding workspace regions.
