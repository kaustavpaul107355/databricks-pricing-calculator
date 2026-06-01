# Requirements — Databricks GenAI TCO Estimator

| Field | Value |
|-------|--------|
| **Product name** | Databricks GenAI TCO Estimator |
| **Repository** | `databricks-pricing-calculator` |
| **Document version** | 1.2 |
| **Last updated** | 2026-05-30 |
| **Status** | Active development — MVP deployed locally / Databricks Apps |

---

## 1. Purpose

Provide **fast, credible ballpark cost estimates** for Databricks **GenAI solutions** during customer conversations, POC scoping, and internal planning. The tool must **not** replace contract pricing, the official instance-type calculator, or workspace-specific `system.billing.list_prices`.

### 1.1 Goals

- Estimate **monthly recurring** and **one-time** costs from published DBU/DSU/token rates.
- Support **cloud + region** selection with illustrative **$/DBU** (and workload overrides where modeled).
- Offer both **line-item (per service)** and **architecture-level (scenario)** views.
- Run as a **web app** (Dash) with optional **CLI** for scripts and automation.
- Deploy on **Databricks Apps** with minimal configuration.

### 1.2 Non-goals

- Authoritative quotes or entitlement checks.
- Full replication of the [instance-type pricing calculator](https://www.databricks.com/product/pricing/product-pricing/instance-types).
- Data Transfer / Connectivity, Platform Add-ons, Managed Services, View Sharing, or plan-specific discounts.
- Live pull from `system.billing.list_prices` (future enhancement only).

---

## 2. Users and use cases

| Persona | Use case |
|---------|----------|
| **Solution Architect / DSA** | Ballpark TCO for RAG, agents, batch doc AI, fine-tuning in QBR / discovery |
| **Field Engineer** | Compare models (open vs proprietary), PT vs PPT break-even before sizing workshops |
| **Customer (indirect)** | View estimates in demos; numbers are illustrative only |

---

## 3. Functional requirements

### 3.1 Global context

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-001 | User selects **cloud** (AWS, Azure, GCP) and **region**; estimates use region **$/DBU** where applicable | Must | Done |
| FR-002 | Sidebar links to **official GenAI pricing pages** (primary sources) | Should | Done |
| FR-003 | All estimates display **USD** with clear “estimate only” disclaimer | Must | Done |

### 3.2 GenAI Calculator (per-service)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-010 | **Vector Search**: tier, endpoint count, hours/month | Must | Done |
| FR-011 | **Vector Search Reranker**: requests (thousands/month) | Should | Done |
| FR-012 | **Agent Bricks**: agent type, CPU request-hours or GPU size + hours | Must | Done |
| FR-013 | **Mosaic AI Gateway**: guardrails note; Inference Tables / Usage Tracking via payload GB | Must | Done |
| FR-014 | **Model Serving**: CPU request-hours or GPU size + hours | Must | Done |
| FR-015 | **Foundation Model (open)**: model, input/output tokens (M), PT hours | Must | Done |
| FR-016 | **Proprietary FM**: model, tier (global / in-geo / long context / combined), tokens, cache, batch | Must | Done |
| FR-017 | **AI Parse**: complexity, pages (thousands), optional **50% promo** through 2026-06-30 | Must | Done |
| FR-017a | **AI Extract**: workload type, inputs (thousands), shared **50% promo** | Must | Done |
| FR-017b | **AI Classify**: workload type, documents (thousands), shared **50% promo** | Must | Done |
| FR-018 | **Agent Evaluation**: type, input/output tokens, questions | Must | Done |
| FR-019 | **Model Training**: one-time cost by model + scale; included in ballpark total | Must | Done |
| FR-020 | **Ballpark total**: sum of monthly line items + one-time training | Must | Done |
| FR-021 | Tile/grid UI with labels, hints, and doc links per service | Should | Done |
| FR-022 | Surface **calculation errors** in UI (not silent zero) | Should | Done |
| FR-023 | **Model retirement warnings** in dropdowns and alerts for catalog models with known retire dates | Should | Done |
| FR-024 | **Gemini proprietary FM**: optional **20% promo** through 2026-06-30 | Should | Done |

### 3.3 Analysis modes

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-030 | **PT vs PPT break-even**: QPM, token sizes, uptime; chart + metrics | Must | Done |
| FR-031 | **Model comparison**: 2–3 models, same monthly token volume; bar chart | Must | Done |
| FR-032 | **Scenario — RAG**: docs, pages, chunks, queries/day, models, parse complexity, refresh | Must | Done |
| FR-033 | **Scenario — Multi-agent**: requests/day, steps, tools, orchestrator/worker models, optional VS | Must | Done |
| FR-034 | **Scenario — Batch AI**: docs, pages, frequency, parse + optional Extract/Classify + inference + jobs + storage | Must | Done |
| FR-035 | **Scenario — Fine-tune**: training amortized, PT serving (or explicit $0 line if no PT rate), eval | Must | Done |
| FR-036 | Scenario results: **total TCO**, pie breakdown (if non-zero lines), expandable line items | Must | Done |
| FR-037 | **Quick Estimate**: S/M/L presets per scenario type (12 presets) | Should | Done |

### 3.4 CLI

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-040 | CLI commands for atomic estimates (SQL, VS, serving, FM, AI Parse/Extract/Classify, storage, etc.) | Should | Done |
| FR-041 | CLI `breakeven`, `compare`, `scenario` aligned with UI logic | Should | Done |
| FR-042 | CLI `list` for models, regions, SKUs, workloads, AI function workloads | Should | Done |

### 3.5 Data and pricing fidelity

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-050 | Rates maintained in `pricing_data.py` with traceability in `PRICING_SOURCES.md` | Must | Done |
| FR-051 | Periodic refresh per [PRICING_FITMENT.md](./PRICING_FITMENT.md) | Must | Ongoing |
| FR-052 | Open FM: PPT, PT entry, **scaling capacity** where published | Should | Done |
| FR-053 | Proprietary FM: tiers, cache, batch per model | Must | Done |

---

## 4. Non-functional requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| NFR-001 | **Local run**: `python app.py` on port **8000** (overridable via `PORT`) | Must | Done |
| NFR-002 | **Databricks Apps**: `app.yaml` runs `python app.py` | Must | Done |
| NFR-003 | No secrets in git; workspace scripts (e.g. keep-alive) gitignored | Must | Done |
| NFR-004 | UI responsive enough for laptop demos (Bootstrap grid) | Should | Done |
| NFR-005 | Core logic **UI-agnostic** (`calculator.py`, `scenarios.py`) | Must | Done |
| NFR-006 | Automated **unit tests** for estimation functions | Should | Done (`pytest tests/`) |
| NFR-007 | **Pinned** lockfiles (`requirements.lock`, `requirements-dev.lock`) for reproducible deploys | Should | Done |

---

## 5. Assumptions and constraints

- **Formula**: cost ≈ DBUs × $/DBU (or DSUs × $/DSU; tokens × DBU/M × $/DBU).
- **$/DBU** is illustrative per region/workload unless customer contract data is applied manually.
- **AI Extract / Classify** assume inputs are already parsed via `ai_parse_document` (per pricing page); combined pipelines should sum Parse + Extract/Classify tiles manually or in scenarios.
- **Scenarios** use documented heuristics (e.g. 256 tokens/chunk, 4 bytes/token for gateway payload) — documented in design doc.
- **Retirement notices** come from supported-models documentation; pricing rows may remain until removal from the pricing page.

---

## 6. Acceptance criteria (MVP — current release)

1. All five Dash tabs load without error; changing cloud updates region list.
2. GenAI Calculator tiles return costs or visible warnings when inputs invalid.
3. AI Parse, Extract, and Classify tiles participate in ballpark total when configured.
4. Selecting a retiring model shows a warning on proprietary, open FM, and break-even selectors.
5. Break-even and model comparison charts render for valid open-model selections.
6. Each scenario type produces a non-empty TCO when defaults are used.
7. CLI `python cli.py ai-extract 10 "Invoices (~1 page)"` prints a cost.
8. `pytest tests/ -q` passes.

---

## 7. Backlog (prioritized)

| Priority | Item | Maps to |
|----------|------|---------|
| P2 | Optional `system.billing.list_prices` import (workspace profile) | FR-050 |
| P2 | Scenario **export** (CSV/JSON) of line items | New FR |
| P2 | Remove or sync **index.html** with current model catalog | Maintenance |
| P3 | Split `pricing_data.py` by domain | Maintainability |

---

## 8. Related documents

| Document | Purpose |
|----------|---------|
| [DESIGN.md](./DESIGN.md) | Architecture and extension guide |
| [DEV_LOG.md](./DEV_LOG.md) | Running build log — **update every session** |
| [PRICING_FITMENT.md](./PRICING_FITMENT.md) | Fitment checklist and source URLs |
| [../PRICING_SOURCES.md](../PRICING_SOURCES.md) | Rate provenance and verification |
| [../README.md](../README.md) | Quick start and layout |

---

## 9. Revision history

| Date | Version | Change |
|------|---------|--------|
| 2026-05-30 | 1.0 | Initial requirements doc from codebase review |
| 2026-05-30 | 1.1 | AI Extract/Classify, retirement UI, Gemini promo, PORT done; backlog trimmed |
| 2026-05-30 | 1.2 | Batch scenario Extract/Classify; `requirements.lock` / `requirements-dev.lock` |
