# ADR-001: Architecture style for Book&Ride

## Status
Accepted - 2026-10-28

## Context
- Team: one small team of 2–3 students.
- Traffic: low, similar for books and rentals (a bookstore café with a few bikes).
- Change frequency: the whole product changes together during the course.
- Data: books and rentals share users and need strong consistency (a bike cannot be rented twice).
- Time to market: we need a working product in one 2-hour session, with no DevOps budget.

## Decision
We build Book&Ride as a **modular monolith**: one FastAPI codebase (`api/`), one container,
one PostgreSQL database, with one router per business module (`books`, `rentals`).

## Consequences
+ Simple to develop, test (`pytest`), deploy (`docker compose up`) and debug: one process, one log.
+ Modules call each other in-process (fast, no network) and can use SQL joins and transactions.
- One deployment unit: a change in pricing rebuilds and restarts the whole API.
- Shared fate: if the API container crashes, books and rentals are both down.
- We will reconsider this decision when rentals needs to scale or ship independently
  (e.g. ×100 traffic, a separate team), or when the gateway of Unit 04 is introduced.
