"""Kiểm thử framework PII đa ngôn ngữ dựa trên Microsoft Presidio."""

import pytest
from presidio_analyzer import Pattern, PatternRecognizer
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.security.pii.factory import (
    build_pii_masking_service,
    get_default_pii_masking_service,
)
from src.infrastructure.security.pii.masking_policy import (
    PiiMaskingPolicy,
    PiiOperator,
)
from src.infrastructure.security.pii.masking_service import PresidioPiiMaskingService
from src.infrastructure.security.pii.pii_entities import EMAIL_ADDRESS, PHONE_NUMBER


@pytest.fixture(scope="module")
def masking_service() -> PresidioPiiMaskingService:
    """Dựng một framework dùng chung cho nhóm test không thay registry."""
    return build_pii_masking_service()


def test_masks_english_text(masking_service: PresidioPiiMaskingService) -> None:
    """Built-in recognizer che email và số điện thoại tiếng Anh."""
    text = "Contact john@example.com or +1 212-555-1234."

    assert masking_service.mask(text, "en") == "Contact <EMAIL> or <PHONE>."


def test_masks_vietnamese_entities(masking_service: PresidioPiiMaskingService) -> None:
    """Recognizer Việt Nam che CCCD, PERSON và LOCATION khi đủ context."""
    text = (
        "CCCD: 001203123456, họ tên: Nguyễn Văn An, "
        "địa chỉ: 12 Nguyễn Trãi, Hà Nội."
    )

    masked = masking_service.mask(text, "vi")

    assert masked == "CCCD: <ID_NUMBER>, họ tên: <PERSON>, địa chỉ: <LOCATION>."


def test_masks_japanese_text(masking_service: PresidioPiiMaskingService) -> None:
    """Provider tiếng Nhật dùng built-in email và phone recognizer."""
    text = "メール taro@example.jp 電話 090-1234-5678"

    assert masking_service.mask(text, "ja") == "メール <EMAIL> 電話 <PHONE>"


def test_masks_mixed_language_text(masking_service: PresidioPiiMaskingService) -> None:
    """Một language provider vẫn che common entity trong văn bản trộn ngôn ngữ."""
    text = "Please email an@example.com hoặc gọi 0901234567."

    assert masking_service.mask(text, "vi") == "Please email <EMAIL> hoặc gọi <PHONE>."


def test_masks_multiple_pii_in_one_input(
    masking_service: PresidioPiiMaskingService,
) -> None:
    """Mọi PII không chồng lấn trong cùng input đều được anonymize."""
    text = (
        "Email a@example.com, phone 0901234567, CCCD: 001203123456, "
        "thẻ 4111111111111111."
    )

    masked = masking_service.mask(text, "vi")

    assert masked.count("<EMAIL>") == 1
    assert masked.count("<PHONE>") == 1
    assert masked.count("<ID_NUMBER>") == 1
    assert masked.count("<PAYMENT_CARD>") == 1


def test_keeps_text_without_pii(masking_service: PresidioPiiMaskingService) -> None:
    """Văn bản không có PII được giữ nguyên."""
    text = "Tăng retention lên 90 ngày cho bảng giao dịch."

    assert masking_service.mask(text, "vi") == text


def test_keeps_low_confidence_numeric_value(
    masking_service: PresidioPiiMaskingService,
) -> None:
    """Chuỗi 12 số không có context định danh không bị coi là CCCD."""
    text = "Mã giao dịch 001203123456 đã hoàn tất."

    assert masking_service.mask(text, "vi") == text


def test_registers_custom_recognizer_without_core_change() -> None:
    """Registry nhận custom PatternRecognizer trong lúc chạy."""
    service = build_pii_masking_service()
    service.register_recognizer(
        PatternRecognizer(
            supported_entity="EMPLOYEE_ID",
            supported_language="en",
            patterns=[Pattern("Employee ID", r"\bEMP-\d{4}\b", 0.9)],
        )
    )
    policy = PiiMaskingPolicy({"EMPLOYEE_ID": PiiOperator.replace("<EMPLOYEE>")})

    assert service.mask("Owner EMP-1234", "en", policy) == "Owner <EMPLOYEE>"


def test_applies_different_masking_policy(
    masking_service: PresidioPiiMaskingService,
) -> None:
    """Caller có thể chọn operator riêng cho từng entity."""
    policy = PiiMaskingPolicy(
        {
            EMAIL_ADDRESS: PiiOperator.replace("<MAILBOX>"),
            PHONE_NUMBER: PiiOperator("redact"),
        }
    )

    masked = masking_service.mask("a@example.com / 0901234567", "vi", policy)

    assert masked == "<MAILBOX> / "


def test_detect_accepts_language_and_entity_filter(
    masking_service: PresidioPiiMaskingService,
) -> None:
    """Detect chỉ trả entity caller yêu cầu cho đúng language."""
    results = masking_service.detect(
        "a@example.com 0901234567",
        "vi",
        (EMAIL_ADDRESS,),
    )

    assert [result.entity_type for result in results] == [EMAIL_ADDRESS]


def test_rejects_unsupported_language(
    masking_service: PresidioPiiMaskingService,
) -> None:
    """Language ngoài cấu hình được dịch thành lỗi hạ tầng có chain."""
    with pytest.raises(InfrastructureException) as error:
        masking_service.mask("a@example.com", "fr")

    assert isinstance(error.value.__cause__, ValueError)


def test_default_framework_is_reused() -> None:
    """Factory mặc định không dựng lại engine và registry theo request."""
    assert get_default_pii_masking_service() is get_default_pii_masking_service()
