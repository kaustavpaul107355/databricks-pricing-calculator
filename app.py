"""
Databricks GenAI TCO Estimator — Dash version.

All business logic lives in calculator.py, scenarios.py, presets.py, pricing_data.py.
This file is purely the UI layer.

Run: python app.py
"""

import datetime
import dash
from dash import dcc, html, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px

from pricing_data import (
    CLOUDS,
    REGIONS_BY_CLOUD,
    VECTOR_SEARCH_DBU_PER_HOUR,
    MODEL_SERVING_GPU_DBU_PER_HOUR,
    MODEL_TRAINING_DBU_ESTIMATES,
    AI_PARSE_DOCUMENT_TYPE_LABELS,
    AI_PARSE_DBU_PER_1K_PAGES,
    AGENT_EVALUATION_DBU,
    FOUNDATION_MODEL_DBU_PER_MILLION,
    PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION,
    MODEL_QUALITY_TIER,
    get_pricing_page_url,
    get_proprietary_model_rates,
    get_proprietary_model_tiers,
    get_all_models_with_pt,
)
from calculator import (
    estimate_vector_search, estimate_vector_search_reranker,
    estimate_model_serving_cpu, estimate_model_serving_gpu,
    estimate_foundation_model_tokens, estimate_proprietary_foundation_model,
    estimate_ai_parse, estimate_agent_evaluation, estimate_model_training,
    estimate_gateway_payload,
)
from scenarios import (
    calculate_pt_vs_ppt_breakeven,
    compare_models,
    estimate_rag_scenario,
    estimate_multi_agent_scenario,
    estimate_batch_pipeline_scenario,
    estimate_fine_tune_scenario,
    inference_model_names,
    embedding_model_names,
)

# ---------------------------------------------------------------------------
# Palette + constants
# ---------------------------------------------------------------------------
DB_RED = "#FF3621"
DB_ORANGE = "#FF6B35"
DB_TEAL = "#00A972"
DB_DARK = "#1B3A4B"
DB_PURPLE = "#7570B3"
DB_LIGHT = "#F8F9FB"
PIE_COLORS = [DB_RED, DB_TEAL, DB_ORANGE, DB_PURPLE, "#1B9E77", "#E6AB02", "#D95F02", "#66A61E"]

GENAI_PRICING_PAGES = [
    ("Agent Bricks", "agent-bricks"),
    ("AI Parse Document", "ai-parse"),
    ("Mosaic AI Gateway", "mosaic-ai-gateway"),
    ("Model Serving", "model-serving"),
    ("Foundation Model Serving", "foundation-model-serving"),
    ("Proprietary Foundation Model Serving", "proprietary-foundation-model-serving"),
    ("Vector Search", "vector-search"),
    ("Agent Evaluation", "agent-evaluation"),
    ("Model Training", "mosaic-foundation-model-training"),
    ("GenAI Pricing Calculator (official)", "genai-pricing-calculator"),
]

PROMO_ACTIVE = datetime.date.today() <= datetime.date.fromisoformat("2026-06-30")

# ---------------------------------------------------------------------------
# App init
# ---------------------------------------------------------------------------
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="Databricks GenAI TCO Estimator",
    suppress_callback_exceptions=True,
)
server = app.server

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def cost_badge(cost, label="monthly"):
    """Return a styled cost display."""
    return dbc.Alert(
        f"${cost:,.2f} / {label}" if cost > 0 else "No cost — adjust inputs above",
        color="success" if cost > 0 else "light",
        className="py-2 mb-0 mt-2",
    )

def none_opt(options):
    """Prepend a '— None —' option to a list."""
    return [{"label": "— None —", "value": "__none__"}] + [{"label": o, "value": o} for o in options]

def region_options(cloud):
    regions = REGIONS_BY_CLOUD.get(cloud, REGIONS_BY_CLOUD["AWS"])
    return [{"label": f"{label} (${price:.3f}/DBU)", "value": rid}
            for rid, (label, price) in regions.items()]

def _safe(val, default=0):
    """Coerce a possibly-None input to a number."""
    return val if val is not None else default

# ---------------------------------------------------------------------------
# Layout: cloud / region bar
# ---------------------------------------------------------------------------
cloud_region_bar = dbc.Card(dbc.CardBody(dbc.Row([
    dbc.Col([
        dbc.Label("Cloud", className="fw-bold small"),
        dbc.Select(id="cloud", options=[{"label": c, "value": c} for c in CLOUDS], value="AWS"),
    ], md=3),
    dbc.Col([
        dbc.Label("Region", className="fw-bold small"),
        dbc.Select(id="region", options=region_options("AWS"), value="us-east-1"),
    ], md=5),
], className="g-3")), className="mb-3 border-start border-4 border-danger")

# ---------------------------------------------------------------------------
# Layout: GenAI Calculator tab
# ---------------------------------------------------------------------------
def _section(title, link, children, item_id):
    caption = html.A(title.split("—")[0].strip() + " pricing", href=link, target="_blank",
                      className="text-decoration-none small text-muted")
    return dbc.AccordionItem([caption, html.Hr(className="my-2")] + children, title=title, item_id=item_id)

_open_models = [m for m, r in FOUNDATION_MODEL_DBU_PER_MILLION.items()
                if (r.get("input") or r.get("provisioned_per_hour")) and "deprecated" not in m.lower()]
_prop_models = list(PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION.keys())
_gpu_sizes = list(MODEL_SERVING_GPU_DBU_PER_HOUR.keys())
_train_models = list(MODEL_TRAINING_DBU_ESTIMATES.keys())
_parse_options = [{"label": lbl, "value": key} for lbl, key in AI_PARSE_DOCUMENT_TYPE_LABELS]
_eval_types = list(AGENT_EVALUATION_DBU.keys())

