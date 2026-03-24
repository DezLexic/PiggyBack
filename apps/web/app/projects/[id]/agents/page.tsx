"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  getProject,
  getWorkspace,
  listAgents,
  listPermissions,
  createAgent,
  grantPermission,
  type Project,
  type Workspace,
  type AgentConnection,
  type Permission,
  type AgentConnectionCreated,
} from "@/lib/api";

const PERMISSION_TYPES = ["read", "propose_update", "write"] as const;

export default function AgentsPage() {
  const { id: projectId } = useParams<{ id: string }>();

  const [project, setProject] = useState<Project | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [agents, setAgents] = useState<AgentConnection[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Grant permission form
  const [grantAgentId, setGrantAgentId] = useState("");
  const [grantType, setGrantType] = useState<string>("read");
  const [granting, setGranting] = useState(false);
  const [grantError, setGrantError] = useState<string | null>(null);

  // Register agent form
  const [registerOpen, setRegisterOpen] = useState(false);
  const [agentName, setAgentName] = useState("");
  const [agentType, setAgentType] = useState("external");
  const [registering, setRegistering] = useState(false);
  const [registerError, setRegisterError] = useState<string | null>(null);
  const [newKey, setNewKey] = useState<AgentConnectionCreated | null>(null);

  const loadAll = () => {
    setLoading(true);
    setError(null);
    Promise.all([getProject(projectId), listAgents(), listPermissions(projectId)])
      .then(([proj, agts, perms]) => {
        setProject(proj);
        setAgents(agts);
        setPermissions(perms);
        if (!grantAgentId && agts.length > 0) setGrantAgentId(agts[0].id);
        return getWorkspace(proj.workspace_id);
      })
      .then(setWorkspace)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(loadAll, [projectId]);

  const handleGrant = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!grantAgentId) return;
    setGranting(true);
    setGrantError(null);
    try {
      const perm = await grantPermission(projectId, grantAgentId, grantType);
      setPermissions((prev) => [...prev, perm]);
    } catch (e: unknown) {
      setGrantError(e instanceof Error ? e.message : "Failed to grant permission");
    } finally {
      setGranting(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!agentName.trim()) return;
    setRegistering(true);
    setRegisterError(null);
    try {
      const created = await createAgent(agentName.trim(), agentType.trim() || "external");
      setAgents((prev) => [...prev, created]);
      setNewKey(created);
      setAgentName("");
      setAgentType("external");
      setRegisterOpen(false);
      if (!grantAgentId) setGrantAgentId(created.id);
    } catch (e: unknown) {
      setRegisterError(e instanceof Error ? e.message : "Failed to register agent");
    } finally {
      setRegistering(false);
    }
  };

  // Map agent id → name for display
  const agentMap = Object.fromEntries(agents.map((a) => [a.id, a]));

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      {/* Breadcrumb */}
      <nav className="mb-6 flex items-center gap-1.5 text-sm text-zinc-400">
        <Link href="/" className="hover:text-zinc-600 dark:hover:text-zinc-300">Workspaces</Link>
        <span>/</span>
        {workspace && (
          <>
            <Link href={`/workspaces/${workspace.id}`} className="hover:text-zinc-600 dark:hover:text-zinc-300">
              {workspace.name}
            </Link>
            <span>/</span>
          </>
        )}
        {project && (
          <>
            <Link href={`/projects/${project.id}`} className="hover:text-zinc-600 dark:hover:text-zinc-300">
              {project.name}
            </Link>
            <span>/</span>
          </>
        )}
        <span className="text-zinc-700 dark:text-zinc-200">Agents</span>
      </nav>

      <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        Agents &amp; Permissions
      </h1>
      <p className="mt-1 text-sm text-zinc-500">
        Control which agents can read or write to <strong>{project?.name}</strong>.
      </p>

      {error && (
        <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-600 dark:bg-red-950 dark:text-red-400">
          {error}
        </p>
      )}

      {/* ── New API key reveal ───────────────────────────────────────────────── */}
      {newKey && (
        <div className="mt-6 rounded-md border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-800 dark:bg-emerald-950">
          <p className="text-sm font-medium text-emerald-800 dark:text-emerald-200">
            Agent <strong>{newKey.name}</strong> registered — copy the API key now, it won&apos;t be shown again.
          </p>
          <pre className="mt-2 select-all overflow-x-auto rounded bg-white px-3 py-2 font-mono text-sm text-emerald-800 dark:bg-zinc-900 dark:text-emerald-300">
            {newKey.api_key}
          </pre>
          <button
            onClick={() => setNewKey(null)}
            className="mt-2 text-xs text-emerald-600 hover:text-emerald-800 dark:text-emerald-400 dark:hover:text-emerald-200"
          >
            Dismiss
          </button>
        </div>
      )}

      {loading ? (
        <p className="mt-8 text-sm text-zinc-400">Loading…</p>
      ) : (
        <>
          {/* ── Project permissions ───────────────────────────────────────────── */}
          <section className="mt-8">
            <h2 className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
              Project permissions
            </h2>

            {permissions.length === 0 ? (
              <p className="mt-2 text-sm text-zinc-400">No permissions granted yet.</p>
            ) : (
              <table className="mt-3 w-full text-sm">
                <thead>
                  <tr className="border-b border-zinc-100 text-left dark:border-zinc-800">
                    <th className="pb-2 font-medium text-zinc-500">Agent</th>
                    <th className="pb-2 font-medium text-zinc-500">Type</th>
                    <th className="pb-2 font-medium text-zinc-500">Granted</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                  {permissions.map((p) => (
                    <tr key={p.id}>
                      <td className="py-2 text-zinc-900 dark:text-zinc-50">
                        {agentMap[p.agent_connection_id]?.name ?? p.agent_connection_id.slice(0, 8)}
                      </td>
                      <td className="py-2">
                        <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-mono text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
                          {p.permission_type}
                        </span>
                      </td>
                      <td className="py-2 text-xs text-zinc-400">
                        {new Date(p.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {/* Grant permission form */}
            <form onSubmit={handleGrant} className="mt-4 flex flex-wrap gap-2">
              <select
                value={grantAgentId}
                onChange={(e) => setGrantAgentId(e.target.value)}
                disabled={agents.length === 0}
                className="rounded-md border border-zinc-300 bg-white px-2.5 py-1.5 text-sm text-zinc-700 focus:outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-200"
              >
                {agents.length === 0 ? (
                  <option value="">No agents registered</option>
                ) : (
                  agents.map((a) => (
                    <option key={a.id} value={a.id}>{a.name}</option>
                  ))
                )}
              </select>
              <select
                value={grantType}
                onChange={(e) => setGrantType(e.target.value)}
                className="rounded-md border border-zinc-300 bg-white px-2.5 py-1.5 text-sm text-zinc-700 focus:outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-200"
              >
                {PERMISSION_TYPES.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
              <button
                type="submit"
                disabled={granting || !grantAgentId}
                className="rounded-md bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-40 dark:bg-zinc-50 dark:text-zinc-900"
              >
                {granting ? "Granting…" : "Grant"}
              </button>
            </form>
            {grantError && (
              <p className="mt-2 text-sm text-red-600 dark:text-red-400">{grantError}</p>
            )}
          </section>

          {/* ── Registered agents ─────────────────────────────────────────────── */}
          <section className="mt-10">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                Registered agents
              </h2>
              {!registerOpen && (
                <button
                  onClick={() => setRegisterOpen(true)}
                  className="text-xs text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200"
                >
                  + Register new
                </button>
              )}
            </div>

            {registerOpen && (
              <form onSubmit={handleRegister} className="mt-3 flex flex-wrap gap-2">
                <input
                  autoFocus
                  type="text"
                  placeholder="Agent name"
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  className="rounded-md border border-zinc-300 bg-white px-3 py-1.5 text-sm text-zinc-900 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50 dark:placeholder-zinc-500"
                />
                <input
                  type="text"
                  placeholder="Type (e.g. claude)"
                  value={agentType}
                  onChange={(e) => setAgentType(e.target.value)}
                  className="w-36 rounded-md border border-zinc-300 bg-white px-3 py-1.5 text-sm text-zinc-900 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50 dark:placeholder-zinc-500"
                />
                <button
                  type="submit"
                  disabled={registering || !agentName.trim()}
                  className="rounded-md bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-40 dark:bg-zinc-50 dark:text-zinc-900"
                >
                  {registering ? "Registering…" : "Register"}
                </button>
                <button
                  type="button"
                  onClick={() => { setRegisterOpen(false); setAgentName(""); setRegisterError(null); }}
                  className="rounded-md px-3 py-1.5 text-sm text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-50"
                >
                  Cancel
                </button>
                {registerError && (
                  <p className="w-full text-sm text-red-600 dark:text-red-400">{registerError}</p>
                )}
              </form>
            )}

            {agents.length === 0 ? (
              <p className="mt-2 text-sm text-zinc-400">No agents registered yet.</p>
            ) : (
              <ul className="mt-3 divide-y divide-zinc-100 dark:divide-zinc-800">
                {agents.map((a) => (
                  <li key={a.id} className="flex items-center justify-between py-2.5">
                    <div>
                      <span className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
                        {a.name}
                      </span>
                      <span className="ml-2 rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-mono text-zinc-500 dark:bg-zinc-800">
                        {a.agent_type}
                      </span>
                    </div>
                    <span className="text-xs text-zinc-400">
                      {new Date(a.created_at).toLocaleDateString()}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}
    </div>
  );
}
