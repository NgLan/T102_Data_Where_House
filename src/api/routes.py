from fastapi import APIRouter, HTTPException, status

from src.agents.graph import agent
from src.agents.schema_agent import schema_agent
from src.models.schema_agent import (
    GenerateSchemaRequest,
    GenerateSchemaResponse,
    ValidateSchemaRequest,
    ValidateSchemaResponse,
)
from src.models.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat với AI agent."""
    try:
        result = await agent.ainvoke({"query": request.message})
        return ChatResponse(
            response=result.get("response", ""),
            analysis=result.get("analysis", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def agent_status():
    """Kiểm tra trạng thái agent."""
    return {"status": "ready", "agent": "BigQuery Data Architecture Agent v1.0"}


@router.post(
    "/agent/generate-schema",
    response_model=GenerateSchemaResponse,
    status_code=status.HTTP_200_OK,
    summary="Sinh Data Warehouse Schema & SQL DDL (BigQuery Standard)",
    description="Nhận yêu cầu nghiệp vụ JSON và trả về BigQuery Kimball Schema gồm Fact/Dim, Grain, PK/FK, DDL SQL và Anti-pattern warnings."
)
async def generate_schema(request: GenerateSchemaRequest) -> GenerateSchemaResponse:
    """Endpoint sinh BigQuery Schema dạng JSON."""
    try:
        data = await schema_agent.generate_schema(request)
        return GenerateSchemaResponse(
            status="success",
            code=200,
            message="BigQuery Data Schema generated successfully",
            data=data,
            error=None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi sinh schema: {str(e)}"
        )


@router.post(
    "/agent/validate-schema",
    response_model=ValidateSchemaResponse,
    status_code=status.HTTP_200_OK,
    summary="Thẩm định DDL SQL & Kiểm tra Anti-patterns",
    description="Nhận đoạn DDL SQL và phân tích bẫy thiết kế (Anti-patterns), chấm điểm chất lượng schema."
)
async def validate_schema(request: ValidateSchemaRequest) -> ValidateSchemaResponse:
    """Endpoint thẩm định DDL SQL."""
    try:
        data = await schema_agent.validate_schema(request)
        return ValidateSchemaResponse(
            status="success",
            code=200,
            message="Schema validation completed",
            data=data,
            error=None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi thẩm định schema: {str(e)}"
        )