genai_tab = html.Div([
    html.H4("GenAI Calculator — Per-Service Estimate", className="mb-1"),
    html.P("Estimate monthly cost for a GenAI solution. Rates from Databricks pricing pages.",
           className="text-muted small mb-3"),
    dbc.Accordion([
        # 1. Vector Search
        _section("Vector Search — embeddings & similarity search",
                 "https://www.databricks.com/product/pricing/vector-search", [
            html.Small("Endpoint tier, number of endpoints, and expected running hours per month.", className="text-muted"),
            dbc.Row([
                dbc.Col([dbc.Label("Tier", className="small fw-semibold mt-2"), dbc.Select(id="vs-tier", options=[{"label": k, "value": k} for k in VECTOR_SEARCH_DBU_PER_HOUR], value="Standard")], md=4),
                dbc.Col([dbc.Label("Number of endpoints", className="small fw-semibold mt-2"), dbc.Input(id="vs-units", type="number", min=0, value=0, step=1, placeholder="e.g. 2")], md=4),
                dbc.Col([dbc.Label("Hours / month", className="small fw-semibold mt-2"), dbc.Input(id="vs-hours", type="number", min=0, value=720, step=72, placeholder="720 = 24×30")], md=4),
            ], className="g-2"),
            html.Div(id="vs-result"),
        ], "vs"),

        # 2. Reranker
        _section("Vector Search Reranker (optional)",
                 "https://www.databricks.com/product/pricing/vector-search", [
            html.Small("Re-ranks retrieved results for higher relevance. Enter expected monthly volume.", className="text-muted"),
            dbc.Label("Reranker requests (thousands / month)", className="small fw-semibold mt-2"),
            dbc.Input(id="reranker-1k", type="number", min=0, value=0, step=1, placeholder="e.g. 50"),
            html.Div(id="reranker-result"),
        ], "reranker"),

        # 3. Agent Bricks
        _section("Agent Bricks — build agents on your data",
                 "https://www.databricks.com/product/pricing/agent-bricks", [
            html.Small("Select agent type. CPU is typical for text-based agents; GPU for vision/multimodal workloads.", className="text-muted"),
            dbc.Label("What are you building?", className="small fw-semibold mt-2"),
            dbc.Select(id="ab-type", options=none_opt(["Knowledge Assistant", "Supervisor Agent"]), value="__none__"),
            dbc.Label("Compute mode", className="small fw-semibold mt-2"),
            dbc.RadioItems(id="ab-mode", options=["CPU (typical)", "GPU"], value="CPU (typical)", inline=True),
            dbc.Row([
                dbc.Col([dbc.Label("Request-hours / month", className="small fw-semibold mt-2"), dbc.Input(id="ab-cpu-req", type="number", min=0, value=0, step=72, placeholder="e.g. 720")], md=6, id="ab-cpu-wrap"),
                dbc.Col([
                    dbc.Label("GPU instance size", className="small fw-semibold mt-2"),
                    dbc.Select(id="ab-gpu-size", options=[{"label": s, "value": s} for s in _gpu_sizes], value="Small"),
                    dbc.Label("GPU hours / month", className="small fw-semibold mt-1"),
                    dbc.Input(id="ab-gpu-hrs", type="number", min=0, value=0, step=72, placeholder="e.g. 720"),
                ], md=6, id="ab-gpu-wrap"),
            ], className="g-2"),
            html.Div(id="ab-result"),
        ], "ab"),

        # 4. AI Gateway
        _section("Mosaic AI Gateway — guardrails, logging, usage tracking",
                 "https://www.databricks.com/product/pricing/mosaic-ai-gateway", [
            html.Small("Select features you plan to use. Guardrails cost is included in Model Serving; Inference Tables and Usage Tracking are billed on payload volume.", className="text-muted"),
            dbc.Label("Features", className="small fw-semibold mt-2"),
            dbc.Checklist(id="gw-features", options=[
                {"label": " AI Guardrails", "value": "guard"},
                {"label": " Inference Tables", "value": "inf"},
                {"label": " Usage Tracking", "value": "usage"},
            ], value=[], inline=True),
            dbc.Label("Total payload volume (GB / month)", className="small fw-semibold mt-2"),
            dbc.Input(id="gw-payload", type="number", min=0, value=0, step=0.5, placeholder="e.g. 10"),
            html.Div(id="gw-result"),
        ], "gw"),

        # 5. Model Serving
        _section("Model Serving — custom or third-party models",
                 "https://www.databricks.com/product/pricing/model-serving", [
            html.Small("For serving your own custom models or external models. Choose CPU for lightweight models, GPU for large/multimodal models.", className="text-muted"),
            dbc.Label("Compute mode", className="small fw-semibold mt-2"),
            dbc.RadioItems(id="serv-mode", options=["CPU", "GPU"], value="CPU", inline=True),
            dbc.Row([
                dbc.Col([dbc.Label("Request-hours / month", className="small fw-semibold mt-2"), dbc.Input(id="serv-cpu-req", type="number", min=0, value=0, step=72, placeholder="e.g. 720")], id="serv-cpu-wrap"),
                dbc.Col([
                    dbc.Label("GPU instance size", className="small fw-semibold mt-2"),
                    dbc.Select(id="serv-gpu-size", options=[{"label": s, "value": s} for s in _gpu_sizes], value="Small"),
                    dbc.Label("GPU hours / month", className="small fw-semibold mt-1"),
                    dbc.Input(id="serv-gpu-hrs", type="number", min=0, value=0, step=72, placeholder="e.g. 720"),
                ], id="serv-gpu-wrap"),
            ], className="g-2"),
            html.Div(id="serv-result"),
        ], "serv"),

        # 6. Foundation Model (open)
        _section("Foundation Model Serving — open models",
                 "https://www.databricks.com/product/pricing/foundation-model-serving", [
            html.Small("Open-source models (Llama, DBRX, etc.) served by Databricks. Enter monthly token volume or Provisioned Throughput (PT) hours.", className="text-muted"),
            dbc.Label("Model", className="small fw-semibold mt-2"),
            dbc.Select(id="fm-model", options=none_opt(_open_models), value="__none__"),
            dbc.Row([
                dbc.Col([dbc.Label("Input tokens (millions / month)", className="small fw-semibold mt-2"), dbc.Input(id="fm-in", type="number", min=0, value=0, step=0.5, placeholder="e.g. 10")], md=4),
                dbc.Col([dbc.Label("Output tokens (millions / month)", className="small fw-semibold mt-2"), dbc.Input(id="fm-out", type="number", min=0, value=0, step=0.5, placeholder="e.g. 2")], md=4),
                dbc.Col([dbc.Label("PT hours / month", className="small fw-semibold mt-2"), dbc.Input(id="fm-pt", type="number", min=0, value=0, step=24, placeholder="e.g. 720")], md=4),
            ], className="g-2"),
            html.Div(id="fm-result"),
        ], "fm"),

        # 7. Proprietary Foundation Model
        _section("Proprietary Foundation Model — OpenAI, Anthropic, Google",
                 "https://www.databricks.com/product/pricing/proprietary-foundation-model-serving", [
            html.Small("Third-party models (GPT-4o, Claude, Gemini) via Databricks. Cache & Batch fields are optional discounts.", className="text-muted"),
            dbc.Label("Model", className="small fw-semibold mt-2"),
            dbc.Select(id="prop-model", options=none_opt(_prop_models), value="__none__"),
            dbc.Label("Pricing tier", className="small fw-semibold mt-2"),
            dbc.RadioItems(id="prop-tier", options=[], value=None, inline=True),
            dbc.Row([
                dbc.Col([dbc.Label("Input tokens (M / mo)", className="small fw-semibold mt-2"), dbc.Input(id="prop-in", type="number", min=0, value=0, step=0.5, placeholder="e.g. 10")], md=3),
                dbc.Col([dbc.Label("Output tokens (M / mo)", className="small fw-semibold mt-2"), dbc.Input(id="prop-out", type="number", min=0, value=0, step=0.5, placeholder="e.g. 2")], md=3),
                dbc.Col([dbc.Label("Cache write (M)", className="small fw-semibold mt-2"), dbc.Input(id="prop-cw", type="number", min=0, value=0, step=0.5, placeholder="0")], md=2),
                dbc.Col([dbc.Label("Cache read (M)", className="small fw-semibold mt-2"), dbc.Input(id="prop-cr", type="number", min=0, value=0, step=0.5, placeholder="0")], md=2),
                dbc.Col([dbc.Label("Batch hours", className="small fw-semibold mt-2"), dbc.Input(id="prop-batch", type="number", min=0, value=0, step=1, placeholder="0")], md=2),
            ], className="g-2"),
            html.Div(id="prop-result"),
        ], "prop"),

        # 8. AI Parse
        _section("AI Parse Document — turn PDFs into structured data",
                 "https://www.databricks.com/product/pricing/ai-parse", [
            html.Small("Convert PDFs, images, and scanned documents into structured data. Pick complexity, then enter page volume.", className="text-muted"),
            html.Small(" 50% promo through June 30, 2026", className="text-success fw-bold") if PROMO_ACTIVE else None,
            dbc.Label("Document type / complexity", className="small fw-semibold mt-2"),
            dbc.Select(id="parse-type", options=none_opt([lbl for lbl, _ in AI_PARSE_DOCUMENT_TYPE_LABELS]),
                       value="__none__"),
            dbc.Row([
                dbc.Col([dbc.Label("Pages (thousands / month)", className="small fw-semibold mt-2"), dbc.Input(id="parse-pages", type="number", min=0, value=0, step=0.5, placeholder="e.g. 100")], md=8),
                dbc.Col(dbc.Checklist(id="parse-promo", options=[{"label": " 50% promo", "value": "yes"}],
                                      value=["yes"] if PROMO_ACTIVE else [], className="mt-4",
                                      style={"display": "block" if PROMO_ACTIVE else "none"}), md=4),
            ], className="g-2"),
            html.Div(id="parse-result"),
        ], "parse"),

        # 9. Agent Evaluation
        _section("Agent Evaluation — LLM Judge, Synthetic Data",
                 "https://www.databricks.com/product/pricing/agent-evaluation", [
            html.Small("LLM-as-a-Judge evaluation and synthetic data generation for testing your agents.", className="text-muted"),
            dbc.Label("Evaluation type", className="small fw-semibold mt-2"),
            dbc.Select(id="eval-type", options=none_opt(_eval_types), value="__none__"),
            dbc.Row([
                dbc.Col([dbc.Label("Input tokens (M / mo)", className="small fw-semibold mt-2"), dbc.Input(id="eval-in", type="number", min=0, value=0, step=0.5, placeholder="e.g. 1")], md=4),
                dbc.Col([dbc.Label("Output tokens (M / mo)", className="small fw-semibold mt-2"), dbc.Input(id="eval-out", type="number", min=0, value=0, step=0.5, placeholder="e.g. 0.5")], md=4),
                dbc.Col([dbc.Label("Questions per eval run", className="small fw-semibold mt-2"), dbc.Input(id="eval-q", type="number", min=0, value=0, step=10, placeholder="e.g. 100")], md=4),
            ], className="g-2"),
            html.Div(id="eval-result"),
        ], "eval"),

        # 10. Model Training
        _section("Model Training — fine-tuning (one-time)",
                 "https://www.databricks.com/product/pricing/mosaic-foundation-model-training", [
            html.Small("One-time fine-tuning cost. Select the base model and training scale (data size).", className="text-muted"),
            dbc.Row([
                dbc.Col([dbc.Label("Base model", className="small fw-semibold mt-2"), dbc.Select(id="train-model", options=none_opt(_train_models), value="__none__")], md=6),
                dbc.Col([dbc.Label("Training scale", className="small fw-semibold mt-2"), dbc.Select(id="train-scale", options=[], value=None)], md=6),
            ], className="g-2"),
            html.Div(id="train-result", className="mt-2"),
        ], "train"),
    ], always_open=True, active_item=["vs", "ab", "fm", "prop", "parse"], className="mb-3"),

    # Stores for per-section costs
    *[dcc.Store(id=f"store-{s}", data=0) for s in
      ["vs", "reranker", "ab", "gw", "serv", "fm", "prop", "parse", "eval"]],
    dcc.Store(id="store-train", data=0),

    # Total summary
    dbc.Card(dbc.CardBody([
        html.H5("Ballpark Total", className="mb-2"),
        html.Div(id="genai-total"),
        html.Div(id="genai-training-total"),
        html.Div(id="genai-line-items"),
    ]), className="border-start border-4 border-success"),
])

