"""Type aliases cho cấu hình FastAPI routing."""

from typing import Any, TypeAlias

ErrorResponses: TypeAlias = dict[int | str, dict[str, Any]]
