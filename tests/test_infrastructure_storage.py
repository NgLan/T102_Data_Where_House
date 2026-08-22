"""Kiểm thử an toàn đường dẫn của local storage adapter."""

from pathlib import Path
from uuid import uuid4

import pytest
from src.application.projects.i_project_service import IProjectArtifactStore
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.storage.local_storage import LocalFileStorage


@pytest.mark.asyncio
async def test_storage_implements_both_ports_and_round_trips(tmp_path: Path) -> None:
    store = LocalFileStorage(tmp_path / "uploads")
    assert isinstance(store, IProjectArtifactStore)
    assert hasattr(store, "save_file")

    project_id = str(uuid4())
    path = await store.save_file(project_id, "data.csv", b"id\n1")

    assert await store.read_file(path) == b"id\n1"
    await store.delete_file(path)
    await store.cleanup_empty_dir(project_id)
    assert not (tmp_path / "uploads" / project_id).exists()


@pytest.mark.asyncio
async def test_storage_rejects_traversal_and_sibling_prefix(tmp_path: Path) -> None:
    root = tmp_path / "upload"
    store = LocalFileStorage(root)
    sibling = tmp_path / "upload-escaped" / "secret.csv"

    with pytest.raises(InfrastructureException):
        await store.save_file("../escaped", "data.csv", b"secret")
    with pytest.raises(InfrastructureException) as exc_info:
        await store.read_file(str(sibling))

    assert str(tmp_path) not in exc_info.value.message


@pytest.mark.asyncio
async def test_project_cleanup_removes_nested_artifacts(tmp_path: Path) -> None:
    store = LocalFileStorage(tmp_path / "uploads")
    project_id = uuid4()
    await store.save_file(str(project_id), "model.dbml", b"Table demo {}")

    await store.delete_project_directory(project_id)

    assert not (tmp_path / "uploads" / str(project_id)).exists()