# ---------------------------------------------------------------------------
# Layout: Break-Even tab
# ---------------------------------------------------------------------------
_pt_models = get_all_models_with_pt()
breakeven_tab = html.Div([
    html.H4("PT vs PPT Break-Even Calculator", className="mb-1"),
    html.P("Find where Provisioned Throughput becomes cheaper than Pay-Per-Token.", className="text-muted small mb-3"),
    dbc.Row([
        dbc.Col([
            dbc.Label("Model"), dbc.Select(id="be-model", options=[{"label": m, "value": m} for m in _pt_models], value=_pt_models[0] if _pt_models else None),
            dbc.Label("Avg input tokens/query", className="mt-2"), dbc.Input(id="be-input", type="number", min=100, value=2000, step=500),
            dbc.Label("Queries per minute", className="mt-2"), dbc.Input(id="be-qpm", type="number", min=0.1, value=5, step=0.5),
        ], md=4),
        dbc.Col([
            html.Div(style={"height": "0"}),  # spacer for alignment
            dbc.Label("Avg output tokens/query", className="mt-4"), dbc.Input(id="be-output", type="number", min=50, value=500, step=100),
            dbc.Label("Uptime hours/day", className="mt-2"), dbc.Input(id="be-uptime", type="number", min=1, max=24, value=12, step=1),
        ], md=4),
        dbc.Col(id="be-metrics", md=4),
    ], className="g-3"),
    html.Div(id="be-chart", className="mt-3"),
])

