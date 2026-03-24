-- Add 'write' as a valid permission_type alongside 'read' and 'propose_update'.
-- Agents with 'write' can call the direct write API on a project.

BEGIN;

ALTER TABLE permissions
    DROP CONSTRAINT IF EXISTS permissions_permission_type_check;

ALTER TABLE permissions
    ADD CONSTRAINT permissions_permission_type_check
    CHECK (permission_type IN ('read', 'propose_update', 'write'));

COMMIT;
