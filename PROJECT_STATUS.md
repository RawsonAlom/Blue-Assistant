# BLUE — Project Status

## Current Milestone

- M0 — Development Infrastructure: DONE
- M1 — Python Environment & Dependencies: DONE
- M2 — Application Skeleton & Shared Contracts: DONE
- M3 — Brain & AI Provider Foundation: DONE
- M4 — OpenRouter Runtime Integration & Text Chat: DONE
- M5 — Memory & Personalization: DONE
- M6 — Skills, Tools & Permissions: NEXT

## Verified Application State

- OpenRouter AI provider integration is implemented.
- The text chat interface is for development and testing.
- The coordinator manages request flow and conversation history.
- SQLite stores persistent conversation messages.
- The memory store supports adding, listing, searching,
  updating, and deleting memory records.
- Automated tests, Ruff linting, and project verification passed
  at the last reported verification.

## Not Yet Implemented

- Skill registry and skill execution
- Tool permission and confirmation rules
- Voice interaction pipeline
- Web dashboard
- Scheduling and reminders
- ESP32 smart-home integration
- Later reliability and advanced features

## Development Roadmap

- M0 — Development Infrastructure: DONE
- M1 — Python Environment & Dependencies: DONE
- M2 — Application Skeleton & Shared Contracts: DONE
- M3 — Brain & AI Provider Foundation: DONE
- M4 — OpenRouter Runtime Integration & Text Chat: DONE
- M5 — Memory & Personalization: DONE
- M6 — Skills, Tools & Permissions: NEXT
- M7 — Voice System: PLANNED
- M8 — Dashboard: PLANNED
- M9 — Scheduler: PLANNED
- M10 — ESP32 Smart Home: PLANNED
- M11 — Reliability: PLANNED
- M12 — Advanced Features: PLANNED

## Development Rules

1. Work on one task at a time.
2. Inspect existing code before changing architecture.
3. Keep text chat as a testing interface, not the primary user interface.
4. Do not execute proposed actions without the appropriate permission checks.
5. Verify tests, linting, and project status before milestone completion.
6. Update this file only when the verified project state changes.
7. Commit at verified milestones, not after every small task.
8. Never store API keys or other secrets in project documentation.
