"""REST endpoints cho Requirement clarification tại Project Init."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Path
from src.application.requirements.input import GetRequirementClarificationInput
from src.presentation.dependencies.requirements import RequirementServiceDependency
from src.presentation.dtos.requirement_clarification.request import (
    AnalyzeRequirementClarificationRequest,
    AnswerRequirementClarificationRequest,
    ChooseRequirementContinuationRequest,
    SendRequirementClarificationMessageRequest,
)
from src.presentation.dtos.requirement_clarification.response import (
    RequirementClarificationResponse,
)
from src.presentation.dtos.requirements.request import ProjectIdPath
from src.presentation.routing import ApiResponseRoute, error_responses

SessionIdPath = Annotated[UUID, Path(description="ID Requirement session")]
QuestionIdPath = Annotated[UUID, Path(description="ID pending question")]

router = APIRouter(
    prefix="/projects/{project_id}/requirement-clarification",
    tags=["Requirement Clarification"],
    route_class=ApiResponseRoute,
)


@router.get(
    "",
    response_model=RequirementClarificationResponse,
    operation_id="getProjectRequirementClarification",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def get_requirement_clarification(
    project_id: ProjectIdPath,
    service: RequirementServiceDependency,
) -> RequirementClarificationResponse:
    output = await service.get_clarification(
        GetRequirementClarificationInput(project_id)
    )
    return RequirementClarificationResponse.from_application(output)


@router.post(
    "/analyze",
    response_model=RequirementClarificationResponse,
    operation_id="analyzeProjectRequirementClarification",
    responses=error_responses(401, 403, 404, 409, 422, 500),
)
async def analyze_requirement_clarification(
    project_id: ProjectIdPath,
    request: AnalyzeRequirementClarificationRequest,
    service: RequirementServiceDependency,
) -> RequirementClarificationResponse:
    output = await service.analyze_clarification(request.to_application(project_id))
    return RequirementClarificationResponse.from_application(output)


@router.post(
    "/{session_id}/questions/{question_id}/answer",
    response_model=RequirementClarificationResponse,
    operation_id="answerProjectRequirementClarification",
    responses=error_responses(401, 403, 404, 409, 422, 500),
)
async def answer_requirement_clarification(
    project_id: ProjectIdPath,
    session_id: SessionIdPath,
    question_id: QuestionIdPath,
    request: AnswerRequirementClarificationRequest,
    service: RequirementServiceDependency,
) -> RequirementClarificationResponse:
    output = await service.answer_clarification(
        request.to_application(project_id, session_id, question_id)
    )
    return RequirementClarificationResponse.from_application(output)


@router.post(
    "/{session_id}/messages",
    response_model=RequirementClarificationResponse,
    operation_id="sendProjectRequirementClarificationMessage",
    responses=error_responses(401, 403, 404, 409, 422, 500),
)
async def send_requirement_clarification_message(
    project_id: ProjectIdPath,
    session_id: SessionIdPath,
    request: SendRequirementClarificationMessageRequest,
    service: RequirementServiceDependency,
) -> RequirementClarificationResponse:
    """Gửi follow-up message và cập nhật Structured Requirements ngay trong turn."""
    output = await service.send_clarification_message(
        request.to_application(project_id, session_id)
    )
    return RequirementClarificationResponse.from_application(output)


@router.post(
    "/{session_id}/continuation",
    response_model=RequirementClarificationResponse,
    operation_id="chooseProjectRequirementContinuation",
    responses=error_responses(401, 403, 404, 409, 422, 500),
)
async def choose_requirement_continuation(
    project_id: ProjectIdPath,
    session_id: SessionIdPath,
    request: ChooseRequirementContinuationRequest,
    service: RequirementServiceDependency,
) -> RequirementClarificationResponse:
    """Persist lựa chọn continuation trước khi Project Init được resume."""
    output = await service.choose_clarification_continuation(
        request.to_application(project_id, session_id)
    )
    return RequirementClarificationResponse.from_application(output)
