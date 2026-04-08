"""
Databricks pricing reference data.
This calculator is based on the following Databricks pricing pages (see PRICING_PAGES).
Additional sources: SKU groups, Azure/Microsoft Learn serverless DBU docs, system.billing.

Disclaimer: List prices and DBU rates are for estimation only. Actual prices vary by
plan, region, and over time. Use system.billing.list_prices in your workspace for
current SKU pricing, or the official calculator.
"""

BASE_URL = "https://www.databricks.com/product/pricing"

# --- Canonical list of pricing pages this calculator is based on ---
# Category matches the left-nav on https://www.databricks.com/product/pricing
# calculator_tab: which app tab (if any) uses this page's data
PRICING_PAGES = [
    {"category": "Overview", "label": "Databricks Pricing", "path": "", "calculator_tab": None},
    {"category": "Data Engineering", "label": "Lakeflow Jobs", "path": "lakeflow-jobs", "calculator_tab": "compute"},
    {"category": "Data Engineering", "label": "Lakeflow Spark Declarative Pipelines", "path": "lakeflow-spark-declarative-pipelines", "calculator_tab": "compute"},
    {"category": "Data Engineering", "label": "Lakeflow Connect", "path": "lakeflow-connect", "calculator_tab": "compute"},
    {"category": "Databricks SQL", "label": "Databricks SQL", "path": "databricks-sql", "calculator_tab": "sql"},
    {"category": "Operational Database", "label": "Lakebase", "path": "lakebase", "calculator_tab": "compute"},
    {"category": "Interactive workloads", "label": "Compute for Data Science", "path": "datascience-ml", "calculator_tab": "compute"},
    {"category": "Interactive workloads", "label": "Databricks Apps", "path": "databricks-apps", "calculator_tab": "compute"},
    {"category": "Artificial Intelligence", "label": "Agent Bricks", "path": "agent-bricks", "calculator_tab": "gpu"},
    {"category": "Artificial Intelligence", "label": "AI Parse Document", "path": "ai-parse", "calculator_tab": "ai_parse"},
    {"category": "Artificial Intelligence", "label": "Mosaic AI Gateway", "path": "mosaic-ai-gateway", "calculator_tab": "gpu"},
    {"category": "Artificial Intelligence", "label": "Model Serving", "path": "model-serving", "calculator_tab": "gpu"},
    {"category": "Artificial Intelligence", "label": "Foundation Model Serving", "path": "foundation-model-serving", "calculator_tab": "gpu"},
    {"category": "Artificial Intelligence", "label": "Proprietary Foundation Model Serving", "path": "proprietary-foundation-model-serving", "calculator_tab": "gpu"},
    {"category": "Artificial Intelligence", "label": "Shutterstock ImageAI", "path": "mosaic-imageai-serving", "calculator_tab": "imageai"},
    {"category": "Artificial Intelligence", "label": "Vector Search", "path": "vector-search", "calculator_tab": "vector"},
    {"category": "Artificial Intelligence", "label": "Agent Evaluation", "path": "agent-evaluation", "calculator_tab": "agent_eval"},
    {"category": "Artificial Intelligence", "label": "Model Training", "path": "mosaic-foundation-model-training", "calculator_tab": "training"},
    {"category": "Platform", "label": "Tiers and Add-ons", "path": "platform-addons", "calculator_tab": None},
    {"category": "Platform", "label": "Managed Services", "path": "managed-services", "calculator_tab": None},
    {"category": "Platform", "label": "Data Transfer and Connectivity", "path": "data-transfer-connectivity", "calculator_tab": None},
    {"category": "Platform", "label": "Storage", "path": "storage", "calculator_tab": "storage"},
    {"category": "Platform", "label": "Delta Share from SAP BDC", "path": "delta-share-sap-business-data-cloud", "calculator_tab": None},
    {"category": "Collaboration", "label": "Clean Rooms", "path": "clean-rooms", "calculator_tab": "compute"},
    {"category": "Collaboration", "label": "View Sharing", "path": "view-sharing", "calculator_tab": None},
    {"category": "Beta Products", "label": "Beta Products", "path": "beta-products", "calculator_tab": None},
    {"category": "Calculator", "label": "Databricks Pricing Calculator (instance types)", "path": "product-pricing/instance-types", "calculator_tab": None},
    {"category": "Calculator", "label": "Generative AI Pricing Calculator", "path": "genai-pricing-calculator", "calculator_tab": None},
    {"category": "Calculator", "label": "SAP Databricks Sizing Calculator", "path": "sap-databricks-pricing-calculator", "calculator_tab": None},
]


def get_pricing_page_url(path: str) -> str:
    if not path:
        return BASE_URL
    return f"{BASE_URL}/{path}" if not path.startswith("http") else path


