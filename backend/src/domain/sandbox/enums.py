"""Định nghĩa các Enum cho miền Sandbox."""

from enum import StrEnum


class SandboxDbType(StrEnum):
    """Loại cơ sở dữ liệu Sandbox."""

    POSTGRESQL = "POSTGRESQL"
    BIGQUERY = "BIGQUERY"
    SNOWFLAKE = "SNOWFLAKE"
    MYSQL = "MYSQL"
    SQLITE = "SQLITE"
    SQLSERVER = "SQLSERVER"


class SandboxStatus(StrEnum):
    """Trạng thái cấu hình của Sandbox."""

    CONFIGURED = "CONFIGURED"
    CONNECTED = "CONNECTED"
    FAILED = "FAILED"


class SandboxEndpointRisk(StrEnum):
    """Mức cảnh báo dựa trên endpoint literal, không thực hiện DNS lookup."""

    LOOPBACK = "LOOPBACK"
    PRIVATE_NETWORK = "PRIVATE_NETWORK"
    REMOTE = "REMOTE"
