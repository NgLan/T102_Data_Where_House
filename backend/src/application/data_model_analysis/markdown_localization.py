"""Locale projection for deterministic Markdown labels and explanations."""

_ENGLISH_REPLACEMENTS = {
    "Phân tích Data Warehouse": "Data Warehouse Analysis",
    "Tổng quan": "Overview",
    "Mục tiêu": "Goal",
    "Requirements chính": "Key Requirements",
    "Analytical Requirements chính": "Key Analytical Requirements",
    "Chưa có": "None available",
    "Chưa xác định": "Unknown",
    "chưa xác định": "unknown",
    "grain chưa rõ": "unknown grain",
    "Thuật ngữ": "Glossary",
    "bảng business event/measure": "business event/measure table",
    "Áp dụng": "Applies to",
    "mức chi tiết của một dòng Fact": "detail level represented by one Fact row",
    "ngữ cảnh filter/group": "context used to filter/group",
    "khóa liên kết được khai báo trong DBML": "relationship key declared in DBML",
    "Thành phần model": "Model component",
    "Mức đáp ứng": "Coverage",
    "Phân tích Fact Table": "Fact Table Analysis",
    "Measures": "Measures",
    "Foreign keys": "Foreign keys",
    "Không có": "None",
    "Vì sao tồn tại": "Rationale",
    "Không phát hiện Fact theo cấu trúc/tên hiện tại": "No Fact table was identified from the current structure/name",
    "Phân tích Dimension Table": "Dimension Table Analysis",
    "Lý do tách Dimension (INFERRED)": "Dimension rationale (INFERRED)",
    "cung cấp ngữ cảnh mô tả để filter/group": "provides descriptive context for filtering/grouping",
    "Không phát hiện Dimension theo cấu trúc/tên hiện tại": "No Dimension table was identified from the current structure/name",
    "khai báo trong DBML": "declared in DBML",
    "Không có relationship được khai báo": "No relationship is declared",
    "Semantic Reasoning / Mapping": "Semantic Reasoning / Mapping",
    "Không có kết luận semantic bổ sung": "No additional semantic observation",
    "Đánh giá theo Data Warehouse Design Rules": "Data Warehouse Design Rule Assessment",
    "là source of truth và trả": "is the source of truth and returned",
    "Kết luận thiếu evidence được giữ là uncertainty, không tạo rule violation mới": "Conclusions without evidence remain uncertainties and do not create new rule violations",
    "Cảnh báo và gợi ý cải thiện": "Validation Warnings and Suggestions",
    "Toàn mô hình": "Whole model",
    "Vấn đề": "Issue",
    "Lý do": "Reason",
    "Ảnh hưởng": "Impact",
    "mô hình có thể vi phạm rule": "the model may violate rule",
    "Gợi ý": "Suggestion",
    "chỉnh đúng object nêu trên rồi chạy lại Validation Engine": "correct the referenced object and rerun the Validation Engine",
    "Không có issue deterministic tại revision này": "No deterministic issue exists at this revision",
    "Các điểm chưa xác định / cần xác nhận": "Uncertainties Requiring Confirmation",
    "Một hoặc nhiều Analytical Requirement chưa xác định grain": "One or more Analytical Requirements have no confirmed grain",
    "Chưa có Source Metadata để chứng minh lineage": "Source Metadata is unavailable to confirm lineage",
    "Có Dimension chưa xác định được key đáng tin cậy": "A Dimension has no reliable confirmed key",
    "SCD strategy cần Requirement hoặc metadata có evidence rõ ràng": "An SCD strategy requires explicit Requirement or metadata evidence",
    "Requirement": "Requirement",
    "và metric": "and metric",
    "liên kết này là INFERRED": "this mapping is INFERRED",
}


def localize_markdown(content: str, locale: str) -> str:
    if locale.casefold() != "en":
        return content
    localized = content
    for source, target in _ENGLISH_REPLACEMENTS.items():
        localized = localized.replace(source, target)
    return localized
