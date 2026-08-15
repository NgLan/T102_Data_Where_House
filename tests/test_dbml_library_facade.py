"""Compatibility tests dùng chung corpus cho DBML backend facade."""

import json
from pathlib import Path

import pytest
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.dbml import parse_dbml_schema

CORPUS_PATH = Path(__file__).parent / "fixtures" / "dbml-corpus.json"
CORPUS = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", CORPUS["valid"], ids=lambda case: case["name"])
def test_dbml_library_accepts_shared_valid_corpus(case: dict[str, str]) -> None:
    """Xác nhận backend chấp nhận mỗi fixture hợp lệ dùng chung với frontend."""
    assert parse_dbml_schema(case["source"]) is None


@pytest.mark.parametrize("case", CORPUS["invalid"], ids=lambda case: case["name"])
def test_dbml_library_translates_shared_invalid_corpus(case: dict[str, str]) -> None:
    """Xác nhận lỗi parser được chuyển thành lỗi nghiệp vụ chuẩn."""
    with pytest.raises(BusinessException) as exc_info:
        parse_dbml_schema(case["source"])

    assert exc_info.value.code == ErrorCode.INVALID_DBML_CONTENT
    assert exc_info.value.__cause__ is not None
