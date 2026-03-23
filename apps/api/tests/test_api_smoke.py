from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

if not os.environ.get("DATABASE_URL"):
    pytest.skip("DATABASE_URL required for integration smoke tests", allow_module_level=True)

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


def test_workspace_project_file_version_proposal_flow(client: TestClient) -> None:
    suffix = str(uuid.uuid4())[:8]
    wname = f"ws-{suffix}"

    r = client.post("/workspaces", json={"name": wname})
    assert r.status_code == 200, r.text
    ws = r.json()
    ws_id = ws["id"]

    r = client.post(f"/workspaces/{ws_id}/projects", json={"name": f"proj-{suffix}"})
    assert r.status_code == 200, r.text
    proj = r.json()
    proj_id = proj["id"]

    r = client.post(
        f"/projects/{proj_id}/files",
        json={"path": "project.md", "content": "v1"},
    )
    assert r.status_code == 200, r.text
    file_row = r.json()
    file_id = file_row["id"]
    assert file_row["content"] == "v1"

    r = client.get(f"/files/{file_id}")
    assert r.status_code == 200
    assert r.json()["content"] == "v1"

    r = client.patch(f"/files/{file_id}", json={"content": "v2"})
    assert r.status_code == 200
    assert r.json()["content"] == "v2"

    r = client.get(f"/files/{file_id}/versions")
    assert r.status_code == 200
    versions = r.json()
    assert len(versions) == 2
    assert versions[0]["content"] == "v1"
    assert versions[1]["content"] == "v2"

    r = client.post(
        f"/files/{file_id}/proposals",
        json={"proposed_content": "from agent"},
    )
    assert r.status_code == 200
    prop = r.json()
    assert prop["proposed_content"] == "from agent"
    assert prop["status"] == "pending"

    r = client.get(f"/files/{file_id}/proposals")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_duplicate_file_path_conflict(client: TestClient) -> None:
    suffix = str(uuid.uuid4())[:8]
    r = client.post("/workspaces", json={"name": f"ws-dup-{suffix}"})
    ws_id = r.json()["id"]
    r = client.post(f"/workspaces/{ws_id}/projects", json={"name": "p"})
    proj_id = r.json()["id"]

    body = {"path": "same.md", "content": "a"}
    assert client.post(f"/projects/{proj_id}/files", json=body).status_code == 200
    r2 = client.post(f"/projects/{proj_id}/files", json=body)
    assert r2.status_code == 409
