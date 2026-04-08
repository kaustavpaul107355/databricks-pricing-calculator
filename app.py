"""
Databricks GenAI TCO Estimator.

Modes: GenAI Calculator (per-service), PT vs PPT Break-Even, Model Comparison,
Scenario Templates (RAG, Agent, Batch, Fine-Tune), Quick Estimate (T-shirt sizing).

Run: streamlit run app.py
"""

import streamlit as st
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

st.set_page_config(
    page_title="Databricks GenAI TCO Estimator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — modern layout, Databricks-inspired palette, colored accents
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* --- Color variables --- */
:root {
    --db-red: #FF3621;
    --db-orange: #FF6B35;
    --db-teal: #00A972;
    --db-blue: #1B3A4B;
    --db-purple: #7570B3;
    --db-light-bg: #F8F9FB;
    --db-card-border: #E4E7EC;
    --db-accent-gradient: linear-gradient(135deg, #FF3621 0%, #FF6B35 100%);
}

/* App header bar */
header[data-testid="stHeader"] {
    background: var(--db-accent-gradient);
}

/* Tab styling */
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    font-weight: 600;
    font-size: 0.95rem;
    padding: 0.6rem 1.2rem;
    border-radius: 8px 8px 0 0;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    background-color: var(--db-red);
    color: white !important;
    border-bottom: 3px solid var(--db-red);
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: var(--db-light-bg);
    border: 1px solid var(--db-card-border);
    border-left: 4px solid var(--db-teal);
    border-radius: 8px;
    padding: 0.8rem 1rem;
}
div[data-testid="stMetric"] label {
    color: #5A6672;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: var(--db-blue);
    font-weight: 700;
}

/* Expander headers */
div[data-testid="stExpander"] summary {
    border-radius: 8px;
    border: 1px solid var(--db-card-border);
    padding: 0.6rem 1rem;
    background: var(--db-light-bg);
}
div[data-testid="stExpander"] summary:hover {
    background: #EEF1F5;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1B2A3D;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #CBD5E1 !important;
}
section[data-testid="stSidebar"] a {
    color: #6DD4B0 !important;
}
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 {
    color: #F1F5F9 !important;
}

/* Plotly chart container */
div[data-testid="stPlotlyChart"] {
    border: 1px solid var(--db-card-border);
    border-radius: 10px;
    padding: 0.5rem;
    background: white;
}

/* Info/Warning/Success boxes */
div[data-testid="stAlert"] {
    border-radius: 8px;
}

/* Page title */
h1 {
    color: var(--db-blue) !important;
    border-bottom: 3px solid var(--db-red);
    padding-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Shared: Cloud & Region selector
# ---------------------------------------------------------------------------

def render_cloud_region_selector():
    col_cloud, col_region, _ = st.columns([1, 2, 2])
    with col_cloud:
        cloud = st.selectbox("Cloud", options=CLOUDS, index=0, key="global_cloud")
    regions_for_cloud = REGIONS_BY_CLOUD.get(cloud, REGIONS_BY_CLOUD["AWS"])
    region_list = list(regions_for_cloud.keys())
    with col_region:
        region = st.selectbox(
            "Region", options=region_list,
            format_func=lambda r: f"{regions_for_cloud[r][0]} (${regions_for_cloud[r][1]:.3f}/DBU)",
            index=0, key="global_region",
        )
    return cloud, region


# ---------------------------------------------------------------------------
# Page: GenAI Calculator (original per-service page)
# ---------------------------------------------------------------------------

def render_genai_calculator(cloud, region):
    from calculator import (
        estimate_vector_search, estimate_vector_search_reranker,
        estimate_model_serving_cpu, estimate_model_serving_gpu,
        estimate_foundation_model_tokens, estimate_proprietary_foundation_model,
        estimate_ai_parse, estimate_agent_evaluation, estimate_model_training,
        estimate_gateway_payload,
    )

    st.title("GenAI Calculator — Per-Service Estimate")
    st.caption(
        "Estimate monthly (and one-time training) cost for a GenAI solution. "
        "Rates from [Databricks GenAI pricing pages](https://www.databricks.com/product/pricing)."
    )

    line_items = []

    # 1. Vector Search
    with st.expander("**Vector Search** — embeddings & similarity search", expanded=True):
        st.caption("[Vector Search pricing](https://www.databricks.com/product/pricing/vector-search)")
        v1, v2, v3 = st.columns(3)
        with v1:
            tier_v = st.selectbox("Tier", options=list(VECTOR_SEARCH_DBU_PER_HOUR.keys()), key="vs_tier")
        with v2:
            units_v = st.number_input("Units", min_value=0, value=0, step=1, key="vs_units")
        with v3:
            hours_v = st.number_input("Hours/month", min_value=0, value=720, step=72, key="vs_hrs")
        if units_v > 0 and hours_v > 0:
            r = estimate_vector_search(tier_v, units_v, hours_v, cloud=cloud, region=region)
            line_items.append(("Vector Search", r.cost_usd, False))
            st.caption(f"→ **${r.cost_usd:,.2f}/month**")

    with st.expander("**Vector Search Reranker** (optional)"):
        st.caption("[Vector Search pricing](https://www.databricks.com/product/pricing/vector-search)")
        reranker_1k = st.number_input("Reranker requests (thousands)", min_value=0.0, value=0.0, step=1.0, key="reranker")
        if reranker_1k > 0:
            r_r = estimate_vector_search_reranker(reranker_1k, cloud=cloud, region=region)
            line_items.append(("Vector Search Reranker", r_r.cost_usd, False))
            st.caption(f"→ **${r_r.cost_usd:,.2f}**")

    # 2a. Agent Bricks
    with st.expander("**Agent Bricks** — build agents on your data", expanded=True):
        st.caption("[Agent Bricks pricing](https://www.databricks.com/product/pricing/agent-bricks)")
        agent_type = st.selectbox("What are you building?", options=["— None —", "Knowledge Assistant", "Supervisor Agent"], key="agent_type")
        if agent_type and agent_type != "— None —":
            mode_ab = st.radio("Compute", ["CPU (typical)", "GPU"], horizontal=True, key="ab_mode")
            if mode_ab == "CPU (typical)":
                req_hrs_ab = st.number_input("Request-hours per month", min_value=0.0, value=0.0, step=72.0, key="ab_cpu_req")
                if req_hrs_ab > 0:
                    r = estimate_model_serving_cpu(req_hrs_ab, cloud=cloud, region=region)
                    line_items.append((f"Agent Bricks ({agent_type})", r.cost_usd, False))
                    st.caption(f"→ **${r.cost_usd:,.2f}/month**")
            else:
                gpu_size_ab = st.selectbox("GPU instance", options=list(MODEL_SERVING_GPU_DBU_PER_HOUR.keys()), key="ab_gpu_size")
                gpu_hrs_ab = st.number_input("Hours per month", min_value=0, value=0, step=72, key="ab_gpu_hrs")
                if gpu_hrs_ab > 0:
                    r = estimate_model_serving_gpu(gpu_size_ab, gpu_hrs_ab, cloud=cloud, region=region)
                    line_items.append((f"Agent Bricks ({agent_type})", r.cost_usd, False))
                    st.caption(f"→ **${r.cost_usd:,.2f}/month**")

    # 2b. Mosaic AI Gateway
    with st.expander("**Mosaic AI Gateway** — guardrails, logging, usage tracking", expanded=True):
        st.caption("[Mosaic AI Gateway pricing](https://www.databricks.com/product/pricing/mosaic-ai-gateway)")
        gw_guardrails = st.checkbox("AI Guardrails", key="gw_guard")
        gw_inference_tables = st.checkbox("Inference Tables", key="gw_inf")
        gw_usage_tracking = st.checkbox("Usage Tracking", key="gw_usage")
        if gw_inference_tables or gw_usage_tracking:
            payload_gb = st.number_input("Payload per month (GB)", min_value=0.0, value=0.0, step=0.5, key="gw_payload")
            if payload_gb > 0:
                r = estimate_gateway_payload(payload_gb, cloud=cloud, region=region)
                line_items.append(("Mosaic AI Gateway", r.cost_usd, False))
                st.caption(f"→ **${r.cost_usd:,.2f}/month**")
        if gw_guardrails and not (gw_inference_tables or gw_usage_tracking):
            st.info("Guardrails cost is part of Model Serving / Agent Bricks above.")

    # 2c. Model Serving
    with st.expander("**Model Serving** — custom or third-party models", expanded=True):
        st.caption("[Model Serving pricing](https://www.databricks.com/product/pricing/model-serving)")
        mode_serving = st.radio("Mode", ["CPU", "GPU"], horizontal=True, key="serv_mode")
        if mode_serving == "CPU":
            req_hrs = st.number_input("Request-hours per month", min_value=0.0, value=0.0, step=72.0, key="cpu_req")
            if req_hrs > 0:
                r = estimate_model_serving_cpu(req_hrs, cloud=cloud, region=region)
                line_items.append(("Model Serving (CPU)", r.cost_usd, False))
                st.caption(f"→ **${r.cost_usd:,.2f}/month**")
        else:
            gpu_size = st.selectbox("GPU instance", options=list(MODEL_SERVING_GPU_DBU_PER_HOUR.keys()), key="gpu_size")
            gpu_hrs = st.number_input("Hours per month", min_value=0, value=0, step=72, key="gpu_hrs")
            if gpu_hrs > 0:
                r = estimate_model_serving_gpu(gpu_size, gpu_hrs, cloud=cloud, region=region)
                line_items.append(("Model Serving (GPU)", r.cost_usd, False))
                st.caption(f"→ **${r.cost_usd:,.2f}/month**")

    # 3. Foundation Model (open)
    with st.expander("**Foundation Model Serving** — open models", expanded=True):
        st.caption("[Foundation Model Serving](https://www.databricks.com/product/pricing/foundation-model-serving)")
        models_open = [m for m, r in FOUNDATION_MODEL_DBU_PER_MILLION.items() if r.get("input") or r.get("provisioned_per_hour")]
        fm_model = st.selectbox("Model", options=["— None —"] + models_open, key="fm_model")
        if fm_model != "— None —":
            c1, c2, c3 = st.columns(3)
            with c1:
                fm_in = st.number_input("Input tokens (M)", min_value=0.0, value=0.0, step=0.5, key="fm_in")
            with c2:
                fm_out = st.number_input("Output tokens (M)", min_value=0.0, value=0.0, step=0.5, key="fm_out")
            with c3:
                fm_pt = st.number_input("PT hours", min_value=0.0, value=0.0, step=24.0, key="fm_pt")
            if fm_in > 0 or fm_out > 0 or fm_pt > 0:
                r = estimate_foundation_model_tokens(fm_model, input_millions=fm_in, output_millions=fm_out, provisioned_hours=fm_pt, cloud=cloud, region=region)
                line_items.append(("Foundation Model (open)", r.cost_usd, False))
                st.caption(f"→ **${r.cost_usd:,.2f}/month**")

    # 4. Proprietary Foundation Model
    with st.expander("**Proprietary Foundation Model** — OpenAI, Anthropic, Google", expanded=True):
        st.caption("[Proprietary Foundation Model Serving](https://www.databricks.com/product/pricing/proprietary-foundation-model-serving)")
        prop_model = st.selectbox("Model", options=["— None —"] + list(PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION.keys()), key="prop_model")
        if prop_model != "— None —":
            tiers = get_proprietary_model_tiers(prop_model)
            tier_labels = {"global": "Global", "in_geo": "In-Geo (~10% premium)", "long_context": "Long Context (>200k tokens)", "in_geo_long_context": "In-Geo + Long Context"}
            tier_display = [tier_labels.get(t, t) for t in tiers]
            selected_tier_display = st.radio("Pricing tier", tier_display, horizontal=True, key="prop_tier")
            selected_tier = tiers[tier_display.index(selected_tier_display)]
            rates = get_proprietary_model_rates(prop_model, selected_tier)
            p1, p2 = st.columns(2)
            with p1:
                prop_in = st.number_input("Input tokens (M)", min_value=0.0, value=0.0, step=0.5, key="prop_in")
            with p2:
                prop_out = st.number_input("Output tokens (M)", min_value=0.0, value=0.0, step=0.5, key="prop_out")
            with st.expander("Cache & Batch (optional)"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    cache_write = st.number_input("Cache write (M)", min_value=0.0, value=0.0, step=0.5, key="prop_cw",
                                                  disabled=not (rates and rates.get("cache_write")))
                with c2:
                    cache_read = st.number_input("Cache read (M)", min_value=0.0, value=0.0, step=0.5, key="prop_cr",
                                                 disabled=not (rates and rates.get("cache_read")))
                with c3:
                    batch_hrs = st.number_input("Batch hours", min_value=0.0, value=0.0, step=1.0, key="prop_batch",
                                                disabled=not (rates and rates.get("batch")))
            if prop_in > 0 or prop_out > 0 or cache_write > 0 or cache_read > 0 or batch_hrs > 0:
                r = estimate_proprietary_foundation_model(
                    prop_model, input_millions=prop_in, output_millions=prop_out,
                    tier=selected_tier, cache_write_millions=cache_write,
                    cache_read_millions=cache_read, batch_hours=batch_hrs,
                    cloud=cloud, region=region)
                line_items.append(("Proprietary Foundation Model", r.cost_usd, False))
                st.caption(f"→ **${r.cost_usd:,.2f}/month**")

    # 5. AI Parse
    with st.expander("**AI Parse Document** — turn PDFs into structured data", expanded=True):
        st.caption("[AI Parse Document](https://www.databricks.com/product/pricing/ai-parse) · *50% promo through June 30, 2026*")
        parse_options = ["— None —"] + [label for label, _ in AI_PARSE_DOCUMENT_TYPE_LABELS]
        parse_complex_display = st.selectbox("What are you parsing?", options=parse_options, key="parse_doc_type")
        if parse_complex_display and parse_complex_display != "— None —":
            complexity_key = next(k for lbl, k in AI_PARSE_DOCUMENT_TYPE_LABELS if lbl == parse_complex_display)
            pc1, pc2 = st.columns([2, 1])
            with pc1:
                pages_1k = st.number_input("Pages (thousands)", min_value=0.0, value=0.0, step=0.5, key="parse_pages")
            with pc2:
                apply_promo = st.checkbox("Apply 50% promo", value=True, key="parse_promo")
            if pages_1k > 0:
                r = estimate_ai_parse(pages_1k, complexity_key, cloud=cloud, region=region, apply_promo=apply_promo)
                line_items.append(("AI Parse Document", r.cost_usd, False))
                st.caption(f"→ **${r.cost_usd:,.2f}**")

    # 6. Agent Evaluation
    with st.expander("**Agent Evaluation** — LLM Judge, Synthetic Data", expanded=True):
        st.caption("[Agent Evaluation](https://www.databricks.com/product/pricing/agent-evaluation)")
        eval_type = st.selectbox("Type", options=["— None —"] + list(AGENT_EVALUATION_DBU.keys()), key="eval_type")
        if eval_type != "— None —":
            e1, e2, e3 = st.columns(3)
            with e1:
                eval_in = st.number_input("Input tokens (M)", min_value=0.0, value=0.0, step=0.5, key="eval_in")
            with e2:
                eval_out = st.number_input("Output tokens (M)", min_value=0.0, value=0.0, step=0.5, key="eval_out")
            with e3:
                eval_q = st.number_input("Questions", min_value=0.0, value=0.0, step=10.0, key="eval_q")
            if eval_in > 0 or eval_out > 0 or eval_q > 0:
                r = estimate_agent_evaluation(eval_type, input_millions=eval_in, output_millions=eval_out, questions=eval_q, cloud=cloud, region=region)
                line_items.append(("Agent Evaluation", r.cost_usd, False))
                st.caption(f"→ **${r.cost_usd:,.2f}**")

    # 7. Model Training
    if "genai_training_one_time" not in st.session_state:
        st.session_state.genai_training_one_time = 0.0
    with st.expander("**Model Training** — fine-tuning (one-time)", expanded=True):
        st.caption("[Model Training](https://www.databricks.com/product/pricing/mosaic-foundation-model-training)")
        train_model = st.selectbox("Model", options=["— None —"] + list(MODEL_TRAINING_DBU_ESTIMATES.keys()), key="train_model")
        if train_model != "— None —":
            scales = list(MODEL_TRAINING_DBU_ESTIMATES[train_model].keys())
            train_scale = st.selectbox("Training scale", options=scales, key="train_scale")
            if st.button("Add training estimate", key="train_btn"):
                r = estimate_model_training(train_model, train_scale, cloud=cloud, region=region)
                st.session_state.genai_training_one_time = r.cost_usd
                st.success(f"One-time: **${r.cost_usd:,.2f}**")
            if st.button("Clear training", key="clear_train"):
                st.session_state.genai_training_one_time = 0.0
                st.rerun()
        training_one_time = st.session_state.genai_training_one_time
        if training_one_time > 0:
            st.info(f"One-time training: **${training_one_time:,.2f}**")

    training_one_time = st.session_state.get("genai_training_one_time", 0.0)

    # Total
    st.markdown("---")
    st.subheader("Ballpark total")
    monthly_total = sum(c for _, c, one_time in line_items if not one_time)
    st.metric("Estimated monthly (recurring)", f"${monthly_total:,.2f}")
    if training_one_time > 0:
        st.metric("One-time (Model Training)", f"${training_one_time:,.2f}")
    if line_items or training_one_time > 0:
        with st.expander("Line items"):
            for label, cost, _ in line_items:
                st.write(f"- **{label}:** ${cost:,.2f}")
            if training_one_time > 0:
                st.write(f"- **Model Training (one-time):** ${training_one_time:,.2f}")


# ---------------------------------------------------------------------------
# Page: PT vs PPT Break-Even
# ---------------------------------------------------------------------------

def render_breakeven_page(cloud, region):
    st.title("PT vs PPT Break-Even Calculator")
    st.caption("Find the crossover point where Provisioned Throughput becomes cheaper than Pay-Per-Token for open foundation models.")

    pt_models = get_all_models_with_pt()
    model = st.selectbox("Model", options=pt_models, key="be_model")

    c1, c2 = st.columns(2)
    with c1:
        avg_input = st.number_input("Avg input tokens per query", min_value=100, max_value=100000, value=2000, step=500, key="be_input")
        qpm = st.slider("Queries per minute", min_value=0.1, max_value=200.0, value=5.0, step=0.5, key="be_qpm")
    with c2:
        avg_output = st.number_input("Avg output tokens per query", min_value=50, max_value=50000, value=500, step=100, key="be_output")
        uptime = st.slider("Uptime hours/day", min_value=1, max_value=24, value=12, step=1, key="be_uptime")

    try:
        result = calculate_pt_vs_ppt_breakeven(model, avg_input, avg_output, qpm, uptime, cloud, region)
    except ValueError as e:
        st.error(str(e))
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Pay-Per-Token (monthly)", f"${result.ppt_monthly:,.2f}")
    col2.metric("Provisioned Throughput (monthly)", f"${result.pt_monthly:,.2f}")
    col3.metric("Break-even at", f"{result.break_even_qpm:.1f} queries/min")

    cheaper_label = "PPT is cheaper" if result.cheaper_mode == "PPT" else "PT is cheaper"
    savings = abs(result.ppt_monthly - result.pt_monthly)
    st.info(f"At {qpm} QPM: **{cheaper_label}** — saving **${savings:,.2f}/month**")

    # Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[d["qpm"] for d in result.data_points],
        y=[d["ppt_cost"] for d in result.data_points],
        name="Pay-Per-Token", line=dict(color="#FF3621", width=3),
    ))
    fig.add_trace(go.Scatter(
        x=[d["qpm"] for d in result.data_points],
        y=[d["pt_cost"] for d in result.data_points],
        name="Provisioned Throughput", line=dict(color="#00A972", width=3, dash="dash"),
    ))
    if result.break_even_qpm < float("inf"):
        fig.add_vline(x=result.break_even_qpm, line_dash="dot", line_color="gray",
                       annotation_text=f"Break-even: {result.break_even_qpm:.1f} QPM")
    fig.update_layout(
        title=f"Monthly Cost: PPT vs PT — {model}",
        xaxis_title="Queries per minute",
        yaxis_title="Monthly cost ($)",
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Page: Model Comparison
# ---------------------------------------------------------------------------

def render_model_comparison_page(cloud, region):
    st.title("Model Cost Comparison")
    st.caption("Compare monthly token costs across 2-3 models for the same traffic.")

    all_models = inference_model_names()
    selected = st.multiselect("Select 2-3 models to compare", all_models, max_selections=3, key="mc_models")

    c1, c2 = st.columns(2)
    with c1:
        input_m = st.number_input("Input tokens (millions/month)", min_value=0.1, value=10.0, step=1.0, key="mc_input")
    with c2:
        output_m = st.number_input("Output tokens (millions/month)", min_value=0.1, value=2.0, step=0.5, key="mc_output")

    if len(selected) >= 2:
        try:
            result = compare_models(selected, input_m, output_m, cloud, region)
        except ValueError as e:
            st.error(str(e))
            return

        # Bar chart
        colors = ["#FF3621", "#00A972", "#7570B3"]
        fig = go.Figure(data=[
            go.Bar(x=result.models, y=result.costs,
                   marker_color=colors[:len(result.models)],
                   text=[f"${c:,.2f}" for c in result.costs], textposition="auto")
        ])
        fig.update_layout(title="Monthly Cost Comparison", yaxis_title="Monthly cost ($)", height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Details table
        cheapest = result.models[result.costs.index(min(result.costs))]
        most_expensive = result.models[result.costs.index(max(result.costs))]
        savings_pct = (1 - min(result.costs) / max(result.costs)) * 100 if max(result.costs) > 0 else 0

        st.success(f"**{cheapest}** is **{savings_pct:.0f}% cheaper** than {most_expensive} for this traffic volume.")

        for model, detail in zip(result.models, result.details):
            tier = MODEL_QUALITY_TIER.get(model, "unknown")
            st.write(f"- **{model}** ({tier}): ${detail.cost_usd:,.2f}/month — {detail.details}")
    else:
        st.info("Select at least 2 models to compare.")


# ---------------------------------------------------------------------------
# Page: Scenario Templates
# ---------------------------------------------------------------------------

def _render_scenario_result(result):
    """Shared renderer for scenario results: metrics, pie chart, line items."""
    st.metric("Estimated Monthly TCO", f"${result.total_monthly_usd:,.2f}")

    if result.line_items:
        nonzero = [(li.service, li.estimate.cost_usd) for li in result.line_items if li.estimate.cost_usd > 0]
        if nonzero:
            names = [n for n, _ in nonzero]
            values = [v for _, v in nonzero]

            fig = px.pie(values=values, names=names, title="Cost Breakdown",
                         color_discrete_sequence=["#FF3621", "#00A972", "#FF6B35", "#7570B3", "#1B9E77", "#E6AB02", "#D95F02", "#66A61E"])
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("All line items rounded to $0 — no cost breakdown to display.")

        with st.expander("Line items"):
            for li in result.line_items:
                pct = (li.estimate.cost_usd / result.total_monthly_usd * 100) if result.total_monthly_usd > 0 else 0
                st.write(f"- **{li.service}**: ${li.estimate.cost_usd:,.2f} ({pct:.0f}%) — {li.estimate.details}")


def render_scenario_templates_page(cloud, region):
    st.title("Scenario Templates")
    st.caption("Estimate total monthly cost for common GenAI architectures.")

    scenario = st.selectbox("Scenario", ["RAG Application", "Multi-Agent System", "Batch AI Pipeline", "Fine-Tuned Model"], key="scenario_type")

    if scenario == "RAG Application":
        c1, c2 = st.columns(2)
        with c1:
            num_docs = st.number_input("Number of documents", 100, 10_000_000, 10_000, step=1000, key="rag_docs")
            avg_pages = st.number_input("Avg pages/doc", 1, 100, 5, key="rag_pages")
            avg_chunks = st.number_input("Avg chunks/doc", 1, 200, 20, key="rag_chunks")
            queries_day = st.number_input("Queries per day", 1, 1_000_000, 500, step=100, key="rag_qday")
        with c2:
            emb_models = embedding_model_names()
            embedding_model = st.selectbox("Embedding model", emb_models, key="rag_emb")
            llm_models = inference_model_names()
            llm_model = st.selectbox("LLM model", llm_models, key="rag_llm")
            parse_options = list(AI_PARSE_DBU_PER_1K_PAGES.keys())
            parse_cx = st.selectbox("Document complexity", parse_options, index=2, key="rag_cx")
            refresh = st.number_input("Refresh freq (times/month)", 1, 30, 1, key="rag_refresh")

        try:
            result = estimate_rag_scenario(num_docs, avg_pages, avg_chunks, queries_day,
                                            embedding_model, llm_model, parse_cx,
                                            refresh_frequency_per_month=refresh,
                                            cloud=cloud, region=region)
            _render_scenario_result(result)
        except ValueError as e:
            st.error(f"Estimation error: {e}")

    elif scenario == "Multi-Agent System":
        c1, c2 = st.columns(2)
        with c1:
            requests_day = st.number_input("Requests per day", 10, 1_000_000, 500, step=100, key="ma_req")
            steps = st.number_input("Avg steps per request", 1, 20, 5, key="ma_steps")
            tools = st.number_input("Tools per step", 1, 10, 2, key="ma_tools")
        with c2:
            llm_models = inference_model_names()
            orch_model = st.selectbox("Orchestrator model", llm_models, key="ma_orch")
            worker_model = st.selectbox("Worker model", llm_models, key="ma_worker")
            include_vs = st.checkbox("Include Vector Search", value=True, key="ma_vs")

        try:
            result = estimate_multi_agent_scenario(
                requests_per_day=requests_day,
                avg_steps_per_request=steps, tools_per_step=tools,
                orchestrator_model=orch_model, worker_model=worker_model,
                include_vector_search=include_vs, cloud=cloud, region=region)

            calls_per_req = result.assumptions.get("llm_calls_per_request", 0)
            st.warning(f"Each user request triggers **~{calls_per_req} LLM calls** ({result.assumptions.get('total_monthly_llm_calls', 0):,} total/month)")
            _render_scenario_result(result)
        except ValueError as e:
            st.error(f"Estimation error: {e}")

    elif scenario == "Batch AI Pipeline":
        c1, c2 = st.columns(2)
        with c1:
            num_docs = st.number_input("Documents per batch", 100, 10_000_000, 10_000, step=1000, key="batch_docs")
            pages_doc = st.number_input("Pages per doc", 1, 100, 5, key="batch_pages")
        with c2:
            parse_cx = st.selectbox("Complexity", list(AI_PARSE_DBU_PER_1K_PAGES.keys()), index=2, key="batch_cx")
            freq = st.number_input("Runs per month", 1, 60, 4, key="batch_freq")
            output_model = st.selectbox("Output model", inference_model_names(), key="batch_model")

        try:
            result = estimate_batch_pipeline_scenario(num_docs, pages_doc, parse_cx, freq, output_model, cloud=cloud, region=region)
            _render_scenario_result(result)
        except ValueError as e:
            st.error(f"Estimation error: {e}")

    elif scenario == "Fine-Tuned Model":
        c1, c2 = st.columns(2)
        with c1:
            base_model = st.selectbox("Base model", list(MODEL_TRAINING_DBU_ESTIMATES.keys()), key="ft_model")
            scales = list(MODEL_TRAINING_DBU_ESTIMATES[base_model].keys())
            training_scale = st.selectbox("Training scale", scales, key="ft_scale")
        with c2:
            serving_hrs = st.slider("Serving hours/day", 1, 24, 12, key="ft_hrs")
            retrain_months = st.number_input("Retraining cadence (months)", 1, 12, 3, key="ft_retrain")
            eval_freq = st.number_input("Eval runs/month", 0, 30, 2, key="ft_eval_freq")
            eval_questions = st.number_input("Questions per eval", 0, 1000, 100, key="ft_eval_q")

        try:
            result = estimate_fine_tune_scenario(base_model, training_scale, eval_freq, eval_questions,
                                                  serving_hrs, retrain_months, cloud=cloud, region=region)
            _render_scenario_result(result)
        except ValueError as e:
            st.error(f"Estimation error: {e}")


# ---------------------------------------------------------------------------
# Page: Quick Estimate
# ---------------------------------------------------------------------------

def render_quick_estimate_page(cloud, region):
    from presets import SCENARIO_PRESETS

    st.title("Quick Estimate")
    st.caption("Get a ballpark TCO in seconds with T-shirt sizing presets.")

    scenario_type = st.radio("What are you building?", list(SCENARIO_PRESETS.keys()), horizontal=True, key="qe_type")
    presets = SCENARIO_PRESETS[scenario_type]

    size = st.radio("Scale", list(presets.keys()), horizontal=True,
                    format_func=lambda s: f"{s} — {presets[s]['label']}", key="qe_size")

    preset = presets[size]
    params = {**preset["params"], "cloud": cloud, "region": region}

    scenario_fn = {
        "RAG": estimate_rag_scenario,
        "Multi-Agent": estimate_multi_agent_scenario,
        "Batch AI": estimate_batch_pipeline_scenario,
        "Fine-Tune": estimate_fine_tune_scenario,
    }[scenario_type]

    try:
        result = scenario_fn(**params)
        _render_scenario_result(result)
    except ValueError as e:
        st.error(f"Estimation error: {e}")

    st.caption("Switch to **Scenario Templates** in the sidebar to customize these inputs.")


# ---------------------------------------------------------------------------
# Main: sidebar navigation
# ---------------------------------------------------------------------------

def main():
    # Sidebar: pricing sources only
    st.sidebar.markdown("### Pricing Sources")
    for label, path in GENAI_PRICING_PAGES:
        url = get_pricing_page_url(path)
        st.sidebar.markdown(f"- [{label}]({url})")

    cloud, region = render_cloud_region_selector()
    st.markdown("---")

    # Top-level tabs for mode navigation
    tab_calc, tab_breakeven, tab_compare, tab_scenarios, tab_quick = st.tabs([
        "GenAI Calculator",
        "PT vs PPT Break-Even",
        "Model Comparison",
        "Scenario Templates",
        "Quick Estimate",
    ])

    with tab_calc:
        render_genai_calculator(cloud, region)
    with tab_breakeven:
        render_breakeven_page(cloud, region)
    with tab_compare:
        render_model_comparison_page(cloud, region)
    with tab_scenarios:
        render_scenario_templates_page(cloud, region)
    with tab_quick:
        render_quick_estimate_page(cloud, region)


if __name__ == "__main__":
    main()
