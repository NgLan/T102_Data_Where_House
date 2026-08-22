"""Regression tests cho coding guidelines của Application layer."""

import ast
import importlib
from pathlib import Path

APPLICATION_ROOT = Path(__file__).parents[1] / "backend" / "src" / "application"
FORBIDDEN_IMPORTS = (
    "fastapi",
    "pydantic",
    "sqlalchemy",
    "starlette",
    "src.infrastructure",
    "src.presentation",
)
MODULE_SERVICES = {
    "auth": "Auth",
    "projects": "Project",
    "requirements": "Requirement",
    "data_sources": "DataSource",
    "data_models": "DataModel",
    "sandbox": "Sandbox",
}
MAX_MODULE_LOGIC_LINES = 120
MAX_COHESIVE_SERVICE_LOGIC_LINES = 320


def _files() -> tuple[Path, ...]:
    return tuple(sorted(APPLICATION_ROOT.rglob("*.py")))


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _logic_lines(path: Path, tree: ast.Module) -> set[int]:
    lines = path.read_text(encoding="utf-8").splitlines()
    ignored: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if ast.get_docstring(node, clean=False) and getattr(node, "body", None):
            doc = node.body[0]
            ignored.update(range(doc.lineno, doc.end_lineno + 1))
    return {
        number
        for number, line in enumerate(lines, 1)
        if number not in ignored and line.strip() and not line.lstrip().startswith("#")
    }


def _function_size(node: ast.FunctionDef | ast.AsyncFunctionDef, logic: set[int]) -> int:
    body = node.body[1:] if ast.get_docstring(node, clean=False) else node.body
    if not body:
        return 0
    return len(set(range(body[0].lineno, body[-1].end_lineno + 1)) & logic)


def _imports(tree: ast.Module) -> tuple[str, ...]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return tuple(modules)


def test_application_has_no_forbidden_dependencies_or_legacy_layout() -> None:
    violations: list[str] = []
    for path in _files():
        for module in _imports(_tree(path)):
            if module.startswith(FORBIDDEN_IMPORTS):
                violations.append(f"{path.relative_to(APPLICATION_ROOT)}: {module}")
        if path.name == "dto.py":
            violations.append(f"{path.relative_to(APPLICATION_ROOT)}: generic dto.py")
    legacy = {"analytical_requirements", "sessions", "workflows"}
    present = {path.name for path in APPLICATION_ROOT.iterdir() if path.is_dir()}
    violations.extend(f"placeholder: {name}" for name in sorted(legacy & present))
    assert violations == []


def test_application_respects_size_type_and_parameter_limits() -> None:
    violations: list[str] = []
    for path in _files():
        tree = _tree(path)
        logic = _logic_lines(path, tree)
        relative = path.relative_to(APPLICATION_ROOT)
        file_limit = (
            MAX_COHESIVE_SERVICE_LOGIC_LINES
            if path.name.endswith("_service.py")
            else MAX_MODULE_LOGIC_LINES
        )
        if len(logic) > file_limit:
            violations.append(f"{relative}: {len(logic)} dòng logic")
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            args = (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
            business_args = [arg for arg in args if arg.arg not in {"self", "cls"}]
            if node.name != "__init__" and len(business_args) > 3:
                violations.append(f"{relative}:{node.lineno}: quá 3 tham số")
            if any(arg.annotation is None for arg in business_args) or node.returns is None:
                violations.append(f"{relative}:{node.lineno}: thiếu type hint")
            if _function_size(node, logic) > 25:
                violations.append(f"{relative}:{node.lineno}: quá 25 dòng logic")
    assert violations == []


def test_each_module_has_one_service_contract_and_implementation() -> None:
    violations: list[str] = []
    for module, prefix in MODULE_SERVICES.items():
        package = APPLICATION_ROOT / module
        interface_path = package / f"i_{module.rstrip('s')}_service.py"
        implementation_path = package / f"{module.rstrip('s')}_service.py"
        interface_files = tuple(package.glob("i_*.py"))
        if interface_files != (interface_path,):
            names = sorted(path.name for path in interface_files)
            violations.append(f"{module}: interface files {names}")
        expected = {f"I{prefix}Service", f"{prefix}Service"}
        found: set[str] = set()
        for path in (interface_path, implementation_path):
            if not path.exists():
                violations.append(f"{module}: thiếu {path.name}")
                continue
            found.update(node.name for node in _tree(path).body if isinstance(node, ast.ClassDef))
        if not expected <= found:
            violations.append(f"{module}: thiếu {sorted(expected - found)}")
        dependency_wrappers = {
            node.name
            for node in _tree(implementation_path).body
            if isinstance(node, ast.ClassDef) and node.name.endswith("ServiceDependencies")
        }
        if dependency_wrappers:
            violations.append(f"{module}: dependency wrapper {sorted(dependency_wrappers)}")
    assert violations == []


def test_service_implementations_mark_public_methods_as_override() -> None:
    violations: list[str] = []
    for module, prefix in MODULE_SERVICES.items():
        path = APPLICATION_ROOT / module / f"{module.rstrip('s')}_service.py"
        service = next(
            node
            for node in _tree(path).body
            if isinstance(node, ast.ClassDef) and node.name == f"{prefix}Service"
        )
        for method in service.body:
            if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) and not method.name.startswith("_"):
                decorators = {ast.unparse(item) for item in method.decorator_list}
                if "override" not in decorators:
                    violations.append(f"{path.name}:{method.lineno}: {method.name}")
    assert violations == []


def test_public_models_are_immutable_dataclasses_and_exports_are_valid() -> None:
    violations: list[str] = []
    for path in _files():
        relative = path.relative_to(APPLICATION_ROOT)
        if "input" in relative.parts or "output" in relative.parts:
            for node in _tree(path).body:
                if not isinstance(node, ast.ClassDef) or node.name.endswith("Dialect"):
                    continue
                if any(ast.unparse(base).endswith("Enum") for base in node.bases):
                    continue
                decorators = [ast.unparse(item) for item in node.decorator_list]
                if "dataclass(frozen=True, slots=True)" not in decorators:
                    violations.append(f"{relative}:{node.lineno}: {node.name}")
        if path.name == "__init__.py":
            module_path = path.parent.relative_to(APPLICATION_ROOT.parent)
            module = importlib.import_module(".".join(("src", *module_path.parts)))
            missing = [name for name in getattr(module, "__all__", ()) if not hasattr(module, name)]
            if missing:
                violations.append(f"{relative}: export {missing}")
    assert violations == []