# --- Clouds and regions (effective $/DBU examples; US often base) ---
# Align with: docs.databricks.com (AWS/GCP supported-regions), learn.microsoft.com/azure/databricks/resources/supported-regions (Azure).
# Azure pricing set by Microsoft. Add any new region from the official lists so the app matches the web pricing dropdowns.
# Structure: cloud -> region_id -> (display_label, price_per_dbu_usd)
REGIONS_BY_CLOUD = {
    "AWS": {
        "us-east-1": ("US East (N. Virginia)", 0.07),
        "us-east-2": ("US East (Ohio)", 0.07),
        "us-west-1": ("US West (N. California)", 0.075),
        "us-west-2": ("US West (Oregon)", 0.07),
        "ca-central-1": ("Canada (Central)", 0.07),
        "eu-west-1": ("EU (Ireland)", 0.077),
        "eu-west-2": ("EU (London)", 0.079),
        "eu-west-3": ("EU (Paris)", 0.077),
        "eu-central-1": ("EU (Frankfurt)", 0.077),
        "ap-northeast-1": ("Asia Pacific (Tokyo)", 0.085),
        "ap-northeast-2": ("Asia Pacific (Seoul)", 0.085),
        "ap-southeast-1": ("Asia Pacific (Singapore)", 0.088),
        "ap-southeast-2": ("Asia Pacific (Sydney)", 0.088),
        "ap-southeast-3": ("Asia Pacific (Jakarta)", 0.088),
        "ap-south-1": ("Asia Pacific (Mumbai)", 0.085),
        "sa-east-1": ("South America (Sao Paulo)", 0.088),
    },
    "Azure": {
        "eastus": ("East US", 0.07),
        "eastus2": ("East US 2", 0.07),
        "centralus": ("Central US", 0.07),
        "northcentralus": ("North Central US", 0.07),
        "southcentralus": ("South Central US", 0.07),
        "westcentralus": ("West Central US", 0.07),
        "westus": ("West US", 0.075),
        "westus2": ("West US 2", 0.07),
        "westus3": ("West US 3", 0.07),
        "canadacentral": ("Canada Central", 0.07),
        "brazilsouth": ("Brazil South", 0.088),
        "westeurope": ("West Europe", 0.077),
        "northeurope": ("North Europe", 0.077),
        "francecentral": ("France Central", 0.077),
        "germanywestcentral": ("Germany West Central", 0.077),
        "swedencentral": ("Sweden Central", 0.077),
        "norwayeast": ("Norway East", 0.077),
        "switzerlandnorth": ("Switzerland North", 0.077),
        "switzerlandwest": ("Switzerland West", 0.077),
        "uksouth": ("UK South", 0.079),
        "ukwest": ("UK West", 0.079),
        "southeastasia": ("Southeast Asia", 0.088),
        "eastasia": ("East Asia (Hong Kong)", 0.088),
        "japaneast": ("Japan East", 0.085),
        "japanwest": ("Japan West", 0.085),
        "koreacentral": ("Korea Central", 0.085),
        "centralindia": ("Central India", 0.085),
        "southindia": ("South India", 0.085),
        "westindia": ("West India", 0.085),
        "australiaeast": ("Australia East", 0.088),
        "australiasoutheast": ("Australia Southeast", 0.088),
        "australiacentral": ("Australia Central", 0.088),
        "australiacentral2": ("Australia Central 2", 0.088),
        "uaenorth": ("UAE North", 0.088),
        "qatarcentral": ("Qatar Central", 0.088),
        "southafricanorth": ("South Africa North", 0.088),
        "mexicocentral": ("Mexico Central", 0.085),
    },
    "GCP": {
        "us-central1": ("us-central1 (Iowa)", 0.07),
        "us-east4": ("us-east4 (N. Virginia)", 0.07),
        "us-east1": ("us-east1 (South Carolina)", 0.07),
        "us-west1": ("us-west1 (Oregon)", 0.07),
        "us-west4": ("us-west4 (Nevada)", 0.07),
        "northamerica-northeast1": ("North America (Montreal)", 0.07),
        "southamerica-east1": ("South America (São Paulo)", 0.088),
        "europe-west1": ("europe-west1 (Belgium)", 0.077),
        "europe-west2": ("europe-west2 (London)", 0.079),
        "europe-west3": ("europe-west3 (Frankfurt)", 0.077),
        "europe-west4": ("europe-west4 (Netherlands)", 0.077),
        "asia-northeast1": ("asia-northeast1 (Tokyo)", 0.085),
        "asia-southeast1": ("asia-southeast1 (Singapore)", 0.088),
        "australia-southeast1": ("australia-southeast1 (Sydney)", 0.088),
        "asia-south1": ("asia-south1 (Mumbai)", 0.085),
        "me-central2": ("me-central2 (Dammam)", 0.088),
    },
}

# Default region per cloud (for CLI/API when region not specified)
DEFAULT_REGION_BY_CLOUD = {"AWS": "us-east-1", "Azure": "eastus", "GCP": "us-central1"}

# --- SQL Serverless warehouse sizes (DBU per hour) ---
# Source: Azure Databricks docs - Serverless DBU consumption by SKU
SQL_SERVERLESS_DBU_PER_HOUR = {
    "2X-Small": 4,
    "X-Small": 6,
    "Small": 12,
    "Medium": 24,
    "Large": 40,
    "X-Large": 80,
    "2X-Large": 144,
    "3X-Large": 272,
    "4X-Large": 528,
}


# --- Vector Search ---
# Source: https://www.databricks.com/product/pricing/vector-search
# DBU/hour per unit; capacity in vectors (768 dim) per unit
VECTOR_SEARCH_DBU_PER_HOUR = {
    "Standard": {"dbu_per_hour": 4.0, "vector_capacity_per_unit": 2_000_000},
    "Storage Optimized": {"dbu_per_hour": 18.29, "vector_capacity_per_unit": 64_000_000},
}


# --- Model Serving (Serverless Real-Time Inference) ---
# Source: https://www.databricks.com/product/pricing/model-serving (GPU table);
# Azure docs for CPU.
# CPU: 1 concurrent request/hr = 1 DBU/hr
MODEL_SERVING_CPU_DBU_PER_HOUR = 1.0

# GPU Serving DBU/hr by instance size (model-serving page + Azure doc)
MODEL_SERVING_GPU_DBU_PER_HOUR = {
    "Small": 10.48,           # T4 or equivalent
    "Medium": 20.00,         # A10G x 1
    "Medium 4X": 112.00,     # A10G x 4
    "Medium 8x": 290.80,     # A10G x 8
    "XLarge": 78.60,         # A100 80GB x 1
    "2XLarge": 157.20,       # A100 80GB x 2
    "4XLarge": 314.40,       # A100 80GB x 4
    "Large 8X 40GB": 538.40, # A100 40GB x 8
    "Large 8X 80GB": 628.00, # A100 80GB x 8
}

# --- Foundation Model Serving (pay-per-token) ---
# Source: https://www.databricks.com/product/pricing/foundation-model-serving
# DBU per 1M input tokens, per 1M output tokens; optional provisioned_per_hour (DBU/hr).
FOUNDATION_MODEL_DBU_PER_MILLION = {
    "Llama 4 Maverick": {"input": 7.143, "output": 21.429, "provisioned_per_hour": 85.714, "scaling_capacity_per_hour": None},
    "Llama 3.3 70B": {"input": 7.143, "output": 21.429, "provisioned_per_hour": 85.714, "scaling_capacity_per_hour": 342.857},
    "Llama 3.1 405B (deprecated)": {"input": 35.714, "output": 142.857, "provisioned_per_hour": 150.0, "scaling_capacity_per_hour": None},  # PPT retired; PT retiring May 15, 2026
    "Llama 3.1 8B": {"input": 2.143, "output": 6.429, "provisioned_per_hour": 53.571, "scaling_capacity_per_hour": 106.0},
    "Llama 3.2 3B": {"input": None, "output": None, "provisioned_per_hour": 46.429, "scaling_capacity_per_hour": 92.857},
    "Llama 3.2 1B": {"input": None, "output": None, "provisioned_per_hour": 42.857, "scaling_capacity_per_hour": 85.714},
    "GPT OSS 120B": {"input": 2.143, "output": 8.571, "provisioned_per_hour": 71.429, "scaling_capacity_per_hour": None},
    "Gemma 3 12B": {"input": 2.143, "output": 7.143, "provisioned_per_hour": 71.429, "scaling_capacity_per_hour": None},
    "GPT OSS 20B": {"input": 1.0, "output": 4.286, "provisioned_per_hour": 53.571, "scaling_capacity_per_hour": None},
    "GTE": {"input": 1.857, "output": None, "provisioned_per_hour": 20.0, "scaling_capacity_per_hour": None},
    "BGE Large": {"input": 1.429, "output": None, "provisioned_per_hour": 24.0, "scaling_capacity_per_hour": None},
}

