"""Cấu hình và đăng ký CORS Middleware chuẩn hóa (cors.py)."""

from typing import Protocol

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class CorsSettings(Protocol):
    """Phần cấu hình tối thiểu mà CORS cần sử dụng."""

    cors_origins_list: list[str]
    cors_allow_credentials: bool
    cors_allow_methods_list: list[str]
    cors_allow_headers_list: list[str]


def setup_cors_middleware(app: FastAPI, settings: CorsSettings) -> None:
    """Cấu hình và gắn CORSMiddleware vào ứng dụng FastAPI dựa trên Settings.

    Args:
        app: FastAPI application cần cấu hình.
        settings: Cấu hình origins, credentials, methods và headers.

    Raises:
        ValueError: Khi wildcard origin được dùng cùng credentials.
    """
    origins = settings.cors_origins_list
    allow_credentials = settings.cors_allow_credentials
    allow_methods = settings.cors_allow_methods_list
    allow_headers = settings.cors_allow_headers_list

    if "*" in origins and allow_credentials:
        raise ValueError("CORS không cho phép wildcard origin khi bật credentials.")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
    )
