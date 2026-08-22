"""Classifier contract giới hạn enum, confidence và sample payload."""

import pytest
from pydantic import ValidationError
from src.application.data_sources.source_analysis_models import ColumnClassificationInput
from src.domain.data_source.column_profile import ColumnProfile
from src.domain.data_source.enums import ColumnDataType
from src.infrastructure.llm.column_type_classifier import _prompt_payload
from src.infrastructure.llm.column_type_outputs import ColumnTypeClassificationResult


def test_prompt_limits_samples_to_ten_and_one_hundred_characters() -> None:
    samples = tuple("x" * 150 for _ in range(12))
    item = ColumnClassificationInput("0:0", ColumnProfile("value", "VARCHAR", samples), ColumnDataType.TEXT)
    payload = _prompt_payload((item,))[0]
    assert len(payload["sample_values"]) == 10
    assert max(map(len, payload["sample_values"])) == 100


@pytest.mark.parametrize(
    "data",
    [
        {"reference": "0:0", "data_type": "UNKNOWN", "confidence": 0.8},
        {"reference": "0:0", "data_type": "TEXT", "confidence": 1.1},
    ],
)
def test_invalid_classifier_output_is_rejected(data: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        ColumnTypeClassificationResult.model_validate({"columns": [data]})