# --- Proprietary Foundation Model Serving (OpenAI, Anthropic, Google) ---
# Source: https://www.databricks.com/product/pricing/proprietary-foundation-model-serving
# Nested structure: model -> tier -> {input, output, cache_write, cache_read, batch}
# Tiers: "global" (always present), "in_geo" (optional, ~10% premium), "long_context" (optional, >200k tokens)
# cache_write/cache_read: DBU per 1M tokens for prompt caching
# batch: DBU/hr for batch inference
PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION = {
    # --- OpenAI ---
    "GPT 5.4": {
        "global": {"input": 35.714, "output": 214.286, "cache_write": 35.714, "cache_read": 3.571, "batch": 192.857},
        "in_geo": {"input": 39.285, "output": 235.715, "cache_write": 39.285, "cache_read": 3.929, "batch": 212.143},
    },
    "GPT 5.2/5.3 Codex": {
        "global": {"input": 25.0, "output": 200.0, "cache_write": 25.0, "cache_read": 2.5, "batch": None},
        "in_geo": {"input": 27.5, "output": 220.0, "cache_write": 27.5, "cache_read": 2.75, "batch": None},
    },
    "GPT 5.2": {
        "global": {"input": 25.0, "output": 200.0, "cache_write": 25.0, "cache_read": 2.5, "batch": 184.286},
        "in_geo": {"input": 27.5, "output": 220.0, "cache_write": 27.5, "cache_read": 2.75, "batch": 202.714},
    },
    "GPT 5.1": {
        "global": {"input": 17.857, "output": 142.857, "cache_write": 17.857, "cache_read": 1.786, "batch": 131.429},
        "in_geo": {"input": 19.643, "output": 157.143, "cache_write": 19.643, "cache_read": 1.965, "batch": 144.571},
    },
    "GPT 5.1 Codex Max": {
        "global": {"input": 17.857, "output": 142.857, "cache_write": 17.857, "cache_read": 1.786, "batch": None},
    },
    "GPT 5.1 Codex Mini": {
        "global": {"input": 3.571, "output": 28.571, "cache_write": 3.571, "cache_read": 0.357, "batch": None},
    },
    "GPT 5": {
        "global": {"input": 17.857, "output": 142.857, "cache_write": 17.857, "cache_read": 1.786, "batch": 131.429},
        "in_geo": {"input": 19.643, "output": 157.143, "cache_write": 19.643, "cache_read": 1.965, "batch": 144.571},
    },
    "GPT 5 mini": {
        "global": {"input": 3.571, "output": 28.571, "cache_write": 3.571, "cache_read": 0.357, "batch": 71.429},
    },
    "GPT 5 nano": {
        "global": {"input": 0.714, "output": 5.714, "cache_write": 0.714, "cache_read": 0.071, "batch": 53.571},
    },
    # --- Anthropic ---
    "Claude Opus 4.6": {
        "global": {"input": 71.429, "output": 357.143, "cache_write": 89.286, "cache_read": 7.143, "batch": 178.571},
        "in_geo": {"input": 78.571, "output": 392.857, "cache_write": 98.214, "cache_read": 7.857, "batch": 196.429},
        "long_context": {"input": 142.858, "output": 535.715, "cache_write": 178.572, "cache_read": 14.286, "batch": 178.571},
    },
    "Claude Opus 4.5": {
        "global": {"input": 71.429, "output": 357.143, "cache_write": 89.286, "cache_read": 7.143, "batch": 178.571},
        "in_geo": {"input": 78.571, "output": 392.857, "cache_write": 98.214, "cache_read": 7.857, "batch": 196.429},
        "long_context": {"input": 142.858, "output": 535.715, "cache_write": 178.572, "cache_read": 14.286, "batch": 178.571},
    },
    "Claude Opus 4/4.1": {
        "global": {"input": 214.286, "output": 1071.429, "cache_write": 267.857, "cache_read": 21.429, "batch": 514.286},
        "in_geo": {"input": 235.715, "output": 1178.572, "cache_write": 294.643, "cache_read": 23.572, "batch": 565.714},
    },
    "Claude Sonnet 4.5/4.6": {
        "global": {"input": 42.857, "output": 214.286, "cache_write": 53.571, "cache_read": 4.286, "batch": 214.286},
        "in_geo": {"input": 47.143, "output": 235.715, "cache_write": 58.928, "cache_read": 4.715, "batch": 235.715},
        "long_context": {"input": 85.714, "output": 321.429, "cache_write": 107.143, "cache_read": 8.571, "batch": 214.286},
        "in_geo_long_context": {"input": 94.285, "output": 353.572, "cache_write": 117.857, "cache_read": 9.428, "batch": 235.715},
    },
    "Claude Sonnet 4/4.1": {
        "global": {"input": 42.857, "output": 214.286, "cache_write": 53.571, "cache_read": 4.286, "batch": 214.286},
        "in_geo": {"input": 47.143, "output": 235.715, "cache_write": 58.928, "cache_read": 4.715, "batch": 235.715},
        "long_context": {"input": 85.714, "output": 321.429, "cache_write": 107.143, "cache_read": 8.571, "batch": 214.286},
        "in_geo_long_context": {"input": 94.285, "output": 353.572, "cache_write": 117.857, "cache_read": 9.428, "batch": 235.715},
    },
    "Claude Haiku 4.5": {
        "global": {"input": 14.286, "output": 71.429, "cache_write": 17.857, "cache_read": 1.429, "batch": 114.286},
        "in_geo": {"input": 15.715, "output": 78.572, "cache_write": 19.643, "cache_read": 1.572, "batch": 125.714},
    },
    # --- Google ---
    "Gemini 3.1 Pro": {
        "global": {"input": 35.714, "output": 214.286, "cache_write": 35.714, "cache_read": 3.571, "batch": 230.357},
        "in_geo": {"input": 39.285, "output": 235.715, "cache_write": 39.285, "cache_read": 3.929, "batch": 253.393},
        "long_context": {"input": 71.429, "output": 321.429, "cache_write": 71.429, "cache_read": 7.143, "batch": 230.357},
    },
    "Gemini 3.0 Flash": {
        "global": {"input": 8.929, "output": 53.571, "cache_write": 8.929, "cache_read": 0.893, "batch": 125.0},
        "long_context": {"input": 8.929, "output": 53.571, "cache_write": 8.929, "cache_read": 0.893, "batch": 125.0},
    },
    "Gemini 2.5 Pro": {
        "global": {"input": 17.857, "output": 142.857, "cache_write": None, "cache_read": None, "batch": 164.286},
        "long_context": {"input": 35.714, "output": 214.286, "cache_write": None, "cache_read": None, "batch": 164.286},
    },
    "Gemini 2.5 Flash": {
        "global": {"input": 4.286, "output": 35.714, "cache_write": None, "cache_read": None, "batch": 107.143},
    },
}


