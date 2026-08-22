"""REST và SSE endpoints cho phiên hội thoại Agent."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request
from fastapi.responses import StreamingResponse
from src.application.project_sessions.input import GetSessionInput, ListSessionEventsInput, ListSessionsInput
from src.presentation.dependencies.project_sessions import ProjectSessionServiceDependency
from src.presentation.dtos.data_models.request import ProjectIdPath
from src.presentation.dtos.sessions.request import (
    CreateProjectSessionRequest,
    ProjectSessionIdPath,
    RenameProjectSessionRequest,
    SendSessionMessageRequest,
)
from src.presentation.dtos.sessions.response import (
    AgentTurnResponse,
    ProjectSessionResponse,
    SessionEventResponse,
    create_agent_turn_response,
)
from src.presentation.routing import ApiResponseRoute, error_responses

router = APIRouter(tags=["Project Sessions"], route_class=ApiResponseRoute)


@router.post(
    "/projects/{project_id}/sessions",
    response_model=ProjectSessionResponse,
    operation_id="createProjectSession",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def create_project_session(project_id: ProjectIdPath, request: CreateProjectSessionRequest, service: ProjectSessionServiceDependency) -> ProjectSessionResponse:
    output = await service.create_session(request.to_application(project_id))
    return ProjectSessionResponse.from_application(output)


@router.get(
    "/projects/{project_id}/sessions",
    response_model=list[ProjectSessionResponse],
    operation_id="listProjectSessions",
    responses=error_responses(401, 403, 404, 500),
)
async def list_project_sessions(project_id: ProjectIdPath, service: ProjectSessionServiceDependency) -> list[ProjectSessionResponse]:
    outputs = await service.list_sessions(ListSessionsInput(project_id))
    return [ProjectSessionResponse.from_application(item) for item in outputs]


@router.get(
    "/sessions/{session_id}",
    response_model=ProjectSessionResponse,
    operation_id="getProjectSession",
    responses=error_responses(401, 403, 404, 500),
)
async def get_project_session(session_id: ProjectSessionIdPath, service: ProjectSessionServiceDependency) -> ProjectSessionResponse:
    output = await service.get_session(GetSessionInput(session_id))
    return ProjectSessionResponse.from_application(output)


@router.patch(
    "/sessions/{session_id}",
    response_model=ProjectSessionResponse,
    operation_id="renameProjectSession",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def rename_project_session(
    session_id: ProjectSessionIdPath,
    request: RenameProjectSessionRequest,
    service: ProjectSessionServiceDependency,
) -> ProjectSessionResponse:
    output = await service.rename_session(request.to_application(session_id))
    return ProjectSessionResponse.from_application(output)


@router.get(
    "/sessions/{session_id}/events",
    response_model=list[SessionEventResponse],
    operation_id="listProjectSessionEvents",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def list_project_session_events(
    session_id: ProjectSessionIdPath,
    service: ProjectSessionServiceDependency,
    after_id: Annotated[UUID | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> list[SessionEventResponse]:
    outputs = await service.list_events(ListSessionEventsInput(session_id, after_id, limit))
    return [SessionEventResponse.from_application(item) for item in outputs]


@router.post(
    "/sessions/{session_id}/messages",
    response_model=AgentTurnResponse,
    operation_id="sendProjectSessionMessage",
    responses=error_responses(401, 403, 404, 409, 422, 500),
)
async def send_project_session_message(session_id: ProjectSessionIdPath, request: SendSessionMessageRequest, service: ProjectSessionServiceDependency) -> AgentTurnResponse:
    output = await service.send_message(request.to_application(session_id))
    return create_agent_turn_response(output)


@router.get(
    "/sessions/{session_id}/events/stream",
    operation_id="streamProjectSessionEvents",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def stream_project_session_events(
    session_id: ProjectSessionIdPath,
    request: Request,
    service: ProjectSessionServiceDependency,
    last_event_id: Annotated[UUID | None, Header(alias="Last-Event-ID")] = None,
) -> StreamingResponse:
    await service.get_session(GetSessionInput(session_id))
    stream = _event_stream(service, session_id, last_event_id, request)
    return StreamingResponse(stream, media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


async def _event_stream(service: ProjectSessionServiceDependency, session_id: UUID, cursor: UUID | None, request: Request) -> AsyncGenerator[str, None]:
    idle_ticks = 0
    while not await request.is_disconnected():
        events = await service.list_events(ListSessionEventsInput(session_id, cursor, 100))
        if events:
            for event in events:
                cursor = event.id
                yield _encode_event(SessionEventResponse.from_application(event))
            idle_ticks = 0
        else:
            idle_ticks += 1
            if idle_ticks >= 30:
                yield ": heartbeat\n\n"
                idle_ticks = 0
        await asyncio.sleep(0.5)


def _encode_event(event: SessionEventResponse) -> str:
    """Mã hóa một event theo chuẩn SSE, dùng UUID làm resume cursor."""
    return f"id: {event.id}\nevent: session.event\ndata: {event.model_dump_json()}\n\n"