# ---------------------------------------------------------------------------
# Layout: Model Comparison tab
# ---------------------------------------------------------------------------
_all_inf_models = inference_model_names()
comparison_tab = html.Div([
    html.H4("Model Cost Comparison", className="mb-1"),
    html.P("Compare monthly token costs across 2-3 models for the same traffic.", className="text-muted small mb-3"),
    dbc.Label("Select 2-3 models"),
    dcc.Dropdown(id="mc-models", options=[{"label": m, "value": m} for m in _all_inf_models],
                 multi=True, placeholder="Pick 2-3 models..."),
    dbc.Row([
        dbc.Col([dbc.Label("Input tokens (M/month)", className="mt-2"),
                 dbc.Input(id="mc-input", type="number", min=0.1, value=10, step=1)], md=6),
        dbc.Col([dbc.Label("Output tokens (M/month)", className="mt-2"),
                 dbc.Input(id="mc-output", type="number", min=0.1, value=2, step=0.5)], md=6),
    ], className="g-3"),
    html.Div(id="mc-result", className="mt-3"),
])

# ---------------------------------------------------------------------------
# Layout: Scenario Templates tab
# ---------------------------------------------------------------------------
_scenario_types = ["RAG Application", "Multi-Agent System", "Batch AI Pipeline", "Fine-Tuned Model"]
_emb_models = embedding_model_names()
_inf_models_list = inference_model_names()

scenarios_tab = html.Div([
    html.H4("Scenario Templates", className="mb-1"),
    html.P("Estimate total monthly cost for common GenAI architectures.", className="text-muted small mb-3"),
    dbc.Select(id="scn-type", options=[{"label": s, "value": s} for s in _scenario_types], value="RAG Application"),

    # RAG form
    html.Div(id="scn-rag-form", children=[
        dbc.Row([
            dbc.Col([
                dbc.Label("Documents"), dbc.Input(id="scn-rag-docs", type="number", min=100, value=10000, step=1000),
                dbc.Label("Avg pages/doc", className="mt-2"), dbc.Input(id="scn-rag-pages", type="number", min=1, value=5),
                dbc.Label("Avg chunks/doc", className="mt-2"), dbc.Input(id="scn-rag-chunks", type="number", min=1, value=20),
                dbc.Label("Queries/day", className="mt-2"), dbc.Input(id="scn-rag-qday", type="number", min=1, value=500, step=100),
            ], md=6),
            dbc.Col([
                dbc.Label("Embedding model"), dbc.Select(id="scn-rag-emb", options=[{"label": m, "value": m} for m in _emb_models], value=_emb_models[0] if _emb_models else None),
                dbc.Label("LLM model", className="mt-2"), dbc.Select(id="scn-rag-llm", options=[{"label": m, "value": m} for m in _inf_models_list], value=_inf_models_list[0] if _inf_models_list else None),
                dbc.Label("Document complexity", className="mt-2"), dbc.Select(id="scn-rag-cx", options=[{"label": k, "value": k} for k in AI_PARSE_DBU_PER_1K_PAGES], value=list(AI_PARSE_DBU_PER_1K_PAGES.keys())[2]),
                dbc.Label("Refresh freq (times/mo)", className="mt-2"), dbc.Input(id="scn-rag-refresh", type="number", min=1, value=1),
            ], md=6),
        ], className="g-3 mt-2"),
    ]),

    # Multi-Agent form
    html.Div(id="scn-ma-form", style={"display": "none"}, children=[
        dbc.Row([
            dbc.Col([
                dbc.Label("Requests/day"), dbc.Input(id="scn-ma-req", type="number", min=10, value=500, step=100),
                dbc.Label("Avg steps/request", className="mt-2"), dbc.Input(id="scn-ma-steps", type="number", min=1, value=5),
                dbc.Label("Tools per step", className="mt-2"), dbc.Input(id="scn-ma-tools", type="number", min=1, value=2),
            ], md=6),
            dbc.Col([
                dbc.Label("Orchestrator model"), dbc.Select(id="scn-ma-orch", options=[{"label": m, "value": m} for m in _inf_models_list], value=_inf_models_list[0] if _inf_models_list else None),
                dbc.Label("Worker model", className="mt-2"), dbc.Select(id="scn-ma-worker", options=[{"label": m, "value": m} for m in _inf_models_list], value=_inf_models_list[1] if len(_inf_models_list) > 1 else None),
                dbc.Checklist(id="scn-ma-vs", options=[{"label": " Include Vector Search", "value": "yes"}], value=["yes"], className="mt-3"),
            ], md=6),
        ], className="g-3 mt-2"),
    ]),

    # Batch form
    html.Div(id="scn-batch-form", style={"display": "none"}, children=[
        dbc.Row([
            dbc.Col([
                dbc.Label("Documents per batch"), dbc.Input(id="scn-batch-docs", type="number", min=100, value=10000, step=1000),
                dbc.Label("Pages per doc", className="mt-2"), dbc.Input(id="scn-batch-pages", type="number", min=1, value=5),
            ], md=6),
            dbc.Col([
                dbc.Label("Complexity"), dbc.Select(id="scn-batch-cx", options=[{"label": k, "value": k} for k in AI_PARSE_DBU_PER_1K_PAGES], value=list(AI_PARSE_DBU_PER_1K_PAGES.keys())[2]),
                dbc.Label("Runs per month", className="mt-2"), dbc.Input(id="scn-batch-freq", type="number", min=1, value=4),
                dbc.Label("Output model", className="mt-2"), dbc.Select(id="scn-batch-model", options=[{"label": m, "value": m} for m in _inf_models_list], value=_inf_models_list[0] if _inf_models_list else None),
            ], md=6),
        ], className="g-3 mt-2"),
    ]),

    # Fine-Tune form
    html.Div(id="scn-ft-form", style={"display": "none"}, children=[
        dbc.Row([
            dbc.Col([
                dbc.Label("Base model"), dbc.Select(id="scn-ft-model", options=[{"label": m, "value": m} for m in _train_models], value=_train_models[0] if _train_models else None),
                dbc.Label("Training scale", className="mt-2"), dbc.Select(id="scn-ft-scale", options=[], value=None),
            ], md=6),
            dbc.Col([
                dbc.Label("Serving hours/day"), dbc.Input(id="scn-ft-hrs", type="number", min=1, max=24, value=12),
                dbc.Label("Retraining cadence (months)", className="mt-2"), dbc.Input(id="scn-ft-retrain", type="number", min=1, value=3),
                dbc.Label("Eval runs/month", className="mt-2"), dbc.Input(id="scn-ft-eval-freq", type="number", min=0, value=2),
                dbc.Label("Questions per eval", className="mt-2"), dbc.Input(id="scn-ft-eval-q", type="number", min=0, value=100),
            ], md=6),
        ], className="g-3 mt-2"),
    ]),

    html.Div(id="scn-result", className="mt-3"),
])

