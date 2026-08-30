"""Application service cho Data Model snapshot và Human Review."""

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_models.i_data_model_service import IDataModelDdlGenerator, IDataModelService
from src.application.data_models.input import (
    ChangeProposalIdInput,
    GenerateDataModelDdlInput,
    GetChangeProposalInput,
    GetDataModelInput,
    GetPendingChangeProposalInput,
    ResolveDataModelTargetInput,
    UpdateDataModelInput,
    ValidateDataModelInput,
)
from src.application.data_models.output import (
    ChangeProposalDetailOutput,
    ChangeProposalSummaryOutput,
    DataModelDdlOutput,
    DataModelOutput,
    ResolvedDataModelTargetOutput,
)
from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataModelValidationEngine,
)
from src.application.data_warehouse_workflows.output import ValidationIssue, ValidationSeverity
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.data_model.enums import DataModelChangeStatus, DataModelTargetKind
from src.domain.data_model.i_data_model_change_repository import IDataModelChangeRepository
from src.domain.data_model.i_data_model_repository import IDataModelRepository
from src.domain.project.entities import Project
from src.domain.shared.types import EntityID
from typing_extensions import override


class DataModelService(IDataModelService):
    """Điều phối snapshot, validation và proposal bằng revision rõ ràng."""

    def __init__(
        self,
        models: IDataModelRepository,
        changes: IDataModelChangeRepository,
        validator: IDataModelValidationEngine,
        unit_of_work: IUnitOfWork,
        access: ProjectAccessPolicy,
        ddl_generator: IDataModelDdlGenerator,
    ) -> None:
        self._models = models
        self._changes = changes
        self._validator = validator
        self._unit_of_work = unit_of_work
        self._access = access
        self._ddl_generator = ddl_generator

    @override
    async def get_data_model(self, data: GetDataModelInput) -> DataModelOutput:
        """Lấy model và tính outdated từ analysis revisions hiện tại."""
        project = (await self._access.require_member(data.project_id)).project
        model = await self._require_project_model(data.project_id)
        outdated = model.is_outdated(project.analyzed_requirement_revision, project.analyzed_source_revision)
        return DataModelOutput.from_domain(model, outdated)

    @override
    async def update_data_model(self, data: UpdateDataModelInput) -> DataModelOutput:
        """Validate rồi lưu trực tiếp DBML do người dùng chỉnh sửa."""
        self._ensure_valid(data.dbml)
        async with self._unit_of_work:
            project = await self._access.require_owner(data.project_id)
            model = await self._require_project_model(data.project_id)
            _validate_update_target(model, data)
            model.update_dbml(data.dbml, data.base_revision)
            saved = await self._models.update_if_revision_matches(model, data.base_revision)
            if saved is None:
                raise BusinessException(ErrorCode.DATA_MODEL_REVISION_CONFLICT, "Data Model đã thay đổi.")
            await self._unit_of_work.commit()
        outdated = saved.is_outdated(
            project.analyzed_requirement_revision,
            project.analyzed_source_revision,
        )
        return DataModelOutput.from_domain(saved, outdated)

    @override
    async def get_validation_issues(self, data: GetDataModelInput) -> tuple[ValidationIssue, ...]:
        """Validate snapshot hiện hành bằng ValidationEngine dùng chung."""
        await self._access.require_member(data.project_id)
        model = await self._require_project_model(data.project_id)
        return self._validator.validate(model.dbml)

    @override
    async def validate_draft(self, data: ValidateDataModelInput) -> tuple[ValidationIssue, ...]:
        """Kiểm tra draft bằng ValidationEngine deterministic dùng chung."""
        await self._access.require_member(data.project_id)
        return self._validator.validate(data.dbml)

    @override
    async def get_change_proposal(self, data: GetChangeProposalInput) -> ChangeProposalDetailOutput:
        """Lấy proposal và tính outdated từ base revision của Data Model."""
        change, model = await self._load_change(data.change_id)
        await self._access.require_member(data.project_id)
        if model.project_id != data.project_id:
            raise BusinessException(
                ErrorCode.DATA_MODEL_CHANGE_NOT_FOUND,
                "Không tìm thấy đề xuất thay đổi Data Model trong dự án.",
            )
        return ChangeProposalDetailOutput.from_domain(change, model)

    @override
    async def get_pending_change_proposal(
        self, data: GetPendingChangeProposalInput
    ) -> ChangeProposalDetailOutput | None:
        await self._access.require_owner(data.project_id)
        model = await self._require_project_model(data.project_id)
        change = await self._changes.get_proposed_by_data_model_and_user(
            model.id, self._access.actor_id
        )
        return ChangeProposalDetailOutput.from_domain(change, model) if change else None

    @override
    async def generate_ddl(self, data: GenerateDataModelDdlInput) -> DataModelDdlOutput:
        """Sinh DDL từ target đã resolve sau khi kiểm tra membership."""
        target = await self.resolve_target(
            ResolveDataModelTargetInput(data.project_id, data.target)
        )
        return DataModelDdlOutput(
            ddl=self._ddl_generator.generate_ddl(target.dbml, data.db_type),
            db_type=data.db_type,
            data_model_revision=target.revision,
            target_kind=target.kind,
            proposal_change_id=target.proposal_change_id,
            current_revision=target.current_revision or target.revision,
            base_revision=target.base_revision or target.revision,
        )

    @override
    async def resolve_target(
        self, data: ResolveDataModelTargetInput
    ) -> ResolvedDataModelTargetOutput:
        """Resolve target mà không fallback proposal sang current model."""
        await self._access.require_member(data.project_id)
        model = await self._require_project_model(data.project_id)
        if data.target.kind is DataModelTargetKind.CURRENT_MODEL:
            return ResolvedDataModelTargetOutput(
                data.project_id,
                model.dbml,
                model.revision,
                DataModelTargetKind.CURRENT_MODEL,
                model.id,
                current_revision=model.revision,
                base_revision=model.revision,
            )
        change = await self._resolve_proposal(model, data.target.change_id)
        return ResolvedDataModelTargetOutput(
            data.project_id,
            change.proposed_dbml,
            change.base_revision,
            DataModelTargetKind.PROPOSAL,
            model.id,
            change.id,
            current_revision=model.revision,
            base_revision=change.base_revision,
        )

    async def _resolve_proposal(
        self, model: DataModel, change_id: EntityID | None
    ) -> DataModelChange:
        change = (
            await self._changes.get_by_id(change_id)
            if change_id
            else await self._changes.get_proposed_by_data_model_and_user(
                model.id, self._access.actor_id
            )
        )
        if change is None or change.data_model_id != model.id:
            raise BusinessException(
                ErrorCode.DATA_MODEL_CHANGE_NOT_FOUND,
                "Không tìm thấy proposal phù hợp với target được yêu cầu.",
            )
        if change.status is not DataModelChangeStatus.PROPOSED:
            raise BusinessException(
                ErrorCode.DATA_MODEL_CHANGE_OUTDATED,
                "Proposal không còn ở trạng thái chờ review.",
            )
        return change

    @override
    async def accept_change_proposal(self, data: ChangeProposalIdInput) -> DataModelOutput:
        """Chỉ áp dụng proposal khi base revision của Data Model còn khớp."""
        model, project, is_outdated = await self._persist_change_acceptance(data.change_id)
        if is_outdated:
            raise BusinessException(
                ErrorCode.DATA_MODEL_CHANGE_OUTDATED,
                "Đề xuất thay đổi dựa trên revision Data Model đã lỗi thời.",
            )
        return DataModelOutput.from_domain(
            model,
            model.is_outdated(
                project.analyzed_requirement_revision,
                project.analyzed_source_revision,
            ),
        )

    async def _persist_change_acceptance(self, change_id: EntityID) -> tuple[DataModel, Project, bool]:
        """Persist trạng thái proposal và snapshot trong cùng transaction."""
        async with self._unit_of_work:
            change, model = await self._load_change(change_id)
            project = await self._access.require_owner(model.project_id)
            outdated = change.base_revision != model.revision
            if outdated:
                change.mark_conflicted()
            else:
                await self._apply_current_change(change, model, project)
            await self._changes.save(change)
            await self._unit_of_work.commit()
        return model, project, outdated

    async def _apply_current_change(self, change: DataModelChange, model: DataModel, project: Project) -> None:
        """Validate và áp dụng proposal còn khớp revision hiện hành."""
        self._ensure_valid(change.proposed_dbml)
        model.apply_change(change)
        model.record_generation_revisions(
            project.analyzed_requirement_revision,
            project.analyzed_source_revision,
        )
        await self._models.save(model)

    @override
    async def reject_change_proposal(self, data: ChangeProposalIdInput) -> ChangeProposalSummaryOutput:
        """Từ chối proposal mà không sửa snapshot."""
        async with self._unit_of_work:
            change, model = await self._load_change(data.change_id)
            await self._access.require_owner(model.project_id)
            change.mark_rejected()
            saved = await self._changes.save(change)
            await self._unit_of_work.commit()
        return ChangeProposalSummaryOutput.from_domain(saved)

    async def _require_project_model(self, project_id: EntityID) -> DataModel:
        model = await self._models.get_by_project_id(project_id)
        if model is None:
            raise BusinessException(ErrorCode.DATA_MODEL_NOT_FOUND, "Không tìm thấy Data Model.")
        return model

    async def _load_change(self, change_id: EntityID) -> tuple[DataModelChange, DataModel]:
        change = await self._changes.get_by_id(change_id)
        if change is None:
            raise BusinessException(
                ErrorCode.DATA_MODEL_CHANGE_NOT_FOUND,
                "Không tìm thấy đề xuất thay đổi Data Model.",
            )
        model = await self._models.get_by_id(change.data_model_id)
        if model is None:
            raise BusinessException(ErrorCode.DATA_MODEL_NOT_FOUND, "Không tìm thấy Data Model.")
        return change, model

    def _ensure_valid(self, dbml: str) -> None:
        """Từ chối DBML có bất kỳ validation ERROR nào."""
        issues = self._validator.validate(dbml)
        if any(item.severity is ValidationSeverity.ERROR for item in issues):
            raise BusinessException(
                ErrorCode.DATA_MODEL_VALIDATION_FAILED,
                "DBML không vượt qua các quy tắc validation Data Model.",
            )


def _validate_update_target(current: DataModel, data: UpdateDataModelInput) -> None:
    """Kiểm tra ID và base revision của manual update."""
    if data.data_model_id != current.id:
        raise BusinessException(
            ErrorCode.DATA_MODEL_UPDATE_ID_MISMATCH,
            "Data Model trong request không khớp snapshot của dự án.",
        )
    if data.base_revision != current.revision:
        raise BusinessException(
            ErrorCode.DATA_MODEL_REVISION_CONFLICT,
            "Base revision không khớp revision Data Model hiện tại.",
        )
