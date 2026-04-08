#!/usr/bin/env python3
"""CLI for Databricks pricing estimates."""

import argparse
import json
from calculator import (
    estimate_sql_warehouse,
    estimate_vector_search,
    estimate_compute_dbu,
    estimate_model_training,
    estimate_model_serving_gpu,
    estimate_model_serving_cpu,
    estimate_storage,
    estimate_ai_parse,
    estimate_foundation_model_tokens,
)
from scenarios import (
    calculate_pt_vs_ppt_breakeven,
    compare_models,
    estimate_rag_scenario,
    estimate_multi_agent_scenario,
    estimate_batch_pipeline_scenario,
    estimate_fine_tune_scenario,
    inference_model_names,
)
from pricing_data import (
    CLOUDS,
    REGIONS_BY_CLOUD,
    DEFAULT_REGION_BY_CLOUD,
    FULL_SKU_CATALOG,
    BILLING_ORIGIN_PRODUCT_TO_CATEGORY,
    DATA_TRANSFER_CONNECTIVITY_SKUS,
    SQL_SERVERLESS_DBU_PER_HOUR,
    VECTOR_SEARCH_DBU_PER_HOUR,
    MODEL_TRAINING_DBU_ESTIMATES,
    EXAMPLE_PRICE_PER_DBU_BY_WORKLOAD,
    MODEL_SERVING_GPU_DBU_PER_HOUR,
    AI_PARSE_DBU_PER_1K_PAGES,
    FOUNDATION_MODEL_DBU_PER_MILLION,
    get_all_models_with_pt,
)
GPU_SIZES = list(MODEL_SERVING_GPU_DBU_PER_HOUR.keys())


def _print_result(r):
    print(f"  {r.description}")
    print(f"  DBUs: {r.dbu_total:,.2f}  |  $/DBU: ${r.price_per_dbu:.4f}  |  Est. cost: ${r.cost_usd:,.2f}")
    if r.details:
        print(f"  ({r.details})")
    print()


def cmd_sql(args):
    r = estimate_sql_warehouse(args.size, args.hours, cloud=args.cloud, region=args.region)
    _print_result(r)
    return r.cost_usd


def cmd_vector_search(args):
    r = estimate_vector_search(args.tier, args.units, args.hours, cloud=args.cloud, region=args.region)
    _print_result(r)
    return r.cost_usd


def cmd_compute(args):
    r = estimate_compute_dbu(args.workload, args.dbu_hours, cloud=args.cloud, region=args.region)
    _print_result(r)
    return r.cost_usd


def cmd_training(args):
    r = estimate_model_training(args.model, args.scale, cloud=args.cloud, region=args.region)
    _print_result(r)
    return r.cost_usd


def cmd_serving_gpu(args):
    r = estimate_model_serving_gpu(args.size, args.hours, cloud=args.cloud, region=args.region)
    _print_result(r)
    return r.cost_usd


def cmd_storage(args):
    r = estimate_storage(
        stored_gb=args.gb,
        writes_1k=args.writes_1k,
        reads_1k=args.reads_1k,
        vector_search_units=args.vector_units,
        price_per_dsu=args.price_per_dsu,
    )
    _print_result(r)
    return r.cost_usd


def cmd_serving_cpu(args):
    r = estimate_model_serving_cpu(args.request_hours, cloud=args.cloud, region=args.region)
    _print_result(r)
    return r.cost_usd


def cmd_ai_parse(args):
    r = estimate_ai_parse(args.pages_1k, args.complexity, cloud=args.cloud, region=args.region)
    _print_result(r)
    return r.cost_usd


def cmd_foundation_model(args):
    r = estimate_foundation_model_tokens(
        args.model,
        input_millions=args.input_m,
        output_millions=args.output_m,
        provisioned_hours=args.provisioned_hours,
        cloud=args.cloud,
        region=args.region,
    )
    _print_result(r)
    return r.cost_usd


def cmd_breakeven(args):
    result = calculate_pt_vs_ppt_breakeven(
        args.model, args.input_tokens, args.output_tokens,
        args.qpm, args.uptime, cloud=args.cloud, region=args.region,
    )
    print(f"  Model: {result.model}")
    print(f"  Pay-Per-Token (monthly):        ${result.ppt_monthly:,.2f}")
    print(f"  Provisioned Throughput (monthly): ${result.pt_monthly:,.2f}")
    print(f"  Cheaper mode: {result.cheaper_mode}")
    print(f"  Break-even at: {result.break_even_qpm:.1f} queries/min")
    savings = abs(result.ppt_monthly - result.pt_monthly)
    print(f"  Savings: ${savings:,.2f}/month")
    print()


