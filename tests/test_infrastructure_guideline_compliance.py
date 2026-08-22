"""Architecture fitness functions cho tầng Infrastructure."""

import ast
import importlib
import io
import pkgutil
import tokenize
from pathlib import Path

import src.infrastructure

INFRASTRUCTURE_ROOT = Path("backend/src/infrastructure")
LEGACY_FILES = {
    "agents/graph.py",
    "agents/state.py",
    "llm/models.py",
    "storage/excel_parser.py",
    "storage/docx_parser.py",
    "storage/csv_inference.py",
    "storage/file_storage.py",
    "storage/local_project_artifact_store.py",
}


def test_no_empty_or_legacy_python_files() -> None:
    files = list(INFRASTRUCTURE_ROOT.rglob("*.py"))
    assert all(path.read_text(encoding="utf-8").strip() for path in files)
    relative_paths = {path.relative_to(INFRASTRUCTURE_ROOT).as_posix() for path in files}
    assert not relative_paths.intersection(LEGACY_FILES)


def test_files_and_functions_stay_within_size_limits() -> None:
    for path in INFRASTRUCTURE_ROOT.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        assert len(_logic_rows(source, tree)) <= 120, path
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                assert len(_function_rows(source, node)) <= 25, f"{path}:{node.name}"


def test_functions_are_typed_and_have_at_most_three_domain_parameters() -> None:
    for path in INFRASTRUCTURE_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            parameters = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
            domain_parameters = [item for item in parameters if item.arg not in {"self", "cls"}]
            assert len(domain_parameters) <= 3 or node.name in {"__aexit__"}, f"{path}:{node.name}"
            assert all(item.annotation is not None for item in domain_parameters), f"{path}:{node.name}"
            assert node.returns is not None, f"{path}:{node.name}"


def test_clean_architecture_import_direction_and_public_docs() -> None:
    for path in INFRASTRUCTURE_ROOT.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "src.presentation" not in source, path
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    assert ast.get_docstring(node), f"{path}:{node.name}"


def test_all_infrastructure_modules_import() -> None:
    modules = pkgutil.walk_packages(
        src.infrastructure.__path__,
        prefix="src.infrastructure.",
    )
    for module in modules:
        importlib.import_module(module.name)


def _logic_rows(source: str, tree: ast.AST) -> set[int]:
    """Lấy các dòng code, không tính comment, dòng trống và docstring."""
    ignored = _docstring_rows(tree)
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    excluded = {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER}
    return {token.start[0] for token in tokens if token.type not in excluded and token.start[0] not in ignored}


def _function_rows(source: str, node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[int]:
    """Đếm dòng logic riêng của function, không tính nested function."""
    rows = _logic_rows(source, node)
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            rows.difference_update(range(child.lineno, child.end_lineno + 1))
    return {row for row in rows if node.lineno <= row <= node.end_lineno}


def _docstring_rows(tree: ast.AST) -> set[int]:
    """Thu thập khoảng dòng của mọi docstring trong cây AST."""
    rows: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(body, list) and body and isinstance(body[0], ast.Expr):
            if not isinstance(body[0].value, ast.Constant):
                continue
            if isinstance(body[0].value.value, str):
                rows.update(range(body[0].lineno, body[0].end_lineno + 1))
    return rows
