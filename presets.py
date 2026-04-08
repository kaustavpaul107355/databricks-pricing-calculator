"""
T-shirt sizing presets for Quick Estimate mode.
Each preset maps to a scenario function's kwargs.
"""

SCENARIO_PRESETS = {
    "RAG": {
        "S": {
            "label": "Small (1K docs, 100 queries/day)",
            "params": {
                "num_docs": 1_000,
                "avg_pages_per_doc": 5,
                "avg_chunks_per_doc": 20,
                "queries_per_day": 100,
                "embedding_model": "GTE",
                "llm_model": "Llama 3.1 8B",
                "parse_complexity": "Low (simple text, e.g. receipts, W2s)",
                "refresh_frequency_per_month": 1,
                "avg_input_tokens_per_query": 1500,
                "avg_output_tokens_per_query": 300,
                "include_guardrails": False,
                "include_eval": False,
            },
        },
        "M": {
            "label": "Medium (50K docs, 1K queries/day)",
            "params": {
                "num_docs": 50_000,
                "avg_pages_per_doc": 8,
                "avg_chunks_per_doc": 30,
                "queries_per_day": 1_000,
                "embedding_model": "GTE",
                "llm_model": "Llama 3.3 70B",
                "parse_complexity": "Medium (text + tables + images, e.g. 10-Ks)",
                "refresh_frequency_per_month": 2,
                "avg_input_tokens_per_query": 2000,
                "avg_output_tokens_per_query": 500,
                "include_guardrails": True,
                "include_eval": True,
                "eval_questions_per_month": 100,
            },
        },
        "L": {
            "label": "Large (500K docs, 10K queries/day)",
            "params": {
                "num_docs": 500_000,
                "avg_pages_per_doc": 10,
                "avg_chunks_per_doc": 40,
                "queries_per_day": 10_000,
                "embedding_model": "BGE Large",
                "llm_model": "GPT 5 mini",
                "parse_complexity": "High (complex diagrams + captions)",
                "refresh_frequency_per_month": 4,
                "avg_input_tokens_per_query": 3000,
                "avg_output_tokens_per_query": 800,
                "include_guardrails": True,
                "include_eval": True,
                "eval_questions_per_month": 500,
            },
        },
    },
    "Multi-Agent": {
        "S": {
            "label": "Small (100 req/day, 3 steps)",
            "params": {
                "requests_per_day": 100,
                "avg_steps_per_request": 3,
                "tools_per_step": 1,
                "orchestrator_model": "Llama 3.1 8B",
                "worker_model": "Llama 3.1 8B",
                "include_vector_search": True,
                "include_guardrails": False,
            },
        },
        "M": {
            "label": "Medium (1K req/day, 5 steps)",
            "params": {
                "requests_per_day": 1_000,
                "avg_steps_per_request": 5,
                "tools_per_step": 2,
                "orchestrator_model": "Llama 3.3 70B",
                "worker_model": "Llama 3.1 8B",
                "include_vector_search": True,
                "include_guardrails": True,
            },
        },
        "L": {
            "label": "Large (10K req/day, 8 steps)",
            "params": {
                "requests_per_day": 10_000,
                "avg_steps_per_request": 8,
                "tools_per_step": 3,
                "orchestrator_model": "GPT 5 mini",
                "worker_model": "Llama 3.3 70B",
                "include_vector_search": True,
                "include_guardrails": True,
            },
        },
    },
    "Batch AI": {
        "S": {
            "label": "Small (1K docs, monthly)",
            "params": {
                "num_docs": 1_000,
                "pages_per_doc": 5,
                "parse_complexity": "Low (simple text, e.g. receipts, W2s)",
                "frequency_per_month": 1,
                "output_model": "Llama 3.1 8B",
            },
        },
        "M": {
            "label": "Medium (50K docs, weekly)",
            "params": {
                "num_docs": 50_000,
                "pages_per_doc": 8,
                "parse_complexity": "Medium (text + tables + images, e.g. 10-Ks)",
                "frequency_per_month": 4,
                "output_model": "Llama 3.3 70B",
            },
        },
        "L": {
            "label": "Large (500K docs, daily)",
            "params": {
                "num_docs": 500_000,
                "pages_per_doc": 10,
                "parse_complexity": "High (complex diagrams + captions)",
                "frequency_per_month": 30,
                "output_model": "GPT 5 mini",
            },
        },
    },
    "Fine-Tune": {
        "S": {
            "label": "Small (8B model, 10M tokens)",
            "params": {
                "base_model": "Llama 3.1 8B",
                "training_scale": "10M tokens",
                "eval_frequency_per_month": 1,
                "eval_questions": 50,
                "serving_hours_per_day": 8,
                "retraining_cadence_months": 6,
            },
        },
        "M": {
            "label": "Medium (70B model, 10M tokens)",
            "params": {
                "base_model": "Llama 3.3 70B",
                "training_scale": "10M tokens",
                "eval_frequency_per_month": 2,
                "eval_questions": 100,
                "serving_hours_per_day": 12,
                "retraining_cadence_months": 3,
            },
        },
        "L": {
            "label": "Large (70B model, 500M tokens)",
            "params": {
                "base_model": "Llama 3.3 70B",
                "training_scale": "500M tokens",
                "eval_frequency_per_month": 4,
                "eval_questions": 200,
                "serving_hours_per_day": 24,
                "retraining_cadence_months": 1,
            },
        },
    },
}