def cmd_compare(args):
    result = compare_models(args.models, args.input_m, args.output_m, cloud=args.cloud, region=args.region)
    print("  Model comparison:")
    for model, cost, detail in zip(result.models, result.costs, result.details):
        print(f"    {model}: ${cost:,.2f}/month  ({detail.details})")
    cheapest = result.models[result.costs.index(min(result.costs))]
    print(f"\n  Cheapest: {cheapest}")
    print()


def cmd_scenario(args):
    if args.scenario_type == "rag":
        result = estimate_rag_scenario(
            args.docs, 5, 20, args.queries_day,
            "GTE", args.llm_model or "Llama 3.3 70B",
            "Medium (text + tables + images, e.g. 10-Ks)",
            cloud=args.cloud, region=args.region,
        )
    elif args.scenario_type == "agent":
        result = estimate_multi_agent_scenario(
            requests_per_day=args.requests_day,
            avg_steps_per_request=args.steps, tools_per_step=args.tools,
            orchestrator_model=args.orch_model or "Llama 3.3 70B",
            worker_model=args.worker_model or "Llama 3.1 8B",
            cloud=args.cloud, region=args.region,
        )
    elif args.scenario_type == "batch":
        result = estimate_batch_pipeline_scenario(
            args.docs, 5, "Medium (text + tables + images, e.g. 10-Ks)",
            args.frequency, args.output_model or "Llama 3.3 70B",
            cloud=args.cloud, region=args.region,
        )
    elif args.scenario_type == "fine-tune":
        result = estimate_fine_tune_scenario(
            args.model or "Llama 3.3 70B", args.scale or "10M tokens",
            2, 100, args.serving_hours, cloud=args.cloud, region=args.region,
        )
    else:
        print(f"Unknown scenario: {args.scenario_type}")
        return

    print(f"  {result.name}: ${result.total_monthly_usd:,.2f}/month")
    for li in result.line_items:
        pct = (li.estimate.cost_usd / result.total_monthly_usd * 100) if result.total_monthly_usd > 0 else 0
        print(f"    {li.service}: ${li.estimate.cost_usd:,.2f} ({pct:.0f}%)")
    print()


