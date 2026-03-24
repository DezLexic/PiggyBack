"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  getWorkspace,
  listProjects,
  createProject,
  type Workspace,
  type Project,
} from "@/lib/api";

export default function WorkspacePage() {
  const { id } = useParams<{ id: string }>();

  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [creating, setCreating] = useState(false);

  const load = () => {
    setLoading(true);
    setError(null);
    Promise.all([getWorkspace(id), listProjects(id)])
      .then(([ws, projs]) => {
        setWorkspace(ws);
        setProjects(projs);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(load, [id]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    setCreating(true);
    setError(null);
    try {
      const proj = await createProject(id, newName.trim());
      setProjects((prev) => [...prev, proj]);
      setNewName("");
      setFormOpen(false);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to create project");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      {/* Breadcrumb */}
      <nav className="mb-6 flex items-center gap-1.5 text-sm text-zinc-400">
        <Link href="/" className="hover:text-zinc-600 dark:hover:text-zinc-300">
          Workspaces
        </Link>
        <span>/</span>
        <span className="text-zinc-700 dark:text-zinc-200">{workspace?.name ?? "…"}</span>
      </nav>

      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          {workspace?.name ?? "Loading…"}
        </h1>
        {!formOpen && (
          <button
            onClick={() => setFormOpen(true)}
            className="rounded-md bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-700 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
          >
            New project
          </button>
        )}
      </div>

      {formOpen && (
        <form onSubmit={handleCreate} className="mt-4 flex gap-2">
          <input
            autoFocus
            type="text"
            placeholder="Project name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            className="flex-1 rounded-md border border-zinc-300 bg-white px-3 py-1.5 text-sm text-zinc-900 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50 dark:placeholder-zinc-500"
          />
          <button
            type="submit"
            disabled={creating || !newName.trim()}
            className="rounded-md bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-40 dark:bg-zinc-50 dark:text-zinc-900"
          >
            {creating ? "Creating…" : "Create"}
          </button>
          <button
            type="button"
            onClick={() => { setFormOpen(false); setNewName(""); }}
            className="rounded-md px-3 py-1.5 text-sm text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-50"
          >
            Cancel
          </button>
        </form>
      )}

      {error && (
        <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-600 dark:bg-red-950 dark:text-red-400">
          {error}
        </p>
      )}

      {loading ? (
        <p className="mt-8 text-sm text-zinc-400">Loading…</p>
      ) : projects.length === 0 ? (
        <div className="mt-12 text-center">
          <p className="text-sm text-zinc-400">No projects yet. Create one to get started.</p>
        </div>
      ) : (
        <ul className="mt-6 divide-y divide-zinc-100 dark:divide-zinc-800">
          {projects.map((proj) => (
            <li key={proj.id}>
              <Link
                href={`/projects/${proj.id}`}
                className="flex items-center justify-between py-3 group"
              >
                <span className="text-sm font-medium text-zinc-900 group-hover:text-zinc-600 dark:text-zinc-50 dark:group-hover:text-zinc-300">
                  {proj.name}
                </span>
                <span className="text-xs text-zinc-400">
                  {new Date(proj.created_at).toLocaleDateString()}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
