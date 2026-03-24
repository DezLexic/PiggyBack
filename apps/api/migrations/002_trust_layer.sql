-- Agent connections and project-level permissions; proposal lifecycle uses existing proposed_updates.status.

BEGIN;

CREATE TABLE IF NOT EXISTS agent_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    agent_type TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_connection_id UUID NOT NULL REFERENCES agent_connections (id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
    permission_type TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT permissions_permission_type_check CHECK (permission_type IN ('read', 'propose_update')),
    UNIQUE (agent_connection_id, project_id, permission_type)
);

CREATE INDEX IF NOT EXISTS idx_permissions_project_id ON permissions (project_id);
CREATE INDEX IF NOT EXISTS idx_permissions_agent_connection_id ON permissions (agent_connection_id);

COMMIT;
