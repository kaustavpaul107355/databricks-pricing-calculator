# Pricing Data Sources & Verification Status

This document tracks every source used to populate `pricing_data.py`, the verification status of each data point, and when the data was last refreshed.

**Last comprehensive refresh:** 2026-04-07

---

## Primary Official Sources

### 1. Azure Databricks Pricing — Serverless DBU Consumption by SKU
- **URL:** https://learn.microsoft.com/en-us/azure/databricks/resources/pricing
- **What it provides:** DBU multipliers for all serverless SKUs, GPU instance DBU/hr rates, Vector Search DBU rates, Lakebase multipliers, Agent Evaluation rates, AI Gateway rates, Storage DSU multipliers
- **Verification status:** CONFIRMED — this is the most authoritative public source for DBU consumption data
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

### 2. Databricks Foundation Model Serving Pricing
- **URL:** https://www.databricks.com/product/pricing/foundation-model-serving
- **What it provides:** Per-model DBU rates for open foundation models (pay-per-token and provisioned throughput)
- **Note:** Page is JS-rendered; data extracted via the official GenAI pricing calculator JS
- **Data points sourced:**
  - All FOUNDATION_MODEL_DBU_PER_MILLION entries (Llama 4 Maverick, 3.3 70B, 3.1 8B, etc.)
  - Entry capacity vs scaling capacity DBU/hr rates

### 3. Databricks Proprietary Foundation Model Serving Pricing
- **URL:** https://www.databricks.com/product/pricing/proprietary-foundation-model-serving
- **What it provides:** Per-model DBU rates for OpenAI, Anthropic, Google models; Global/In-Geo/Long Context tiers; cache write/read rates; batch inference rates
- **Note:** Page is JS-rendered; data extracted via calculator JS and cross-referenced with Azure docs
- **Data points sourced:**
  - All PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION entries
  - Cache write/read rates for all models
  - Batch inference DBU/hr rates
  - In-Geo and Long Context tier rates

### 4. Databricks AI Parse Pricing
- **URL:** https://www.databricks.com/product/pricing/ai-parse
- **What it provides:** DBU per 1K pages by complexity tier, promotional discount
- **Data points sourced:**
  - AI_PARSE_DBU_PER_1K_PAGES (Low 12.5, Low 22.5, Medium 62.5, High 87.5)
  - 50% promotional discount through June 30, 2026

### 5. Databricks Model Training Pricing
- **URL:** https://www.databricks.com/product/pricing/mosaic-foundation-model-training
- **What it provides:** Training DBU estimates by model and data scale
- **Data points confirmed:** All MODEL_TRAINING_DBU_ESTIMATES entries match

### 6. Databricks Model Serving Pricing
- **URL:** https://www.databricks.com/product/pricing/model-serving
- **What it provides:** GPU instance sizes and DBU/hr rates, CPU serving rate
- **Note:** Only Small/XLarge/2XLarge/4XLarge confirmed via Azure docs; Medium/Medium 4X/Medium 8x/Large 8X rates are from this JS-rendered page

### 7. Databricks Vector Search Pricing
- **URL:** https://www.databricks.com/product/pricing/vector-search
- **What it provides:** Standard and Storage Optimized tiers, vector capacity per unit
- **Data points confirmed via Azure docs:** Standard 4.0 DBU/hr, Storage Optimized 18.29 DBU/hr

### 8. Databricks Agent Evaluation Pricing
- **URL:** https://www.databricks.com/product/pricing/agent-evaluation
- **What it provides:** LLM Judge and Synthetic Data rates
- **Data points confirmed via Azure docs**

### 9. Databricks AI Gateway Pricing
- **URL:** https://www.databricks.com/product/pricing/mosaic-ai-gateway
- **What it provides:** Inference Tables and Usage Tracking rates
- **Data points confirmed via Azure docs:** 7.143 DBU/GB, 1.429 DBU/GB

### 10. Databricks GenAI Pricing Calculator (Official)
- **URL:** https://www.databricks.com/product/pricing/genai-pricing-calculator
- **What it provides:** Interactive calculator with embedded model data, benchmark-driven PT throughput estimation
- **Data extracted:** Model lists, regional rates, batch inference rates, Knowledge Assistant costing model
- **Note:** Calculator JS was reverse-engineered to extract model-specific data not available in static HTML

---

## Secondary Official Sources

### 11. AWS Databricks Docs — Create Serving Endpoints
- **URL:** https://docs.databricks.com/en/machine-learning/model-serving/create-manage-serving-endpoints.html
- **Confirms:** AWS GPU types: GPU_SMALL (T4), GPU_MEDIUM (A10G x1), MULTIGPU_MEDIUM (A10G x4), GPU_MEDIUM_8 (A10G x8)

