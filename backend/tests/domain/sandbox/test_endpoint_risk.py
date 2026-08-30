"""Kiểm thử phân loại rủi ro endpoint Sandbox không cần DNS lookup."""

import pytest
from src.domain.sandbox.enums import SandboxEndpointRisk
from src.domain.sandbox.rules import classify_sandbox_endpoint


@pytest.mark.parametrize(
    ("host", "expected"),
    [
        ("localhost", SandboxEndpointRisk.LOOPBACK),
        ("127.0.0.1", SandboxEndpointRisk.LOOPBACK),
        ("::1", SandboxEndpointRisk.LOOPBACK),
        ("10.20.30.40", SandboxEndpointRisk.PRIVATE_NETWORK),
        ("192.168.1.5", SandboxEndpointRisk.PRIVATE_NETWORK),
        ("169.254.10.2", SandboxEndpointRisk.PRIVATE_NETWORK),
        ("8.8.8.8", SandboxEndpointRisk.REMOTE),
        ("database.example.com", SandboxEndpointRisk.REMOTE),
    ],
)
def test_endpoint_risk_uses_only_literal_host(
    host: str, expected: SandboxEndpointRisk
) -> None:
    assert classify_sandbox_endpoint(host) is expected
