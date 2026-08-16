"""PII Guard — che thông tin cá nhân trước khi gửi dữ liệu sang LLM API (FR6.2).

Tương ứng thành phần **PII Guard** trong `docs/guide_cho_ca_nhom/data_flow.md` §2.4, chặn
giữa Agent và LLM API theo luồng:

    Agent -> PII guard -> masked -> LLM API -> completion -> PII guard -> Agent

Module cung cấp hai cơ chế khác nhau cho hai loại dữ liệu:

* **Tên cột trong DBML** — thay thế *có hoàn nguyên*: `phone_number` -> `pii_field_01`.
  Bắt buộc khôi phục được vì DBML phải quay về nguyên trạng, nếu không mô hình dữ liệu
  chính thức sẽ bị hỏng tên cột.
* **Giá trị PII trong văn bản tự do** — che *một chiều*: `0901234567` -> `[PII_PHONE]`.
  Không cần khôi phục vì câu lệnh của người dùng không được LLM trả lại.

Bảng ánh xạ chỉ tồn tại trong vòng đời một lời gọi: KHÔNG lưu xuống CSDL, KHÔNG ghi ra log.
"""

import re
from dataclasses import dataclass, field
from typing import Final

from src.common.logging import get_logger

logger = get_logger(__name__)

# Từ khóa nhận diện tên cột chứa thông tin cá nhân. Bám theo FR6.2 (phone, email,
# social_security_number, credit_card) và bổ sung một số trường phổ biến ở Việt Nam.
PII_COLUMN_KEYWORDS: Final[tuple[str, ...]] = (
    "phone",
    "email",
    "ssn",
    "social_security",
    "credit_card",
    "card_number",
    "address",
    "birth",
    "dob",
    "passport",
    "national_id",
    "cccd",
    "cmnd",
    "tax_code",
    "full_name",
)

# Mẫu nhận diện GIÁ TRỊ PII xuất hiện trong văn bản tự do người dùng nhập.
PII_VALUE_PATTERNS: Final[tuple[tuple[str, str], ...]] = (
    (r"[\w.+-]+@[\w-]+\.[\w.]+", "[PII_EMAIL]"),
    (r"(?:\+84|0)\d{9,10}\b", "[PII_PHONE]"),
    (r"\b\d{12}\b", "[PII_NATIONAL_ID]"),
    (r"\b(?:\d[ -]?){13,19}\b", "[PII_CARD_NUMBER]"),
)

# Tiền tố và định dạng mã thay thế. Là định danh DBML hợp lệ nên không phá cú pháp.
PLACEHOLDER_PREFIX: Final[str] = "pii_field_"
PLACEHOLDER_TEMPLATE: Final[str] = PLACEHOLDER_PREFIX + "{index:02d}"
RESIDUAL_PLACEHOLDER_REGEX: Final[re.Pattern[str]] = re.compile(
    rf"\b{PLACEHOLDER_PREFIX}\d+\b"
)

# Nhận diện tên cột ở đầu mỗi dòng khai báo trong khối `Table { ... }` của DBML.
# Nhận diện mọi token định danh (tên bảng, tên cột) trong văn bản bất kỳ.
_IDENTIFIER_REGEX: Final[re.Pattern[str]] = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")

_COLUMN_LINE_REGEX: Final[re.Pattern[str]] = re.compile(
    r"^(?P<indent>\s+)(?P<name>[A-Za-z_][A-Za-z0-9_]*)(?=\s+\S)"
)

# Các từ khóa mở đầu dòng KHÔNG phải là khai báo cột, không được đụng tới.
_NON_COLUMN_LINE_KEYWORDS: Final[frozenset[str]] = frozenset(
    {"table", "ref", "indexes", "note", "enum", "project", "tablegroup"}
)


@dataclass(frozen=True)
class MaskedPayload:
    """Kết quả che dữ liệu có thể hoàn nguyên."""

    text: str
    mapping: dict[str, str] = field(default_factory=dict)

    @property
    def masked_count(self) -> int:
        """Số lượng trường đã được che."""
        return len(self.mapping)