def get_proprietary_model_rates(model: str, tier: str = "global") -> dict | None:
    """Return flat rate dict for a proprietary model and tier.
    Falls back to 'global' if requested tier not found.
    """
    model_data = PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION.get(model)
    if not model_data:
        return None
    return model_data.get(tier) or model_data.get("global")


def get_proprietary_model_tiers(model: str) -> list[str]:
    """Return available pricing tiers for a proprietary model."""
    model_data = PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION.get(model)
    if not model_data:
        return []
    return list(model_data.keys())

# --- Mosaic AI Gateway (Inference Tables, Usage Tracking) ---
# Source: https://www.databricks.com/product/pricing/mosaic-ai-gateway
# Inference Tables: 7.143 DBU per 1 GB of payload
# Usage Tracking: 1.429 DBU per 1 GB of payload
# Combined rate (both features): 8.572 DBU per 1 GB
GATEWAY_INFERENCE_TABLES_DBU_PER_GB = 7.143
GATEWAY_USAGE_TRACKING_DBU_PER_GB = 1.429
# Legacy: per-1KB approximation for backward compat (Inference Tables + Usage Tracking combined)
GATEWAY_PAYLOAD_DBU_PER_1KB = (7.143 + 1.429) / (1024 * 1024)  # ~0.00000817 DBU/KB

# --- AI Parse Document ---
# Source: https://www.databricks.com/product/pricing/ai-parse
# Estimated SRTI DBUs per 1,000 pages by job complexity (midpoint of range used for calculation).
# Keys match page; use AI_PARSE_DOCUMENT_TYPE_LABELS for solution-oriented UI.
AI_PARSE_DBU_PER_1K_PAGES = {
    "Low (simple text, e.g. receipts, W2s)": 12.5,
    "Low (simple images + captions)": 22.5,
    "Medium (text + tables + images, e.g. 10-Ks)": 62.5,
    "High (complex diagrams + captions)": 87.5,
}

# AI Parse promotional discount (50% off through June 30, 2026)
AI_PARSE_PROMO_DISCOUNT = 0.50
AI_PARSE_PROMO_EXPIRY = "2026-06-30"

# Solution-oriented labels for AI Parse: "What are you parsing?" -> (display label, key in AI_PARSE_DBU_PER_1K_PAGES)
AI_PARSE_DOCUMENT_TYPE_LABELS = [
    ("Receipts, W2s (simple text)", "Low (simple text, e.g. receipts, W2s)"),
    ("Images with captions", "Low (simple images + captions)"),
    ("Company 10-Ks (tables + text + images)", "Medium (text + tables + images, e.g. 10-Ks)"),
    ("Engineering diagrams (complex)", "High (complex diagrams + captions)"),
]


# --- Model Training ---
# Source: Azure docs - Model Training Fine Tuning ($0.65/DBU US East cited)
MODEL_TRAINING_USD_PER_DBU_EAST = 0.65

MODEL_TRAINING_DBU_ESTIMATES = {
    "Llama 3.3 70B": {"10M tokens": 225, "500M tokens": 11000},
    "Llama 3.1 70B": {"10M tokens": 225, "500M tokens": 11000},
    "Llama 3.1 8B": {"10M tokens": 100, "500M tokens": 4400},
    "Llama 3.2 3B": {"10M tokens": 75, "500M tokens": 2750},
    "Llama 3.2 1B": {"10M tokens": 25, "500M tokens": 1100},
}


# --- Databricks Storage (DSU multipliers) ---
# Source: Azure Databricks - Databricks Storage SKU
STORAGE_DSU_MULTIPLIER = {
    "vector_search": 10.0,
    "per_gb_stored": 1.0,
    "per_1000_writes": 0.3535,
    "per_1000_reads": 0.0226,
    "lakebase_database": 15.0,
    "lakebase_pitr": 8.7,
    "lakebase_snapshots": 3.91,
}


# --- Serverless DBU multipliers (for consumption relative to base DBUs) ---
# Source: Azure - Automated / Interactive / Database Serverless SKU
SERVERLESS_DBU_MULTIPLIER = {
    "Automated": {"jobs": 1.0, "dlt": 1.0, "predictive_optimization": 1.0, "data_quality_monitoring": 2.0, "fgac": 1.0, "materialized_views_streaming_tables": 1.0, "data_classification": 3.0},
    "Interactive": {"notebook": 1.0, "apps_medium": 0.5, "apps_large": 1.0},
    "Database": {"lakebase_autoscaling": 0.213},
}


# --- Lakebase (Operational Database) ---
# Source: https://www.databricks.com/product/pricing/lakebase
# Compute: Database Serverless SKU with 0.213X DBU multiplier for autoscaling
# Storage: Uses STORAGE_DSU_MULTIPLIER lakebase_* keys above (15.0, 8.7, 3.91)
LAKEBASE_COMPUTE_DBU_MULTIPLIER = 0.213  # autoscaling compute


# --- Lakeflow Connect ---
# Source: https://www.databricks.com/product/pricing/lakeflow-connect
LAKEFLOW_CONNECT_USD_PER_DBU = 0.35  # flat rate, all clouds
LAKEFLOW_CONNECT_FREE_TIER_DBU_PER_DAY = 100  # Azure: 100 DBU/day free (~$35/day)
LAKEFLOW_CONNECT_ZEROBUS_USD_PER_GB = 0.050  # 50% promo until Sept 1, 2026


