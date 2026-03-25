const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_ADMIN_API_KEY ?? "";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Workspace {
  id: string;
  name: string;
  created_at: string;
}

export interface Project {
  id: string;
  workspace_id: string;
  name: string;
  created_at: string;
}

export interface PiggyFile {
  id: string;
  project_id: string;
  path: string;
  current_version_id: string | null;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface FileVersion {
  id: string;
  file_id: string;
  content: string;
  created_at: string;
}

export interface Proposal {
  id: string;
  file_id: string;
  proposed_content: string;
  status: "pending" | "accepted" | "rejected";
  created_at: string;
}

export interface AgentConnection {
  id: string;
  name: string;
  agent_type: string;
  created_at: string;
}

export interface AgentConnectionCreated extends AgentConnection {
  api_key: string;
}

export interface Permission {
  id: string;
  project_id: string;
  agent_connection_id: string;
  permission_type: "read" | "propose_update" | "write";
  created_at: string;
}

export interface WriteResponse {
  file: { id: string; path: string; current_version_id: string | null };
  version: { id: string; created_at: string };
}

// ─── Base fetch ───────────────────────────────────────────────────────────────

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(API_KEY ? { "X-API-Key": API_KEY } : {}),
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// ─── Workspaces ───────────────────────────────────────────────────────────────

export const listWorkspaces = () => apiFetch<Workspace[]>("/workspaces");

export const getWorkspace = (id: string) => apiFetch<Workspace>(`/workspaces/${id}`);

export const createWorkspace = (name: string) =>
  apiFetch<Workspace>("/workspaces", {
    method: "POST",
    body: JSON.stringify({ name }),
  });

// ─── Projects ─────────────────────────────────────────────────────────────────

export const listProjects = (workspaceId: string) =>
  apiFetch<Project[]>(`/workspaces/${workspaceId}/projects`);

export const getProject = (id: string) => apiFetch<Project>(`/projects/${id}`);

export const createProject = (workspaceId: string, name: string) =>
  apiFetch<Project>(`/workspaces/${workspaceId}/projects`, {
    method: "POST",
    body: JSON.stringify({ name }),
  });

// ─── Files ────────────────────────────────────────────────────────────────────

export const listFiles = (projectId: string) =>
  apiFetch<PiggyFile[]>(`/projects/${projectId}/files`);

export const getFile = (fileId: string) => apiFetch<PiggyFile>(`/files/${fileId}`);

export const updateFile = (fileId: string, content: string) =>
  apiFetch<PiggyFile>(`/files/${fileId}`, {
    method: "PATCH",
    body: JSON.stringify({ content }),
  });

export const listVersions = (fileId: string) =>
  apiFetch<FileVersion[]>(`/files/${fileId}/versions`);

export const writeFile = (
  projectId: string,
  path: string,
  content: string,
  mode: "replace" | "append" = "replace"
) =>
  apiFetch<WriteResponse>(`/projects/${projectId}/files/write`, {
    method: "POST",
    body: JSON.stringify({ path, content, mode }),
  });

// ─── Proposals ────────────────────────────────────────────────────────────────

export const listProposals = (fileId: string) =>
  apiFetch<Proposal[]>(`/files/${fileId}/proposals`);

export const acceptProposal = (proposalId: string) =>
  apiFetch<unknown>(`/proposals/${proposalId}/accept`, { method: "POST" });

export const rejectProposal = (proposalId: string) =>
  apiFetch<unknown>(`/proposals/${proposalId}/reject`, { method: "POST" });

// ─── Agents & permissions ─────────────────────────────────────────────────────

export const listAgents = () => apiFetch<AgentConnection[]>("/agent-connections");

export const createAgent = (name: string, agent_type: string) =>
  apiFetch<AgentConnectionCreated>("/agent-connections", {
    method: "POST",
    body: JSON.stringify({ name, agent_type }),
  });

export const listPermissions = (projectId: string) =>
  apiFetch<Permission[]>(`/projects/${projectId}/permissions`);

export const grantPermission = (
  projectId: string,
  agent_connection_id: string,
  permission_type: string
) =>
  apiFetch<Permission>(`/projects/${projectId}/permissions`, {
    method: "POST",
    body: JSON.stringify({ agent_connection_id, permission_type }),
  });
