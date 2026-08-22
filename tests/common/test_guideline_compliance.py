"""Regression tests cho các giới hạn bắt buộc trong common backend."""

import ast
from pathlib import Path

COMMON_ROOT = Path(__file__).parents[2] / "backend" / "src" / "common"
FORBIDDEN_IMPORTS = {
    "dto": ("fastapi", "starlette", "sqlalchemy", "src.domain", "src.infrastructure"),
    "interceptors": ("fastapi", "starlette", "sqlalchemy", "langgraph", "langfuse"),
    "logging": ("fastapi", "starlette", "sqlalchemy", "langgraph", "langfuse"),
    "utils": ("fastapi", "starlette", "sqlalchemy", "src.infrastructure"),
}


def _python_files() -> list[Path]:
    """Lấy mọi source file thuộc common."""
    return sorted(COMMON_ROOT.rglob("*.py"))


def _docstring_lines(tree: ast.AST) -> set[int]:
    """Lấy các dòng docstring để loại khỏi phép đếm logic."""
    lines: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(body, list) or not body or not isinstance(body[0], ast.Expr):
            continue
        value = body[0].value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            lines.update(range(body[0].lineno, body[0].end_lineno + 1))
    return lines


def _logic_lines(source_lines: list[str], ignored: set[int]) -> set[int]:
    """Lấy dòng code không rỗng, không comment và không phải docstring."""
    return {
        number
        for number, line in enumerate(source_lines, start=1)
        if number not in ignored and line.strip() and not line.lstrip().startswith("#")
    }


def _parameter_count(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Đếm tham số nghiệp vụ và bỏ qua ``self`` hoặc ``cls``."""
    positional = [*node.args.posonlyargs, *node.args.args]
    if positional and positional[0].arg in {"self", "cls"}:
        positional = positional[1:]
    return (
        len(positional)
        + len(node.args.kwonlyargs)
        + int(node.args.vararg is not None)
        + int(node.args.kwarg is not None)
    )


def test_common_size_limits() -> None:
    """Đảm bảo file và function không vượt giới hạn logic."""
    violations: list[str] = []
    for path in _python_files():
        source_lines = path.read_text(encoding="utf-8").splitlines()
        tree = ast.parse("\n".join(source_lines))
        logic_lines = _logic_lines(source_lines, _docstring_lines(tree))
        if len(logic_lines) > 120:
            violations.append(f"{path}: {len(logic_lines)} dòng logic")
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            body_start = node.body[0].lineno if node.body else node.end_lineno
            function_lines = set(range(body_start, node.end_lineno + 1)) & logic_lines
            if len(function_lines) > 25:
                violations.append(f"{path}:{node.lineno} {node.name}: {len(function_lines)} dòng")
            if _parameter_count(node) > 3:
                violations.append(f"{path}:{node.lineno} {node.name}: quá 3 tham số")
    assert not violations, "\n".join(violations)


def test_common_dependency_boundaries() -> None:
    """Đảm bảo các common package nhẹ không import dependency bị cấm."""
    violations: list[str] = []
    for package, forbidden_prefixes in FORBIDDEN_IMPORTS.items():
        for path in sorted((COMMON_ROOT / package).rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            modules = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
            modules += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
            for module in filter(None, modules):
                if module.startswith(forbidden_prefixes):
                    violations.append(f"{path}: import cấm {module}")
    assert not violations, "\n".join(violations)
