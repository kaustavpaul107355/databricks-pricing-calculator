#!/usr/bin/env python3
"""Print catalog counts and promo windows for a quick pricing fitment sanity check.

Run from repo root:
  python scripts/pricing_fitment_check.py

See docs/PRICING_FITMENT.md for the full refresh procedure and source URLs.
"""

from __future__ import annotations

import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pricing_data import (  # noqa: E402
    AI_CLASSIFY_DBU_PER_1K_DOCUMENTS,
    AI_EXTRACT_DBU_PER_1K_INPUTS,
    AI_PARSE_PROMO_EXPIRY,
    FOUNDATION_MODEL_DBU_PER_MILLION,
    GEMINI_FM_PROMO_EXPIRY,
    MODEL_RETIREMENT_NOTICES,
    PRICING_PAGES,
    PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION,
    get_pricing_page_url,
)


def _promo_active(expiry: str) -> bool:
    return datetime.date.today() <= datetime.date.fromisoformat(expiry)


def main() -> None:
    today = datetime.date.today().isoformat()
    print(f"Pricing fitment snapshot — {today}\n")

    open_models = [m for m in FOUNDATION_MODEL_DBU_PER_MILLION if "deprecated" not in m.lower()]
    prop_models = list(PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION.keys())
    gemini = [m for m in prop_models if m.startswith("Gemini")]

    print(f"Open foundation models: {len(open_models)}")
    for name in sorted(open_models):
        print(f"  - {name}")
    print(f"\nProprietary models: {len(prop_models)}")
    for name in sorted(prop_models):
        tiers = list(PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION[name].keys())
        print(f"  - {name} [{', '.join(tiers)}]")

    print(f"\nGemini models ({len(gemini)}):")
    for name in gemini:
        g = PROPRIETARY_FOUNDATION_MODEL_DBU_PER_MILLION[name]["global"]
        print(f"  - {name}: in={g.get('input')} out={g.get('output')}")

    print(f"\nAI Extract workloads: {len(AI_EXTRACT_DBU_PER_1K_INPUTS)}")
    for name, dbu in AI_EXTRACT_DBU_PER_1K_INPUTS.items():
        print(f"  - {name}: {dbu} DBU/1k inputs")
    print(f"\nAI Classify workloads: {len(AI_CLASSIFY_DBU_PER_1K_DOCUMENTS)}")
    for name, dbu in AI_CLASSIFY_DBU_PER_1K_DOCUMENTS.items():
        print(f"  - {name}: {dbu} DBU/1k documents")

    print(f"\nModels with retirement notices: {len(MODEL_RETIREMENT_NOTICES)}")
    for name, meta in MODEL_RETIREMENT_NOTICES.items():
        print(f"  - {name}: {meta['retire_date']}")

    print("\nPromotions:")
    print(f"  AI Parse 50% through {AI_PARSE_PROMO_EXPIRY}: active={_promo_active(AI_PARSE_PROMO_EXPIRY)}")
    print(f"  Gemini FM 20% through {GEMINI_FM_PROMO_EXPIRY}: active={_promo_active(GEMINI_FM_PROMO_EXPIRY)}")

    genai_pages = [p for p in PRICING_PAGES if p.get("calculator_tab")]
    print(f"\nGenAI pricing pages tracked ({len(genai_pages)}):")
    for p in genai_pages:
        print(f"  - {p['label']}: {get_pricing_page_url(p['path'])}")

    print("\nFull fitment procedure: docs/PRICING_FITMENT.md")


if __name__ == "__main__":
    main()
