"""Routing primitives dùng chung cho Presentation layer."""

from src.presentation.routing.api_response_route import ApiResponseRoute
from src.presentation.routing.error_responses import error_responses
from src.presentation.routing.types import ErrorResponses

__all__ = ["ApiResponseRoute", "ErrorResponses", "error_responses"]
