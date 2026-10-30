# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint
## [1.0.1] - 2026-10-30

### Fixed
- Fixed mypy type error in `backend/app/models/database.py`: corrected `get_db()` return type from `AsyncSession` to `AsyncGenerator[AsyncSession, None]` with proper import

### Verified
- mypy: passes with no errors
- Backend pytest: 9 tests pass
- Frontend vitest: 6 tests pass
- Frontend build (tsc + vite): passes

## 1.0.0 — work-in-progress checkpoint
Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-22

### Added
- Initial project scaffold with FastAPI backend and React + TypeScript + Vite frontend
- Deterministic PHP issue classification engine for 5 known bug categories:
  - JIT segmentation faults (php/php-src#7817)
  - GC threshold performance regressions (php/php-src#9993)
  - macOS fork() safety crashes (php/php-src#11818)
  - array_unique() SORT_REGULAR non-transitive comparison bug (php/php-src#20262)
  - LDAP/OpenSSL cleanup segfaults (php/php-src#8620)
- REST API endpoints:
  - `GET /api/v1/health` — Service health check
  - `GET /api/v1/health/db` — Database connectivity
  - `POST /api/v1/issues/analyze` — Issue classification with reproduction hints
  - `GET /api/v1/issues/types` — List known issue types
- React frontend with:
  - Dashboard with stats, workflows, and reference issue table
  - Issue Analyzer form with real-time API integration
  - Health check page with API/db status
  - Responsive design with CSS modules
- Docker Compose with:
  - Backend (FastAPI, non-root)
  - Frontend (nginx, SPA proxy)
  - PostgreSQL 16
  - Keycloak 26 (OIDC with realm import)
- CI/CD pipeline (GitHub Actions):
  - Backend pytest tests
  - Frontend typecheck, build, vitest
  - Docker image builds (backend + frontend)
  - Integration test with docker compose
- Documentation: README, LICENSE, portfolio.json, CHANGELOG
- Configuration: .env.example, .gitignore, pyproject.toml

### Security
- Non-root Docker containers
- HttpOnly cookie auth architecture (planned)
- LLM API keys server-side only
- No hardcoded secrets or credentials

### Known Limitations
- Authentication (Keycloak OIDC) not yet implemented — demo mode only
- Reproduction runner and bisect automation planned for future releases
- SQLite default for development; PostgreSQL required for production