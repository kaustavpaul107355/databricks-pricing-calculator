# Calculation coverage checklist — GenAI TCO Estimator

Use when adding or changing GenAI pricing. The **Dash app** implements the rows marked **UI + calc**; CLI may expose additional workloads.

## GenAI pricing pages → app mapping

| # | Pricing page | App location | Calculator | Notes |
|---|--------------|--------------|------------|-------|
| 1 | [Agent Bricks](https://www.databricks.com/product/pricing/agent-bricks) | GenAI tile **Agent Bricks** | Model Serving CPU/GPU | Billed as serverless inference |
| 2 | [AI Functions](https://www.databricks.com/product/pricing/ai-parse) | GenAI tile **AI Parse** | `estimate_ai_parse` | Dropdown value = complexity **key** |
| 2a | Same page | GenAI tile **AI Extract** | `estimate_ai_extract` | Workload key; inputs in thousands |
| 2b | Same page | GenAI tile **AI Classify** | `estimate_ai_classify` | Workload key; documents in thousands |
| 3 | [Mosaic AI Gateway](https://www.databricks.com/product/pricing/mosaic-ai-gateway) | GenAI tile **Mosaic AI Gateway** | `estimate_gateway_payload` | Guardrails: informational only |
| 4 | [Model Serving](https://www.databricks.com/product/pricing/model-serving) | GenAI tile **Model Serving** | CPU / GPU serving | |
| 5 | [Foundation Model Serving](https://www.databricks.com/product/pricing/foundation-model-serving) | GenAI tile **Foundation Model** | `estimate_foundation_model_tokens` | PPT + PT (+ scaling capacity in data) |
| 6 | [Proprietary FM Serving](https://www.databricks.com/product/pricing/proprietary-foundation-model-serving) | GenAI tile **Proprietary Model** | `estimate_proprietary_foundation_model` | Tier `dbc.Select`; validate tier on calc |
| 7 | [Vector Search](https://www.databricks.com/product/pricing/vector-search) | GenAI tiles **Vector Search** + **Reranker** | `estimate_vector_search`, reranker | |
| 8 | [Agent Evaluation](https://www.databricks.com/product/pricing/agent-evaluation) | GenAI tile **Agent Evaluation** | `estimate_agent_evaluation` | |
| 9 | [Model Training](https://www.databricks.com/product/pricing/mosaic-foundation-model-training) | GenAI tile **Model Training** | `estimate_model_training` | One-time in total |
| 10 | [GenAI Pricing Calculator](https://www.databricks.com/product/pricing/genai-pricing-calculator) | Sidebar link | — | External reference |

## Scenario templates (composite)

| Scenario | Inputs (Dash) | Estimator | Line items (typical) |
|----------|---------------|-----------|----------------------|
| RAG Application | docs, pages, chunks, Q/day, emb + LLM models, parse complexity | `estimate_rag_scenario` | Parse, embeddings, VS, LLM, gateway, eval, storage |
| Multi-Agent System | requests/day, steps, tools, models, VS checkbox | `estimate_multi_agent_scenario` | Orchestrator + worker LLM, optional VS, gateway |
| Batch AI Pipeline | docs, pages, frequency, model, optional Extract/Classify | `estimate_batch_pipeline_scenario` | Parse, Extract, Classify, batch inference, Jobs, storage |
| Fine-Tuned Model | base model, scale, serving hrs, retrain cadence, eval | `estimate_fine_tune_scenario` | Amortized training, PT serving, eval |

**Parse complexity in scenarios:** Must use keys from `AI_PARSE_DBU_PER_1K_PAGES` (same as GenAI tile values).

## When adding a new GenAI price dimension

1. Add constants to `pricing_data.py` with source comment + row in `PRICING_SOURCES.md`.
2. Add or extend `estimate_*` in `calculator.py`.
3. Add GenAI tile + callback in `app.py` (use `ui_helpers` for dropdown patterns).
4. Add `dcc.Store` + label in `GENAI_STORE_LABELS` if part of monthly total.
5. Extend CLI if needed.
6. Add pytest in `tests/`.
7. Update this file and `STATUS_AND_COVERAGE.md`.
8. Log session in `docs/DEV_LOG.md`.

## UI dropdown rules (avoid common bugs)

| Control | Value stored | Coercion |
|---------|--------------|----------|
| AI Parse complexity | `AI_PARSE_DBU_PER_1K_PAGES` **key** | `parse_complexity_options()` |
| AI Extract workload | `AI_EXTRACT_DBU_PER_1K_INPUTS` **key** | `ai_extract_workload_options()` |
| AI Classify workload | `AI_CLASSIFY_DBU_PER_1K_DOCUMENTS` **key** | `ai_classify_workload_options()` |
| FM / proprietary model | catalog name | `model_options_with_retirement()`; `retirement_alert()` |
| Proprietary tier | tier id (`global`, `in_geo`, …) | `resolve_proprietary_tier(model, tier)` on every calc |
| Training scale | scale string | `resolve_training_scale(model, scale)` |
| Cloud → Region | region id per cloud | Preserve region when still valid after cloud change |
| Multi-agent VS | Checklist `yes` | `checklist_enabled(ma_vs)` not `bool(list)` |

## CLI-only workloads (not in Dash)

Still in `pricing_data.py` / `cli.py`: SQL warehouse, storage DSU, compute DBU-hours, ImageAI, SKU listing.