# ---------------------------------------------------------------------------
# Layout: Quick Estimate tab
# ---------------------------------------------------------------------------
from presets import SCENARIO_PRESETS

quick_tab = html.Div([
    html.H4("Quick Estimate", className="mb-1"),
    html.P("Ballpark TCO in seconds with T-shirt sizing presets.", className="text-muted small mb-3"),
    dbc.RadioItems(id="qe-type", options=[{"label": k, "value": k} for k in SCENARIO_PRESETS], value="RAG", inline=True, className="mb-2"),
    dbc.RadioItems(id="qe-size", options=[], value=None, inline=True, className="mb-3"),
    html.Div(id="qe-result"),
])

# ---------------------------------------------------------------------------
# Layout: Sidebar
# ---------------------------------------------------------------------------
sidebar_links = [html.Li(html.A(label, href=get_pricing_page_url(path), target="_blank",
                                className="text-decoration-none"))
                 for label, path in GENAI_PRICING_PAGES]
sidebar = dbc.Card(dbc.CardBody([
    html.H6("Pricing Sources", className="fw-bold mb-2"),
    html.Ul(sidebar_links, className="list-unstyled small"),
]), className="bg-dark text-light")

# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------
app.layout = html.Div([
    # Navbar
    dbc.Navbar(dbc.Container([
        html.Span("Databricks GenAI TCO Estimator", className="navbar-brand mb-0 h1 text-white"),
        html.Small("Estimate only — use system.billing.list_prices for actuals",
                   className="text-white-50"),
    ], fluid=True), color=DB_RED, dark=True, className="mb-3"),

    dbc.Container([
        dbc.Row([
            # Main content
            dbc.Col([
                cloud_region_bar,
                dbc.Tabs([
                    dbc.Tab(genai_tab, label="GenAI Calculator", tab_id="tab-genai",
                            active_label_class_name="fw-bold", className="pt-3"),
                    dbc.Tab(breakeven_tab, label="PT vs PPT Break-Even", tab_id="tab-be",
                            active_label_class_name="fw-bold", className="pt-3"),
                    dbc.Tab(comparison_tab, label="Model Comparison", tab_id="tab-mc",
                            active_label_class_name="fw-bold", className="pt-3"),
                    dbc.Tab(scenarios_tab, label="Scenario Templates", tab_id="tab-scn",
                            active_label_class_name="fw-bold", className="pt-3"),
                    dbc.Tab(quick_tab, label="Quick Estimate", tab_id="tab-qe",
                            active_label_class_name="fw-bold", className="pt-3"),
                ], active_tab="tab-genai"),
            ], md=9),
            # Sidebar
            dbc.Col(sidebar, md=3),
        ]),
    ], fluid=True),
], style={"backgroundColor": DB_LIGHT, "minHeight": "100vh"})

# ===================================================================
# CALLBACKS
# ===================================================================

# --- Region dropdown update ---
@callback(Output("region", "options"), Output("region", "value"),
          Input("cloud", "value"))
def update_regions(cloud):
    opts = region_options(cloud)
    return opts, opts[0]["value"] if opts else None

# --- GenAI: per-section callbacks ---
# Each returns (result_div_children, store_data)

@callback(Output("vs-result", "children"), Output("store-vs", "data"),
          Input("vs-tier", "value"), Input("vs-units", "value"), Input("vs-hours", "value"),
          Input("cloud", "value"), Input("region", "value"))
def calc_vs(tier, units, hours, cloud, region):
    units, hours = _safe(units), _safe(hours)
    if units <= 0 or hours <= 0:
        return None, 0
    try:
        r = estimate_vector_search(tier, int(units), hours, cloud=cloud, region=region)
        return cost_badge(r.cost_usd), r.cost_usd
    except Exception:
        return None, 0

@callback(Output("reranker-result", "children"), Output("store-reranker", "data"),
          Input("reranker-1k", "value"), Input("cloud", "value"), Input("region", "value"))
def calc_reranker(req_1k, cloud, region):
    req_1k = _safe(req_1k)
    if req_1k <= 0:
        return None, 0
    r = estimate_vector_search_reranker(req_1k, cloud=cloud, region=region)
    return cost_badge(r.cost_usd), r.cost_usd

@callback(Output("ab-result", "children"), Output("store-ab", "data"),
          Output("ab-cpu-wrap", "style"), Output("ab-gpu-wrap", "style"),
          Input("ab-type", "value"), Input("ab-mode", "value"),
          Input("ab-cpu-req", "value"), Input("ab-gpu-size", "value"), Input("ab-gpu-hrs", "value"),
          Input("cloud", "value"), Input("region", "value"))
def calc_ab(ab_type, mode, cpu_req, gpu_size, gpu_hrs, cloud, region):
    cpu_show = {"display": "block"} if mode == "CPU (typical)" else {"display": "none"}
    gpu_show = {"display": "block"} if mode == "GPU" else {"display": "none"}
    if ab_type == "__none__":
        return None, 0, cpu_show, gpu_show
    if mode == "CPU (typical)":
        cpu_req = _safe(cpu_req)
        if cpu_req <= 0:
            return None, 0, cpu_show, gpu_show
        r = estimate_model_serving_cpu(cpu_req, cloud=cloud, region=region)
    else:
        gpu_hrs = _safe(gpu_hrs)
        if gpu_hrs <= 0:
            return None, 0, cpu_show, gpu_show
        r = estimate_model_serving_gpu(gpu_size, gpu_hrs, cloud=cloud, region=region)
    return cost_badge(r.cost_usd), r.cost_usd, cpu_show, gpu_show

