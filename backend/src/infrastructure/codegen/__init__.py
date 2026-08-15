"""Module Codegen: biên dịch mô hình dữ liệu DBML thành mã DDL đa hệ quản trị CSDL."""

from src.infrastructure.codegen.dbml_parser import parse_dbml
from src.infrastructure.codegen.ddl_generator import DbmlDdlGenerator

__all__: list[str] = [
    "DbmlDdlGenerator",
    "parse_dbml",
]
