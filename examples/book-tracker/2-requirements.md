# Stage 2: After `/init-project` Stage 0

## Refinement Summary

Claude analyzed IDEA.md and identified 3 gaps:
1. **No error handling** for invalid book data
2. **No data validation** on ISBN / required fields
3. **Missing auth consideration** ("will you keep this local or access remotely?")

User confirmed: local-only for MVP, no auth needed yet. Added CSV export as a stretch feature after dialogue.

## Generated `docs/requirements.md`

```markdown
# Project Requirements: Book Tracker

*Generated via interactive refinement on 2026-04-13*

## 1. Overview

### Problem Statement
Book lovers lose track of their reading status across physical and digital books.
A lightweight personal tracker helps remember what was read, what's in progress,
and what's on the wishlist.

### Target Users
Single user (personal use). May expand to shared household use later.

### Success Metrics
- User logs 10+ books within first week of use
- User consults the app at least weekly
- Sub-200ms response for all read operations

## 2. Functional Requirements

### FR-001: Book Creation
- User Story: As a user, I want to add a book so that I can track it.
- Acceptance: Title + author required; ISBN optional; status defaults to "want-to-read".
- Priority: Must-have

### FR-002: Book Listing
- User Story: As a user, I want to see all my books so I know what I have.
- Acceptance: Returns paginated list (20/page), sorted by added date desc.
- Priority: Must-have

### FR-003: Status Filter
- User Story: As a user, I want to filter by status so I can find my in-progress books.
- Acceptance: Filter by read / reading / want-to-read; combinable with search.
- Priority: Must-have

### FR-004: Search
- User Story: As a user, I want to search by title or author.
- Acceptance: Case-insensitive substring match; results <200ms for 10k books.
- Priority: Must-have

### FR-005: Update Status
- User Story: As a user, I want to change a book's status as I progress.
- Acceptance: PATCH endpoint; validates status enum; records updated_at.
- Priority: Must-have

### FR-006: CSV Export
- User Story: As a user, I want to export my library for backup.
- Acceptance: Streams CSV with all fields; UTF-8 encoded.
- Priority: Should-have

## 3. Non-Functional Requirements

### NFR-001: Performance
Read operations <200ms p95 at 10k books. Write <500ms p95.

### NFR-002: Data Integrity
ISBN validated against ISBN-10/13 format when present. Status must be enum value.

### NFR-003: Reliability
Local SQLite/PostgreSQL persistence with daily auto-backup to `~/backups/`.

## 4. Technical Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Go | Simple deploy, fast, user comfortable with it |
| Framework | Chi | Lightweight router, idiomatic Go |
| Database | PostgreSQL | Good search, upgrade path from SQLite later |
| Migrations | goose | Simple SQL migrations |
| Query layer | sqlc | Type-safe queries generated from SQL |

## 5. Constraints & Assumptions
- Single-user, single-tenant (no multi-user)
- Local deployment only; no hosted version yet
- No authentication in MVP

## 6. Out of Scope
- Multi-user / social features
- Mobile app (web/API only)
- Goodreads/Amazon import
- Recommendations engine

## 7. Open Questions
- Should "currently reading" support multiple books simultaneously? **Resolved**: Yes.
- Do we need a separate "did-not-finish" status? **Deferred to v2.**
```
