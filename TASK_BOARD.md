# BLUE — Development Task Board

Last verified milestone: Module contracts committed
Current phase: Development Infrastructure

## Task Status Definitions

- NOT STARTED: Work has not begun.
- IN PROGRESS: Work is actively being implemented.
- BLOCKED: Work cannot proceed because a dependency or issue remains.
- REVIEW: Implementation exists but requires verification.
- DONE: Completion has been verified and documented.

Never mark a task DONE based only on an AI's claim.
Verify the files, commands, tests, and Git state.

## Phase 0 — Repository Foundation

- [x] TASK-001 Initialize Git repository and main branch
- [x] TASK-002 Create `.gitignore`
- [x] TASK-003 Create `PROJECT_CONTEXT.md`
- [x] TASK-004 Create `AGENTS.md`
- [x] TASK-005 Create `PROJECT_STATUS.md`
- [x] TASK-006 Create `ARCHITECTURE.md`
- [x] TASK-007 Create `MODULE_CONTRACTS.md`

These tasks were completed in the current repository history.

## Phase 1 — AI Development Infrastructure

- [ ] TASK-008 Create and review `TASK_BOARD.md`
- [ ] TASK-009 Define AI task assignment and handoff procedures
- [ ] TASK-010 Define usage tracking for free AI tools
- [ ] TASK-011 Define AI failure and recovery procedures
- [ ] TASK-012 Design a secret-safe project context builder
- [ ] TASK-013 Define local verification and testing commands
- [ ] TASK-014 Review development documentation for consistency

## Phase 2 — Technical Design

- [ ] TASK-015 Verify Python and dependency compatibility
- [ ] TASK-016 Finalize module boundaries and shared schemas
- [ ] TASK-017 Define provider adapter selection and fallback behaviour
- [ ] TASK-018 Define voice pipeline and error-handling design
- [ ] TASK-019 Define memory storage and retrieval design
- [ ] TASK-020 Define skill permissions and confirmation rules
- [ ] TASK-021 Review and approve the initial implementation plan

## Phase 3 — First Working Application Flow

- [ ] TASK-022 Set up the Python development environment
- [ ] TASK-023 Add minimal application entry point
- [ ] TASK-024 Add initial shared contracts and unit tests
- [ ] TASK-025 Implement a basic text interaction flow
- [ ] TASK-026 Connect a replaceable AI provider interface
- [ ] TASK-027 Verify the flow using tests and a real development run

## Phase 4 — Incremental Feature Development

- [ ] TASK-028 Implement persistent memory
- [ ] TASK-029 Implement the initial voice pipeline
- [ ] TASK-030 Implement the skill registry
- [ ] TASK-031 Add the web dashboard
- [ ] TASK-032 Add reminder and scheduling support
- [ ] TASK-033 Add ESP32 integration using a mock first
- [ ] TASK-034 Integrate and verify the first complete user flow

## Rules for Moving Tasks

1. Work on one active task at a time unless independent parallel work
   is explicitly planned and its file ownership is separated.
2. Read repository instructions and inspect actual code before starting.
3. Record blockers instead of silently skipping them.
4. Record relevant file changes and verification results.
5. Update task status when the actual state changes.
6. Do not mark a dependent task ready until its prerequisites pass.
7. Preserve uncommitted work and review the Git diff before committing.
8. Use small, reviewable commits at verified milestones.

## Current Next Task

TASK-008 — Verify this task board and commit it.

After TASK-008, continue with TASK-009.
Do not begin application feature implementation until the required
development infrastructure and technical design tasks are reviewed.
