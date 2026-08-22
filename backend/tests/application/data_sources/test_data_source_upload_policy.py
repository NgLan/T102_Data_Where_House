"""Upload limit tính theo tổng source và replacement case-insensitive."""

from uuid import uuid4

import pytest
from src.application.data_sources.data_source_upload_policy import validate_upload
from src.application.data_sources.input import UploadDataSourcesInput, UploadFileInput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode


def upload(*names: str) -> UploadDataSourcesInput:
    return UploadDataSourcesInput(uuid4(), tuple(UploadFileInput(name, b"id\n1") for name in names))


def test_replacing_same_name_does_not_increase_total() -> None:
    existing = frozenset({f"source_{index}.csv" for index in range(19)} | {"orders.csv"})
    validate_upload(upload("ORDERS.CSV"), existing)


def test_total_source_limit_is_enforced() -> None:
    existing = frozenset({f"source_{index}.csv" for index in range(20)})
    with pytest.raises(BusinessException) as captured:
        validate_upload(upload("another.csv"), existing)
    assert captured.value.code is ErrorCode.MAX_FILES_EXCEEDED
