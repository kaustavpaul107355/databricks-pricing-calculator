"""
UI helpers for the Dash app — dropdown option builders and value coercion.

Kept separate from app.py so dropdown/callback logic can be unit-tested without Dash.
"""

from __future__ import annotations

from pricing_data import (
    AI_CLASSIFY_WORKLOAD_LABELS,
    AI_EXTRACT_WORKLOAD_LABELS,
    AI_PARSE_DOCUMENT_TYPE_LABELS,
    MODEL_TRAINING_DBU_ESTIMATES,
    format_model_option_label,
    get_proprietary_model_tiers,
)

PROP_TIER_LABELS = {
    "global": "Global",
    "in_geo": "In-Geo (~10% premium)",
    "long_context": "Long Context (>200k tokens)",
    "in_geo_long_context": "In-Geo + Long Context",
}

GENAI_STORE_KEYS = (
    "vs",
    "reranker",
    "ab",
    "gw",
    "serv",
    "fm",
    "prop",
    "parse",
    "extract",
    "classify",
    "eval",
)

GENAI_STORE_LABELS = {
    "vs": "Vector Search",
    "reranker": "Vector Search Reranker",
    "ab": "Agent Bricks",
    "gw": "Mosaic AI Gateway",
    "serv": "Model Serving",
    "fm": "Foundation Model (open)",
    "prop": "Proprietary Foundation Model",
    "parse": "AI Parse Document",
    "extract": "AI Extract",
    "classify": "AI Classify",
    "eval": "Agent Evaluation",
}


def none_option() -> dict:
    return {"label": "— None —", "value": "__none__"}


def none_opt(options: list[dict]) -> list[dict]:
    """Prepend a '— None —' option to select options (list of {label, value})."""
    return [none_option()] + options


def none_opt_strings(values: list[str]) -> list[dict]:
    """Prepend none option; label and value are the same string."""
    return none_opt([{"label": v, "value": v} for v in values])


def parse_complexity_options() -> list[dict]:
    """AI Parse dropdown: short label, complexity key as value (matches pricing_data keys)."""
    return none_opt(
        [{"label": lbl, "value": key} for lbl, key in AI_PARSE_DOCUMENT_TYPE_LABELS]
    )


def ai_extract_workload_options() -> list[dict]:
    return none_opt([{"label": lbl, "value": key} for lbl, key in AI_EXTRACT_WORKLOAD_LABELS])


def ai_classify_workload_options() -> list[dict]:
    return none_opt([{"label": lbl, "value": key} for lbl, key in AI_CLASSIFY_WORKLOAD_LABELS])


def model_options_with_retirement(models: list[str]) -> list[dict]:
    """Select options with retirement date in label when applicable."""
    return none_opt([{"label": format_model_option_label(m), "value": m} for m in models])


def retirement_alert(model: str | None, *, color: str = "warning"):
    """Build a Dash alert for models with a known retirement date."""
    import dash_bootstrap_components as dbc
    from pricing_data import get_model_retirement_notice

    if not model or model == "__none__":
        return None
    notice = get_model_retirement_notice(model)
    if not notice:
        return None
    body = f"Retiring {notice['retire_date']}. Recommended: {notice['replacement']}."
    if note := notice.get("note"):
        body += f" {note}"
    return dbc.Alert(body, color=color, className="py-2 small mb-2")


def proprietary_tier_options(model: str) -> list[dict]:
    tiers = get_proprietary_model_tiers(model)
    return [{"label": PROP_TIER_LABELS.get(t, t.replace("_", " ").title()), "value": t} for t in tiers]


def resolve_proprietary_tier(model: str | None, tier: str | None) -> str | None:
    """Return a valid tier for model, or None if model unset / unknown."""
    if not model or model == "__none__":
        return None
    tiers = get_proprietary_model_tiers(model)
    if not tiers:
        return None
    if tier and tier in tiers:
        return tier
    return tiers[0]


def resolve_training_scale(model: str | None, scale: str | None) -> str | None:
    if not model or model == "__none__":
        return None
    scales = list(MODEL_TRAINING_DBU_ESTIMATES.get(model, {}).keys())
    if not scales:
        return None
    if scale and scale in scales:
        return scale
    return scales[0]


def coerce_input(value, default: float = 0.0) -> float:
    """Coerce Dash Input values (often strings) to float for comparisons and math."""
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def coerce_store_amount(value) -> float:
    """Normalize dcc.Store data to a non-negative float."""
    return max(0.0, coerce_input(value, 0.0))


def tile_input_hint(message: str = "Enter a value greater than zero to see an estimate."):
    """Light alert when a tile has no billable inputs yet."""
    from dash import html
    import dash_bootstrap_components as dbc

    return dbc.Alert(message, color="light", className="py-2 mt-2 mb-0")


def checklist_enabled(values, flag: str = "yes") -> bool:
    """True if a dbc.Checklist value list contains flag."""
    return flag in (values or [])
