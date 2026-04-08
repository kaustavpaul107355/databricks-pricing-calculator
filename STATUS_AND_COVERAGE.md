# Databricks Pricing Calculator — Status & Coverage

## Where we are

- **Single app:** One Streamlit app in `databricks-pricing-calculator` (no separate fullstack).
- **Sources:** All rates and formulas are derived from the [Databricks pricing pages](https://www.databricks.com/product/pricing) and related docs (e.g. Azure Serverless DBU consumption). The app lists 29 source pages in the sidebar and runs **all calculations locally** (no “link-only” estimates).
- **UI:** Main page has Cloud, Region, and optional SKU. Tabs: SQL Warehouse, Vector Search (incl. Reranker), Compute (DBU-hours), Model Training, Model Serving (CPU + GPU), Foundation Model, AI Parse, Storage, Agent Evaluation, ImageAI, and Scenarios (save/compare/export CSV). Sidebar: Pricing Pages (29 links) and SKU Reference.

---

## Coverage vs. web pricing pages

### Fully covered (calculator tab + formula + data from page)

| Web pricing page | App tab | Confidence |
|------------------|--------|------------|
| [Databricks SQL](https://www.databricks.com/product/pricing/databricks-sql) | SQL Warehouse | **High** — Serverless DBU/hr by size; region $/DBU |
| [Vector Search](https://www.databricks.com/product/pricing/vector-search) | Vector Search (+ Reranker in expander) | **High** — DBU/hr per unit for Standard & Storage Optimized; Reranker DBU/1k requests |
| [Lakeflow Jobs](https://www.databricks.com/product/pricing/lakeflow-jobs), [Lakeflow Pipelines](https://www.databricks.com/product/pricing/lakeflow-spark-declarative-pipelines), [Lakeflow Connect](https://www.databricks.com/product/pricing/lakeflow-connect), [Lakebase](https://www.databricks.com/product/pricing/lakebase), [Data Science/ML](https://www.databricks.com/product/pricing/datascience-ml), [Databricks Apps](https://www.databricks.com/product/pricing/databricks-apps), [Clean Rooms](https://www.databricks.com/product/pricing/clean-rooms) | Compute (DBU-hours) | **High** — Workload dropdown with $/DBU; same formula (DBU × $/DBU). *Rates are example list prices; exact $/DBU from `system.billing.list_prices`* |
| [Model Training](https://www.databricks.com/product/pricing/mosaic-foundation-model-training) | Model Training | **High** — DBU estimates per model/scale; $0.65/DBU (US East) from docs |
| [Model Serving](https://www.databricks.com/product/pricing/model-serving) | Model Serving | **High** — CPU (1 DBU/hr per request) and GPU (DBU/hr by instance size) |
| [Foundation Model Serving](https://www.databricks.com/product/pricing/foundation-model-serving), [Proprietary Foundation Model Serving](https://www.databricks.com/product/pricing/proprietary-foundation-model-serving) | Foundation Model | **High** — $/DBU per 1M input/output tokens and provisioned throughput; model list from pages |
| [AI Parse Document](https://www.databricks.com/product/pricing/ai-parse) | AI Parse | **High** — DBU per 1k pages by complexity (low/medium/high) |
| [Storage](https://www.databricks.com/product/pricing/storage) | Storage | **High** — DSU formula (GB + write/read ops + Vector Search units); $/DSU configurable |
| [Agent Evaluation](https://www.databricks.com/product/pricing/agent-evaluation) | Agent Evaluation | **High** — LLM Judge (input/output tokens), Synthetic Data (per question); DBU rates from Azure doc |
| [Shutterstock ImageAI](https://www.databricks.com/product/pricing/mosaic-imageai-serving) | ImageAI | **High** — DBU per image |
| [Lakeflow Connect](https://www.databricks.com/product/pricing/lakeflow-connect) | Compute → workload **Lakeflow Connect** | **High** — Explicit workload in dropdown |
| [Lakeflow Spark Declarative Pipelines](https://www.databricks.com/product/pricing/lakeflow-spark-declarative-pipelines) | Compute → workload **Lakeflow Pipelines** | **High** — Explicit workload in dropdown |
| [Databricks Apps](https://www.databricks.com/product/pricing/databricks-apps) | Compute → workload **Databricks Apps** | **High** — Explicit workload; All-Purpose Serverless SKU maps here |
| Data Quality Monitoring (LAKEHOUSE_MONITORING, DATA_QUALITY_MONITORING) | Compute → workload **Data Quality Monitoring** | **High** — Explicit workload in dropdown |

Agent Bricks and Mosaic AI Gateway are **billed like Model Serving** (serverless inference); the app covers them via the same Model Serving (CPU/GPU) tab and workload/SKU mapping.

---

### Partially covered or reference-only

| Web pricing page | Status |
|------------------|--------|
| [Data Transfer and Connectivity](https://www.databricks.com/product/pricing/data-transfer-connectivity) | **SKU list only** in sidebar (no calculator). Pricing is in PDF/contract; we don’t have a per-GB or per-endpoint formula in the app. |
| [Platform Add-ons](https://www.databricks.com/product/pricing/platform-addons), [Managed Services](https://www.databricks.com/product/pricing/managed-services) | **Linked** in Pricing Pages; no in-app calculation (add-ons and managed services are plan-specific). |
| [Delta Share from SAP BDC](https://www.databricks.com/product/pricing/delta-share-sap-business-data-cloud), [View Sharing](https://www.databricks.com/product/pricing/view-sharing), [Beta Products](https://www.databricks.com/product/pricing/beta-products) | **Linked** only; no calculator. |

---

### Not replicated by design

- **[Databricks Pricing Calculator (instance types)](https://www.databricks.com/product/pricing/product-pricing/instance-types)** — Official instance-type calculator; we link to it and use our own DBU-based estimates instead of reimplementing it.
- **[GenAI Pricing Calculator](https://www.databricks.com/product/pricing/genai-pricing-calculator)**, **[SAP Databricks Sizing Calculator](https://www.databricks.com/product/pricing/sap-databricks-pricing-calculator)** — Specialized external tools; we link only.

---

## Confidence summary

| Area | Confidence | Notes |
|------|------------|--------|
| **Formulas** | High | DBU × $/DBU, DSU × $/DSU, token rates, and DBU/hr rules match the documented model. |
| **Rates in app** | Medium–High | SQL, Vector Search, Model Serving, Foundation Model, AI Parse, Storage, Training: sourced from pricing pages or Azure/docs. Compute **workload $/DBU** is “example list price”; real $/DBU from `system.billing.list_prices` or contract. |
| **Region $/DBU** | Medium | Fixed per-region values (e.g. 0.07, 0.088); sufficient for estimates but may not match every plan or date. |
| **Replicating “all” web calculation options** | High | We replicate **all** calculable product pricing pages: SQL, Vector Search (+ Reranker), Compute (with explicit workloads: Jobs, Lakeflow Connect, Lakeflow Pipelines, Databricks Apps, Data Quality Monitoring, DLT, Lakebase, Clean Rooms, etc.), Model Training, Model Serving, Foundation Model, AI Parse, Storage, Agent Evaluation, Shutterstock ImageAI. We do **not** replicate: Data Transfer/Connectivity (no public formula), Platform Add-ons, Managed Services, View Sharing, Delta Share SAP BDC, Beta, or the three external calculators. |

---

## Bottom line

- The app **does** replicate **all calculable** product pricing pages: SQL, Vector Search (incl. Reranker), Compute (with explicit workloads including Lakeflow Connect, Lakeflow Pipelines, Databricks Apps, Data Quality Monitoring), Model Training, Model Serving, Foundation Model, AI Parse, Storage, Agent Evaluation, and Shutterstock ImageAI. Formulas and rates are sourced from the pricing pages or Azure/docs.
- It **does not** replicate: Data Transfer/Connectivity (no public per-GB formula), Platform Add-ons, Managed Services, View Sharing, Delta Share SAP BDC, Beta, or the three external calculators. For those, the app provides links and SKU reference only.
- **Audit:** See `CALCULATION_COVERAGE.md` for a page-by-page checklist so we don’t miss any calculation offering when adding or changing pricing pages.
