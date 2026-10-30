# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

fix-mypy-type-annotation

## Roadmap

### fix-mypy-type-annotation — Fixed mypy type error in database async generator return type

Status: done

Acceptance:
- mypy passes with no errors
- All backend tests pass

Implementation: `backend/app/models/database.py`

Tests: `backend/tests/test_health.py`

### add-issue-history-api — Add issue analysis history API

Status: planned

Acceptance:
- POST /api/v1/issues/analyze stores analysis in database
- GET /api/v1/issues/history returns paginated history
- GET /api/v1/issues/history/{id} returns single analysis
- Database migration for issue_analysis table

### add-llm-advisory-analysis — Add opt-in LLM advisory analysis

Status: planned

Acceptance:
- New endpoint POST /api/v1/issues/analyze-with-llm
- LLM response includes advisory disclaimer
- Provider errors surface cleanly (no fabricated success)
- Config via LLM_API_KEY, LLM_PROVIDER, LLM_MODEL, LLM_BASE_URL

### add-reproduction-runner — Add automated reproduction runner

Status: planned

Acceptance:
- POST /api/v1/reproduction/run executes PHP in sandbox
- Timeout and memory limits enforced
- Output captured and returned
- Security: non-root container, no network, read-only filesystem

