from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

if not os.environ.get("DATABASE_URL"):
    pytest.skip("DATABASE_URL required for integration tests", allow_module_level=True)

from tests.conftest import TEST_API_KEY

from app.main import app


@pytest.fixture()
def admin() -> TestClient:
    with TestClient(app, headers={"X-API-Key": TEST_API_KEY}) as c:
        yield c


def _new_project(admin: TestClient) -> tuple[str, str]:
    suffix = str(uuid.uuid4())[:8]
    ws = admin.post("/workspaces", json={"name": f"ws-perm-{suffix}"}).json()
    proj = admin.post(f"/workspaces/{ws['id']}/projects", json={"name": f"p-{suffix}"}).json()
    return ws["id"], proj["id"]


def _agent_client(admin: TestClient, agent_type: str = "test") -> tuple[TestClient, str]:
    """Register a new agent and return (client-with-key, agent_id)."""
    suffix = str(uuid.uuid4())[:8]
    r = admin.post("/agent-connections", json={"name": f"agent-{suffix}", "agent_type": agent_type})
    body = r.json()
    client = TestClient(app, headers={"X-API-Key": body["api_key"]})
    return client, body["id"]


# ---------------------------------------------------------------------------
# Read permission
# ---------------------------------------------------------------------------

class TestReadPermission:
    def test_read_agent_can_list_and_get_files(self, admin: TestClient) -> None:
        _, proj_id = _new_project(admin)
        admin.post(f"/projects/{proj_id}/files/write", json={"path": "x.md", "content": "hello"})

        agent_client, agent_id = _agent_client(admin)
        with agent_client:
            # No permission yet — should 403
            r = agent_client.get(f"/projects/{proj_id}/files")
            assert r.status_code == 403

            # Grant read
            admin.post(
                f"/projects/{proj_id}/permissions",
                json={"agent_connection_id": agent_id, "permission_type": "read"},
            )

            r = agent_client.get(f"/projects/{proj_id}/files")
            assert r.status_code == 200
            files = r.json()
            assert len(files) >= 1
            file_id = files[0]["id"]

            assert agent_client.get(f"/files/{file_id}").status_code == 200
            assert agent_client.get(f"/files/{file_id}/versions").status_code == 200
            assert agent_client.get(f"/files/{file_id}/proposals").status_code == 200

    def test_read_agent_cannot_write(self, admin: TestClient) -> None:
        _, proj_id = _new_project(admin)
        file_row = admin.post(
            f"/projects/{proj_id}/files/write", json={"path": "x.md", "content": "v1"}
        ).json()
        file_id = file_row["file"]["id"]

        agent_client, agent_id = _agent_client(admin)
        admin.post(
            f"/projects/{proj_id}/permissions",
            json={"agent_connection_id": agent_id, "permission_type": "read"},
        )
        with agent_client:
            assert agent_client.patch(f"/files/{file_id}", json={"content": "v2"}).status_code == 403
            assert agent_client.post(
                f"/projects/{proj_id}/files/write", json={"path": "y.md", "content": "x"}
            ).status_code == 403

    def test_read_agent_cannot_propose(self, admin: TestClient) -> None:
        _, proj_id = _new_project(admin)
        file_row = admin.post(
            f"/projects/{proj_id}/files/write", json={"path": "x.md", "content": "v1"}
        ).json()
        file_id = file_row["file"]["id"]

        agent_client, agent_id = _agent_client(admin)
        admin.post(
            f"/projects/{proj_id}/permissions",
            json={"agent_connection_id": agent_id, "permission_type": "read"},
        )
        with agent_client:
            r = agent_client.post(
                f"/files/{file_id}/proposals", json={"proposed_content": "attempt"}
            )
            assert r.status_code == 403


# ---------------------------------------------------------------------------
# propose_update permission
# ---------------------------------------------------------------------------