# --- List price per DBU by workload — PER CLOUD (Premium tier, US regions) ---
# Sources: learn.microsoft.com (Azure DBU multipliers confirmed), databricks.com pricing pages (JS-rendered),
#   azure.microsoft.com/pricing/details/databricks (timed out during scraping)
# VERIFICATION STATUS: The DBU consumption rates (DBU/hr, DBU/1M tokens) are confirmed via official docs.
#   The $/DBU rates below could NOT be fully verified via scraping (JS-rendered pages). They are derived
#   from the Databricks pricing pages and cross-referenced where possible. For authoritative per-customer
#   rates, use system.billing.list_prices in your workspace.
# Key insight: Azure is 10-100% more expensive than AWS/GCP depending on SKU
PRICE_PER_DBU_BY_WORKLOAD_AND_CLOUD = {
    "Jobs Compute": {"AWS": 0.15, "Azure": 0.30, "GCP": 0.15},
    "Jobs Compute (Photon)": {"AWS": 0.20, "Azure": 0.24, "GCP": 0.20},
    "Jobs Serverless": {"AWS": 0.37, "Azure": 0.45, "GCP": 0.37},
    "Jobs Light Compute": {"AWS": 0.12, "Azure": 0.12, "GCP": 0.12},
    "All-Purpose Compute": {"AWS": 0.55, "Azure": 0.55, "GCP": 0.55},
    "All-Purpose Compute (Photon)": {"AWS": 0.65, "Azure": 0.65, "GCP": 0.65},
    "All-Purpose Serverless": {"AWS": 0.75, "Azure": 0.95, "GCP": 0.75},
    "SQL Compute": {"AWS": 0.22, "Azure": 0.22, "GCP": 0.22},
    "SQL Pro Compute": {"AWS": 0.55, "Azure": 0.55, "GCP": 0.69},
    "Serverless SQL": {"AWS": 0.70, "Azure": 0.70, "GCP": 0.88},
    "DLT Core": {"AWS": 0.20, "Azure": 0.30, "GCP": 0.20},
    "DLT Pro": {"AWS": 0.25, "Azure": 0.38, "GCP": 0.25},
    "DLT Advanced": {"AWS": 0.36, "Azure": 0.54, "GCP": 0.36},
    "Model Serving (CPU/GPU)": {"AWS": 0.07, "Azure": 0.08, "GCP": 0.07},
    "Foundation Model APIs": {"AWS": 0.07, "Azure": 0.08, "GCP": 0.07},
    "Model Training": {"AWS": 0.65, "Azure": 0.65, "GCP": 0.65},
    "Vector Search": {"AWS": 0.07, "Azure": 0.08, "GCP": 0.07},
    "Database Serverless (Lakebase)": {"AWS": 0.07, "Azure": 0.08, "GCP": 0.07},
    "Lakeflow Connect": {"AWS": 0.35, "Azure": 0.35, "GCP": 0.35},
    "Lakeflow Pipelines": {"AWS": 0.20, "Azure": 0.30, "GCP": 0.20},
    "Databricks Apps": {"AWS": 0.07, "Azure": 0.08, "GCP": 0.07},
    "Clean Rooms Collaborator": {"AWS": 0.22, "Azure": 0.22, "GCP": 0.22},
    "Enhanced Security and Compliance": {"AWS": 0.10, "Azure": 0.10, "GCP": 0.10},
}


def get_price_per_dbu_for_workload(workload: str, cloud: str = "AWS") -> float | None:
    """Return $/DBU for a specific workload and cloud. Returns None if not found."""
    workload_rates = PRICE_PER_DBU_BY_WORKLOAD_AND_CLOUD.get(workload)
    if workload_rates:
        return workload_rates.get(cloud, workload_rates.get("AWS"))
    return None


# Legacy flat map (AWS rates) for backward compatibility with existing code
EXAMPLE_PRICE_PER_DBU_BY_WORKLOAD = {
    workload: rates["AWS"]
    for workload, rates in PRICE_PER_DBU_BY_WORKLOAD_AND_CLOUD.items()
}
# Add aliases for backward compat
EXAMPLE_PRICE_PER_DBU_BY_WORKLOAD["Serverless Real-Time Inference"] = 0.07
EXAMPLE_PRICE_PER_DBU_BY_WORKLOAD["Data Quality Monitoring"] = 0.14


