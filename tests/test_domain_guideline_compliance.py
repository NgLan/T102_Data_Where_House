"""Kiểm tra tự động các ràng buộc kiến trúc và kích thước của Domain."""

import ast
import importlib
import re
from pathlib import Path

DOMAIN_ROOT = Path(__file__).parents[1] / "backend" / "src" / "domain"
FORBIDDEN_IMPORT_PREFIXES = (
    "fastapi",
    "langchain",
    "pydantic",
    "sqlalchemy",
    "src.application",
    "src.infrastructure",
    "src.presentation",
)
MAX_FILE_LOGIC_LINES = 120
MAX_FUNCTION_LOGIC_LINES = 25
MAX_BUSINESS_PARAMETERS = 3


def _domain_files() -> tuple[Path, ...]:
    """Trả về toàn bộ source Python thuộc Domain theo thứ tự ổn định."""
    return tuple(sorted(DOMAIN_ROOT.rglob("*.py")))


def _tree(path: Path) -> ast.Module:
    """Đọc và phân tích cú pháp một module Domain."""
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _logic_lines(lines: list[str], start: int = 1, end: int | None = None) -> int:
    """Đếm dòng logic, bỏ qua dòng trống và comment thuần."""
    selected = lines[start - 1 : end]
    return sum(bool(line.strip()) and not line.lstrip().startswith("#") for line in selected)


def test_domain_has_no_forbidden_layer_or_framework_imports() -> None:
    """Domain không được phụ thuộc layer ngoài hoặc framework bị cấm."""
    violations: list[str] = []
    for path in _domain_files():
        for node in ast.walk(_tree(path)):
            modules = _imported_modules(node)
            for module in modules:
                if module.startswith(FORBIDDEN_IMPORT_PREFIXES):
                    violations.append(f"{path.relative_to(DOMAIN_ROOT)}:{node.lineno}: {module}")
    assert violations == []


def test_domain_interfaces_use_dedicated_i_filename() -> None:
    """Mỗi interface IName phải nằm trong file i_name.py riêng."""
    violations: list[str] = []
    for path in _domain_files():
        interfaces = [
            node.name
            for node in _tree(path).body
            if isinstance(node, ast.ClassDef) and node.name.startswith("I") and node.name[1:2].isupper()
        ]
        if interfaces:
            expected = "i_" + re.sub(r"(?<!^)(?=[A-Z])", "_", interfaces[0][1:]).lower()
            if len(interfaces) != 1 or path.stem != expected:
                violations.append(f"{path.relative_to(DOMAIN_ROOT)}: {interfaces}")
    assert violations == []


def test_domain_uses_complete_types_without_any() -> None:
    """Domain không dùng Any và không để collection annotation ở dạng thô."""
    violations: list[str] = []
    for path in _domain_files():
        tree = _tree(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "Any":
                violations.append(f"{path.relative_to(DOMAIN_ROOT)}:{node.lineno}: Any")
            if isinstance(node, ast.arg) and node.arg not in {"self", "cls"} and node.annotation is None:
                violations.append(f"{path.relative_to(DOMAIN_ROOT)}:{node.lineno}: {node.arg}")
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns is None:
                violations.append(f"{path.relative_to(DOMAIN_ROOT)}:{node.lineno}: return")
        for annotation in _annotations(tree):
            if isinstance(annotation, ast.Name) and annotation.id in {"list", "dict", "set", "tuple"}:
                violations.append(
                    f"{path.relative_to(DOMAIN_ROOT)}:{annotation.lineno}: bare {annotation.id}"
                )
    assert violations == []


def test_domain_uses_shared_uuid_utility_and_valid_exports() -> None:
    """Domain không gọi uuid4 trực tiếp và mọi ``__all__`` đều có symbol thật."""
    violations: list[str] = []
    for path in _domain_files():
        if any(isinstance(node, ast.Name) and node.id == "uuid4" for node in ast.walk(_tree(path))):
            violations.append(f"{path.relative_to(DOMAIN_ROOT)}: uuid4")
        if path.name == "__init__.py":
            relative = path.parent.relative_to(DOMAIN_ROOT)
            module = importlib.import_module(".".join(("src", "domain", *relative.parts)))
            missing = [name for name in getattr(module, "__all__", ()) if not hasattr(module, name)]
            if missing:
                violations.append(f"{path.relative_to(DOMAIN_ROOT)}: {missing}")
    assert violations == []


def test_domain_respects_size_and_parameter_limits() -> None:
    """File, function và business parameter không vượt giới hạn guideline."""
    violations: list[str] = []
    for path in _domain_files():
        lines = path.read_text(encoding="utf-8").splitlines()
        if _logic_lines(lines) > MAX_FILE_LOGIC_LINES:
            violations.append(f"{path.relative_to(DOMAIN_ROOT)}: file")
        for node in ast.walk(_tree(path)):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                params = [arg.arg for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)]
                business_params = [name for name in params if name not in {"self", "cls"}]
                if len(business_params) > MAX_BUSINESS_PARAMETERS:
                    violations.append(f"{path.relative_to(DOMAIN_ROOT)}:{node.lineno}: params")
                if _function_logic_lines(lines, node) > MAX_FUNCTION_LOGIC_LINES:
                    violations.append(f"{path.relative_to(DOMAIN_ROOT)}:{node.lineno}: function")
    assert violations == []


def _function_logic_lines(lines: list[str], node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Đếm phần thân function và bỏ docstring đầu hàm."""
    body = node.body[1:] if ast.get_docstring(node, clean=False) and node.body else node.body
    if not body:
        return 0
    return _logic_lines(lines, body[0].lineno, body[-1].end_lineno)


def _imported_modules(node: ast.AST) -> tuple[str, ...]:
    """Lấy module được import bởi một AST node nếu có."""
    if isinstance(node, ast.Import):
        return tuple(alias.name for alias in node.names)
    if isinstance(node, ast.ImportFrom) and node.module:
        return (node.module,)
    return ()


def _annotations(tree: ast.Module) -> tuple[ast.expr, ...]:
    """Thu thập annotation của field, parameter và return value."""
    annotations: list[ast.expr] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign):
            annotations.append(node.annotation)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
            annotations.extend(arg.annotation for arg in args if arg.annotation is not None)
            if node.returns is not None:
                annotations.append(node.returns)
    return tuple(annotations)