class TestProposeUpdatePermission:
    def test_propose_agent_can_read_and_propose(self, admin: TestClient) -> None:
        _, proj_id = _new_project(admin)
        file_row = admin.post(
            f"/projects/{proj_id}/files/write", json={"path": "x.md", "content": "base"}
        ).json()
        file_id = file_row["file"]["id"]

        agent_client, agent_id = _agent_client(admin)
        admin.post(
            f"/projects/{proj_id}/permissions",
            json={"agent_connection_id": agent_id, "permission_type": "propose_update"},
        )
        with agent_client:
            assert agent_client.get(f"/files/{file_id}").status_code == 200
            r = agent_client.post(
                f"/files/{file_id}/proposals", json={"proposed_content": "new content"}
            )
            assert r.status_code == 200
            assert r.json()["status"] == "pending"

    def test_propose_agent_cannot_directly_write(self, admin: TestClient) -> None:
        _, proj_id = _new_project(admin)
        file_row = admin.post(
            f"/projects/{proj_id}/files/write", json={"path": "x.md", "content": "base"}
        ).json()
        file_id = file_row["file"]["id"]

        agent_client, agent_id = _agent_client(admin)
        admin.post(
            f"/projects/{proj_id}/permissions",
            json={"agent_connection_id": agent_id, "permission_type": "propose_update"},
        )
        with agent_client:
            assert agent_client.patch(f"/files/{file_id}", json={"content": "x"}).status_code == 403
            assert agent_client.post(
                f"/projects/{proj_id}/files/write", json={"path": "y.md", "content": "x"}
            ).status_code == 403

    def test_propose_agent_cannot_accept_or_reject(self, admin: TestClient) -> None:
        _, proj_id = _new_project(admin)
        file_row = admin.post(
            f"/projects/{proj_id}/files/write", json={"path": "x.md", "content": "base"}
        ).json()
        file_id = file_row["file"]["id"]

        agent_client, agent_id = _agent_client(admin)
        admin.post(
            f"/projects/{proj_id}/permissions",
            json={"agent_connection_id": agent_id, "permission_type": "propose_update"},
        )
        with agent_client:
            prop = agent_client.post(
                f"/files/{file_id}/proposals", json={"proposed_content": "x"}
            ).json()
            assert agent_client.post(f"/proposals/{prop['id']}/accept").status_code == 403
            assert agent_client.post(f"/proposals/{prop['id']}/reject").status_code == 403


# ---------------------------------------------------------------------------
# write permission
# ---------------------------------------------------------------------------

class TestWritePermission:
    def test_write_agent_can_use_write_api(self, admin: TestClient) -> None:
        _, proj_id = _new_project(admin)
        agent_client, agent_id = _agent_client(admin)
        admin.post(
            f"/projects/{proj_id}/permissions",
            json={"agent_connection_id": agent_id, "permission_type": "write"},
        )
        with agent_client:
            r = agent_client.post(
                f"/projects/{proj_id}/files/write",
                json={"path": "status.md", "content": "done"},
            )
            assert r.status_code == 200

            r = agent_client.post(
                f"/projects/{proj_id}/summary",
                json={"type": "handoff", "content": "notes"},
            )
            assert r.status_code == 200

            r = agent_client.post(
                f"/projects/{proj_id}/batch-write",
                json={"writes": [{"path": "a.md", "content": "x"}]},
            )
            assert r.status_code == 200

    def test_write_agent_can_also_propose(self, admin: TestClient) -> None:
        _, proj_id = _new_project(admin)
        file_row = admin.post(
            f"/projects/{proj_id}/files/write", json={"path": "x.md", "content": "base"}
        ).json()
        file_id = file_row["file"]["id"]

        agent_client, agent_id = _agent_client(admin)
        admin.post(
            f"/projects/{proj_id}/permissions",
            json={"agent_connection_id": agent_id, "permission_type": "write"},
        )
        with agent_client:
            r = agent_client.post(
                f"/files/{file_id}/proposals", json={"proposed_content": "x"}
            )
            assert r.status_code == 200

    def test_write_agent_cannot_accept_proposals(self, admin: TestClient) -> None:
        _, proj_id = _new_project(admin)
        file_row = admin.post(
            f"/projects/{proj_id}/files/write", json={"path": "x.md", "content": "base"}
        ).json()
        file_id = file_row["file"]["id"]
        prop = admin.post(
            f"/files/{file_id}/proposals", json={"proposed_content": "y"}
        ).json()

        agent_client, agent_id = _agent_client(admin)
        admin.post(
            f"/projects/{proj_id}/permissions",
            json={"agent_connection_id": agent_id, "permission_type": "write"},
        )
        with agent_client:
            assert agent_client.post(f"/proposals/{prop['id']}/accept").status_code == 403


# ---------------------------------------------------------------------------
# Admin always passes
# ---------------------------------------------------------------------------

class TestAdminAccess:
    def test_admin_can_accept_and_reject(self, admin: TestClient) -> None:
        _, proj_id = _new_project(admin)
        file_row = admin.post(
            f"/projects/{proj_id}/files/write", json={"path": "x.md", "content": "base"}
        ).json()
        file_id = file_row["file"]["id"]

        prop = admin.post(
            f"/files/{file_id}/proposals", json={"proposed_content": "y"}
        ).json()
        assert admin.post(f"/proposals/{prop['id']}/accept").status_code == 200

        prop2 = admin.post(
            f"/files/{file_id}/proposals", json={"proposed_content": "z"}
        ).json()
        assert admin.post(f"/proposals/{prop2['id']}/reject").status_code == 200

    def test_admin_can_read_any_project(self, admin: TestClient) -> None:
        _, proj_id = _new_project(admin)
        assert admin.get(f"/projects/{proj_id}/files").status_code == 200

    def test_no_permission_agent_gets_403_on_read(self, admin: TestClient) -> None:
        _, proj_id = _new_project(admin)
        agent_client, _ = _agent_client(admin)
        with agent_client:
            assert agent_client.get(f"/projects/{proj_id}/files").status_code == 403