# --- Full SKU catalog (from https://www.databricks.com/product/sku-groups) ---
# Every SKU listed on the SKU groups page, by cloud and category. "Included" = in cross-service
# SKU group; "Excluded" = excluded from cross-service (e.g. third-party, preview).
# Source: Databricks Product SKU groups, Feb 2024+; billing docs billing_origin_product.
FULL_SKU_CATALOG = {
    "AWS": {
        "Compute – Jobs Light": [
            "AWS Premium Jobs Light Compute",
            "AWS Enterprise Jobs Light Compute",
        ],
        "Compute – Jobs": [
            "AWS Premium Jobs Compute",
            "AWS Enterprise Jobs Compute",
            "AWS Premium Jobs Compute (Photon)",
            "AWS Enterprise Jobs Compute (Photon)",
        ],
        "Compute – All-Purpose": [
            "AWS Premium All-Purpose Compute",
            "AWS Enterprise All-Purpose Compute",
            "AWS Premium All-Purpose Compute (Photon)",
            "AWS Enterprise All-Purpose Compute (Photon)",
        ],
        "Compute – DLT": [
            "AWS Premium DLT Core Compute",
            "AWS Enterprise DLT Core Compute",
            "AWS Premium DLT Pro Compute",
            "AWS Enterprise DLT Pro Compute",
            "AWS Premium DLT Advanced Compute",
            "AWS Enterprise DLT Advanced Compute",
            "AWS Premium DLT Core Compute (Photon)",
            "AWS Enterprise DLT Core Compute (Photon)",
            "AWS Premium DLT Pro Compute (Photon)",
            "AWS Enterprise DLT Pro Compute (Photon)",
            "AWS Premium DLT Advanced Compute (Photon)",
            "AWS Enterprise DLT Advanced Compute (Photon)",
        ],
        "Compute – SQL": [
            "AWS Premium SQL Compute",
            "AWS Enterprise SQL Compute",
            "AWS Premium SQL Pro Compute",
            "AWS Enterprise SQL Pro Compute",
        ],
        "Compute – Serverless SQL": [
            "AWS Premium Serverless SQL Compute",
            "AWS Enterprise Serverless SQL Compute",
        ],
        "Compute – Serverless Jobs/All-Purpose": [
            "AWS Premium Jobs Serverless Compute",
            "AWS Premium All-Purpose Serverless Compute",
            "AWS Enterprise Jobs Serverless Compute",
            "AWS Enterprise All-Purpose Serverless Compute",
        ],
        "Compute – Database Serverless": [
            "AWS Enterprise Database Serverless Compute",
            "AWS Premium Database Serverless Compute",
        ],
        "Security & Compliance": [
            "AWS Enhanced Security and Compliance",
        ],
        "Clean Rooms": [
            "AWS Premium Clean Rooms Collaborator",
            "AWS Enterprise Clean Rooms Collaborator",
        ],
        "Excluded (not in cross-service SKU group)": [
            "AWS Premium Serverless Real-Time Inference",
            "AWS Enterprise Serverless Real-Time Inference",
            "AWS Premium Model Training",
            "AWS Enterprise Model Training",
            "AWS Public Connectivity Data Processed",
            "AWS Private Connectivity Data Processed",
            "AWS Private Connectivity Endpoint",
            "AWS Inter-Region Egress",
            "AWS Inter-Availability Zone Egress",
            "AWS Internet Egress",
            "AWS Databricks Storage",
            "AWS Premium OpenAI Model Serving",
            "AWS Enterprise OpenAI Model Serving",
            "AWS Premium Anthropic Model Serving",
            "AWS Enterprise Anthropic Model Serving",
            "AWS Premium Gemini Model Serving",
            "AWS Enterprise Gemini Model Serving",
        ],
    },
    "GCP": {
        "Compute – Jobs": [
            "GCP Premium Jobs Compute",
            "GCP Enterprise Jobs Compute",
            "GCP Premium Jobs Compute (Photon)**",
            "GCP Enterprise Jobs Compute (Photon)**",
        ],
        "Compute – All-Purpose": [
            "GCP Premium All-Purpose Compute",
            "GCP Enterprise All-Purpose Compute",
            "GCP Premium All-Purpose Compute (Photon)**",
            "GCP Enterprise All-Purpose Compute (Photon)**",
        ],
        "Compute – DLT": [
            "GCP Premium DLT Core Compute*",
            "GCP Enterprise DLT Core Compute*",
            "GCP Premium DLT Pro Compute*",
            "GCP Enterprise DLT Pro Compute*",
            "GCP Premium DLT Advanced Compute**",
            "GCP Enterprise DLT Advanced Compute**",
            "GCP Premium DLT Core Compute (Photon)*",
            "GCP Enterprise DLT Core Compute (Photon)*",
            "GCP Premium DLT Pro Compute (Photon)*",
            "GCP Enterprise DLT Pro Compute (Photon)*",
            "GCP Premium DLT Advanced Compute (Photon)**",
            "GCP Enterprise DLT Advanced Compute (Photon)**",
        ],
        "Compute – SQL": [
            "GCP Premium SQL Compute**",
            "GCP Premium SQL Pro Compute**",
            "GCP Enterprise SQL Compute**",
            "GCP Enterprise SQL Pro Compute**",
        ],
        "Compute – Serverless SQL": [
            "GCP Premium Serverless SQL Compute",
            "GCP Enterprise Serverless SQL Compute",
        ],
        "Compute – Serverless Jobs/All-Purpose": [
            "GCP Premium Jobs Serverless Compute",
            "GCP Premium All-Purpose Serverless Compute",
            "GCP Enterprise Jobs Serverless Compute",
            "GCP Enterprise All-Purpose Serverless Compute",
        ],
        "Compute – Database Serverless": [
            "GCP Enterprise Database Serverless Compute",
            "GCP Premium Database Serverless Compute",
        ],
        "Security & Compliance": [
            "GCP HIPAA Compliance",
        ],
        "Clean Rooms": [
            "GCP Premium Clean Rooms Collaborator",
            "GCP Enterprise Clean Rooms Collaborator",
            "GCP Enterprise Clean Room Collaborator",
        ],
        "Excluded (not in cross-service SKU group)": [
            "GCP Inter Region Egress",
            "GCP Inter Availability Zone Egress",
            "GCP Internet Egress",
            "GCP Public Connectivity Data Processed",
            "GCP Private Connectivity Data Processed",
            "GCP Private Connectivity Endpoint",
            "GCP Databricks Storage",
            "GCP Premium Serverless Real-Time Inference",
            "GCP Enterprise Serverless Real-Time Inference",
            "GCP Premium Model Training",
            "GCP Enterprise Model Training",
            "GCP Premium OpenAI Model Serving",
            "GCP Enterprise OpenAI Model Serving",
            "GCP Premium Anthropic Model Serving",
            "GCP Enterprise Anthropic Model Serving",
            "GCP Premium Gemini Model Serving",
            "GCP Enterprise Gemini Model Serving",
        ],
    },
    "Azure": {
        "Model Serving (Azure-specific SKUs)": [
            "Azure Premium OpenAI Model Serving",
            "Azure Premium Gemini Model Serving",
        ],
    },
    "MCT": {
        "Model Training": [
            "MCT Model Training On Demand",
            "MCT Model Training Hero Res",
            "MCT Model Training Res",
        ],
    },
}

# Billing origin product (system.billing.usage) -> rough SKU category. Source: docs Billable usage system table.
BILLING_ORIGIN_PRODUCT_TO_CATEGORY = {
    "JOBS": "Jobs Compute / Jobs Serverless",
    "DLT": "DLT Compute",
    "SQL": "SQL Compute / Serverless SQL",
    "ALL_PURPOSE": "All-Purpose Compute",
    "MODEL_SERVING": "Serverless Real-Time Inference / OpenAI / Anthropic / Gemini",
    "INTERACTIVE": "All-Purpose Serverless (notebooks, apps)",
    "DEFAULT_STORAGE": "Databricks Storage",
    "VECTOR_SEARCH": "Vector Search",
    "LAKEHOUSE_MONITORING": "Data Quality Monitoring (Serverless)",
    "PREDICTIVE_OPTIMIZATION": "Serverless Jobs",
    "FOUNDATION_MODEL_TRAINING": "Model Training",
    "AGENT_EVALUATION": "Agent Evaluation (Serverless Inference)",
    "FINE_GRAINED_ACCESS_CONTROL": "Serverless",
    "BASE_ENVIRONMENTS": "Base Environments",
    "DATA_CLASSIFICATION": "Data Classification (Serverless)",
    "DATA_QUALITY_MONITORING": "Data Quality Monitoring (Serverless)",
    "DATA_SHARING": "Delta Sharing",
    "AI_GATEWAY": "AI Gateway",
    "AI_RUNTIME": "Serverless GPU",
    "NETWORKING": "Data Transfer & Connectivity",
    "APPS": "All-Purpose Serverless (Apps)",
    "DATABASE": "Database Serverless (Lakebase)",
    "AI_FUNCTIONS": "AI Functions",
    "AGENT_BRICKS": "Agent Bricks",
    "CLEAN_ROOM": "Clean Rooms",
    "LAKEFLOW_CONNECT": "Lakeflow Connect",
}