### 12. Azure Databricks Docs — Create Serving Endpoints
- **URL:** https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/create-manage-serving-endpoints
- **Confirms:** Azure GPU types: GPU_SMALL (T4), GPU_LARGE (A100 x1), GPU_LARGE_2 (A100 x2)
- **Key finding:** A10G instances are AWS-only; A100 instances are on both AWS and Azure

### 13. Databricks Foundation Model Overview
- **URL:** https://docs.databricks.com/en/machine-learning/model-serving/foundation-model-overview.html
- **Confirms:** Supported model list, Llama 3.1 405B retirement (PPT retired, PT retiring May 15, 2026)

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
- **AWS:** https://docs.databricks.com/en/resources/supported-regions.html
- **Azure:** https://learn.microsoft.com/en-us/azure/databricks/resources/supported-regions
- **GCP:** https://docs.databricks.com/gcp/en/resources/supported-regions.html
- **Used for:** REGIONS_BY_CLOUD region lists

---

## Verification Status Summary

| Data Category | Status | Primary Source |
|---|---|---|
| Foundation Model DBU rates (open) | Confirmed (Azure docs + calculator JS) | Sources 1, 2, 10 |
| Proprietary Model DBU rates | Partially confirmed (Azure Anthropic confirmed; GPT/Gemini from calculator JS) | Sources 1, 3, 10 |
| Cache write/read rates | From calculator JS (not in static docs) | Source 10 |
| Batch inference rates | From calculator JS (not in static docs) | Source 10 |
| GPU instance DBU/hr (Small, XLarge, 2XL, 4XL) | Confirmed | Source 1 |
| GPU instance DBU/hr (Medium, Medium 4X, Medium 8x, Large 8X) | From databricks.com (JS-rendered, unverifiable via scraping) | Source 6 |
| GPU cloud availability | Confirmed (AWS/Azure docs) | Sources 11, 12 |
| Vector Search rates | Confirmed | Source 1 |
| Lakebase multipliers | Confirmed | Source 1 |
| AI Gateway rates | Confirmed | Source 1 |
| Agent Evaluation rates | Confirmed | Source 1 |
| AI Parse DBU rates | From databricks.com pricing page | Source 4 |
| Model Training estimates | From databricks.com pricing page | Source 5 |
| SQL Warehouse DBU/hr | Confirmed | Source 1 |
| Storage DSU multipliers | Confirmed | Source 1 |
| $/DBU by workload (per-cloud) | PARTIALLY UNCONFIRMED — JS-rendered pages could not be scraped | Sources 1, 6 (Azure $/DBU from azure.microsoft.com not fetchable) |
| Lakeflow Connect $0.35/DBU | UNCONFIRMED — source page JS-rendered | Source 6 |
| Regional $/DBU rates | From databricks.com pricing pages (JS-rendered) | Sources 2-9 |

---

## Known Limitations

1. **JS-rendered pricing pages:** Most databricks.com/product/pricing/* pages render pricing tables via JavaScript. Static scraping returns no data. The official GenAI calculator JS was the most reliable extraction method.

2. **$/DBU rates are not in docs:** The Azure Learn docs page publishes DBU *consumption* rates (DBU/hr, DBU/1M tokens, multipliers) but NOT the $/DBU dollar rates. The $/DBU rates are published on azure.microsoft.com/pricing/details/databricks/ (Azure) and databricks.com/product/pricing (AWS/GCP), both of which are JS-rendered.

3. **Committed-use discounts not modeled:** Actual customer rates can be 20-40% below list. Use `system.billing.list_prices` for contract rates.

4. **Deprecated models:** Llama 3.1 405B is flagged as deprecated (PPT retired, PT retiring May 15, 2026). Rates are kept for historical reference but should not be used for new estimates.

5. **GCP feature gaps:** Many GenAI features are "limited" or "preview" on GCP. The calculator does not currently block estimates for unavailable cloud/feature combinations.

---

## How to Refresh

1. **Quick refresh:** Query `system.billing.list_prices` in your workspace for current per-SKU rates
2. **Full refresh:** Re-extract data from the official GenAI calculator JS at databricks.com/product/pricing/genai-pricing-calculator
3. **Azure DBU multipliers:** Check learn.microsoft.com/en-us/azure/databricks/resources/pricing for updated tables
4. **Model availability:** Check docs.databricks.com/en/machine-learning/model-serving/foundation-model-overview.html for model additions/retirements
