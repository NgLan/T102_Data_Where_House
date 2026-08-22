"""Unit tests cho Common DTO Layer (src/common/dto)."""

import pytest
from pydantic import BaseModel, ValidationError
from src.common.dto import (
    ApiResponse,
    PaginatedResponse,
    PaginationMeta,
    PaginationRequest,
    ResponseMeta,
    SortOrder,
    SortRequest,
)


class SampleItem(BaseModel):
    """Sample DTO dùng cho generic test."""

    id: int
    name: str


class SamplePayloadWithMeta(BaseModel):
    """Payload ví dụ tự sở hữu metadata tùy chọn."""

    item: SampleItem
    meta: ResponseMeta | None = None


def test_pagination_request_defaults():
    """Test giá trị mặc định của PaginationRequest."""
    req = PaginationRequest()
    assert req.page == 1
    assert req.page_size == 20


def test_pagination_request_valid_custom():
    """Test PaginationRequest với tham số hợp lệ."""
    req = PaginationRequest(page=3, page_size=50)
    assert req.page == 3
    assert req.page_size == 50


def test_pagination_request_invalid_page():
    """Test validate page < 1."""
    with pytest.raises(ValidationError):
        PaginationRequest(page=0)

    with pytest.raises(ValidationError):
        PaginationRequest(page=-5)


def test_pagination_request_invalid_page_size():
    """Test validate page_size < 1 hoặc > MAX_PAGE_SIZE (100)."""
    with pytest.raises(ValidationError):
        PaginationRequest(page_size=0)

    with pytest.raises(ValidationError):
        PaginationRequest(page_size=101)


def test_pagination_meta_calculation():
    """Test tính toán total_pages trong PaginationMeta.create."""
    meta1 = PaginationMeta.create(page=1, page_size=20, total_items=100)
    assert meta1.total_pages == 5

    meta2 = PaginationMeta.create(page=1, page_size=20, total_items=101)
    assert meta2.total_pages == 6

    meta3 = PaginationMeta.create(page=1, page_size=20, total_items=0)
    assert meta3.total_pages == 0


def test_paginated_response_generic():
    """Test PaginatedResponse serialization với Generic Type."""
    items = [SampleItem(id=1, name="Item A"), SampleItem(id=2, name="Item B")]
    meta = PaginationMeta.create(page=1, page_size=20, total_items=2)

    res = PaginatedResponse[SampleItem](data=items, meta=meta)
    dumped = res.model_dump()

    assert dumped == {
        "data": [
            {"id": 1, "name": "Item A"},
            {"id": 2, "name": "Item B"},
        ],
        "meta": {
            "page": 1,
            "page_size": 20,
            "total_items": 2,
            "total_pages": 1,
        },
    }


def test_sort_request_defaults():
    """Test giá trị mặc định của SortRequest."""
    sort_req = SortRequest()
    assert sort_req.sort_by is None
    assert sort_req.sort_order == SortOrder.DESC


def test_sort_request_custom():
    """Test SortRequest với sort_by và SortOrder.ASC."""
    sort_req = SortRequest(sort_by="created_at", sort_order=SortOrder.ASC)
    assert sort_req.sort_by == "created_at"
    assert sort_req.sort_order == "asc"


def test_sort_order_invalid():
    """Test validate sort_order không nằm trong enum."""
    with pytest.raises(ValidationError):
        SortRequest(sort_order="invalid_order")


def test_api_response_envelope():
    """Test ApiResponse envelope chuẩn hóa theo TECHNICAL_CODING_GUIDELINES.md."""
    item = SampleItem(id=10, name="Test Item")
    response = ApiResponse[SampleItem](data=item)
    dumped = response.model_dump()

    assert dumped == {
        "status": "success",
        "code": 200,
        "message": "Xử lý thành công",
        "data": {"id": 10, "name": "Test Item"},
    }


def test_payload_specific_meta():
    """Test metadata nằm trong payload thay vì top-level envelope."""
    item = SampleItem(id=10, name="Test Item")
    meta = ResponseMeta(request_id="req_9a8b7c6d", timestamp="2026-08-12T10:00:00Z")
    payload = SamplePayloadWithMeta(item=item, meta=meta)
    response = ApiResponse[SamplePayloadWithMeta](data=payload)
    dumped = response.model_dump(mode="json")

    assert "meta" not in dumped
    assert dumped["data"]["meta"] == {
        "request_id": "req_9a8b7c6d",
        "timestamp": "2026-08-12T10:00:00Z",
    }


def test_api_response_paginated():
    """Test ApiResponse bọc PaginatedResponse (data lồng nhau sạch sẽ)."""
    items = [SampleItem(id=1, name="Item 1")]
    meta = PaginationMeta.create(page=1, page_size=20, total_items=1)
    paginated_data = PaginatedResponse[SampleItem](data=items, meta=meta)

    response = ApiResponse[PaginatedResponse[SampleItem]](data=paginated_data)
    dumped = response.model_dump()

    assert dumped["status"] == "success"
    assert dumped["code"] == 200
    assert dumped["data"]["meta"]["total_items"] == 1


def test_response_meta():
    """Test ResponseMeta DTO."""
    meta = ResponseMeta(request_id="req_12345", timestamp="2026-08-12T10:00:00Z")
    assert meta.request_id == "req_12345"
    assert meta.timestamp is not None
    assert meta.timestamp.isoformat() == "2026-08-12T10:00:00+00:00"


def test_common_dto_forbids_extra_fields():
    """Test common DTO không âm thầm nhận field ngoài contract."""
    with pytest.raises(ValidationError):
        PaginationRequest(page=1, page_size=20, offset=0)
    with pytest.raises(ValidationError):
        ApiResponse[SampleItem](data=SampleItem(id=1, name="A"), meta=None)


def test_api_response_rejects_invalid_success_contract():
    """Test status và code chỉ nhận giá trị hợp lệ cho success response."""
    with pytest.raises(ValidationError):
        ApiResponse[SampleItem](status="failed", data=None)
    with pytest.raises(ValidationError):
        ApiResponse[SampleItem](code=500, data=None)


def test_clean_architecture_isolation():
    """Test kiểm tra Clean Architecture isolation: common/dto không import framework hoặc infrastructure."""
    import src.common.dto.pagination as p_mod
    import src.common.dto.response as r_mod
    import src.common.dto.sorting as s_mod

    forbidden_modules = ["fastapi", "sqlalchemy", "redis", "langchain", "langgraph"]

    for mod in [p_mod, r_mod, s_mod]:
        code = open(mod.__file__, encoding="utf-8").read()
        for forbidden in forbidden_modules:
            assert f"import {forbidden}" not in code, f"Module {mod.__file__} violates Clean Architecture by importing {forbidden}"
            assert f"from {forbidden}" not in code, f"Module {mod.__file__} violates Clean Architecture by importing {forbidden}"