@callback(Output("gw-result", "children"), Output("store-gw", "data"),
          Input("gw-features", "value"), Input("gw-payload", "value"),
          Input("cloud", "value"), Input("region", "value"))
def calc_gw(features, payload, cloud, region):
    payload = _safe(payload)
    if not features or payload <= 0:
        if features and "guard" in features and not ("inf" in features or "usage" in features):
            return dbc.Alert("Guardrails cost is part of Model Serving / Agent Bricks.", color="info", className="py-2 mt-2"), 0
        return None, 0
    r = estimate_gateway_payload(payload, cloud=cloud, region=region)
    return cost_badge(r.cost_usd), r.cost_usd

@callback(Output("serv-result", "children"), Output("store-serv", "data"),
          Output("serv-cpu-wrap", "style"), Output("serv-gpu-wrap", "style"),
          Input("serv-mode", "value"), Input("serv-cpu-req", "value"),
          Input("serv-gpu-size", "value"), Input("serv-gpu-hrs", "value"),
          Input("cloud", "value"), Input("region", "value"))
def calc_serv(mode, cpu_req, gpu_size, gpu_hrs, cloud, region):
    cpu_show = {"display": "block"} if mode == "CPU" else {"display": "none"}
    gpu_show = {"display": "block"} if mode == "GPU" else {"display": "none"}
    if mode == "CPU":
        cpu_req = _safe(cpu_req)
        if cpu_req <= 0:
            return None, 0, cpu_show, gpu_show
        r = estimate_model_serving_cpu(cpu_req, cloud=cloud, region=region)
    else:
        gpu_hrs = _safe(gpu_hrs)
        if gpu_hrs <= 0:
            return None, 0, cpu_show, gpu_show
        r = estimate_model_serving_gpu(gpu_size, gpu_hrs, cloud=cloud, region=region)
    return cost_badge(r.cost_usd), r.cost_usd, cpu_show, gpu_show

@callback(Output("fm-result", "children"), Output("store-fm", "data"),
          Input("fm-model", "value"), Input("fm-in", "value"), Input("fm-out", "value"), Input("fm-pt", "value"),
          Input("cloud", "value"), Input("region", "value"))
def calc_fm(model, fm_in, fm_out, fm_pt, cloud, region):
    if model == "__none__":
        return None, 0
    fm_in, fm_out, fm_pt = _safe(fm_in), _safe(fm_out), _safe(fm_pt)
    if fm_in <= 0 and fm_out <= 0 and fm_pt <= 0:
        return None, 0
    try:
        r = estimate_foundation_model_tokens(model, input_millions=fm_in, output_millions=fm_out, provisioned_hours=fm_pt, cloud=cloud, region=region)
        return cost_badge(r.cost_usd), r.cost_usd
    except Exception:
        return None, 0

# Proprietary FM: update tier options when model changes
@callback(Output("prop-tier", "options"), Output("prop-tier", "value"),
          Input("prop-model", "value"))
def update_prop_tiers(model):
    if model == "__none__":
        return [], None
    tiers = get_proprietary_model_tiers(model)
    labels = {"global": "Global", "in_geo": "In-Geo (~10%)", "long_context": "Long Context", "in_geo_long_context": "In-Geo + Long"}
    opts = [{"label": labels.get(t, t), "value": t} for t in tiers]
    return opts, tiers[0] if tiers else None

@callback(Output("prop-result", "children"), Output("store-prop", "data"),
          Input("prop-model", "value"), Input("prop-tier", "value"),
          Input("prop-in", "value"), Input("prop-out", "value"),
          Input("prop-cw", "value"), Input("prop-cr", "value"), Input("prop-batch", "value"),
          Input("cloud", "value"), Input("region", "value"))
def calc_prop(model, tier, p_in, p_out, cw, cr, batch, cloud, region):
    if model == "__none__" or not tier:
        return None, 0
    p_in, p_out, cw, cr, batch = _safe(p_in), _safe(p_out), _safe(cw), _safe(cr), _safe(batch)
    if p_in <= 0 and p_out <= 0 and cw <= 0 and cr <= 0 and batch <= 0:
        return None, 0
    try:
        r = estimate_proprietary_foundation_model(model, input_millions=p_in, output_millions=p_out,
                                                   tier=tier, cache_write_millions=cw, cache_read_millions=cr,
                                                   batch_hours=batch, cloud=cloud, region=region)
        return cost_badge(r.cost_usd), r.cost_usd
    except Exception:
        return None, 0

@callback(Output("parse-result", "children"), Output("store-parse", "data"),
          Input("parse-type", "value"), Input("parse-pages", "value"), Input("parse-promo", "value"),
          Input("cloud", "value"), Input("region", "value"))
def calc_parse(doc_type, pages, promo, cloud, region):
    if doc_type == "__none__":
        return None, 0
    pages = _safe(pages)
    if pages <= 0:
        return None, 0
    complexity_key = next((k for lbl, k in AI_PARSE_DOCUMENT_TYPE_LABELS if lbl == doc_type), None)
    if not complexity_key:
        return None, 0
    apply_promo = "yes" in (promo or [])
    r = estimate_ai_parse(pages, complexity_key, cloud=cloud, region=region, apply_promo=apply_promo)
    return cost_badge(r.cost_usd), r.cost_usd

@callback(Output("eval-result", "children"), Output("store-eval", "data"),
          Input("eval-type", "value"), Input("eval-in", "value"), Input("eval-out", "value"), Input("eval-q", "value"),
          Input("cloud", "value"), Input("region", "value"))
def calc_eval(eval_type, e_in, e_out, e_q, cloud, region):
    if eval_type == "__none__":
        return None, 0
    e_in, e_out, e_q = _safe(e_in), _safe(e_out), _safe(e_q)
    if e_in <= 0 and e_out <= 0 and e_q <= 0:
        return None, 0
    try:
        r = estimate_agent_evaluation(eval_type, input_millions=e_in, output_millions=e_out, questions=e_q, cloud=cloud, region=region)
        return cost_badge(r.cost_usd), r.cost_usd
    except Exception:
        return None, 0

# Training: update scale options when model changes
@callback(Output("train-scale", "options"), Output("train-scale", "value"),
          Input("train-model", "value"))
