"""Search assertions ngăn contract API/metadata đã loại bỏ quay lại production source."""

from pathlib import Path

ROOT = Path(__file__).parents[1]
PRODUCTION_TARGETS = (
    ROOT / "backend" / "src",
    ROOT / "frontend" / "src",
)
REMOVED_REFERENCES = (
    "/data-model/update-proposal",
    "/data-model/ai-revisions",
    '"/api/v1/projects/{project_id}/analysis"',
    "/api/v1/projects/{project_id}/sandbox/ddl",
    '"/api/v1/sandbox/test-connection"',
    "extracted_requirement_text",
    "semantic_type",
    "ColumnSemanticType",
    "GenerateSandboxDdl",
    "ISandboxDdlGenerator",
)


def test_removed_contracts_are_absent_from_production_and_openapi() -> None:
    """Legacy chỉ được đọc trong SQL migration, không được tồn tại ở runtime contract."""
    content = "\n".join(_production_text())

    for reference in REMOVED_REFERENCES:
        assert reference not in content


def _production_text() -> list[str]:
    """Đọc source runtime và OpenAPI snapshot, bỏ qua generated cache/build artifacts."""
    files = [
        path
        for target in PRODUCTION_TARGETS
        for path in target.rglob("*")
        if path.suffix in {".py", ".ts", ".tsx"}
    ]
    files.append(ROOT / "frontend" / "openapi.json")
    return [path.read_text(encoding="utf-8") for path in files]
