# Stage 1: After `/ideate`

## User's Raw Input

> "I want to build something that helps me track my reading habits."

## Dialogue Summary

Claude asked 4 questions across 2 rounds:

1. **The Why**: "What specific problem does this solve?" → *"I keep forgetting which books I've read and which I want to read next."*
2. **The Why**: "Who would use this?" → *"Just me for now, maybe friends later."*
3. **The What**: "What are the 2-3 things this absolutely must do?" → *"Track books, mark them as read/reading/want-to-read, maybe search."*
4. **Tech** (smart default kicked in): User said *"I don't know"* → Claude suggested Go + Chi + PostgreSQL based on "simple REST API with CRUD."

## Generated IDEA.md

```markdown
# Book Tracker

## One-Liner
A personal app to track books I've read, am reading, or want to read.

## The Problem
I keep forgetting which books I've read and which I want to read next. A simple tool
to log reading status would help me stay organized and never lose track of a good
recommendation.

## Core Features
- Add books with title, author, and reading status
- Filter by status (read / reading / want-to-read)
- Search by title or author

## Tech Preferences
Suggested during /ideate — revisit during /init-project:
- Language: Go
- Framework: Chi
- Database: PostgreSQL

## Notes
- Single-user initially, may share with friends later
- Personal project, not production-grade
```