# --- Additional DBU/price data from Azure doc (Serverless DBU consumption by SKU) ---
# Agent Evaluation: Source Azure doc
AGENT_EVALUATION_DBU = {
    "LLM Judge": {"input_per_m_tokens": 2.14, "output_per_m_tokens": 8.57},
    "Synthetic Data": {"per_question": 5.0},
}
# AI Functions (e.g. AI Parse Document): estimated SRTI DBUs per doc
AI_FUNCTIONS_ESTIMATED_DBU = {
    "AI Parse Document": {"simple": (10, 15), "with_captions": (20, 25), "medium": (60, 65), "high": (85, 90)},
}
# Vector Search Reranker: DBUs per 1k requests
VECTOR_SEARCH_RERANKER_DBU_PER_1K_REQUESTS = 28.571
# Shutterstock Image AI: DBUs per image
SHUTTERSTOCK_DBU_PER_IMAGE = 0.857
# Model Training – Forecasting: DBU multiplier
MODEL_FORECASTING_DBU_MULTIPLIER = 4.0

# Data Transfer & Connectivity: SKU names only; pricing in PDF. Source: data-transfer-connectivity page.
DATA_TRANSFER_CONNECTIVITY_SKUS = [
    "AWS Public Connectivity Data Processed",
    "AWS Private Connectivity Data Processed",
    "AWS Private Connectivity Endpoint",
    "AWS Inter-Region Egress",
    "AWS Inter-Availability Zone Egress",
    "AWS Internet Egress",
    "GCP Public Connectivity Data Processed",
    "GCP Private Connectivity Data Processed",
    "GCP Private Connectivity Endpoint",
    "GCP Inter Region Egress",
    "GCP Inter Availability Zone Egress",
    "GCP Internet Egress",
]

# --- SKU group names (for reference; from https://www.databricks.com/product/sku-groups) ---
AWS_SKU_GROUPS = [
    "AWS Premium Jobs Light Compute", "AWS Enterprise Jobs Light Compute",
    "AWS Premium Jobs Compute", "AWS Enterprise Jobs Compute",
    "AWS Premium Jobs Compute (Photon)", "AWS Enterprise Jobs Compute (Photon)",
    "AWS Premium All-Purpose Compute", "AWS Enterprise All-Purpose Compute",
    "AWS Premium All-Purpose Compute (Photon)", "AWS Enterprise All-Purpose Compute (Photon)",
    "AWS Premium SQL Compute", "AWS Enterprise SQL Compute",
    "AWS Premium SQL Pro Compute", "AWS Enterprise SQL Pro Compute",
    "AWS Premium Serverless SQL Compute", "AWS Enterprise Serverless SQL Compute",
    "AWS Premium Jobs Serverless Compute", "AWS Enterprise Jobs Serverless Compute",
    "AWS Premium All-Purpose Serverless Compute", "AWS Enterprise All-Purpose Serverless Compute",
    "AWS Premium DLT Core/Pro/Advanced Compute (incl. Photon)", "AWS Database Serverless Compute",
    "AWS Premium Serverless Real-Time Inference", "AWS Enterprise Serverless Real-Time Inference",
    "AWS Premium Model Training", "AWS Enterprise Model Training",
    "AWS Data Transfer", "AWS Databricks Storage", "AWS Clean Rooms", "AWS OpenAI/Anthropic/Gemini Model Serving",
]

PLANS = ["Standard", "Premium", "Enterprise"]
CLOUDS = ["AWS", "Azure", "GCP"]

# --- SKU → product tab and workload key (for pricing) ---
# Drives main-page estimates: which calculator to use and which $/DBU (workload) applies.
# product: "sql" | "vector" | "compute" | "training" | "gpu" | "storage"
# workload_key: key in EXAMPLE_PRICE_PER_DBU_BY_WORKLOAD for compute, or None (use region $/DBU)
def _build_sku_to_product_workload():
    out = {}
    workload_map = [
        (["Jobs Light Compute"], "compute", "Jobs Light Compute"),
        (["Jobs Compute (Photon)"], "compute", "Jobs Compute (Photon)"),
        (["Jobs Compute"], "compute", "Jobs Compute"),
        (["Lakeflow Connect"], "compute", "Lakeflow Connect"),
        (["Lakeflow Pipelines"], "compute", "Lakeflow Pipelines"),
        (["All-Purpose Compute (Photon)"], "compute", "All-Purpose Compute (Photon)"),
        (["All-Purpose Compute"], "compute", "All-Purpose Compute"),
        (["DLT Advanced Compute"], "compute", "DLT Advanced"),
        (["DLT Pro Compute"], "compute", "DLT Pro"),
        (["DLT Core Compute"], "compute", "DLT Core"),
        (["Serverless SQL Compute"], "sql", None),  # before SQL Compute so it matches first
        (["SQL Pro Compute"], "compute", "SQL Pro Compute"),
        (["SQL Compute"], "compute", "SQL Compute"),
        (["Jobs Serverless Compute"], "compute", "Jobs Compute"),
        (["All-Purpose Serverless Compute"], "compute", "Databricks Apps"),  # notebooks, apps
        (["Database Serverless Compute"], "compute", "Database Serverless (Lakebase)"),
        (["Serverless Real-Time Inference"], "gpu", None),
        (["Model Training"], "training", None),
        (["Clean Rooms Collaborator", "Clean Room Collaborator"], "compute", "Clean Rooms Collaborator"),
        (["Enhanced Security and Compliance", "HIPAA Compliance"], "compute", "Enhanced Security and Compliance"),
        (["Databricks Storage"], "storage", None),
        (["OpenAI Model Serving", "Anthropic Model Serving", "Gemini Model Serving"], "gpu", None),
    ]
    for sku_list, product, workload in workload_map:
        for sub in sku_list:
            out[sub] = {"product": product, "workload_key": workload}
    # Apply to every SKU in catalog that contains one of these substrings
    result = {}
    for cloud, categories in FULL_SKU_CATALOG.items():
        for skus in categories.values():
            for sku in skus:
                if sku in result:
                    continue
                for pattern, product, workload in workload_map:
                    for sub in pattern:
                        if sub in sku:
                            result[sku] = {"product": product, "workload_key": workload}
                            break
                    else:
                        continue
                    break
                else:
                    result[sku] = {"product": "compute", "workload_key": "Jobs Compute"}  # fallback
    return result


SKU_TO_PRODUCT_AND_WORKLOAD = _build_sku_to_product_workload()

# Flat list of SKU names per cloud (for sidebar dropdown)
def get_skus_for_cloud(cloud: str) -> list[str]:
    cats = FULL_SKU_CATALOG.get(cloud, {})
    skus = []
    for sku_list in cats.values():
        skus.extend(sku_list)
    return sorted(skus)


