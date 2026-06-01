"""Regression: Model Serving tile must accept string inputs from Dash."""


def test_model_serving_cpu_with_string_hours():
    from app import _safe
    from calculator import estimate_model_serving_cpu

    hrs = _safe("720")
    assert hrs == 720.0
    r = estimate_model_serving_cpu(hrs, cloud="AWS", region="us-east-1")
    assert r.cost_usd > 0


def test_model_serving_gpu_with_string_hours():
    from app import _safe
    from calculator import estimate_model_serving_gpu

    hrs = _safe("100")
    r = estimate_model_serving_gpu("Small", hrs, cloud="AWS", region="us-east-1")
    assert r.cost_usd > 0
