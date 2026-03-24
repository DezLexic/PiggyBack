-- API keys for authenticating write operations.
-- key_hash stores SHA-256 of the plaintext key (never stored in plaintext).
-- agent_connection_id links a key to its agent; nullable for standalone keys.

BEGIN;

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_hash TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    agent_connection_id UUID REFERENCES agent_connections (id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_api_keys_agent_connection_id ON api_keys (agent_connection_id);

COMMIT;
