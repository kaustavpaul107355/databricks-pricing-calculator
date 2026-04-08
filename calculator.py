"""
Databricks pricing calculator.

Formulas:
- Cost = DBUs × price_per_dbu (per second granularity; we use hours for simplicity where applicable)
- SQL Serverless: DBU = warehouse_size_dbu_per_hour × hours
- Vector Search: DBU = dbu_per_hour_per_unit × units × hours
"""

from dataclasses import dataclass
from typing import Optional

import datetime

from pricing_data import (
    REGIONS_BY_CLOUD,
    get_price_per_dbu_for_region,
    get_price_per_dbu_for_workload,
    get_proprietary_model_rates,
    SQL_SERVERLESS_DBU_PER_HOUR,
    VECTOR_SEARCH_DBU_PER_HOUR,
    MODEL_SERVING_CPU_DBU_PER_HOUR,
    MODEL_SERVING_GPU_DBU_PER_HOUR,
    MODEL_TRAINING_DBU_ESTIMATES,
    STORAGE_DSU_MULTIPLIER,
    FOUNDATION_MODEL_DBU_PER_MILLION,
    PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION,
    AI_PARSE_DBU_PER_1K_PAGES,
    AI_PARSE_PROMO_DISCOUNT,
    AI_PARSE_PROMO_EXPIRY,
    AGENT_EVALUATION_DBU,
    SHUTTERSTOCK_DBU_PER_IMAGE,
    VECTOR_SEARCH_RERANKER_DBU_PER_1K_REQUESTS,
    GATEWAY_INFERENCE_TABLES_DBU_PER_GB,
    GATEWAY_USAGE_TRACKING_DBU_PER_GB,
)


@dataclass
class EstimateResult:
    """Result of a cost estimate."""
    description: str
    dbu_total: float
    price_per_dbu: float
    cost_usd: float
    details: Optional[str] = None


def get_price_per_dbu(
    cloud: str = "AWS",
    region: str = "us-east-1",
    workload_key: Optional[str] = None,
) -> float:
    """Get $/DBU for a cloud and region, optionally for a specific workload.
    Uses cloud-aware workload rates when available, falls back to region default."""
    if workload_key:
        rate = get_price_per_dbu_for_workload(workload_key, cloud)
        if rate is not None:
            return rate
    return get_price_per_dbu_for_region(cloud, region)


def _region_label(cloud: str, region: str) -> str:
    """Return human-readable region label for display."""
    region_info = (REGIONS_BY_CLOUD.get(cloud) or {}).get(region)
    return region_info[0] if isinstance(region_info, tuple) else region


