"""Sinh PostgreSQL DDL và insight cấu trúc bằng PyDBML."""

try:
    from pydbml import PyDBML
except ImportError:
    PyDBML = None  # type: ignore

try:
    from sqlglot import transpile
except ImportError:
    transpile = None  # type: ignore
from src.application.data_models.artifact_generator import IDataModelArtifactGenerator
from src.application.data_models.output import DataModelInsightOutput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from typing_extensions import override


class PyDbmlArtifactGenerator(IDataModelArtifactGenerator):
    """Adapter PyDBML cho codegen và phân tích Data Model."""

    @override
    def generate_ddl(self, dbml: str, dialect: str) -> str:
        normalized = dialect.strip().lower()
        if normalized not in {"postgresql", "postgres"}:
            raise BusinessException(
                code=ErrorCode.UNSUPPORTED_DDL_DIALECT,
                message=f"Dialect '{dialect}' chưa được hỗ trợ.",
            )
        database = self._parse(dbml)
        statements = transpile(database.sql, read="sqlite", write="postgres")
        return ";\n\n".join(statements).strip() + ";"

    @override
    def analyze(self, dbml: str) -> list[DataModelInsightOutput]:
        database = self._parse(dbml)
        outgoing_tables = {
            ref.col1[0].table.name
            for ref in database.refs
            if ref.col1 and getattr(ref.col1[0], "table", None) is not None
        }
        insights: list[DataModelInsightOutput] = []
        for table in database.tables:
            primary_keys = [column.name for column in table.columns if column.pk]
            if primary_keys:
                insights.append(
                    DataModelInsightOutput(
                        id=f"{table.name}:grain",
                        table_name=table.name,
                        severity="info",
                        title="Grain của bảng",
                        description=("Mỗi dòng được định danh bởi khóa " + ", ".join(primary_keys) + "."),
                    )
                )
            else:
                insights.append(
                    DataModelInsightOutput(
                        id=f"{table.name}:missing-primary-key",
                        table_name=table.name,
                        severity="error",
                        title="Thiếu khóa chính",
                        description="Bảng chưa có cột khóa chính để xác định grain ổn định.",
                    )
                )

            is_fact = table.name.lower().startswith("fact_") or table.name in outgoing_tables
            if is_fact and table.name not in outgoing_tables:
                insights.append(
                    DataModelInsightOutput(
                        id=f"{table.name}:missing-reference",
                        table_name=table.name,
                        severity="warn",
                        title="Fact chưa liên kết dimension",
                        description="Nên kiểm tra lại các foreign key tới bảng dimension.",
                    )
                )
            if not table.indexes and len(table.columns) >= 3:
                insights.append(
                    DataModelInsightOutput(
                        id=f"{table.name}:index-review",
                        table_name=table.name,
                        severity="warn",
                        title="Cần rà soát index",
                        description="Ngoài khóa chính, bảng chưa khai báo index phục vụ truy vấn.",
                    )
                )
        return insights

    @staticmethod
    def _parse(dbml: str):
        try:
            return PyDBML(dbml)
        except Exception as exc:
            raise BusinessException(
                code=ErrorCode.INVALID_DBML_CONTENT,
                message="Không thể sinh artifact từ DBML không hợp lệ.",
            ) from exc