def update_train_scales(model):
    if model == "__none__":
        return [], None
    scales = list(MODEL_TRAINING_DBU_ESTIMATES.get(model, {}).keys())
    opts = [{"label": s, "value": s} for s in scales]
    return opts, scales[0] if scales else None

@callback(Output("train-result", "children"), Output("store-train", "data"),
          Input("train-model", "value"), Input("train-scale", "value"),
          Input("cloud", "value"), Input("region", "value"))
def calc_train(model, scale, cloud, region):
    if model == "__none__" or not scale:
        return None, 0
    try:
        r = estimate_model_training(model, scale, cloud=cloud, region=region)
        return dbc.Alert(f"One-time training: ${r.cost_usd:,.2f}", color="info", className="py-2"), r.cost_usd
    except Exception:
        return None, 0

# --- GenAI: total summary ---
@callback(Output("genai-total", "children"), Output("genai-training-total", "children"),
          *[Input(f"store-{s}", "data") for s in ["vs", "reranker", "ab", "gw", "serv", "fm", "prop", "parse", "eval"]],
          Input("store-train", "data"))
def genai_total(vs, reranker, ab, gw, serv, fm, prop, parse_cost, eval_cost, train):
    monthly = sum(c for c in [vs, reranker, ab, gw, serv, fm, prop, parse_cost, eval_cost] if c)
    monthly_el = html.Div([
        html.Span("Estimated monthly: ", className="fw-bold"),
        html.Span(f"${monthly:,.2f}", className="fs-4 fw-bold", style={"color": DB_TEAL}),
    ])
    train_el = html.Div([
        html.Span("One-time training: ", className="fw-bold"),
        html.Span(f"${train:,.2f}", style={"color": DB_DARK}),
    ]) if train > 0 else None
    return monthly_el, train_el

# --- Break-Even ---
@callback(Output("be-metrics", "children"), Output("be-chart", "children"),
          Input("be-model", "value"), Input("be-input", "value"), Input("be-output", "value"),
          Input("be-qpm", "value"), Input("be-uptime", "value"),
          Input("cloud", "value"), Input("region", "value"))
def calc_breakeven(model, avg_in, avg_out, qpm, uptime, cloud, region):
    if not model:
        return None, None
    avg_in, avg_out, qpm, uptime = _safe(avg_in, 2000), _safe(avg_out, 500), _safe(qpm, 5), _safe(uptime, 12)
    try:
        r = calculate_pt_vs_ppt_breakeven(model, int(avg_in), int(avg_out), qpm, uptime, cloud, region)
    except ValueError as e:
        return dbc.Alert(str(e), color="danger"), None

    cheaper = "PPT is cheaper" if r.cheaper_mode == "PPT" else "PT is cheaper"
    savings = abs(r.ppt_monthly - r.pt_monthly)
    metrics = html.Div([
        dbc.Card(dbc.CardBody([html.Small("Pay-Per-Token"), html.H5(f"${r.ppt_monthly:,.2f}/mo")]), className="mb-2"),
        dbc.Card(dbc.CardBody([html.Small("Provisioned Throughput"), html.H5(f"${r.pt_monthly:,.2f}/mo")]), className="mb-2"),
        dbc.Card(dbc.CardBody([html.Small("Break-even at"), html.H5(f"{r.break_even_qpm:.1f} QPM")]), className="mb-2"),
        dbc.Alert(f"At {qpm} QPM: {cheaper} — saving ${savings:,.2f}/mo", color="info"),
    ])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[d["qpm"] for d in r.data_points], y=[d["ppt_cost"] for d in r.data_points],
                              name="Pay-Per-Token", line=dict(color=DB_RED, width=3)))
    fig.add_trace(go.Scatter(x=[d["qpm"] for d in r.data_points], y=[d["pt_cost"] for d in r.data_points],
                              name="Provisioned Throughput", line=dict(color=DB_TEAL, width=3, dash="dash")))
    if r.break_even_qpm < float("inf"):
        fig.add_vline(x=r.break_even_qpm, line_dash="dot", line_color="gray",
                       annotation_text=f"Break-even: {r.break_even_qpm:.1f} QPM")
    fig.update_layout(title=f"Monthly Cost: PPT vs PT — {model}", xaxis_title="Queries per minute",
                       yaxis_title="Monthly cost ($)", height=450, template="plotly_white")
    return metrics, dcc.Graph(figure=fig)

# --- Model Comparison ---
@callback(Output("mc-result", "children"),
          Input("mc-models", "value"), Input("mc-input", "value"), Input("mc-output", "value"),
          Input("cloud", "value"), Input("region", "value"))
def calc_comparison(models, input_m, output_m, cloud, region):
    if not models or len(models) < 2:
        return dbc.Alert("Select at least 2 models to compare.", color="light")
    input_m, output_m = _safe(input_m, 10), _safe(output_m, 2)
    try:
        r = compare_models(models[:3], input_m, output_m, cloud, region)
    except ValueError as e:
        return dbc.Alert(str(e), color="danger")

    colors = [DB_RED, DB_TEAL, DB_PURPLE]
    fig = go.Figure(data=[go.Bar(x=r.models, y=r.costs, marker_color=colors[:len(r.models)],
                                  text=[f"${c:,.2f}" for c in r.costs], textposition="auto")])
    fig.update_layout(title="Monthly Cost Comparison", yaxis_title="Monthly cost ($)", height=400, template="plotly_white")

    cheapest = r.models[r.costs.index(min(r.costs))]
    most_exp = r.models[r.costs.index(max(r.costs))]
    pct = (1 - min(r.costs) / max(r.costs)) * 100 if max(r.costs) > 0 else 0

    details = []
    for model, detail in zip(r.models, r.details):
        tier = MODEL_QUALITY_TIER.get(model, "")
        details.append(html.Li(f"{model} ({tier}): ${detail.cost_usd:,.2f}/mo — {detail.details}"))

    return html.Div([
        dcc.Graph(figure=fig),
        dbc.Alert(f"{cheapest} is {pct:.0f}% cheaper than {most_exp} for this traffic.", color="success"),
        html.Ul(details, className="small"),
    ])

# --- Scenario Templates ---
@callback(Output("scn-rag-form", "style"), Output("scn-ma-form", "style"),
          Output("scn-batch-form", "style"), Output("scn-ft-form", "style"),
          Input("scn-type", "value"))
