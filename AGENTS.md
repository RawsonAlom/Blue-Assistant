# BLUE — Repository-Wide AI Instructions

These instructions apply to every AI coding agent working in this repository.

## 1. Read Before Acting

Before starting a task, read:

- `PROJECT_CONTEXT.md`
- `AGENTS.md`
- `PROJECT_STATUS.md`, if it exists
- `ARCHITECTURE.md`, if it exists
- `MODULE_CONTRACTS.md`, if it exists
- `TASK_BOARD.md`, if it exists
- Relevant module documentation and tests

Do not assume that files listed in future plans already exist.

## 2. Inspect the Actual Project State

Before editing:

1. Check the current working directory and Git branch.
2. Run `git status` and inspect uncommitted changes.
3. Inspect the repository structure.
4. Read the source code of the assigned module.
5. Read the interfaces, tests, and implementations of related modules.
6. Inspect relevant recent commits when necessary.
7. Identify dependencies, incomplete work, and integration risks.

Documentation is a guide, not proof that code works.
When documentation conflicts with verified source code or test results,
report the disagreement rather than silently guessing.

Never overwrite, discard, or revert another person's uncommitted changes.

## 3. Understand the Whole System

An agent owns its assigned task, but must understand the modules
that interact with that task.

Before implementation, provide a brief discovery report containing:

- Current project state
- Assigned task and boundaries
- Relevant modules and dependencies
- Existing interfaces and data structures
- Related tests and known failures
- Proposed files to create or modify
- Risks and unresolved questions

If a required interface is missing or contradictory, propose a solution
before making a breaking change.

## 4. Scope and Change Management

- Work only on the assigned task.
- Avoid unrelated refactoring.
- Prefer small, reviewable changes.
- Keep existing public interfaces stable unless a change is approved.
- Explain new dependencies and why they are necessary.
- Do not create duplicate implementations of existing features.
- Do not mark a task complete while required work remains.
- Do not automatically commit or push unless explicitly requested.

## 5. Git Safety

- Inspect Git status before editing.
- Preserve unrelated changes.
- Use a dedicated branch or worktree for independent, conflicting tasks.
- Review the diff before accepting changes.
- Run appropriate checks before a change is considered complete.
- Never use destructive Git commands without explicit authorization.
- Report the commit identifier when a verified checkpoint is created.

## 6. Tests and Honest Reporting

- Add or update tests for meaningful code changes.
- Prefer local, deterministic tests where possible.
- Run relevant checks when the environment supports them.
- Report the exact checks executed and their actual results.
- Clearly identify tests that could not be run.
- Never claim that unexecuted tests passed.
- Record known failures and reproduction steps.

## 7. Free AI Usage Management

- Assume that AI tools have finite and potentially changing usage limits.
- Do not assume a fixed quota or invent a reset time.
- Record reported restrictions and reset information when available.
- Use focused task descriptions and provide only relevant context.
- Prefer local search, formatting, linting, and tests for deterministic work.
- Save progress and prepare a handoff before ending a substantial task.
- Do not automate account rotation to bypass a service's usage limits.
- Do not assume that a chat subscription includes API or IDE-agent access.
- Preserve enough project information to resume without the previous chat.

## 8. Security

- Never put credentials, access tokens, or API keys in source code.
- Never include `.env` contents in context reports or AI prompts.
- Validate tool arguments and handle external-service errors.
- Require appropriate confirmation for destructive or sensitive actions.
- Use least-privilege access where practical.
- Never claim a real-world action succeeded without verifying its result.

## 9. Context Handoff

When finishing or pausing a task, provide:

- Task and implementation status
- Files created or modified
- Important design decisions
- Interfaces added or changed
- Commands and tests executed
- Actual test results
- Remaining issues and blockers
- Exact next step
- Relevant Git branch and commit, if applicable

Update project status and task documentation when those files exist
and the verified project state changes.

## 10. Definition of Done

A task is complete only when:

1. The requested scope is implemented.
2. Related interfaces remain compatible or approved changes are documented.
3. Appropriate tests or checks have been executed.
4. Actual results and limitations have been reported.
5. Relevant documentation and handoff information are updated.
6. The user can review the changes before they are accepted.

Do not begin dependent tasks until required prerequisites are verified.
