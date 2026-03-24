from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

if not os.environ.get("DATABASE_URL"):
    pytest.skip("DATABASE_URL required for integration tests", allow_module_level=True)

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


def _bootstrap_project(client: TestClient) -> tuple[str, str]:
    suffix = str(uuid.uuid4())[:8]
    ws = client.post("/workspaces", json={"name": f"ws-trust-{suffix}"}).json()
    proj = client.post(
        f"/workspaces/{ws['id']}/projects",
        json={"name": f"proj-{suffix}"},
    ).json()
    return ws["id"], proj["id"]


def test_agent_connections_create_and_list(client: TestClient) -> None:
    r = client.post(
        "/agent-connections",
        json={"name": "Test Agent", "agent_type": "local"},
    )
    assert r.status_code == 200, r.text
    created = r.json()
    assert created["name"] == "Test Agent"
    assert created["agent_type"] == "local"

    r = client.get("/agent-connections")
    assert r.status_code == 200
    ids = {row["id"] for row in r.json()}
    assert created["id"] in ids


def test_permissions_grant_list_duplicate(client: TestClient) -> None:
    _, project_id = _bootstrap_project(client)
    agent = client.post(
        "/agent-connections",
        json={"name": "Perm Agent", "agent_type": "test"},
    ).json()
    aid = agent["id"]

    body = {"agent_connection_id": aid, "permission_type": "read"}
    r = client.post(f"/projects/{project_id}/permissions", json=body)
    assert r.status_code == 200, r.text
    row = r.json()
    assert row["permission_type"] == "read"

    r = client.get(f"/projects/{project_id}/permissions")
    assert r.status_code == 200
    assert len(r.json()) >= 1

    r2 = client.post(f"/projects/{project_id}/permissions", json=body)
    assert r2.status_code == 409


def test_accept_proposal_updates_file_and_version(client: TestClient) -> None:
    _, project_id = _bootstrap_project(client)
    file_row = client.post(
        f"/projects/{project_id}/files",
        json={"path": "handoff.md", "content": "original"},
    ).json()
    file_id = file_row["id"]
    assert file_row["content"] == "original"

    prop = client.post(
        f"/files/{file_id}/proposals",
        json={"proposed_content": "from proposal"},
    ).json()
    pid = prop["id"]
    assert prop["status"] == "pending"

    v_before = client.get(f"/files/{file_id}/versions").json()
    assert len(v_before) == 1

    r = client.post(f"/proposals/{pid}/accept")
    assert r.status_code == 200, r.text
    payload = r.json()
    assert payload["proposal"]["status"] == "accepted"
    assert payload["file"]["content"] == "from proposal"

    v_after = client.get(f"/files/{file_id}/versions").json()
    assert len(v_after) == 2
    assert v_after[-1]["content"] == "from proposal"


def test_reject_proposal_does_not_change_file(client: TestClient) -> None:
    _, project_id = _bootstrap_project(client)
    file_row = client.post(
        f"/projects/{project_id}/files",
        json={"path": "x.md", "content": "baseline"},
    ).json()
    file_id = file_row["id"]
    prop = client.post(
        f"/files/{file_id}/proposals",
        json={"proposed_content": "ignored"},
    ).json()
    pid = prop["id"]

    r = client.post(f"/proposals/{pid}/reject")
    assert r.status_code == 200
    assert r.json()["status"] == "rejected"

    f2 = client.get(f"/files/{file_id}").json()
    assert f2["content"] == "baseline"
    versions = client.get(f"/files/{file_id}/versions").json()
    assert len(versions) == 1


def test_accept_after_reject_returns_409(client: TestClient) -> None:
    _, project_id = _bootstrap_project(client)
    file_row = client.post(
        f"/projects/{project_id}/files",
        json={"path": "z.md", "content": "x"},
    ).json()
    prop = client.post(
        f"/files/{file_row['id']}/proposals",
        json={"proposed_content": "y"},
    ).json()
    assert client.post(f"/proposals/{prop['id']}/reject").status_code == 200
    assert client.post(f"/proposals/{prop['id']}/accept").status_code == 409


def test_finalize_proposal_twice_returns_409(client: TestClient) -> None:
    _, project_id = _bootstrap_project(client)
    file_row = client.post(
        f"/projects/{project_id}/files",
        json={"path": "y.md", "content": "a"},
    ).json()
    file_id = file_row["id"]
    p_accept = client.post(
        f"/files/{file_id}/proposals",
        json={"proposed_content": "b"},
    ).json()
    p_reject = client.post(
        f"/files/{file_id}/proposals",
        json={"proposed_content": "c"},
    ).json()

    assert client.post(f"/proposals/{p_accept['id']}/accept").status_code == 200
    assert client.post(f"/proposals/{p_accept['id']}/accept").status_code == 409

    assert client.post(f"/proposals/{p_reject['id']}/reject").status_code == 200
    assert client.post(f"/proposals/{p_reject['id']}/reject").status_code == 409