def toggle_scenario_forms(scn):
    show = {"display": "block"}
    hide = {"display": "none"}
    return (show if scn == "RAG Application" else hide,
            show if scn == "Multi-Agent System" else hide,
            show if scn == "Batch AI Pipeline" else hide,
            show if scn == "Fine-Tuned Model" else hide)

# Fine-tune scale options
@callback(Output("scn-ft-scale", "options"), Output("scn-ft-scale", "value"),
          Input("scn-ft-model", "value"))
def update_ft_scales(model):
    if not model:
        return [], None
    scales = list(MODEL_TRAINING_DBU_ESTIMATES.get(model, {}).keys())
    return [{"label": s, "value": s} for s in scales], scales[0] if scales else None

@callback(Output("scn-result", "children"),
          Input("scn-type", "value"),
          # RAG inputs
          Input("scn-rag-docs", "value"), Input("scn-rag-pages", "value"),
          Input("scn-rag-chunks", "value"), Input("scn-rag-qday", "value"),
          Input("scn-rag-emb", "value"), Input("scn-rag-llm", "value"),
          Input("scn-rag-cx", "value"), Input("scn-rag-refresh", "value"),
          # Multi-Agent inputs
          Input("scn-ma-req", "value"), Input("scn-ma-steps", "value"),
          Input("scn-ma-tools", "value"), Input("scn-ma-orch", "value"),
          Input("scn-ma-worker", "value"), Input("scn-ma-vs", "value"),
          # Batch inputs
          Input("scn-batch-docs", "value"), Input("scn-batch-pages", "value"),
          Input("scn-batch-cx", "value"), Input("scn-batch-freq", "value"),
          Input("scn-batch-model", "value"),
          # Fine-tune inputs
          Input("scn-ft-model", "value"), Input("scn-ft-scale", "value"),
          Input("scn-ft-hrs", "value"), Input("scn-ft-retrain", "value"),
          Input("scn-ft-eval-freq", "value"), Input("scn-ft-eval-q", "value"),
          # Global
          Input("cloud", "value"), Input("region", "value"))
def calc_scenario(scn, rag_docs, rag_pages, rag_chunks, rag_qday, rag_emb, rag_llm, rag_cx, rag_refresh,
                  ma_req, ma_steps, ma_tools, ma_orch, ma_worker, ma_vs,
                  batch_docs, batch_pages, batch_cx, batch_freq, batch_model,
                  ft_model, ft_scale, ft_hrs, ft_retrain, ft_eval_freq, ft_eval_q,
                  cloud, region):
    try:
        if scn == "RAG Application":
            result = estimate_rag_scenario(
                int(_safe(rag_docs, 10000)), _safe(rag_pages, 5), _safe(rag_chunks, 20),
                int(_safe(rag_qday, 500)), rag_emb, rag_llm, rag_cx,
                refresh_frequency_per_month=int(_safe(rag_refresh, 1)), cloud=cloud, region=region)
        elif scn == "Multi-Agent System":
            result = estimate_multi_agent_scenario(
                requests_per_day=int(_safe(ma_req, 500)),
                avg_steps_per_request=int(_safe(ma_steps, 5)),
                tools_per_step=int(_safe(ma_tools, 2)),
                orchestrator_model=ma_orch, worker_model=ma_worker,
                include_vector_search=bool(ma_vs), cloud=cloud, region=region)
        elif scn == "Batch AI Pipeline":
            result = estimate_batch_pipeline_scenario(
                int(_safe(batch_docs, 10000)), _safe(batch_pages, 5), batch_cx,
                int(_safe(batch_freq, 4)), batch_model, cloud=cloud, region=region)
        elif scn == "Fine-Tuned Model":
            if not ft_model or not ft_scale:
                return dbc.Alert("Select a model and scale.", color="light")
            result = estimate_fine_tune_scenario(
                ft_model, ft_scale, int(_safe(ft_eval_freq, 2)), int(_safe(ft_eval_q, 100)),
                _safe(ft_hrs, 12), int(_safe(ft_retrain, 3)), cloud=cloud, region=region)
        else:
            return None
    except (ValueError, TypeError) as e:
        return dbc.Alert(f"Estimation error: {e}", color="danger")

    return _render_scenario_result(result)

def _render_scenario_result(result):
    """Shared renderer for scenario results."""
    elements = [
        html.H5(f"${result.total_monthly_usd:,.2f} / month", style={"color": DB_TEAL}),
    ]
    nonzero = [(li.service, li.estimate.cost_usd) for li in result.line_items if li.estimate.cost_usd > 0]
    if nonzero:
        names, values = zip(*nonzero)
        fig = px.pie(values=list(values), names=list(names), title="Cost Breakdown",
                     color_discrete_sequence=PIE_COLORS)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(height=380, template="plotly_white")
        elements.append(dcc.Graph(figure=fig))
    items = []
    for li in result.line_items:
        pct = (li.estimate.cost_usd / result.total_monthly_usd * 100) if result.total_monthly_usd > 0 else 0
        items.append(html.Li(f"{li.service}: ${li.estimate.cost_usd:,.2f} ({pct:.0f}%) — {li.estimate.details}"))
    if items:
        elements.append(html.Details([html.Summary("Line items"), html.Ul(items, className="small mt-1")]))
    return html.Div(elements)

# --- Quick Estimate ---
@callback(Output("qe-size", "options"), Output("qe-size", "value"),
          Input("qe-type", "value"))
def update_qe_sizes(qe_type):
    presets = SCENARIO_PRESETS.get(qe_type, {})
    opts = [{"label": f"{s} — {p['label']}", "value": s} for s, p in presets.items()]
    return opts, opts[0]["value"] if opts else None

@callback(Output("qe-result", "children"),
          Input("qe-type", "value"), Input("qe-size", "value"),
          Input("cloud", "value"), Input("region", "value"))
def calc_quick(qe_type, size, cloud, region):
    if not qe_type or not size:
        return None
    presets = SCENARIO_PRESETS.get(qe_type, {})
    preset = presets.get(size)
    if not preset:
        return None
    params = {**preset["params"], "cloud": cloud, "region": region}
    fn_map = {
        "RAG": estimate_rag_scenario,
        "Multi-Agent": estimate_multi_agent_scenario,
        "Batch AI": estimate_batch_pipeline_scenario,
        "Fine-Tune": estimate_fine_tune_scenario,
    }
    try:
        result = fn_map[qe_type](**params)
        return _render_scenario_result(result)
    except (ValueError, TypeError) as e:
        return dbc.Alert(f"Estimation error: {e}", color="danger")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
