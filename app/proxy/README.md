# NaturalSQL Gateway (Nginx)

Single public entrypoint for NaturalSQL.

## Purpose

- Expose only one public service (this gateway)
- Keep backend and frontend private in the Docker network
- Route:
  - `/` -> frontend container
  - `/api/*` -> backend container (keeps `/api` prefix)

## Files

- `Dockerfile`: Nginx image + runtime templating with `envsubst`
- `nginx.conf.template`: Reverse proxy rules

## Required environment variables

- `NGINX_SERVER_NAME` (default: `naturalsql.online`)
- `FRONTEND_UPSTREAM` (default: `naturalsql-client-ahpyii:80`)
- `BACKEND_UPSTREAM` (default: `naturalsql-backend-9lrxni:8000`)

If your Railpack frontend runs on a different internal port, update `FRONTEND_UPSTREAM` (for example `naturalsql-client-ahpyii:4173`).

## Dokploy checklist

1. Create service from `app/proxy`.
2. Build with Dockerfile.
3. Attach domain `naturalsql.online` + HTTPS.
4. Remove Domains from frontend/backend services.
5. Ensure gateway, frontend, and backend share the same Dokploy network.