def cmd_list(args):
    if args.what == "sql-sizes":
        print("SQL Serverless warehouse sizes (DBU/hour):")
        for k, v in SQL_SERVERLESS_DBU_PER_HOUR.items():
            print(f"  {k}: {v}")
    elif args.what == "vector-tiers":
        print("Vector Search tiers:")
        for k, v in VECTOR_SEARCH_DBU_PER_HOUR.items():
            print(f"  {k}: {v['dbu_per_hour']} DBU/hr, {v['vector_capacity_per_unit']:,} vectors/unit")
    elif args.what == "workloads":
        print("Example $/DBU by workload (indicative):")
        for k, v in EXAMPLE_PRICE_PER_DBU_BY_WORKLOAD.items():
            print(f"  {k}: ${v}")
    elif args.what == "training-models":
        print("Model training DBU estimates:")
        for model, scales in MODEL_TRAINING_DBU_ESTIMATES.items():
            print(f"  {model}: {scales}")
    elif args.what == "clouds":
        print("Clouds:", ", ".join(CLOUDS))
    elif args.what == "regions":
        cloud = getattr(args, "cloud", None) or "AWS"
        print(f"Regions for {cloud}:")
        for rid, (label, price) in REGIONS_BY_CLOUD.get(cloud, {}).items():
            print(f"  {rid} — {label} (${price:.3f}/DBU)")
    elif args.what == "skus":
        cloud = getattr(args, "cloud", None)
        if cloud:
            cats = FULL_SKU_CATALOG.get(cloud, {})
            if not cats:
                print(f"No SKU catalog for cloud '{cloud}'. Clouds: {', '.join(FULL_SKU_CATALOG.keys())}")
                return 0
            print(f"SKUs for {cloud} (source: databricks.com/product/sku-groups):")
            for category, skus in cats.items():
                print(f"\n  [{category}]")
                for s in skus:
                    print(f"    {s}")
        else:
            print("All clouds – SKU catalog (source: databricks.com/product/sku-groups):")
            for c in FULL_SKU_CATALOG:
                n = sum(len(skus) for skus in FULL_SKU_CATALOG[c].values())
                print(f"  {c}: {n} SKUs across {len(FULL_SKU_CATALOG[c])} categories")
            print("\nUse: list skus --cloud AWS|GCP|Azure|MCT to list by cloud.")
    elif args.what == "billing-products":
        print("Billing origin product -> category (source: docs billable usage system table):")
        for product, category in sorted(BILLING_ORIGIN_PRODUCT_TO_CATEGORY.items()):
            print(f"  {product}: {category}")
    elif args.what == "ai-parse-complexity":
        print("AI Parse complexity (DBU per 1k pages):")
        for k, v in AI_PARSE_DBU_PER_1K_PAGES.items():
            print(f"  {k}: {v}")
    elif args.what == "foundation-models":
        print("Foundation Model Serving models (pay-per-token / PT):")
        for m, r in FOUNDATION_MODEL_DBU_PER_MILLION.items():
            parts = []
            if r.get("input") is not None:
                parts.append(f"input {r['input']} DBU/M")
            if r.get("output") is not None:
                parts.append(f"output {r['output']} DBU/M")
            if r.get("provisioned_per_hour") is not None:
                parts.append(f"PT {r['provisioned_per_hour']} DBU/hr")
            print(f"  {m}: {', '.join(parts)}")
    else:
        print("Usage: list sql-sizes | vector-tiers | workloads | training-models | clouds | regions | skus | billing-products | ai-parse-complexity | foundation-models")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Databricks pricing calculator (estimate only)")
    parser.add_argument("--cloud", choices=CLOUDS, default="AWS", help="Cloud provider (AWS, Azure, GCP)")
    parser.add_argument("--region", default=None, help="Region id (default: default for chosen cloud, e.g. us-east-1 for AWS)")
    sub = parser.add_subparsers(dest="command", help="Command")

    # sql
    p_sql = sub.add_parser("sql", help="SQL Serverless warehouse estimate")
    p_sql.add_argument("size", choices=list(SQL_SERVERLESS_DBU_PER_HOUR.keys()), help="Warehouse size")
    p_sql.add_argument("--hours", type=float, default=720, help="Hours per month")
    p_sql.set_defaults(func=cmd_sql)

    # vector-search
    p_vs = sub.add_parser("vector-search", help="Vector Search estimate")
    p_vs.add_argument("tier", choices=list(VECTOR_SEARCH_DBU_PER_HOUR.keys()))
    p_vs.add_argument("--units", type=int, default=1)
    p_vs.add_argument("--hours", type=float, default=720)
    p_vs.set_defaults(func=cmd_vector_search)

    # compute
    p_comp = sub.add_parser("compute", help="Compute cost from DBU-hours")
    p_comp.add_argument("workload", choices=list(EXAMPLE_PRICE_PER_DBU_BY_WORKLOAD.keys()))
    p_comp.add_argument("dbu_hours", type=float, help="Total DBU-hours")
    p_comp.set_defaults(func=cmd_compute)

    # training
    p_tr = sub.add_parser("training", help="Model training estimate")
    p_tr.add_argument("model", choices=list(MODEL_TRAINING_DBU_ESTIMATES.keys()))
    scales = set()
    for s in MODEL_TRAINING_DBU_ESTIMATES.values():
        scales.update(s.keys())
    p_tr.add_argument("scale", choices=list(scales))
    p_tr.set_defaults(func=cmd_training)

    # serving-gpu
    p_gpu = sub.add_parser("serving-gpu", help="GPU model serving estimate")
    p_gpu.add_argument("size", choices=GPU_SIZES)
    p_gpu.add_argument("--hours", type=float, default=720)
    p_gpu.set_defaults(func=cmd_serving_gpu)

    # serving-cpu
    p_cpu = sub.add_parser("serving-cpu", help="CPU model serving estimate")
    p_cpu.add_argument("request_hours", type=float, help="Concurrent request-hours per month")
    p_cpu.set_defaults(func=cmd_serving_cpu)

    # ai-parse
    p_ap = sub.add_parser("ai-parse", help="AI Parse Document estimate")
    p_ap.add_argument("pages_1k", type=float, help="Pages in thousands (e.g. 1 = 1000 pages)")
    p_ap.add_argument("complexity", choices=list(AI_PARSE_DBU_PER_1K_PAGES.keys()))
    p_ap.set_defaults(func=cmd_ai_parse)

    # foundation-model
    fm_models = list(FOUNDATION_MODEL_DBU_PER_MILLION.keys())
    p_fm = sub.add_parser("foundation-model", help="Foundation Model Serving (pay-per-token) estimate")
    p_fm.add_argument("model", choices=fm_models)
    p_fm.add_argument("--input-m", type=float, default=0, help="Input tokens (millions)")
    p_fm.add_argument("--output-m", type=float, default=0, help="Output tokens (millions)")
    p_fm.add_argument("--provisioned-hours", type=float, default=0, help="Provisioned Throughput hours")
    p_fm.set_defaults(func=cmd_foundation_model)

    # storage
    p_st = sub.add_parser("storage", help="Storage (DSU) estimate")
    p_st.add_argument("--gb", type=float, default=0, help="GB stored")
    p_st.add_argument("--writes-1k", type=float, default=0, help="Thousands of write ops")
    p_st.add_argument("--reads-1k", type=float, default=0, help="Thousands of read ops")
    p_st.add_argument("--vector-units", type=float, default=0, help="Vector Search storage units")
    p_st.add_argument("--price-per-dsu", type=float, default=0.07)
    p_st.set_defaults(func=cmd_storage)

    # breakeven
    p_be = sub.add_parser("breakeven", help="PT vs PPT break-even analysis")
    p_be.add_argument("model", choices=get_all_models_with_pt(), help="Foundation model")
    p_be.add_argument("--input-tokens", type=int, default=2000, help="Avg input tokens per query")
    p_be.add_argument("--output-tokens", type=int, default=500, help="Avg output tokens per query")
    p_be.add_argument("--qpm", type=float, default=5.0, help="Queries per minute")
    p_be.add_argument("--uptime", type=float, default=12, help="Uptime hours per day")
    p_be.set_defaults(func=cmd_breakeven)

    # compare
    p_cmp = sub.add_parser("compare", help="Compare model costs")
    p_cmp.add_argument("models", nargs="+", help="2-3 model names")
    p_cmp.add_argument("--input-m", type=float, default=10, help="Input tokens (millions/month)")
    p_cmp.add_argument("--output-m", type=float, default=2, help="Output tokens (millions/month)")
    p_cmp.set_defaults(func=cmd_compare)

    # scenario
    p_sc = sub.add_parser("scenario", help="Scenario TCO estimate")
    p_sc.add_argument("scenario_type", choices=["rag", "agent", "batch", "fine-tune"], help="Scenario type")
    p_sc.add_argument("--docs", type=int, default=10000, help="Number of documents")
    p_sc.add_argument("--queries-day", type=int, default=500, help="Queries per day (RAG)")
    p_sc.add_argument("--requests-day", type=int, default=500, help="Requests per day (agent)")
    p_sc.add_argument("--steps", type=int, default=5, help="Avg steps per request (agent)")
    p_sc.add_argument("--tools", type=int, default=2, help="Tools per step (agent)")
    p_sc.add_argument("--frequency", type=int, default=4, help="Runs per month (batch)")
    p_sc.add_argument("--serving-hours", type=float, default=12, help="Serving hours/day (fine-tune)")
    p_sc.add_argument("--llm-model", default=None, help="LLM model override")
    p_sc.add_argument("--orch-model", default=None, help="Orchestrator model (agent)")
    p_sc.add_argument("--worker-model", default=None, help="Worker model (agent)")
    p_sc.add_argument("--output-model", default=None, help="Output model (batch)")
    p_sc.add_argument("--model", default=None, help="Base model (fine-tune)")
    p_sc.add_argument("--scale", default=None, help="Training scale (fine-tune)")
    p_sc.set_defaults(func=cmd_scenario)

    # list
    p_list = sub.add_parser("list", help="List options")
    p_list.add_argument("what", choices=["sql-sizes", "vector-tiers", "workloads", "training-models", "clouds", "regions", "skus", "billing-products", "ai-parse-complexity", "foundation-models"])
    p_list.add_argument("--cloud", default=None, help="For 'regions': AWS|GCP|Azure. For 'skus': AWS|GCP|Azure|MCT (omit to show summary)")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0
    # Resolve default region by cloud
    if getattr(args, "region", None) is None and hasattr(args, "cloud"):
        args.region = DEFAULT_REGION_BY_CLOUD.get(args.cloud, "us-east-1")
    args.func(args)
    return 0


if __name__ == "__main__":
    main()
