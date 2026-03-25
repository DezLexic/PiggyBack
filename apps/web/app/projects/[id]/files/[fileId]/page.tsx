"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  getFile,
  getProject,
  getWorkspace,
  updateFile,
  listVersions,
  listProposals,
  acceptProposal,
  rejectProposal,
  type PiggyFile,
  type Project,
  type Workspace,
  type FileVersion,
  type Proposal,
} from "@/lib/api";

export default function FilePage() {
  const { id: projectId, fileId } = useParams<{ id: string; fileId: string }>();

  const [file, setFile] = useState<PiggyFile | null>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [versions, setVersions] = useState<FileVersion[]>([]);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Edit state
  const [editing, setEditing] = useState(false);
  const [editContent, setEditContent] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Versions panel
  const [showVersions, setShowVersions] = useState(false);

  // Proposal action state
  const [proposalPending, setProposalPending] = useState<string | null>(null);
  const [proposalError, setProposalError] = useState<string | null>(null);

  const loadAll = () => {
    setLoading(true);
    setError(null);
    Promise.all([getFile(fileId), listVersions(fileId), listProposals(fileId)])
      .then(([f, vs, ps]) => {
        setFile(f);
        setVersions(vs);
        setProposals(ps);
        return getProject(f.project_id);
      })
      .then((proj) => {
        setProject(proj);
        return getWorkspace(proj.workspace_id);
      })
      .then(setWorkspace)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(loadAll, [fileId]);

  const handleSave = async () => {
    if (!file) return;
    setSaving(true);
    setSaveError(null);
    try {
      const updated = await updateFile(fileId, editContent);
      setFile(updated);
      const vs = await listVersions(fileId);
      setVersions(vs);
      setEditing(false);
    } catch (e: unknown) {
      setSaveError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const handleProposal = async (proposalId: string, action: "accept" | "reject") => {
    setProposalPending(proposalId);
    setProposalError(null);
    try {
      if (action === "accept") {
        await acceptProposal(proposalId);
      } else {
        await rejectProposal(proposalId);
      }
      const [f, vs, ps] = await Promise.all([
        getFile(fileId),
        listVersions(fileId),
        listProposals(fileId),
      ]);
      setFile(f);
      setVersions(vs);
      setProposals(ps);
    } catch (e: unknown) {
      setProposalError(e instanceof Error ? e.message : "Action failed");
    } finally {
      setProposalPending(null);
    }
  };

  const pendingProposals = proposals.filter((p) => p.status === "pending");
  const resolvedProposals = proposals.filter((p) => p.status !== "pending");

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-10">
        <p className="text-sm text-zinc-400">Loading…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-10">
        <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-600 dark:bg-red-950 dark:text-red-400">
          {error}
        </p>
      </div>
    );
  }

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
        <span className="font-mono text-zinc-700 dark:text-zinc-200">{file?.path ?? "…"}</span>
      </nav>

      <div className="flex items-center justify-between">
        <h1 className="font-mono text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          {file?.path}
        </h1>
        <div className="flex items-center gap-2 text-xs text-zinc-400">
          <span>{versions.length} version{versions.length !== 1 ? "s" : ""}</span>
          {pendingProposals.length > 0 && (
            <span className="rounded-full bg-amber-100 px-2 py-0.5 text-amber-700 dark:bg-amber-900 dark:text-amber-300">
              {pendingProposals.length} proposal{pendingProposals.length !== 1 ? "s" : ""}
            </span>
          )}
        </div>
      </div>

      {/* ── Content ─────────────────────────────────────────────────────────── */}
      <section className="mt-6">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Content</h2>
          {!editing && (
            <button
              onClick={() => { setEditing(true); setEditContent(file?.content ?? ""); setSaveError(null); }}
              className="text-xs text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200"
            >
              Edit
            </button>
          )}
        </div>

        {editing ? (
          <div className="mt-2 space-y-2">
            <textarea
              autoFocus
              rows={14}
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 font-mono text-sm text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50"
            />
            {saveError && <p className="text-sm text-red-600 dark:text-red-400">{saveError}</p>}
            <div className="flex gap-2">
              <button
                onClick={handleSave}
                disabled={saving}
                className="rounded-md bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-40 dark:bg-zinc-50 dark:text-zinc-900"
              >
                {saving ? "Saving…" : "Save"}
              </button>
              <button
                onClick={() => { setEditing(false); setSaveError(null); }}
                className="rounded-md px-3 py-1.5 text-sm text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-50"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <pre className="mt-2 overflow-x-auto whitespace-pre-wrap rounded-md border border-zinc-100 bg-white px-4 py-3 font-mono text-sm text-zinc-800 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-200">
            {file?.content || <span className="text-zinc-400 italic">Empty file</span>}
          </pre>
        )}
      </section>

      {/* ── Proposals ───────────────────────────────────────────────────────── */}
      {proposals.length > 0 && (
        <section className="mt-10">
          <h2 className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Proposals</h2>

          {proposalError && (
            <p className="mt-2 text-sm text-red-600 dark:text-red-400">{proposalError}</p>
          )}

          {pendingProposals.length > 0 && (
            <ul className="mt-3 space-y-3">
              {pendingProposals.map((p) => (
                <li
                  key={p.id}
                  className="rounded-md border border-zinc-200 bg-white p-4 dark:border-zinc-700 dark:bg-zinc-900"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-zinc-400">
                      {new Date(p.created_at).toLocaleString()}
                    </span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleProposal(p.id, "accept")}
                        disabled={proposalPending === p.id}
                        className="rounded bg-emerald-600 px-2.5 py-1 text-xs font-medium text-white hover:bg-emerald-700 disabled:opacity-40"
                      >
                        Accept
                      </button>
                      <button
                        onClick={() => handleProposal(p.id, "reject")}
                        disabled={proposalPending === p.id}
                        className="rounded bg-zinc-200 px-2.5 py-1 text-xs font-medium text-zinc-700 hover:bg-zinc-300 disabled:opacity-40 dark:bg-zinc-700 dark:text-zinc-200 dark:hover:bg-zinc-600"
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                  <pre className="mt-2 overflow-x-auto whitespace-pre-wrap font-mono text-sm text-zinc-800 dark:text-zinc-200">
                    {p.proposed_content}
                  </pre>
                </li>
              ))}
            </ul>
          )}

          {resolvedProposals.length > 0 && (
            <details className="mt-3">
              <summary className="cursor-pointer text-xs text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300">
                {resolvedProposals.length} resolved
              </summary>
              <ul className="mt-2 space-y-2">
                {resolvedProposals.map((p) => (
                  <li
                    key={p.id}
                    className="rounded-md border border-zinc-100 bg-zinc-50 p-3 opacity-60 dark:border-zinc-800 dark:bg-zinc-900"
                  >
                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                          p.status === "accepted"
                            ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300"
                            : "bg-zinc-200 text-zinc-600 dark:bg-zinc-700 dark:text-zinc-400"
                        }`}
                      >
                        {p.status}
                      </span>
                      <span className="text-xs text-zinc-400">
                        {new Date(p.created_at).toLocaleString()}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            </details>
          )}
        </section>
      )}

      {/* ── Version history ──────────────────────────────────────────────────── */}
      <section className="mt-10">
        <button
          onClick={() => setShowVersions((v) => !v)}
          className="flex items-center gap-1.5 text-sm font-medium text-zinc-700 hover:text-zinc-900 dark:text-zinc-300 dark:hover:text-zinc-50"
        >
          <span>{showVersions ? "▾" : "▸"}</span>
          Version history
          <span className="text-xs font-normal text-zinc-400">({versions.length})</span>
        </button>

        {showVersions && (
          <ul className="mt-3 space-y-2">
            {[...versions].reverse().map((v, i) => (
              <li
                key={v.id}
                className="rounded-md border border-zinc-100 bg-white p-3 dark:border-zinc-800 dark:bg-zinc-900"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs text-zinc-400">
                    {new Date(v.created_at).toLocaleString()}
                  </span>
                  {i === 0 && (
                    <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-500 dark:bg-zinc-800">
                      current
                    </span>
                  )}
                </div>
                <pre className="mt-1.5 overflow-x-auto whitespace-pre-wrap font-mono text-xs text-zinc-600 dark:text-zinc-400">
                  {v.content.length > 200 ? v.content.slice(0, 200) + "…" : v.content}
                </pre>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
