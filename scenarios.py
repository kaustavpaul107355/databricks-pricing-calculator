"""
Composite scenario estimators and analysis tools for GenAI TCO.

Includes:
- PT vs PPT break-even calculator
- Model cost comparison
- RAG, Multi-Agent, Batch, Fine-Tune scenario templates
"""

from dataclasses import dataclass, field

from calculator import (
    EstimateResult,
    estimate_vector_search,
    estimate_foundation_model_tokens,
    estimate_proprietary_foundation_model,
    estimate_ai_parse,
    estimate_agent_evaluation,
    estimate_model_training,
    estimate_model_serving_cpu,
    estimate_storage,
    estimate_gateway_payload,
    estimate_compute_dbu,
    get_price_per_dbu,
)
from pricing_data import (
    FOUNDATION_MODEL_DBU_PER_MILLION,
    PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION,
    VECTOR_SEARCH_DBU_PER_HOUR,
    AI_PARSE_DBU_PER_1K_PAGES,
    MODEL_TRAINING_DBU_ESTIMATES,
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ScenarioLineItem:
    service: str
    estimate: EstimateResult


@dataclass
class ScenarioResult:
    name: str
    line_items: list[ScenarioLineItem] = field(default_factory=list)
    total_monthly_usd: float = 0.0
    total_one_time_usd: float = 0.0
    assumptions: dict = field(default_factory=dict)


@dataclass
class BreakEvenResult:
    model: str
    ppt_monthly: float
    pt_monthly: float
    cheaper_mode: str
    break_even_qpm: float
    data_points: list[dict] = field(default_factory=list)


@dataclass
class ModelComparisonResult:
    models: list[str]
    costs: list[float]
    details: list[EstimateResult]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_open_model(model: str) -> bool:
    return model in FOUNDATION_MODEL_DBU_PER_MILLION


def _is_proprietary_model(model: str) -> bool:
    return model in PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION


def _estimate_model_cost(
    model: str,
    input_millions: float,
    output_millions: float,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> EstimateResult:
    """Estimate token cost for any model (open or proprietary)."""
    if _is_open_model(model):
        return estimate_foundation_model_tokens(
            model, input_millions=input_millions, output_millions=output_millions,
            cloud=cloud, region=region,
        )
    elif _is_proprietary_model(model):
        return estimate_proprietary_foundation_model(
            model, input_millions=input_millions, output_millions=output_millions,
            cloud=cloud, region=region,
        )
    else:
        raise ValueError(f"Unknown model '{model}'")


def inference_model_names() -> list[str]:
    """Return model names that support input+output tokens (not embedding-only)."""
    models = []
    for m, r in FOUNDATION_MODEL_DBU_PER_MILLION.items():
        if r.get("input") and r.get("output"):
            models.append(m)
    models.extend(PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION.keys())
    return models


def embedding_model_names() -> list[str]:
    """Return model names that are embedding models (input only, no output)."""
    return [m for m, r in FOUNDATION_MODEL_DBU_PER_MILLION.items()
            if r.get("input") and not r.get("output")]


# ---------------------------------------------------------------------------
# PT vs PPT Break-Even
# ---------------------------------------------------------------------------

def calculate_pt_vs_ppt_breakeven(
    model: str,
    avg_input_tokens: int,
    avg_output_tokens: int,
    queries_per_min: float,
    uptime_hours_per_day: float = 24,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> BreakEvenResult:
    """Calculate break-even between Pay-Per-Token and Provisioned Throughput.
    Only works for open foundation models with both PPT and PT rates."""
    rates = FOUNDATION_MODEL_DBU_PER_MILLION.get(model)
    if not rates:
        raise ValueError(f"Model '{model}' not found in Foundation Model catalog")
    if not (rates.get("input") and rates.get("provisioned_per_hour")):
        raise ValueError(f"Model '{model}' does not support both PPT and PT")

    price_per_dbu = get_price_per_dbu(cloud, region)

    # PPT cost for given QPM
    monthly_queries = queries_per_min * 60 * uptime_hours_per_day * 30
    input_m = monthly_queries * avg_input_tokens / 1e6
    output_m = monthly_queries * avg_output_tokens / 1e6
    dbu_ppt = (rates["input"] * input_m) + (rates.get("output", 0) * output_m)
    ppt_monthly = dbu_ppt * price_per_dbu

    # PT cost (fixed capacity)
    pt_dbu = rates["provisioned_per_hour"] * uptime_hours_per_day * 30
    pt_monthly = pt_dbu * price_per_dbu

    # Break-even QPM: solve ppt_cost(x) = pt_cost for x
    # ppt_cost = x * 60 * uptime * 30 * (input_tokens/1e6 * rate_in + output_tokens/1e6 * rate_out) * price_per_dbu
    cost_per_query_dbu = (avg_input_tokens / 1e6 * rates["input"]) + (avg_output_tokens / 1e6 * rates.get("output", 0))
    if cost_per_query_dbu > 0:
        queries_at_breakeven = pt_dbu / cost_per_query_dbu
        break_even_qpm = queries_at_breakeven / (60 * uptime_hours_per_day * 30)
    else:
        break_even_qpm = float("inf")

    cheaper = "PT" if ppt_monthly > pt_monthly else "PPT"

    # Generate data points for chart
    max_qpm = max(break_even_qpm * 2.5, queries_per_min * 2) if break_even_qpm < float("inf") else queries_per_min * 3
    data_points = []
    for i in range(51):
        qpm = max_qpm * i / 50
        q_month = qpm * 60 * uptime_hours_per_day * 30
        in_m = q_month * avg_input_tokens / 1e6
        out_m = q_month * avg_output_tokens / 1e6
        ppt_cost = ((rates["input"] * in_m) + (rates.get("output", 0) * out_m)) * price_per_dbu
        data_points.append({"qpm": round(qpm, 2), "ppt_cost": round(ppt_cost, 2), "pt_cost": round(pt_monthly, 2)})

    return BreakEvenResult(
        model=model,
        ppt_monthly=round(ppt_monthly, 2),
        pt_monthly=round(pt_monthly, 2),
        cheaper_mode=cheaper,
        break_even_qpm=round(break_even_qpm, 2),
        data_points=data_points,
    )


# ---------------------------------------------------------------------------
# Model Comparison
# ---------------------------------------------------------------------------

def compare_models(
    models: list[str],
    input_millions: float,
    output_millions: float,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> ModelComparisonResult:
    """Compare monthly token costs across 2+ models."""
    costs = []
    details = []
    for model in models:
        r = _estimate_model_cost(model, input_millions, output_millions, cloud, region)
        costs.append(r.cost_usd)
        details.append(r)
    return ModelComparisonResult(models=models, costs=costs, details=details)


# ---------------------------------------------------------------------------
# Scenario: RAG Application
# ---------------------------------------------------------------------------

def estimate_rag_scenario(
    num_docs: int,
    avg_pages_per_doc: float,
    avg_chunks_per_doc: float,
    queries_per_day: int,
    embedding_model: str,
    llm_model: str,
    parse_complexity: str,
    refresh_frequency_per_month: int = 1,
    avg_input_tokens_per_query: int = 2000,
    avg_output_tokens_per_query: int = 500,
    include_guardrails: bool = True,
    include_eval: bool = True,
    eval_questions_per_month: int = 100,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> ScenarioResult:
    """Estimate total monthly cost for a RAG application."""
    items = []

    # 1. AI Parse (document ingestion)
    total_pages_1k = (num_docs * avg_pages_per_doc * refresh_frequency_per_month) / 1000
    if total_pages_1k > 0 and parse_complexity in AI_PARSE_DBU_PER_1K_PAGES:
        r = estimate_ai_parse(total_pages_1k, parse_complexity, cloud=cloud, region=region)
        items.append(ScenarioLineItem("AI Parse (ingestion)", r))

    # 2. Embedding generation
    total_chunks = num_docs * avg_chunks_per_doc * refresh_frequency_per_month
    tokens_per_chunk = 256
    embedding_input_m = total_chunks * tokens_per_chunk / 1e6
    emb_rates = FOUNDATION_MODEL_DBU_PER_MILLION.get(embedding_model, {})
    if emb_rates.get("input") and embedding_input_m > 0:
        r = estimate_foundation_model_tokens(embedding_model, input_millions=embedding_input_m, cloud=cloud, region=region)
        items.append(ScenarioLineItem("Embedding generation", r))

    # 3. Vector Search
    total_vectors = num_docs * avg_chunks_per_doc
    vs_info = VECTOR_SEARCH_DBU_PER_HOUR.get("Standard", {})
    capacity = vs_info.get("vector_capacity_per_unit", 2_000_000)
    units = max(1, -(-total_vectors // capacity))  # ceiling division
    r = estimate_vector_search("Standard", units=units, hours_per_month=720, cloud=cloud, region=region)
    items.append(ScenarioLineItem("Vector Search", r))

    # 4. LLM inference
    monthly_queries = queries_per_day * 30
    llm_input_m = monthly_queries * avg_input_tokens_per_query / 1e6
    llm_output_m = monthly_queries * avg_output_tokens_per_query / 1e6
    r = _estimate_model_cost(llm_model, llm_input_m, llm_output_m, cloud, region)
    items.append(ScenarioLineItem("LLM inference", r))

    # 5. Guardrails (approximation: gateway payload)
    if include_guardrails:
        avg_payload_bytes = (avg_input_tokens_per_query + avg_output_tokens_per_query) * 4  # ~4 bytes/token
        payload_gb = monthly_queries * avg_payload_bytes / (1024**3)
        if payload_gb > 0:
            r = estimate_gateway_payload(payload_gb, cloud=cloud, region=region)
            items.append(ScenarioLineItem("AI Gateway (guardrails)", r))

    # 6. Agent Evaluation
    if include_eval and eval_questions_per_month > 0:
        r = estimate_agent_evaluation("Synthetic Data", questions=eval_questions_per_month, cloud=cloud, region=region)
        items.append(ScenarioLineItem("Agent Evaluation", r))

    # 7. Storage
    storage_gb = num_docs * avg_pages_per_doc * 0.05  # ~50KB/page
    if storage_gb > 0:
        r = estimate_storage(stored_gb=storage_gb)
        items.append(ScenarioLineItem("Storage (documents + vectors)", r))

    total_monthly = sum(li.estimate.cost_usd for li in items)
    return ScenarioResult(
        name="RAG Application",
        line_items=items,
        total_monthly_usd=round(total_monthly, 2),
        assumptions={
            "num_docs": num_docs, "avg_pages_per_doc": avg_pages_per_doc,
            "avg_chunks_per_doc": avg_chunks_per_doc, "queries_per_day": queries_per_day,
            "embedding_model": embedding_model, "llm_model": llm_model,
        },
    )


# ---------------------------------------------------------------------------
# Scenario: Multi-Agent System
# ---------------------------------------------------------------------------

def estimate_multi_agent_scenario(
    requests_per_day: int,
    avg_steps_per_request: int,
    tools_per_step: int,
    orchestrator_model: str,
    worker_model: str,
    include_vector_search: bool = True,
    include_guardrails: bool = True,
    avg_orchestrator_input_tokens: int = 3000,
    avg_orchestrator_output_tokens: int = 1000,
    avg_worker_input_tokens: int = 1500,
    avg_worker_output_tokens: int = 500,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> ScenarioResult:
    """Estimate total monthly cost for a multi-agent system."""
    items = []
    monthly_requests = requests_per_day * 30

    # Orchestrator: 1 initial + 1 per step (routing/planning)
    orch_calls = monthly_requests * (1 + avg_steps_per_request)
    orch_input_m = orch_calls * avg_orchestrator_input_tokens / 1e6
    orch_output_m = orch_calls * avg_orchestrator_output_tokens / 1e6
    r = _estimate_model_cost(orchestrator_model, orch_input_m, orch_output_m, cloud, region)
    items.append(ScenarioLineItem(f"Orchestrator ({orchestrator_model})", r))

    # Worker agents: steps × tools per request
    worker_calls = monthly_requests * avg_steps_per_request * tools_per_step
    worker_input_m = worker_calls * avg_worker_input_tokens / 1e6
    worker_output_m = worker_calls * avg_worker_output_tokens / 1e6
    r = _estimate_model_cost(worker_model, worker_input_m, worker_output_m, cloud, region)
    items.append(ScenarioLineItem(f"Worker agents ({worker_model})", r))

    # Vector Search (if RAG tools)
    if include_vector_search:
        r = estimate_vector_search("Standard", units=1, hours_per_month=720, cloud=cloud, region=region)
        items.append(ScenarioLineItem("Vector Search (RAG tools)", r))

    # Guardrails
    if include_guardrails:
        total_calls = orch_calls + worker_calls
        avg_tokens = (avg_orchestrator_input_tokens + avg_worker_input_tokens) / 2
        payload_gb = total_calls * avg_tokens * 4 / (1024**3)
        if payload_gb > 0:
            r = estimate_gateway_payload(payload_gb, cloud=cloud, region=region)
            items.append(ScenarioLineItem("AI Gateway (guardrails)", r))

    total_monthly = sum(li.estimate.cost_usd for li in items)
    total_llm_calls = orch_calls + worker_calls
    calls_per_request = (1 + avg_steps_per_request) + (avg_steps_per_request * tools_per_step)

    return ScenarioResult(
        name="Multi-Agent System",
        line_items=items,
        total_monthly_usd=round(total_monthly, 2),
        assumptions={
            "requests_per_day": requests_per_day,
            "llm_calls_per_request": calls_per_request,
            "total_monthly_llm_calls": total_llm_calls,
        },
    )


# ---------------------------------------------------------------------------
# Scenario: Batch AI Pipeline
# ---------------------------------------------------------------------------

def estimate_batch_pipeline_scenario(
    num_docs: int,
    pages_per_doc: float,
    parse_complexity: str,
    frequency_per_month: int,
    output_model: str,
    avg_input_tokens_per_doc: int = 2000,
    avg_output_tokens_per_doc: int = 1000,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> ScenarioResult:
    """Estimate total monthly cost for a batch AI processing pipeline."""
    items = []

    # 1. AI Parse
    total_pages_1k = (num_docs * pages_per_doc * frequency_per_month) / 1000
    if total_pages_1k > 0 and parse_complexity in AI_PARSE_DBU_PER_1K_PAGES:
        r = estimate_ai_parse(total_pages_1k, parse_complexity, cloud=cloud, region=region)
        items.append(ScenarioLineItem("AI Parse (document processing)", r))

    # 2. Batch inference
    total_docs = num_docs * frequency_per_month
    input_m = total_docs * avg_input_tokens_per_doc / 1e6
    output_m = total_docs * avg_output_tokens_per_doc / 1e6
    r = _estimate_model_cost(output_model, input_m, output_m, cloud, region)
    items.append(ScenarioLineItem(f"Batch inference ({output_model})", r))

    # 3. Pipeline orchestration (Jobs compute)
    # Rough estimate: 0.5 DBU-hour per 1K docs processed
    jobs_dbu_hours = total_docs / 1000 * 0.5
    if jobs_dbu_hours > 0:
        r = estimate_compute_dbu("Jobs Compute", jobs_dbu_hours, cloud=cloud, region=region)
        items.append(ScenarioLineItem("Pipeline orchestration (Jobs)", r))

    # 4. Output storage
    output_gb = total_docs * avg_output_tokens_per_doc * 4 / (1024**3)  # ~4 bytes/token
    if output_gb > 0:
        r = estimate_storage(stored_gb=output_gb)
        items.append(ScenarioLineItem("Output storage", r))

    total_monthly = sum(li.estimate.cost_usd for li in items)
    return ScenarioResult(
        name="Batch AI Pipeline",
        line_items=items,
        total_monthly_usd=round(total_monthly, 2),
        assumptions={
            "num_docs": num_docs, "pages_per_doc": pages_per_doc,
            "frequency_per_month": frequency_per_month, "output_model": output_model,
        },
    )


# ---------------------------------------------------------------------------
# Scenario: Fine-Tuned Model Deployment
# ---------------------------------------------------------------------------

def estimate_fine_tune_scenario(
    base_model: str,
    training_scale: str,
    eval_frequency_per_month: int,
    eval_questions: int,
    serving_hours_per_day: float,
    retraining_cadence_months: int = 3,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> ScenarioResult:
    """Estimate monthly cost for fine-tuned model deployment (amortized training + serving + eval)."""
    items = []

    # 1. Training (amortized monthly)
    if base_model in MODEL_TRAINING_DBU_ESTIMATES:
        r = estimate_model_training(base_model, training_scale, cloud=cloud, region=region)
        amortized_monthly = r.cost_usd / retraining_cadence_months
        amortized_result = EstimateResult(
            description=f"Training {base_model} ({training_scale}), amortized over {retraining_cadence_months}mo",
            dbu_total=r.dbu_total / retraining_cadence_months,
            price_per_dbu=r.price_per_dbu,
            cost_usd=round(amortized_monthly, 2),
            details=f"${r.cost_usd:,.2f} one-time / {retraining_cadence_months} months",
        )
        items.append(ScenarioLineItem("Training (amortized)", amortized_result))

    # 2. Provisioned Throughput serving (only if model has PT rates)
    rates = FOUNDATION_MODEL_DBU_PER_MILLION.get(base_model, {})
    if rates.get("provisioned_per_hour"):
        pt_hours = serving_hours_per_day * 30
        r = estimate_foundation_model_tokens(base_model, provisioned_hours=pt_hours, cloud=cloud, region=region)
        items.append(ScenarioLineItem("Provisioned Throughput serving", r))
    else:
        items.append(ScenarioLineItem(
            "Provisioned Throughput serving",
            EstimateResult(
                description=f"No PT rates available for {base_model}",
                dbu_total=0, price_per_dbu=0, cost_usd=0,
                details=f"Model '{base_model}' has no provisioned_per_hour rate — PT serving not included",
            ),
        ))

    # 3. Evaluation
    if eval_frequency_per_month > 0 and eval_questions > 0:
        total_questions = eval_frequency_per_month * eval_questions
        r = estimate_agent_evaluation("Synthetic Data", questions=total_questions, cloud=cloud, region=region)
        items.append(ScenarioLineItem("Agent Evaluation", r))

    total_monthly = sum(li.estimate.cost_usd for li in items)
    return ScenarioResult(
        name="Fine-Tuned Model Deployment",
        line_items=items,
        total_monthly_usd=round(total_monthly, 2),
        assumptions={
            "base_model": base_model, "training_scale": training_scale,
            "serving_hours_per_day": serving_hours_per_day,
            "retraining_cadence_months": retraining_cadence_months,
        },
    )
