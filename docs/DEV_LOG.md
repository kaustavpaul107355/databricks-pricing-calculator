# Development log — Databricks GenAI TCO Estimator

**How to use this file:** Add a dated entry at the **top** of [Session log](#session-log) whenever you work on the project. Update [Current status](#current-status) when milestones shift. Keep entries short: what changed, why, and what’s next.

---

## Current status

| Item | State |
|------|--------|
| **Last updated** | 2026-05-30 |
| **Phase** | MVP — GenAI-focused Dash app, deployable via Databricks Apps |
| **UI** | Dash + dash-bootstrap-components + Plotly; frosted-glass theme; GenAI tab = tile grid |
| **Core** | `calculator.py`, `scenarios.py`, `ui_helpers.py`, `presets.py`, `pricing_data.py` |
| **Models** | ~12 open FM + ~26 proprietary (see `pricing_data.py`) |
| **Regions** | 69 across AWS / Azure / GCP |
| **Tests** | `pytest tests/` — 52 tests |
| **GenAI tiles** | 12 monthly services + training (incl. AI Extract, AI Classify) |
| **Deps** | `requirements.lock` + `requirements-dev.lock` (pip-compile) |
| **Data refresh** | Fitment pass **2026-05-30**; full audit **2026-05-04** — see `docs/PRICING_FITMENT.md` |
| **Docs** | `STATUS_AND_COVERAGE.md` + `CALCULATION_COVERAGE.md` updated for Dash GenAI scope |

### Run locally

```bash
cd databricks-pricing-calculator
pip install -r requirements.txt
python app.py   # http://localhost:8000
```

### Git (repo root)

Recent history (newest first): `054f2dc` deps pin → `a65bb02` data audit → `5661ef3` model catalog → `5fcf79b` README/callback errors → `8469dd2` tile grid → `1baf5d0` UI theme → `5695595` Streamlit→Dash migration.

---

## Session log

_Newest first._

### 2026-05-30 — Cross-tab tile verification (automated)

**Done**
- Added `tests/test_all_tiles_callbacks.py`: all 12 GenAI tiles + training + ballpark total, Break-Even, Model Comparison, 4 scenario types, and Quick Estimate presets — each with Dash-like **string** numeric inputs.
- **52 tests** passing.

### 2026-05-30 — GenAI tile input coercion (Model Serving fix)

**Done**
- **Root cause**: Dash `dbc.Input(type="number")` often returns strings; comparisons like `"720" <= 0` raised `TypeError` and broke callbacks silently (especially Model Serving).
- Added `coerce_input()` / `tile_input_hint()` in `ui_helpers.py`; `_safe()` and `coerce_store_amount()` use coercion.
- All GenAI tile callbacks now coerce inputs and show hints instead of blank `None` results; Model Serving / Agent Bricks use explicit RadioItems `{label, value}`.
- Regression tests: `test_model_serving_tile.py`, `test_coerce_input_string_from_dash`.

**Next**
- Restart `python app.py` and spot-check tiles after deploy.

### 2026-05-30 — Backlog complete: Batch scenario + lockfiles

**Done**
- **Batch AI scenario**: optional AI Extract / AI Classify line items (`include_extract`, `include_classify`, workload keys); Dash form checkboxes; CLI `--extract` / `--classify`; Quick Estimate M/L presets updated.
- **`requirements.lock`** and **`requirements-dev.lock`** via `pip-compile`; README install/regenerate instructions.
- Tests: `test_batch_pipeline_*` in `test_scenarios.py`.

**Next**
- Optional: `system.billing.list_prices` import; scenario CSV export.

### 2026-05-30 — Backlog: AI Extract/Classify + retirement UI + docs

**Done**
- **AI Extract** and **AI Classify** GenAI tiles, `estimate_ai_extract` / `estimate_ai_classify`, shared 50% promo, ballpark stores, CLI commands.
- **`MODEL_RETIREMENT_NOTICES`**: Codex models (2026-07-16), Llama 3.1 405B; dropdown labels + `dbc.Alert` on proprietary, open FM, break-even.
- Updated `docs/REQUIREMENTS.md` (v1.1), `docs/DESIGN.md`, `CALCULATION_COVERAGE.md`, `STATUS_AND_COVERAGE.md`, `PRICING_FITMENT.md`.
- Tests: `test_ai_functions.py`, `test_retirement.py`; extended `test_ui_helpers.py`.

### 2026-05-30 — Pricing fitment research + Gemini catalog refresh

**Done**
- Added [PRICING_FITMENT.md](PRICING_FITMENT.md): canonical URLs, fitment matrix, 2026-05-30 diff table, refresh procedure, promo rules.
- Updated `pricing_data.py`: Gemini rate corrections; new models (3.5 Flash, 2.5 Flash Lite, Opus 4.8); `GEMINI_FM_PROMO_*`.
- `estimate_proprietary_foundation_model(..., apply_gemini_promo)` + Dash checkbox on proprietary tile.
- `scripts/pricing_fitment_check.py` for quick catalog/promo snapshot.
- Extended `PRICING_SOURCES.md` audit row; tests for Gemini 3.1 Flash Lite rates + promo.

### 2026-05-30 — UI fixes, tests, coverage docs

**Done**

- Fixed dropdown/calculation issues:
  - **AI Parse:** option `value` = complexity key (not short label); invalid selection shows warning.
  - **Proprietary FM:** tier `dbc.Select` + `resolve_proprietary_tier()` prevents stale tier after model change.
  - **Model Training:** `resolve_training_scale()` on calc.
  - **Cloud/Region:** keep region when still valid after cloud switch.
  - **Multi-agent:** `checklist_enabled()` for Vector Search (was `bool(list)`).
  - **Gateway:** clearer messages when payload required vs guardrails-only.
  - **Ballpark total:** `coerce_store_amount()` + **line items** list wired (`genai-line-items` callback).
- Added `ui_helpers.py`, `tests/` (15 pytest cases), `requirements-dev.txt`.
- Rewrote `STATUS_AND_COVERAGE.md` and `CALCULATION_COVERAGE.md` for Dash GenAI app.
- `PORT` env support in `app.run()`.

**Next**

- [ ] Manual smoke test in browser (all 5 tabs).
- [ ] Re-verify AI Parse promo before **2026-06-30**.
- [ ] Optional: `requirements.lock` for reproducible deploys.

---

### 2026-05-30 — Documentation pass

**Done**

- Added `docs/REQUIREMENTS.md`, `docs/DESIGN.md`, `docs/DEV_LOG.md`.
- Linked docs from `README.md`.

---

### 2026-05-04 — Pricing data audit (commit `a65bb02`, `5661ef3`)

**Done**

- Full pass on open + proprietary FM rates vs Azure Learn and pricing pages.
- Added models (e.g. Qwen 3 Next 80B, Qwen embedding, GPT 5.4/5.5 family); fixed retired/batch/tier issues.
- Documented changes in `PRICING_SOURCES.md`.

**Next**

- Schedule next refresh before AI Parse promo expiry (**2026-06-30**).

---

### 2026-05 (est.) — Dash migration + UI polish (`5695595` … `8469dd2`)

**Done**

- Replaced Streamlit with Dash (`app.py` UI-only).
- Frosted-glass CSS (`assets/style.css`).
- GenAI Calculator: expandable sections → **tile grid** (2-col + full-width proprietary/training).
- Callback errors surfaced as `dbc.Alert` (warning) instead of silent zeros.
- README updated for Dash / port 8000; removed `.streamlit` from active path.

**Next**

- Consider splitting `app.py` into `layout/` + `callbacks/` if file grows past ~1k lines.

---

### Earlier — Streamlit GenAI ballpark app

**Done**

- Initial GenAI per-service calculator + scenario templates + CLI.
- `pricing_data.py` consolidated rates from 29 pricing page references (broader than current UI).

**Superseded**

- Streamlit UI removed from `app.py`; `index.html` left as deprecated offline artifact.

---

## Decision log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05 | **Dash over Streamlit** | Finer layout control (tile grid, Bootstrap), callback-based partial updates, Databricks Apps fit |
| 2026-05 | **GenAI-only UI** | Focus SA demo on GenAI TCO; SQL/storage/compute remain CLI + `pricing_data` only |
| 2026-05 | **No runtime API to Databricks** | Offline estimates; avoids auth and keeps app portable |
| 2026-05 | **Scenarios use heuristics** | Pages don’t publish end-to-end RAG TCO formulas; transparency via line items |
| 2026-05 | **`app_keepalive.py` gitignored** | Workspace notebook ops; personal email / Apps API |
| 2026-05 | **Port 8000 hardcoded** | Matches Databricks Apps default documented in README |

---

## Backlog (living)

| ID | Task | Priority |
|----|------|----------|
| B-01 | Refresh `STATUS_AND_COVERAGE.md` + `CALCULATION_COVERAGE.md` | Done |
| B-02 | `tests/test_calculator.py`, `tests/test_scenarios.py` | Done |
| B-03 | `requirements.lock` or pip-tools lock | P1 |
| B-04 | README: dynamic model count or “see pricing_data” | P2 |
| B-05 | Scenario export CSV/JSON | P2 |
| B-06 | Optional `list_prices` workspace integration | P3 |
| B-07 | `PORT` env in `app.run()` | P3 |
| B-08 | Delete or regenerate `index.html` | P3 |

---

## Data refresh log

| Date | Scope | Notes |
|------|--------|-------|
| 2026-05-04 | Open FM, proprietary FM, tiers, batch | See `PRICING_SOURCES.md` |
| 2026-04-07 | Prior refresh | Baseline in `PRICING_SOURCES.md` |
| _Next_ | Before 2026-06-30 | AI Parse 50% promo ends; re-verify parse rates |

---

## Revision history (this document)

| Date | Change |
|------|--------|
| 2026-05-30 | Created dev log with current status and historical summary from git |