def get_price_per_dbu_for_region(cloud: str, region_id: str) -> float:
    """Return $/DBU for a cloud and region. Uses default region if region_id not in cloud."""
    regions = REGIONS_BY_CLOUD.get(cloud, REGIONS_BY_CLOUD["AWS"])
    if region_id in regions:
        return regions[region_id][1]
    default_id = DEFAULT_REGION_BY_CLOUD.get(cloud, "us-east-1")
    return regions.get(default_id, (None, 0.07))[1]


def get_all_models_with_pt() -> list[str]:
    """Return model names that have both pay-per-token and provisioned throughput pricing (for break-even calculator)."""
    return [m for m, r in FOUNDATION_MODEL_DBU_PER_MILLION.items()
            if r.get("input") and r.get("provisioned_per_hour") and "deprecated" not in m.lower()]


# Quality tier hints for model comparison narrative
MODEL_QUALITY_TIER = {
    "Llama 3.2 1B": "edge",
    "Llama 3.2 3B": "edge",
    "Llama 3.1 8B": "entry",
    "Llama 3.3 70B": "mid-high",
    "Llama 3.1 405B (deprecated)": "frontier",
    "Llama 4 Maverick": "high",
    "GPT OSS 20B": "entry",
    "GPT OSS 120B": "mid-high",
    "Gemma 3 12B": "mid",
    "GTE": "embedding",
    "BGE Large": "embedding",
    "GPT 5 nano": "entry",
    "GPT 5 mini": "mid",
    "GPT 5": "high",
    "GPT 5.1": "high",
    "GPT 5.1 Codex Max": "high",
    "GPT 5.1 Codex Mini": "mid",
    "GPT 5.2": "frontier",
    "GPT 5.2/5.3 Codex": "frontier",
    "GPT 5.4": "frontier",
    "Claude Haiku 4.5": "mid",
    "Claude Sonnet 4/4.1": "high",
    "Claude Sonnet 4.5/4.6": "high",
    "Claude Opus 4/4.1": "frontier",
    "Claude Opus 4.5": "frontier",
    "Claude Opus 4.6": "frontier",
    "Gemini 2.5 Flash": "mid",
    "Gemini 2.5 Pro": "high",
    "Gemini 3.0 Flash": "mid",
    "Gemini 3.1 Pro": "frontier",
}


# --- GenAI Feature Availability by Cloud ---
# Source: https://docs.databricks.com/en/resources/feature-region-support
# "full" = GA in most regions, "limited" = GA in select regions, "preview" = public preview, "none" = not available
GENAI_FEATURE_AVAILABILITY = {
    "Foundation Model APIs (PPT)": {"AWS": "full", "Azure": "full", "GCP": "limited"},
    "Foundation Model APIs (PT)": {"AWS": "full", "Azure": "full", "GCP": "limited"},
    "Proprietary Models (Claude)": {"AWS": "full", "Azure": "full", "GCP": "full"},
    "Proprietary Models (GPT)": {"AWS": "full", "Azure": "full", "GCP": "full"},
    "Proprietary Models (Gemini)": {"AWS": "full", "Azure": "full", "GCP": "full"},
    "GPU Model Serving": {"AWS": "full", "Azure": "full", "GCP": "limited"},
    "Vector Search": {"AWS": "full", "Azure": "full", "GCP": "limited"},
    "Agent Bricks": {"AWS": "full", "Azure": "full", "GCP": "limited"},
    "Agent Evaluation": {"AWS": "full", "Azure": "full", "GCP": "limited"},
    "AI Parse (AI Functions)": {"AWS": "full", "Azure": "full", "GCP": "limited"},
    "Model Training (Fine-Tuning)": {"AWS": "full", "Azure": "full", "GCP": "limited"},
    "Lakebase": {"AWS": "full", "Azure": "full", "GCP": "limited"},
    "Lakeflow Connect": {"AWS": "full", "Azure": "full", "GCP": "preview"},
    "Mosaic AI Gateway": {"AWS": "full", "Azure": "full", "GCP": "limited"},
}


# --- GPU Instance Availability by Cloud ---
# AWS: T4, A10G (1/4/8). Azure: T4, A100 (1/2/4/8). GCP: T4, limited.
# --- GPU Instance Availability by Cloud ---
# Source: docs.databricks.com create-manage-serving-endpoints (AWS + Azure)
# AWS GPU types: GPU_SMALL (T4), GPU_MEDIUM (A10G x1), MULTIGPU_MEDIUM (A10G x4), GPU_MEDIUM_8 (A10G x8)
# Azure GPU types: GPU_SMALL (T4), GPU_LARGE (A100 x1), GPU_LARGE_2 (A100 x2)
# Confirmed: A10G sizes are AWS-only. A100 single/dual are on both AWS and Azure.
# DBU/hr rates for Small (10.48), XLarge (78.6), 2XLarge (157.2), 4XLarge (314.4) confirmed via learn.microsoft.com.
# DBU/hr rates for Medium (20), Medium 4X (112), Medium 8x (290.8), Large 8X sizes are from databricks.com (JS-rendered, unverifiable via scraping).
GPU_SERVING_AVAILABILITY = {
    "Small": {"AWS": True, "Azure": True, "GCP": True},           # T4, 10.48 DBU/hr [CONFIRMED]
    "Medium": {"AWS": True, "Azure": False, "GCP": False},        # A10G x1, 20 DBU/hr [AWS docs confirmed]
    "Medium 4X": {"AWS": True, "Azure": False, "GCP": False},     # A10G x4, 112 DBU/hr [AWS docs confirmed]
    "Medium 8x": {"AWS": True, "Azure": False, "GCP": False},     # A10G x8, 290.8 DBU/hr [AWS docs confirmed]
    "XLarge": {"AWS": True, "Azure": True, "GCP": False},         # A100 80GB x1, 78.6 DBU/hr [CONFIRMED both clouds]
    "2XLarge": {"AWS": True, "Azure": True, "GCP": False},        # A100 80GB x2, 157.2 DBU/hr [CONFIRMED]
    "4XLarge": {"AWS": True, "Azure": True, "GCP": False},        # A100 80GB x4, 314.4 DBU/hr [CONFIRMED]
    "Large 8X 40GB": {"AWS": True, "Azure": False, "GCP": False}, # A100 40GB x8, 538.4 DBU/hr [unconfirmed rate]
    "Large 8X 80GB": {"AWS": True, "Azure": True, "GCP": False},  # A100 80GB x8, 628 DBU/hr [unconfirmed rate]
}
