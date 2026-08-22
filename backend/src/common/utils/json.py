"""Utilities xử lý JSON (json.py).

Hỗ trợ serialize an toàn cho các kiểu dữ liệu phổ biến:
UUID, datetime, Enum, Decimal, Pydantic BaseModel.
"""

import json
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder xử lý UUID, datetime, Enum, Decimal và Pydantic BaseModel."""

    def default(self, o: Any) -> Any:  # chữ ký chuẩn của JSONEncoder
        """Chuyển kiểu dữ liệu được hỗ trợ thành giá trị JSON.

        Args:
            o: Đối tượng cần chuyển đổi.

        Returns:
            Giá trị mà ``json`` có thể tuần tự hóa.

        Raises:
            TypeError: Khi kiểu dữ liệu không được hỗ trợ.
        """
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, Decimal):
            return float(o) if o % 1 != 0 else int(o)
        if isinstance(o, BaseModel):
            return o.model_dump(mode="json")
        return super().default(o)


def safe_json_dumps(
    obj: Any,  # noqa: ANN401 - contract utility nhận mọi giá trị Python
    *,
    ensure_ascii: bool = False,
    indent: int | None = None,
) -> str:
    """Serialize đối tượng Python thành chuỗi JSON an toàn.

    Args:
        obj: Đối tượng cần tuần tự hóa.
        ensure_ascii: Có escape ký tự ngoài ASCII hay không.
        indent: Số khoảng trắng thụt lề, hoặc ``None`` cho JSON gọn.

    Returns:
        Chuỗi JSON.

    Raises:
        TypeError: Khi gặp kiểu dữ liệu không được hỗ trợ.
    """
    return json.dumps(
        obj,
        cls=CustomJSONEncoder,
        ensure_ascii=ensure_ascii,
        indent=indent,
    )


def safe_json_loads(json_str: str) -> Any:  # noqa: ANN401 - JSON có kiểu đệ quy động
    """Parse chuỗi JSON thành Python object primitives.

    Args:
        json_str: Chuỗi JSON cần phân tích.

    Returns:
        Giá trị Python chỉ gồm các kiểu dữ liệu JSON.

    Raises:
        ValueError: Khi chuỗi rỗng hoặc sai định dạng JSON.
    """
    if not isinstance(json_str, str) or not json_str.strip():
        raise ValueError("Chuỗi JSON đầu vào không được rỗng.")

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Chuỗi JSON không đúng định dạng: {e}") from e
