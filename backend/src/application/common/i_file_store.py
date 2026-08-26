"""Shared outbound port cho project-scoped file storage."""

from typing import Protocol


class IFileStore(Protocol):
    """Hợp đồng storage dùng chung, không chứa business semantics."""

    async def save_file(
        self, project_id: str, filename: str, content: bytes
    ) -> str: ...

    async def read_file(self, file_path: str) -> bytes: ...

    async def delete_file(self, file_path: str) -> None: ...

    async def cleanup_empty_dir(self, project_id: str) -> None: ...
