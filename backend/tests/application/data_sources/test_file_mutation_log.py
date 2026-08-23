"""Filesystem compensation for transactional data-source changes."""

from unittest.mock import AsyncMock, MagicMock, call

import pytest
from src.application.data_sources.file_mutation_log import FileMutationLog, FileReplacement


@pytest.mark.asyncio
async def test_rollback_deletes_a_new_file() -> None:
    files = MagicMock()
    files.save_file = AsyncMock(return_value="uploads/project/orders.csv")
    files.delete_file = AsyncMock()
    mutations = FileMutationLog(files)

    await mutations.replace(FileReplacement("project", "orders.csv", b"new", None))
    await mutations.rollback()

    files.delete_file.assert_awaited_once_with("uploads/project/orders.csv")


@pytest.mark.asyncio
async def test_rollback_restores_replaced_bytes() -> None:
    files = MagicMock()
    files.read_file = AsyncMock(return_value=b"old")
    files.save_file = AsyncMock(return_value="uploads/project/orders.csv")
    files.delete_file = AsyncMock()
    mutations = FileMutationLog(files)

    await mutations.replace(
        FileReplacement("project", "orders.csv", b"new", "uploads/project/orders.csv")
    )
    await mutations.rollback()

    assert files.save_file.await_args_list == [
        call("project", "orders.csv", b"new"),
        call("project", "orders.csv", b"old"),
    ]
    files.delete_file.assert_not_awaited()


@pytest.mark.asyncio
async def test_rollback_restores_a_deleted_file() -> None:
    files = MagicMock()
    files.read_file = AsyncMock(return_value=b"old")
    files.delete_file = AsyncMock()
    files.save_file = AsyncMock(return_value="uploads/project/orders.csv")
    mutations = FileMutationLog(files)

    await mutations.remove("project", "orders.csv", "uploads/project/orders.csv")
    await mutations.rollback()

    files.delete_file.assert_awaited_once_with("uploads/project/orders.csv")
    files.save_file.assert_awaited_once_with("project", "orders.csv", b"old")
