"""Unit tests cho AuditInterceptor (test_audit.py)."""

import pytest
from src.common.interceptors.audit import AuditInterceptor
from src.common.interceptors.context import InterceptorContext


@pytest.mark.asyncio
async def test_audit_interceptor_attaches_metadata() -> None:
    """Kiểm tra AuditInterceptor đính kèm audit record hợp lệ vào context metadata."""
    interceptor = AuditInterceptor(
        actor="user_999",
        action="ApproveProposal",
        resource_id="proposal_123",
    )
    context = InterceptorContext.create("ApproveProposal")

    async def sample_op() -> bool:
        return True

    res = await interceptor.intercept(context, sample_op)

    assert res is True
    assert "audit" in context.metadata
    audit_data = context.metadata["audit"]
    assert audit_data["actor"] == "user_999"
    assert audit_data["action"] == "ApproveProposal"
    assert audit_data["resource_id"] == "proposal_123"
    assert "timestamp" in audit_data


@pytest.mark.asyncio
async def test_audit_interceptor_no_sensitive_data_leak() -> None:
    """Kiểm tra AuditInterceptor không rò rỉ dữ liệu nhạy cảm."""
    interceptor = AuditInterceptor(actor="admin_1")
    context = InterceptorContext.create(
        "LoginOperation",
        password="SuperSecretPassword123",  # noqa: S106
        access_token="Bearer secret_token",  # noqa: S106
    )

    async def login_op() -> str:
        return "logged_in"

    await interceptor.intercept(context, login_op)

    audit_data = context.metadata["audit"]
    # Kiểm tra audit dictionary chỉ chứa thông tin định danh không nhạy cảm
    assert "password" not in audit_data
    assert "access_token" not in audit_data
