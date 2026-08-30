"""Artifact-producing Agent tool adapters."""

from dataclasses import dataclass

from src.application.agent_tools.models import AgentToolRequest, AgentToolResult, ToolArtifact
from src.application.common.i_file_store import IFileStore
from src.application.data_model_analysis import GenerateAnalysisDocumentInput, IDataModelAnalysisService
from src.application.data_models.i_data_model_service import IDataModelService
from src.application.data_models.input import GenerateDataModelDdlInput
from src.common.utils.uuid import generate_uuid
from src.domain.data_model.enums import DataModelTargetKind
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class _ArtifactDraft:
    filename: str
    mime_type: str
    content: str
    revision: int
    target_kind: DataModelTargetKind
    proposal_change_id: EntityID | None
    current_revision: int | None
    base_revision: int | None


class AgentArtifactToolHandler:
    def __init__(
        self,
        models: IDataModelService,
        analysis: IDataModelAnalysisService,
        files: IFileStore,
    ) -> None:
        self._models = models
        self._analysis = analysis
        self._files = files

    async def generate_analysis(self, data: AgentToolRequest) -> AgentToolResult:
        document = await self._analysis.generate_document(
            GenerateAnalysisDocumentInput(data.project_id, data.target, data.locale)
        )
        draft = _ArtifactDraft(
            document.filename,
            document.mime_type,
            document.content,
            document.data_model_revision,
            document.target_kind,
            document.proposal_change_id,
            document.current_revision,
            document.base_revision,
        )
        artifact = await self._save(data, draft)
        return AgentToolResult(data.name, True, "Tài liệu phân tích đã sẵn sàng.", artifact)

    async def generate_ddl(self, data: AgentToolRequest) -> AgentToolResult:
        ddl = await self._models.generate_ddl(GenerateDataModelDdlInput(data.project_id, data.db_type, data.target))
        draft = _ArtifactDraft(
            f"data_model_{data.db_type.value.casefold()}.sql",
            "text/plain",
            ddl.ddl,
            ddl.data_model_revision,
            ddl.target_kind,
            ddl.proposal_change_id,
            ddl.current_revision,
            ddl.base_revision,
        )
        artifact = await self._save(data, draft)
        return AgentToolResult(data.name, True, "File SQL đã sẵn sàng.", artifact)

    async def read(self, storage_path: str) -> bytes:
        return await self._files.read_file(storage_path)

    async def _save(self, data: AgentToolRequest, draft: _ArtifactDraft) -> ToolArtifact:
        artifact_id = generate_uuid()
        suffix = ".md" if draft.mime_type == "text/markdown" else ".sql"
        location = await self._files.save_file(
            str(data.project_id),
            f"agent-artifact-{artifact_id}{suffix}",
            draft.content.encode("utf-8"),
        )
        return ToolArtifact(
            artifact_id,
            draft.filename,
            location,
            draft.mime_type,
            draft.revision,
            draft.target_kind,
            draft.proposal_change_id,
            draft.current_revision,
            draft.base_revision,
        )
