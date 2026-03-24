# Piggyback

Monorepo for Piggyback: FastAPI (`apps/api`), Next.js (`apps/web`), and optional shared code (`packages/`). Product direction lives in [`core.md`](./core.md); stack and scope are summarized in [`ARCHITECTURE.md`](./ARCHITECTURE.md). The first Postgres schema and REST resources are described in [`docs/data-model.md`](./docs/data-model.md). Agents, project permissions, and proposal accept/reject are summarized in [`docs/trust-model.md`](./docs/trust-model.md).

## Quick start

1. Copy `.env.example` to `.env` in the repo root (adjust values if needed).
2. Start Postgres and the API:

   ```bash
   docker compose up --build
   ```

3. Open [http://localhost:8000/docs](http://localhost:8000/docs) for the API, or run the web app locally:

   ```bash
   cd apps/web
   ```

   Copy `apps/web/.env.local.example` to `apps/web/.env.local` (same values work for a local API on port 8000). Then:

   ```bash
   npm run dev
   ```

   Edit `.env.local` so `NEXT_PUBLIC_API_URL` matches your API URL (default `http://localhost:8000`).

4. Optional: run the web app in Docker (includes hot reload):

   ```bash
   docker compose --profile frontend up --build
   ```

   Then open [http://localhost:3000](http://localhost:3000).
