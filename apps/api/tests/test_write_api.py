from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

if not os.environ.get("DATABASE_URL"):
    pytest.skip("DATABASE_URL required for integration smoke tests", allow_module_level=True)

from tests.conftest import TEST_API_KEY

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app, headers={"X-API-Key": TEST_API_KEY}) as c:
        yield c


@pytest.fixture()
def project(client: TestClient):
    suffix = str(uuid.uuid4())[:8]
    r = client.post("/workspaces", json={"name": f"ws-{suffix}"})
    ws_id = r.json()["id"]
    r = client.post(f"/workspaces/{ws_id}/projects", json={"name": f"proj-{suffix}"})
    return r.json()


def test_write_creates_new_file(client: TestClient, project: dict) -> None:
    proj_id = project["id"]
    r = client.post(
        f"/projects/{proj_id}/files/write",
        json={"path": "status.md", "content": "initial content"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["file"]["path"] == "status.md"
    assert body["version"]["id"] is not None
    assert body["version"]["created_at"] is not None


def test_write_replaces_existing_file(client: TestClient, project: dict) -> None:
    proj_id = project["id"]
    client.post(
        f"/projects/{proj_id}/files/write",
        json={"path": "status.md", "content": "v1"},
    )
    r = client.post(
        f"/projects/{proj_id}/files/write",
        json={"path": "status.md", "content": "v2", "mode": "replace"},
    )
    assert r.status_code == 200
    file_id = r.json()["file"]["id"]
    # Confirm content was replaced and two versions exist
    versions = client.get(f"/files/{file_id}/versions").json()
    assert len(versions) == 2
    assert versions[-1]["content"] == "v2"


def test_write_append_mode(client: TestClient, project: dict) -> None:
    proj_id = project["id"]
    client.post(
        f"/projects/{proj_id}/files/write",
        json={"path": "handoff.md", "content": "first line"},
    )
    r = client.post(
        f"/projects/{proj_id}/files/write",
        json={"path": "handoff.md", "content": "second line", "mode": "append"},
    )
    assert r.status_code == 200
    file_id = r.json()["file"]["id"]
    file_data = client.get(f"/files/{file_id}").json()
    assert "first line" in file_data["content"]
    assert "second line" in file_data["content"]


def test_append_endpoint(client: TestClient, project: dict) -> None:
    proj_id = project["id"]
    client.post(
        f"/projects/{proj_id}/files/write",
        json={"path": "notes.md", "content": "line 1"},
    )
    r = client.post(
        f"/projects/{proj_id}/files/append",
        json={"path": "notes.md", "content": "line 2"},
    )
    assert r.status_code == 200
    file_id = r.json()["file"]["id"]
    content = client.get(f"/files/{file_id}").json()["content"]
    assert "line 1" in content
    assert "line 2" in content


def test_append_endpoint_creates_file_if_missing(client: TestClient, project: dict) -> None:
    proj_id = project["id"]
    r = client.post(
        f"/projects/{proj_id}/files/append",
        json={"path": "new.md", "content": "hello"},
    )
    assert r.status_code == 200
    assert r.json()["file"]["path"] == "new.md"


def test_summary_status(client: TestClient, project: dict) -> None:
    proj_id = project["id"]
    r = client.post(
        f"/projects/{proj_id}/summary",
        json={"type": "status", "content": "80% done"},
    )
    assert r.status_code == 200
    assert r.json()["file"]["path"] == "status.md"


def test_summary_overwrites_on_second_call(client: TestClient, project: dict) -> None:
    proj_id = project["id"]
    client.post(f"/projects/{proj_id}/summary", json={"type": "handoff", "content": "v1"})
    r = client.post(f"/projects/{proj_id}/summary", json={"type": "handoff", "content": "v2"})
    assert r.status_code == 200
    file_id = r.json()["file"]["id"]
    versions = client.get(f"/files/{file_id}/versions").json()
    assert len(versions) == 2
    assert versions[-1]["content"] == "v2"


def test_batch_write(client: TestClient, project: dict) -> None:
    proj_id = project["id"]
    r = client.post(
        f"/projects/{proj_id}/batch-write",
        json={
            "writes": [
                {"path": "status.md", "content": "Status A"},
                {"path": "handoff.md", "content": "Handoff B"},
            ],
            "created_by": {"type": "agent", "name": "test-agent"},
        },
    )
    assert r.status_code == 200
    results = r.json()["results"]
    assert len(results) == 2
    paths = {res["file"]["path"] for res in results}
    assert paths == {"status.md", "handoff.md"}


def test_batch_write_mixed_modes(client: TestClient, project: dict) -> None:
    proj_id = project["id"]
    # Create initial file
    client.post(f"/projects/{proj_id}/files/write", json={"path": "log.md", "content": "entry 1"})
    r = client.post(
        f"/projects/{proj_id}/batch-write",
        json={
            "writes": [
                {"path": "log.md", "content": "entry 2", "mode": "append"},
                {"path": "status.md", "content": "fresh", "mode": "replace"},
            ]
        },
    )
    assert r.status_code == 200
    results = r.json()["results"]
    log_result = next(res for res in results if res["file"]["path"] == "log.md")
    log_id = log_result["file"]["id"]
    content = client.get(f"/files/{log_id}").json()["content"]
    assert "entry 1" in content
    assert "entry 2" in content


def test_write_404_on_missing_project(client: TestClient) -> None:
    r = client.post(
        f"/projects/{uuid.uuid4()}/files/write",
        json={"path": "x.md", "content": "y"},
    )
    assert r.status_code == 404


def test_summary_404_on_missing_project(client: TestClient) -> None:
    r = client.post(
        f"/projects/{uuid.uuid4()}/summary",
        json={"type": "status", "content": "y"},
    )
    assert r.status_code == 404


def test_batch_write_404_on_missing_project(client: TestClient) -> None:
    r = client.post(
        f"/projects/{uuid.uuid4()}/batch-write",
        json={"writes": [{"path": "x.md", "content": "y"}]},
    )
    assert r.status_code == 404
