"""Safe provider failure detail inspection cho compatibility path."""


def contains_quota_marker(detail: object) -> bool:
    """Nhận diện quota/billing marker mà không trả raw detail."""
    markers = (
        "insufficient_quota",
        "quota_exceeded",
        "quota exceeded",
        "quota exhausted",
        "billing_hard_limit",
    )
    return contains_any(str(detail).casefold(), markers)


def google_status_code(exc: Exception) -> int | None:
    """Đọc status chính thức hoặc exception class của Google SDK."""
    code = getattr(exc, "code", None)
    if isinstance(code, int):
        return code
    response = getattr(exc, "response", None)
    response_code = getattr(response, "status_code", None)
    if isinstance(response_code, int):
        return response_code
    names = {
        "unauthenticated": 401,
        "permissiondenied": 403,
        "notfound": 404,
        "resourceexhausted": 429,
        "deadlineexceeded": 408,
    }
    return names.get(type(exc).__name__.casefold())


def contains_any(value: str, markers: tuple[str, ...]) -> bool:
    """Kiểm tra marker giới hạn cho fallback compatibility."""
    return any(marker in value for marker in markers)
