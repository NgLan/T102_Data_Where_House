"""PyDBML adapter cho cấu trúc dùng bởi analysis application."""

from src.application.data_model_analysis.i_data_model_analysis_service import IDataModelStructureExtractor
from src.application.data_model_analysis.models import ModelColumn, ModelRelationship, ModelStructure, ModelTable
from src.infrastructure.codegen.dbml_parser import parse_dbml
from typing_extensions import override


class PyDbmlStructureExtractor(IDataModelStructureExtractor):
    """Chuyển AST PyDBML thành cấu trúc typed độc lập thư viện."""

    @override
    def extract(self, dbml: str) -> ModelStructure:
        database = parse_dbml(dbml)
        foreign_keys = _foreign_key_endpoints(database)
        tables = tuple(
            ModelTable(
                table.name,
                tuple(ModelColumn(column.name, str(column.type), bool(getattr(column, "pk", False)),
                                  f"{table.name}.{column.name}" in foreign_keys) for column in table.columns),
                _note(table),
            )
            for table in database.tables
        )
        relationships = tuple(_relationship(item) for item in getattr(database, "refs", ()))
        return ModelStructure(tables, relationships)


def _foreign_key_endpoints(database: object) -> set[str]:
    return {
        f"{column.table.name}.{column.name}"
        for reference in getattr(database, "refs", ())
        for column in getattr(reference, "col1", ())
        if getattr(column, "table", None) is not None
    }


def _relationship(reference: object) -> ModelRelationship:
    left = _endpoint(getattr(reference, "col1", ()))
    right = _endpoint(getattr(reference, "col2", ()))
    return ModelRelationship(left, right, str(getattr(reference, "type", "UNKNOWN")))


def _endpoint(columns: object) -> str:
    return ", ".join(f"{item.table.name}.{item.name}" for item in columns)


def _note(table: object) -> str:
    note = getattr(table, "note", None)
    return str(getattr(note, "text", None) or getattr(note, "value", None) or note or "")