def estimate_sql_warehouse(
    warehouse_size: str,
    hours_per_month: float = 720,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> EstimateResult:
    """Estimate monthly cost for a serverless SQL warehouse."""
    dbu_per_hour = SQL_SERVERLESS_DBU_PER_HOUR.get(warehouse_size)
    if dbu_per_hour is None:
        valid = ", ".join(SQL_SERVERLESS_DBU_PER_HOUR.keys())
        raise ValueError(f"Unknown warehouse size '{warehouse_size}'. Valid: {valid}")
    dbu_total = dbu_per_hour * hours_per_month
    price_per_dbu = get_price_per_dbu(cloud, region, None)  # use region $/DBU
    cost = dbu_total * price_per_dbu
    label = _region_label(cloud, region)
    return EstimateResult(
        description=f"SQL Serverless warehouse ({warehouse_size}) — {cloud} · {label}",
        dbu_total=dbu_total,
        price_per_dbu=price_per_dbu,
        cost_usd=round(cost, 2),
        details=f"{dbu_per_hour} DBU/hr × {hours_per_month} hrs = {dbu_total:,.0f} DBUs",
    )


def estimate_vector_search(
    tier: str,
    units: int = 1,
    hours_per_month: float = 720,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> EstimateResult:
    """Estimate monthly cost for Vector Search (Standard or Storage Optimized)."""
    info = VECTOR_SEARCH_DBU_PER_HOUR.get(tier)
    if not info:
        raise ValueError(f"Unknown tier '{tier}'. Use 'Standard' or 'Storage Optimized'.")
    dbu_per_hour = info["dbu_per_hour"]
    dbu_total = dbu_per_hour * units * hours_per_month
    price_per_dbu = get_price_per_dbu(cloud, region, None)  # use region $/DBU
    cost = dbu_total * price_per_dbu
    label = _region_label(cloud, region)
    return EstimateResult(
        description=f"Vector Search ({tier}), {units} unit(s) — {cloud} · {label}",
        dbu_total=dbu_total,
        price_per_dbu=price_per_dbu,
        cost_usd=round(cost, 2),
        details=f"{dbu_per_hour} DBU/hr/unit × {units} × {hours_per_month} hrs = {dbu_total:,.0f} DBUs",
    )


def estimate_compute_dbu(
    workload_type: str,
    dbu_hours: float,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> EstimateResult:
    """Estimate cost from total DBU-hours for a workload type (uses example $/DBU)."""
    price_per_dbu = get_price_per_dbu(cloud, region, workload_type)
    cost = dbu_hours * price_per_dbu
    label = _region_label(cloud, region)
    return EstimateResult(
        description=f"{workload_type}: {dbu_hours:,.0f} DBU-hours — {cloud} · {label}",
        dbu_total=dbu_hours,
        price_per_dbu=price_per_dbu,
        cost_usd=round(cost, 2),
    )


def estimate_model_training(
    model_name: str,
    training_scale: str,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> EstimateResult:
    """Estimate one-time training cost (uses DBU estimates from docs)."""
    model_estimates = MODEL_TRAINING_DBU_ESTIMATES.get(model_name)
    if not model_estimates:
        valid = ", ".join(MODEL_TRAINING_DBU_ESTIMATES.keys())
        raise ValueError(f"Unknown model '{model_name}'. Valid: {valid}")
    dbu = model_estimates.get(training_scale)
    if dbu is None:
        valid = ", ".join(model_estimates.keys())
        raise ValueError(f"Unknown scale '{training_scale}'. Valid: {valid}")
    price_per_dbu = get_price_per_dbu(cloud, region, "Model Training")  # workload override
    cost = dbu * price_per_dbu
    label = _region_label(cloud, region)
    return EstimateResult(
        description=f"Model Training {model_name} ({training_scale}) — {cloud} · {label}",
        dbu_total=float(dbu),
        price_per_dbu=price_per_dbu,
        cost_usd=round(cost, 2),
        details=f"~{dbu} DBUs at ${price_per_dbu}/DBU",
    )


def estimate_model_serving_gpu(
    instance_size: str,
    hours_per_month: float = 720,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> EstimateResult:
    """Estimate monthly cost for GPU model serving (DBU/hr by instance size)."""
    dbu_per_hour = MODEL_SERVING_GPU_DBU_PER_HOUR.get(instance_size)
    if dbu_per_hour is None:
        valid = ", ".join(MODEL_SERVING_GPU_DBU_PER_HOUR.keys())
        raise ValueError(f"Unknown GPU size '{instance_size}'. Valid: {valid}")
    dbu_total = dbu_per_hour * hours_per_month
    price_per_dbu = get_price_per_dbu(cloud, region)
    cost = dbu_total * price_per_dbu
    label = _region_label(cloud, region)
    return EstimateResult(
        description=f"GPU Model Serving ({instance_size}) — {cloud} · {label}",
        dbu_total=dbu_total,
        price_per_dbu=price_per_dbu,
        cost_usd=round(cost, 2),
        details=f"{dbu_per_hour} DBU/hr × {hours_per_month} hrs",
    )


def estimate_storage(
    stored_gb: float = 0,
    writes_1k: float = 0,
    reads_1k: float = 0,
    vector_search_units: float = 0,
    price_per_dsu: float = 0.07,
) -> EstimateResult:
    """Estimate storage cost (DSUs × price; default price illustrative). Region-agnostic: $/DSU does not vary by cloud/region."""
    dsu = (
        stored_gb * STORAGE_DSU_MULTIPLIER["per_gb_stored"]
        + writes_1k * STORAGE_DSU_MULTIPLIER["per_1000_writes"]
        + reads_1k * STORAGE_DSU_MULTIPLIER["per_1000_reads"]
        + vector_search_units * STORAGE_DSU_MULTIPLIER["vector_search"]
    )
    cost = dsu * price_per_dsu
    return EstimateResult(
        description="Databricks Storage (DSU)",
        dbu_total=dsu,
        price_per_dbu=price_per_dsu,
        cost_usd=round(cost, 2),
        details=f"GB×1 + writes_1k×0.3535 + reads_1k×0.0226 + vector_units×10 = {dsu:.2f} DSUs",
    )


def estimate_model_serving_cpu(
    concurrent_request_hours_per_month: float,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> EstimateResult:
    """Estimate monthly cost for CPU model serving (1 DBU/hr per concurrent request). Source: model-serving page."""
    dbu_total = MODEL_SERVING_CPU_DBU_PER_HOUR * concurrent_request_hours_per_month
    price_per_dbu = get_price_per_dbu(cloud, region)
    cost = dbu_total * price_per_dbu
    label = _region_label(cloud, region)
    return EstimateResult(
        description=f"CPU Model Serving — {cloud} · {label}",
        dbu_total=dbu_total,
        price_per_dbu=price_per_dbu,
        cost_usd=round(cost, 2),
        details=f"1 DBU/hr per concurrent request × {concurrent_request_hours_per_month:,.0f} request-hours = {dbu_total:,.0f} DBUs",
    )


def estimate_ai_parse(
    pages_1k: float,
    complexity: str,
    cloud: str = "AWS",
    region: str = "us-east-1",
    apply_promo: bool = True,
) -> EstimateResult:
    """Estimate cost for AI Parse Document (DBU per 1k pages by complexity).
    apply_promo: auto-applies 50% discount if current date is before promo expiry.
    Source: ai-parse page."""
    dbu_per_1k = AI_PARSE_DBU_PER_1K_PAGES.get(complexity)
    if dbu_per_1k is None:
        valid = ", ".join(AI_PARSE_DBU_PER_1K_PAGES.keys())
        raise ValueError(f"Unknown complexity '{complexity}'. Valid: {valid}")
    dbu_total = dbu_per_1k * pages_1k
    price_per_dbu = get_price_per_dbu(cloud, region)
    cost = dbu_total * price_per_dbu

    promo_applied = False
    if apply_promo:
        expiry = datetime.date.fromisoformat(AI_PARSE_PROMO_EXPIRY)
        if datetime.date.today() <= expiry:
            cost *= (1 - AI_PARSE_PROMO_DISCOUNT)
            promo_applied = True

    label = _region_label(cloud, region)
    promo_note = " (50% promo applied)" if promo_applied else ""
    return EstimateResult(
        description=f"AI Parse Document ({complexity}){promo_note} — {cloud} · {label}",
        dbu_total=dbu_total,
        price_per_dbu=price_per_dbu,
        cost_usd=round(cost, 2),
        details=f"{dbu_per_1k} DBU/1k pages × {pages_1k} (1k pages) = {dbu_total:,.0f} DBUs{promo_note}",
    )


def estimate_foundation_model_tokens(
    model: str,
    input_millions: float = 0,
    output_millions: float = 0,
    provisioned_hours: float = 0,
    scaling_capacity_hours: float = 0,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> EstimateResult:
    """Estimate cost for Foundation Model Serving (pay-per-token and/or provisioned).
    scaling_capacity_hours: additional hours at the scaling capacity rate (higher than entry PT).
    Source: foundation-model-serving page."""
    rates = FOUNDATION_MODEL_DBU_PER_MILLION.get(model)
    if not rates:
        valid = ", ".join(FOUNDATION_MODEL_DBU_PER_MILLION.keys())
        raise ValueError(f"Unknown model '{model}'. Valid: {valid}")
    price_per_dbu = get_price_per_dbu(cloud, region)
    dbu_total = 0.0
    parts = []
    if input_millions > 0 and rates.get("input"):
        dbu_input = rates["input"] * input_millions
        dbu_total += dbu_input
        parts.append(f"input {input_millions}M × {rates['input']} DBU/M = {dbu_input:,.0f} DBU")
    if output_millions > 0 and rates.get("output"):
        dbu_output = rates["output"] * output_millions
        dbu_total += dbu_output
        parts.append(f"output {output_millions}M × {rates['output']} DBU/M = {dbu_output:,.0f} DBU")
    if provisioned_hours > 0 and rates.get("provisioned_per_hour"):
        dbu_pt = rates["provisioned_per_hour"] * provisioned_hours
        dbu_total += dbu_pt
        parts.append(f"PT entry {provisioned_hours}h × {rates['provisioned_per_hour']} DBU/h = {dbu_pt:,.0f} DBU")
    if scaling_capacity_hours > 0 and rates.get("scaling_capacity_per_hour"):
        dbu_sc = rates["scaling_capacity_per_hour"] * scaling_capacity_hours
        dbu_total += dbu_sc
        parts.append(f"PT scaling {scaling_capacity_hours}h × {rates['scaling_capacity_per_hour']} DBU/h = {dbu_sc:,.0f} DBU")
    if dbu_total <= 0:
        raise ValueError("Set at least one of input_millions, output_millions, provisioned_hours, or scaling_capacity_hours > 0")
    cost = dbu_total * price_per_dbu
    label = _region_label(cloud, region)
    return EstimateResult(
        description=f"Foundation Model ({model}) — {cloud} · {label}",
        dbu_total=dbu_total,
        price_per_dbu=price_per_dbu,
        cost_usd=round(cost, 2),
        details=" | ".join(parts) if parts else f"{dbu_total:,.0f} DBUs",
    )


def estimate_agent_evaluation(
    evaluation_type: str,
    input_millions: float = 0,
    output_millions: float = 0,
    questions: float = 0,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> EstimateResult:
    """Estimate cost for Agent Evaluation (LLM Judge or Synthetic Data). Source: agent-evaluation page."""
    rates = AGENT_EVALUATION_DBU.get(evaluation_type)
    if not rates:
        valid = ", ".join(AGENT_EVALUATION_DBU.keys())
        raise ValueError(f"Unknown evaluation type '{evaluation_type}'. Valid: {valid}")
    price_per_dbu = get_price_per_dbu(cloud, region)
    dbu_total = 0.0
    parts = []
    if "input_per_m_tokens" in rates and input_millions > 0:
        dbu_in = rates["input_per_m_tokens"] * input_millions
        dbu_total += dbu_in
        parts.append(f"input {input_millions}M × {rates['input_per_m_tokens']} = {dbu_in:,.0f} DBU")
    if "output_per_m_tokens" in rates and output_millions > 0:
        dbu_out = rates["output_per_m_tokens"] * output_millions
        dbu_total += dbu_out
        parts.append(f"output {output_millions}M × {rates['output_per_m_tokens']} = {dbu_out:,.0f} DBU")
    if "per_question" in rates and questions > 0:
        dbu_q = rates["per_question"] * questions
        dbu_total += dbu_q
        parts.append(f"questions {questions:,.0f} × {rates['per_question']} = {dbu_q:,.0f} DBU")
    if dbu_total <= 0:
        raise ValueError("Set at least one of input_millions, output_millions, or questions > 0")
    cost = dbu_total * price_per_dbu
    label = _region_label(cloud, region)
    return EstimateResult(
        description=f"Agent Evaluation ({evaluation_type}) — {cloud} · {label}",
        dbu_total=dbu_total,
        price_per_dbu=price_per_dbu,
        cost_usd=round(cost, 2),
        details=" | ".join(parts) if parts else f"{dbu_total:,.0f} DBUs",
    )


def estimate_shutterstock_imageai(
    images: float,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> EstimateResult:
    """Estimate cost for Shutterstock ImageAI (DBU per image). Source: mosaic-imageai-serving page."""
    dbu_total = SHUTTERSTOCK_DBU_PER_IMAGE * images
    price_per_dbu = get_price_per_dbu(cloud, region)
    cost = dbu_total * price_per_dbu
    label = _region_label(cloud, region)
    return EstimateResult(
        description=f"Shutterstock ImageAI — {images:,.0f} images — {cloud} · {label}",
        dbu_total=dbu_total,
        price_per_dbu=price_per_dbu,
        cost_usd=round(cost, 2),
        details=f"{SHUTTERSTOCK_DBU_PER_IMAGE} DBU/image × {images:,.0f} images = {dbu_total:,.0f} DBUs",
    )


def estimate_proprietary_foundation_model(
    model: str,
    input_millions: float = 0,
    output_millions: float = 0,
    tier: str = "global",
    cache_write_millions: float = 0,
    cache_read_millions: float = 0,
    batch_hours: float = 0,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> EstimateResult:
    """Estimate cost for Proprietary Foundation Model Serving (pay-per-token).
    Supports tiers: global, in_geo, long_context.
    Supports cache_write/cache_read tokens and batch inference hours.
    Source: proprietary-foundation-model-serving page."""
    rates = get_proprietary_model_rates(model, tier)
    if not rates:
        valid = ", ".join(PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION.keys())
        raise ValueError(f"Unknown model '{model}'. Valid: {valid}")
    price_per_dbu = get_price_per_dbu(cloud, region)
    dbu_total = 0.0
    parts = []
    tier_label = {"global": "Global", "in_geo": "In-Geo", "long_context": "Long Context"}.get(tier, tier)
    if input_millions > 0 and rates.get("input"):
        dbu_in = rates["input"] * input_millions
        dbu_total += dbu_in
        parts.append(f"input {input_millions}M × {rates['input']} = {dbu_in:,.0f} DBU")
    if output_millions > 0 and rates.get("output"):
        dbu_out = rates["output"] * output_millions
        dbu_total += dbu_out
        parts.append(f"output {output_millions}M × {rates['output']} = {dbu_out:,.0f} DBU")
    if cache_write_millions > 0 and rates.get("cache_write"):
        dbu_cw = rates["cache_write"] * cache_write_millions
        dbu_total += dbu_cw
        parts.append(f"cache write {cache_write_millions}M × {rates['cache_write']} = {dbu_cw:,.0f} DBU")
    if cache_read_millions > 0 and rates.get("cache_read"):
        dbu_cr = rates["cache_read"] * cache_read_millions
        dbu_total += dbu_cr
        parts.append(f"cache read {cache_read_millions}M × {rates['cache_read']} = {dbu_cr:,.0f} DBU")
    if batch_hours > 0 and rates.get("batch"):
        dbu_batch = rates["batch"] * batch_hours
        dbu_total += dbu_batch
        parts.append(f"batch {batch_hours}h × {rates['batch']} = {dbu_batch:,.0f} DBU")
    if dbu_total <= 0:
        raise ValueError("Set at least one of input_millions, output_millions, cache_write/read_millions, or batch_hours > 0")
    cost = dbu_total * price_per_dbu
    label = _region_label(cloud, region)
    return EstimateResult(
        description=f"Proprietary Foundation Model ({model}, {tier_label}) — {cloud} · {label}",
        dbu_total=dbu_total,
        price_per_dbu=price_per_dbu,
        cost_usd=round(cost, 2),
        details=" | ".join(parts) if parts else f"{dbu_total:,.0f} DBUs",
    )


def estimate_vector_search_reranker(
    requests_1k: float,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> EstimateResult:
    """Estimate cost for Vector Search Reranker (DBU per 1k requests). Source: vector-search page."""
    dbu_total = VECTOR_SEARCH_RERANKER_DBU_PER_1K_REQUESTS * requests_1k
    price_per_dbu = get_price_per_dbu(cloud, region)
    cost = dbu_total * price_per_dbu
    label = _region_label(cloud, region)
    return EstimateResult(
        description=f"Vector Search Reranker — {requests_1k:,.0f}k requests — {cloud} · {label}",
        dbu_total=dbu_total,
        price_per_dbu=price_per_dbu,
        cost_usd=round(cost, 2),
        details=f"{VECTOR_SEARCH_RERANKER_DBU_PER_1K_REQUESTS} DBU/1k requests × {requests_1k:,.0f}k = {dbu_total:,.0f} DBUs",
    )


def estimate_gateway_payload(
    payload_gb_per_month: float,
    cloud: str = "AWS",
    region: str = "us-east-1",
) -> EstimateResult:
    """Estimate cost for Mosaic AI Gateway Inference Tables + Usage Tracking.
    Inference Tables: 7.143 DBU/GB, Usage Tracking: 1.429 DBU/GB.
    Source: mosaic-ai-gateway page."""
    combined_dbu_per_gb = GATEWAY_INFERENCE_TABLES_DBU_PER_GB + GATEWAY_USAGE_TRACKING_DBU_PER_GB
    dbu_total = combined_dbu_per_gb * payload_gb_per_month
    price_per_dbu = get_price_per_dbu(cloud, region)
    cost = dbu_total * price_per_dbu
    label = _region_label(cloud, region)
    return EstimateResult(
        description=f"Mosaic AI Gateway (Inference Tables + Usage Tracking) — {cloud} · {label}",
        dbu_total=dbu_total,
        price_per_dbu=price_per_dbu,
        cost_usd=round(cost, 2),
        details=f"{payload_gb_per_month:,.1f} GB/mo × {combined_dbu_per_gb:.3f} DBU/GB = {dbu_total:,.2f} DBUs",
    )
