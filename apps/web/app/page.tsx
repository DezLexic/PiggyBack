"use client";

import { useEffect, useState } from "react";

const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type HealthState = "loading" | "ok" | "error";

export default function Home() {
  const [health, setHealth] = useState<HealthState>("loading");
  const [healthBody, setHealthBody] = useState<string>("");
  const [dbHealth, setDbHealth] = useState<HealthState>("loading");
  const [dbBody, setDbBody] = useState<string>("");

  useEffect(() => {
    fetch(`${apiBase}/health`)
      .then((res) => {
        setHealth(res.ok ? "ok" : "error");
        return res.text();
      })
      .then(setHealthBody)
      .catch(() => setHealth("error"));

    fetch(`${apiBase}/health/db`)
      .then((res) => {
        setDbHealth(res.ok ? "ok" : "error");
        return res.text();
      })
      .then(setDbBody)
      .catch(() => setDbHealth("error"));
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-50 px-6 font-sans dark:bg-zinc-950">
      <main className="w-full max-w-lg rounded-xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          Piggyback
        </h1>
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
          User-owned AI workspace — scaffolding. API base:{" "}
          <code className="rounded bg-zinc-100 px-1 py-0.5 text-xs dark:bg-zinc-800">
            {apiBase}
          </code>
        </p>
        <dl className="mt-6 space-y-4 text-sm">
          <div>
            <dt className="font-medium text-zinc-700 dark:text-zinc-300">
              GET /health
            </dt>
            <dd className="mt-1 text-zinc-600 dark:text-zinc-400">
              {health === "loading" && "Loading…"}
              {health !== "loading" && (
                <span
                  className={
                    health === "ok" ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"
                  }
                >
                  {health === "ok" ? "OK" : "Failed"}
                </span>
              )}
              {healthBody && (
                <pre className="mt-2 overflow-x-auto rounded bg-zinc-100 p-2 text-xs dark:bg-zinc-800">
                  {healthBody}
                </pre>
              )}
            </dd>
          </div>
          <div>
            <dt className="font-medium text-zinc-700 dark:text-zinc-300">
              GET /health/db
            </dt>
            <dd className="mt-1 text-zinc-600 dark:text-zinc-400">
              {dbHealth === "loading" && "Loading…"}
              {dbHealth !== "loading" && (
                <span
                  className={
                    dbHealth === "ok" ? "text-emerald-600 dark:text-emerald-400" : "text-amber-600 dark:text-amber-400"
                  }
                >
                  {dbHealth === "ok" ? "Connected" : "Unavailable or error"}
                </span>
              )}
              {dbBody && (
                <pre className="mt-2 overflow-x-auto rounded bg-zinc-100 p-2 text-xs dark:bg-zinc-800">
                  {dbBody}
                </pre>
              )}
            </dd>
          </div>
        </dl>
      </main>
    </div>
  );
}