class PiiGuard:
    """Bộ che thông tin cá nhân đặt giữa AI Agent và LLM API.

    Khi `enabled=False`, mọi phương thức trở thành no-op — dùng để gỡ lỗi chất lượng
    đầu ra của Agent mà không bị nhiễu bởi mã thay thế.
    """

    def __init__(self, enabled: bool = True) -> None:
        """Khởi tạo bộ che PII, mặc định luôn bật."""
        self._enabled: bool = enabled

    @property
    def enabled(self) -> bool:
        """Trạng thái bật/tắt của bộ che."""
        return self._enabled

    def mask_schema(self, dbml: str) -> MaskedPayload:
        """Thay tên cột nhạy cảm trong DBML bằng mã ẩn danh có thể hoàn nguyên."""
        if not self._enabled or not dbml:
            return MaskedPayload(text=dbml)

        return self._apply_placeholders(dbml, self._collect_sensitive_columns(dbml))

    def _apply_placeholders(self, text: str, originals: list[str]) -> MaskedPayload:
        """Thay danh sách định danh gốc bằng mã ẩn danh và dựng bảng ánh xạ ngược."""
        original_to_placeholder: dict[str, str] = {}
        for name in originals:
            index = len(original_to_placeholder) + 1
            original_to_placeholder[name] = PLACEHOLDER_TEMPLATE.format(index=index)

        masked_text = text
        for original, placeholder in original_to_placeholder.items():
            masked_text = re.sub(rf"\b{re.escape(original)}\b", placeholder, masked_text)

        mapping = {
            placeholder: original for original, placeholder in original_to_placeholder.items()
        }
        if mapping:
            logger.info("pii_schema_masked fields=%d", len(mapping))
        return MaskedPayload(text=masked_text, mapping=mapping)

    def mask_identifiers(self, text: str) -> MaskedPayload:
        """Che mọi định danh nhạy cảm xuất hiện BẤT KỲ ĐÂU trong văn bản (có hoàn nguyên).

        Khác `mask_schema` vốn chỉ quét dòng khai báo cột của DBML, hàm này quét toàn bộ
        token định danh nên dùng được cho văn xuôi mô tả nguồn dữ liệu và cho JSON schema —
        đây mới là dạng đầu vào của các agent trong pipeline sinh mô hình.
        """
        if not self._enabled or not text:
            return MaskedPayload(text=text)

        originals: list[str] = []
        for token in _IDENTIFIER_REGEX.findall(text):
            if self._is_sensitive_column(token) and token not in originals:
                originals.append(token)

        return self._apply_placeholders(text, originals)

    def mask_free_text(self, text: str) -> str:
        """Che các giá trị PII xuất hiện trong văn bản tự do (che một chiều)."""
        if not self._enabled or not text:
            return text

        masked = text
        replaced = 0
        for pattern, placeholder in PII_VALUE_PATTERNS:
            masked, count = re.subn(pattern, placeholder, masked)
            replaced += count

        if replaced:
            logger.info("pii_free_text_masked occurrences=%d", replaced)
        return masked

    def unmask(self, text: str, mapping: dict[str, str]) -> str:
        """Khôi phục tên gốc từ mã thay thế."""
        if not mapping or not text:
            return text

        restored = text
        for placeholder, original in mapping.items():
            restored = re.sub(rf"\b{re.escape(placeholder)}\b", original, restored)
        return restored

    def has_residual_placeholder(self, text: str) -> bool:
        """Kiểm tra văn bản còn sót mã thay thế PII sau khi đã hoàn nguyên hay không.

        Dùng làm chốt chặn fail-closed: nếu LLM tự đổi mã thay thế (ví dụ `pii_field_01`
        thành `pii_field_1`) thì phép hoàn nguyên sẽ hụt và DBML không được phép lưu.
        """
        if not text:
            return False
        return RESIDUAL_PLACEHOLDER_REGEX.search(text) is not None

    def _collect_sensitive_columns(self, dbml: str) -> list[str]:
        """Duyệt DBML và thu thập tên cột khớp danh sách từ khóa nhạy cảm."""
        collected: list[str] = []
        for line in dbml.splitlines():
            match = _COLUMN_LINE_REGEX.match(line)
            if not match:
                continue

            name = match.group("name")
            if name.lower() in _NON_COLUMN_LINE_KEYWORDS:
                continue
            if not self._is_sensitive_column(name):
                continue
            if name not in collected:
                collected.append(name)
        return collected

    def _is_sensitive_column(self, column_name: str) -> bool:
        """Kiểm tra tên cột có chứa từ khóa nhạy cảm hay không."""
        lowered = column_name.lower()
        return any(keyword in lowered for keyword in PII_COLUMN_KEYWORDS)
