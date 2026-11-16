# ADR-002: API gateway and extraction of the rentals service

## Status
Accepted - 2026-10-28 (supersedes the "single API on :8080" part of ADR-001)

## Context
- Clients called the monolith directly and could send any `X-User-Id` (no authentication).
- Rentals is the module expected to grow and change fastest; books is stable.
- We want to learn the strangler fig pattern: move one feature behind a gateway without changing clients.

## Decision
- **NGINX** as API gateway: free, light (`nginx:alpine`), declarative config, already known; enough
  for routing, API keys and rate limiting (Kong/Traefik would add a database or more concepts).
- The gateway is the **only published port** (`GATEWAY_PORT`, 8000 by default). Services and
  databases are only reachable inside the Docker network.
- **Authentication at the gateway**: `X-API-Key` → user id through a `map`; the gateway
  overwrites `X-User-Id`. `/books` stays public, `/rentals` requires a key (401 otherwise).
- **Rate limiting**: 10 requests/s per client IP, burst 20 (`RATE_LIMIT`, `RATE_BURST`),
  then 429. Enough for a human client, stops a naive flood.
- **Rentals extracted** into `rentals-service` with **its own PostgreSQL** (database per service).
- All values (ports, keys, passwords, limits) come from `.env`; the NGINX config is a template.

## Consequences
+ Rentals can be deployed, scaled and can fail independently (books keep working: 502 only on rentals).
+ Security is added in one place, without changing the services' code.
- More moving parts: 5 containers, 2 databases, more configuration and monitoring.
- No SQL join between books and rentals anymore; old rentals stay in the books database (data migration needed).
- The gateway is a single point of failure → several replicas behind a load balancer in production.
- API keys in a config file are acceptable for a lab only; production would use JWT / an identity provider.
