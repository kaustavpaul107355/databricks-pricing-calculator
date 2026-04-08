# Databricks GenAI TCO Estimator

Ballpark pricing and Total Cost of Ownership estimator for GenAI solutions on Databricks. Covers 30 models across 3 clouds and 69 regions, with scenario-based TCO modeling for RAG, multi-agent, batch AI, and fine-tuning workloads.

## Features

| Mode | What it does |
|------|-------------|
| **GenAI Calculator** | Per-service estimates: Vector Search, Agent Bricks, AI Gateway, Model Serving, Foundation Models (open + proprietary with cache/batch/in-geo/long-context pricing), AI Parse (with 50% promo), Agent Evaluation, Model Training |
| **PT vs PPT Break-Even** | Interactive chart showing where Provisioned Throughput becomes cheaper than Pay-Per-Token for open foundation models |
| **Model Comparison** | Side-by-side cost comparison of 2-3 models (open or proprietary) for the same traffic volume |
| **Scenario Templates** | End-to-end TCO for RAG, Multi-Agent, Batch AI Pipeline, and Fine-Tuned Model architectures — with pie chart cost breakdowns |
| **Quick Estimate** | S/M/L presets for instant ballpark TCO (12 presets across 4 scenario types) |

## Coverage

- **30 models**: 11 open foundation models + 19 proprietary (OpenAI GPT 5.x, Anthropic Claude 4.x, Google Gemini 2.5-3.1)
- **3 clouds**: AWS, Azure, GCP with per-cloud $/DBU rates for 23 workload types
- **69 regions** with region-specific $/DBU
- **New pricing dimensions**: cache write/read, batch inference, in-geo routing, long context (>200k tokens), scaling capacity
- **Lakebase, Lakeflow Connect, AI Gateway** rates included

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

Or: `./run_app.sh`

## CLI

```bash
# Per-service estimates
python cli.py foundation-model "Llama 3.3 70B" --input-m 10 --output-m 2
python cli.py vector-search Standard --units 3 --hours 720
python cli.py serving-gpu XLarge --hours 720
python cli.py ai-parse 5 "Medium (text + tables + images, e.g. 10-Ks)"

# Break-even analysis
python cli.py breakeven "Llama 3.3 70B" --input-tokens 2000 --output-tokens 500 --qpm 10

# Model comparison
python cli.py compare "Llama 3.3 70B" "GPT 5 mini" "Claude Haiku 4.5" --input-m 10 --output-m 2

# Scenario estimates
python cli.py scenario rag --docs 10000 --queries-day 500
python cli.py scenario agent --requests-day 1000 --steps 5 --tools 2
python cli.py scenario batch --docs 50000 --frequency 4
python cli.py scenario fine-tune --model "Llama 3.3 70B" --scale "10M tokens"

# List options
python cli.py list foundation-models
python cli.py list regions --cloud GCP
python cli.py list skus --cloud AWS
```

## Project layout

```
databricks-pricing-calculator/
├── app.py              # Streamlit TCO estimator (5 modes)
├── app.yaml            # Databricks Apps deployment config
├── calculator.py       # Atomic estimation functions
├── scenarios.py        # Composite scenario estimators + break-even + comparison
├── presets.py          # T-shirt sizing presets (S/M/L)
├── pricing_data.py     # All reference data (models, rates, regions, SKUs)
├── cli.py              # Command-line interface
├── index.html          # Legacy standalone calculator (limited, no server needed)
├── requirements.txt    # Python dependencies
├── PRICING_SOURCES.md  # Data sources and verification status
└── README.md           # This file
```

## Pricing data

All rates are from official Databricks pricing pages and Azure Databricks docs. See [PRICING_SOURCES.md](PRICING_SOURCES.md) for the full source list and verification status.

For actual per-customer rates, query `system.billing.list_prices` in your workspace.

## Disclaimer

Estimates only. List prices and DBU rates are for ballpark estimation and may not match your contract, region, or current pricing. Azure pricing is set by Microsoft. Use `system.billing.list_prices` or the [official pricing calculator](https://www.databricks.com/product/pricing/product-pricing/instance-types) for authoritative rates.
