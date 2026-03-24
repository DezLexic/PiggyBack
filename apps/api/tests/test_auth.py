from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

if not os.environ.get("DATABASE_URL"):
    pytest.skip("DATABASE_URL required for integration tests", allow_module_level=True)

from tests.conftest import TEST_API_KEY

from app.main import app

PROTECTED_ROUTES = [
    ("PATCH", "/files/{file_id}"),
    ("POST", "/files/{file_id}/proposals"),
    ("POST", "/proposals/{proposal_id}/accept"),
    ("POST", "/proposals/{proposal_id}/reject"),
    ("POST", "/projects/{project_id}/files/write"),
    ("POST", "/projects/{project_id}/files/append"),
    ("POST", "/projects/{project_id}/summary"),
    ("POST", "/projects/{project_id}/batch-write"),
]


@pytest.fixture()
def unauthed_client() -> TestClient:
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture()
def authed_client() -> TestClient:
    with TestClient(app, headers={"X-API-Key": TEST_API_KEY}) as c:
        yield c


def _bootstrap(authed_client: TestClient) -> tuple[str, str, str]:
    suffix = str(uuid.uuid4())[:8]
    ws = authed_client.post("/workspaces", json={"name": f"ws-auth-{suffix}"}).json()
    proj = authed_client.post(
        f"/workspaces/{ws['id']}/projects", json={"name": f"proj-{suffix}"}
    ).json()
    file_row = authed_client.post(
        f"/projects/{proj['id']}/files", json={"path": "test.md", "content": "base"}
    ).json()
    return proj["id"], file_row["id"], str(uuid.uuid4())  # last is a fake proposal id


def test_missing_key_returns_401(unauthed_client: TestClient, authed_client: TestClient) -> None:
    proj_id, file_id, _ = _bootstrap(authed_client)
    fake_id = str(uuid.uuid4())

    cases = [
        ("PATCH", f"/files/{file_id}", {"content": "x"}),
        ("POST", f"/files/{file_id}/proposals", {"proposed_content": "x"}),
        ("POST", f"/proposals/{fake_id}/accept", {}),
        ("POST", f"/proposals/{fake_id}/reject", {}),
        ("POST", f"/projects/{proj_id}/files/write", {"path": "a.md", "content": "x"}),
        ("POST", f"/projects/{proj_id}/files/append", {"path": "a.md", "content": "x"}),
        ("POST", f"/projects/{proj_id}/summary", {"type": "status", "content": "x"}),
        (
            "POST",
            f"/projects/{proj_id}/batch-write",
            {"writes": [{"path": "a.md", "content": "x"}]},
        ),
    ]
    for method, url, body in cases:
        r = unauthed_client.request(method, url, json=body)
        assert r.status_code == 401, f"Expected 401 for {method} {url}, got {r.status_code}"


def test_invalid_key_returns_401(unauthed_client: TestClient, authed_client: TestClient) -> None:
    proj_id, file_id, _ = _bootstrap(authed_client)
    bad_client = TestClient(app, headers={"X-API-Key": "piggb_invalid_key_xyz"})
    with bad_client:
        r = bad_client.patch(f"/files/{file_id}", json={"content": "x"})
        assert r.status_code == 401


def test_admin_key_allows_writes(authed_client: TestClient) -> None:
    proj_id, file_id, _ = _bootstrap(authed_client)
    r = authed_client.patch(f"/files/{file_id}", json={"content": "updated"})
    assert r.status_code == 200
    assert r.json()["content"] == "updated"


def test_agent_key_allows_writes(authed_client: TestClient) -> None:
    """Key generated on agent registration should authenticate write calls."""
    suffix = str(uuid.uuid4())[:8]
    agent_resp = authed_client.post(
        "/agent-connections",
        json={"name": f"agent-{suffix}", "agent_type": "test"},
    )
    assert agent_resp.status_code == 200
    agent_key = agent_resp.json()["api_key"]
    assert agent_key.startswith("piggb_")

    # Bootstrap a project with the admin key, then write with the agent key
    ws = authed_client.post("/workspaces", json={"name": f"ws-agentauth-{suffix}"}).json()
    proj = authed_client.post(
        f"/workspaces/{ws['id']}/projects", json={"name": f"p-{suffix}"}
    ).json()

    agent_client = TestClient(app, headers={"X-API-Key": agent_key})
    with agent_client:
        r = agent_client.post(
            f"/projects/{proj['id']}/files/write",
            json={"path": "status.md", "content": "hello"},
        )
        assert r.status_code == 200, r.text


def test_read_routes_remain_open(unauthed_client: TestClient, authed_client: TestClient) -> None:
    proj_id, file_id, _ = _bootstrap(authed_client)
    assert unauthed_client.get(f"/files/{file_id}").status_code == 200
    assert unauthed_client.get(f"/files/{file_id}/versions").status_code == 200
    assert unauthed_client.get(f"/projects/{proj_id}/files").status_code == 200
    assert unauthed_client.get("/agent-connections").status_code == 200


def test_agent_connection_creation_returns_key(authed_client: TestClient) -> None:
    suffix = str(uuid.uuid4())[:8]
    r = authed_client.post(
        "/agent-connections",
        json={"name": f"myagent-{suffix}", "agent_type": "claude"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "api_key" in body
    assert body["api_key"].startswith("piggb_")
    # List endpoint should NOT expose the key
    listed = authed_client.get("/agent-connections").json()
    agent = next(a for a in listed if a["id"] == body["id"])
    assert "api_key" not in agent
