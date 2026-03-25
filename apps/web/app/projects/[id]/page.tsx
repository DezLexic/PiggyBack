"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  getProject,
  getWorkspace,
  listFiles,
  writeFile,
  type Project,
  type Workspace,
  type PiggyFile,
} from "@/lib/api";

export default function ProjectPage() {
  const { id } = useParams<{ id: string }>();

  const [project, setProject] = useState<Project | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [files, setFiles] = useState<PiggyFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Write file form
  const [formOpen, setFormOpen] = useState(false);
  const [filePath, setFilePath] = useState("");
  const [fileContent, setFileContent] = useState("");
  const [fileMode, setFileMode] = useState<"replace" | "append">("replace");
  const [writing, setWriting] = useState(false);
  const [writeError, setWriteError] = useState<string | null>(null);

  const loadProject = () => {
    setLoading(true);
    setError(null);
    getProject(id)
      .then((proj) => {
        setProject(proj);
        return Promise.all([getWorkspace(proj.workspace_id), listFiles(id)]);
      })
      .then(([ws, fs]) => {
        setWorkspace(ws);
        setFiles(fs);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(loadProject, [id]);

  const refreshFiles = () => listFiles(id).then(setFiles).catch(() => null);

  const handleWrite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!filePath.trim()) return;
    setWriting(true);
    setWriteError(null);
    try {
      await writeFile(id, filePath.trim(), fileContent, fileMode);
      await refreshFiles();
      setFilePath("");
      setFileContent("");
      setFileMode("replace");
      setFormOpen(false);
    } catch (e: unknown) {
      setWriteError(e instanceof Error ? e.message : "Write failed");
    } finally {
      setWriting(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      {/* Breadcrumb */}
      <nav className="mb-6 flex items-center gap-1.5 text-sm text-zinc-400">
        <Link href="/" className="hover:text-zinc-600 dark:hover:text-zinc-300">Workspaces</Link>
        <span>/</span>
        {workspace && (
          <>
            <Link
              href={`/workspaces/${workspace.id}`}
              className="hover:text-zinc-600 dark:hover:text-zinc-300"
            >
              {workspace.name}
            </Link>
            <span>/</span>
          </>
        )}
        <span className="text-zinc-700 dark:text-zinc-200">{project?.name ?? "…"}</span>
      </nav>

      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          {project?.name ?? "Loading…"}
        </h1>
        <div className="flex items-center gap-2">
          <Link
            href={`/projects/${id}/agents`}
            className="rounded-md px-3 py-1.5 text-sm text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-50"
          >
            Agents
          </Link>
          {!formOpen && (
            <button
              onClick={() => setFormOpen(true)}
              className="rounded-md bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-700 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
            >
              Write file
            </button>
          )}
        </div>
      </div>

      {/* Write file form */}
      {formOpen && (
        <form
          onSubmit={handleWrite}
          className="mt-4 space-y-3 rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900"
        >
          <div className="flex gap-2">
            <input
              autoFocus
              type="text"
              placeholder="path/to/file.md"
              value={filePath}
              onChange={(e) => setFilePath(e.target.value)}
              className="flex-1 rounded-md border border-zinc-300 bg-white px-3 py-1.5 text-sm font-mono text-zinc-900 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-50 dark:placeholder-zinc-500"
            />
            <select
              value={fileMode}
              onChange={(e) => setFileMode(e.target.value as "replace" | "append")}
              className="rounded-md border border-zinc-300 bg-white px-2 py-1.5 text-sm text-zinc-700 focus:outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-200"
            >
              <option value="replace">Replace</option>
              <option value="append">Append</option>
            </select>
          </div>
          <textarea
            rows={6}
            placeholder="File content…"
            value={fileContent}
            onChange={(e) => setFileContent(e.target.value)}
            className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 font-mono text-sm text-zinc-900 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-50 dark:placeholder-zinc-500"
          />
          {writeError && (
            <p className="text-sm text-red-600 dark:text-red-400">{writeError}</p>
          )}
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={writing || !filePath.trim()}
              className="rounded-md bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-40 dark:bg-zinc-50 dark:text-zinc-900"
            >
              {writing ? "Writing…" : "Write"}
            </button>
            <button
              type="button"
              onClick={() => { setFormOpen(false); setFilePath(""); setFileContent(""); setWriteError(null); }}
              className="rounded-md px-3 py-1.5 text-sm text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-50"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {error && (
        <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-600 dark:bg-red-950 dark:text-red-400">
          {error}
        </p>
      )}

      {loading ? (
        <p className="mt-8 text-sm text-zinc-400">Loading…</p>
      ) : files.length === 0 ? (
        <div className="mt-12 text-center">
          <p className="text-sm text-zinc-400">No files yet.</p>
          <p className="mt-1 text-sm text-zinc-400">Use &ldquo;Write file&rdquo; to add context.</p>
        </div>
      ) : (
        <ul className="mt-6 divide-y divide-zinc-100 dark:divide-zinc-800">
          {files.map((f) => (
            <li key={f.id}>
              <Link
                href={`/projects/${id}/files/${f.id}`}
                className="flex items-center justify-between py-3 group"
              >
                <span className="font-mono text-sm text-zinc-900 group-hover:text-zinc-600 dark:text-zinc-50 dark:group-hover:text-zinc-300">
                  {f.path}
                </span>
                <span className="text-xs text-zinc-400">
                  {new Date(f.updated_at).toLocaleString()}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
