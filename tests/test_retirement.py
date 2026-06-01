"""Model retirement metadata and UI labels."""

from pricing_data import format_model_option_label, get_model_retirement_notice


def test_codex_retirement_notice():
    notice = get_model_retirement_notice("GPT 5.2/5.3 Codex")
    assert notice is not None
    assert notice["retire_date"] == "2026-07-16"


def test_format_model_option_label_with_retirement():
    label = format_model_option_label("GPT 5.1 Codex Mini")
    assert "retiring" in label.lower()
    assert "2026-07-16" in label


def test_format_model_option_label_active_model():
    label = format_model_option_label("GPT 5.4")
    assert label == "GPT 5.4"
