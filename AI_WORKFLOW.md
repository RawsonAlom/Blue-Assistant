# BLUE — AI Development Workflow

This document consolidates AI usage, task assignment, handoff, and failure recovery procedures.

Read this file together with AGENTS.md and the relevant project context, architecture, and status.

---

## Usage Budget and Free-Tier Rules

### Purpose
Track free AI tool availability without depending on fixed quotas
or bypassing service restrictions.

### Rules
- Check each tool's own usage indicator before substantial work.
- Record limits and reset information only when actually reported.
- Never invent a quota, remaining message count, or reset time.
- Do not automate account rotation to bypass usage limits.
- Chat subscriptions, API access, and IDE-agent access are different.
- Prefer local tests and deterministic tools when AI is unnecessary.
- Keep enough time and usage capacity for integration and debugging.

### Usage Ledger

| Date | Tool | Task | Observed Status | Reset Information | Notes |
|---|---|---|---|---|---|
| | | | | | |

Possible statuses: Available, Limited, Exhausted, Unknown.

Do not store passwords, authentication tokens, or private account data.

### Before a Large Task
1. Check current tool availability.
2. Estimate the task scope.
3. Split large work into reviewable subtasks.
4. Prepare the necessary context before sending the request.
5. Save progress at meaningful milestones.
6. Reserve independent review for high-risk changes.

### When a Limit Is Reached
- Save all local changes and record the task status.
- Do not repeatedly retry a blocked request.
- Continue local checks that do not require the unavailable AI.
- Resume when service access is available, or use another
  permitted tool with the same project context.

---

## Task Assignment Template

### Task
[Task ID and title]

### Goal
[Describe one specific outcome.]

### Required Context
Read:
- PROJECT_CONTEXT.md
- AGENTS.md
- PROJECT_STATUS.md
- ARCHITECTURE.md
- MODULE_CONTRACTS.md
- TASK_BOARD.md
- Relevant source files, tests, and module documentation

Check which files actually exist before reading them.

### Current State
[Describe verified behaviour, related changes, and known problems.]

### Scope
Allowed files:
- [File or directory]

Do not change unrelated modules without approval.

### Requirements
1. Inspect actual code before proposing changes.
2. Follow current module contracts.
3. Reuse existing utilities when appropriate.
4. Report contradictions between documentation and implementation.
5. Do not invent APIs or claim unverified behaviour works.
6. Keep secrets out of code, prompts, logs, and context reports.
7. Add or update relevant tests.
8. Do not discard another contributor's changes.

### Acceptance Criteria
- [ ] Requested behaviour implemented
- [ ] Relevant interfaces preserved or approved for change
- [ ] Relevant tests executed
- [ ] Actual test results reported
- [ ] Documentation updated where needed
- [ ] Remaining issues documented

### Final Report
Provide:
- Summary
- Files changed
- Dependencies changed
- Tests and actual results
- Known issues
- Contract changes, if any
- Git branch and commit, if applicable
- Recommended next step

---

## AI Handoff Record

Purpose: Let another AI resume work without depending on the
previous AI conversation.

### Current Handoff

- Task ID:
- Task status: Not started / In progress / Blocked / Review / Done
- Last updated:
- Git branch:
- Last verified commit:
- Current working-tree status:

### Completed and Verified
- [Record actual completed work and evidence.]

### Work in Progress
- [Record unfinished implementation.]

### Files Created or Modified
- [List paths and why they changed.]

### Current Interfaces
- [Record relevant public functions, schemas, and contracts.]

### Validation
- Commands executed:
- Results:
- Tests not run:
- Known failures:

### Decisions and Assumptions
- [Record decisions and their rationale.]
- [Clearly label assumptions that are not verified.]

### Blockers
- [Describe each blocker and the information needed to resolve it.]

### Exact Next Action
[One specific, actionable next step.]

### Handoff Rules
1. Read the current repository state before relying on this note.
2. Check uncommitted changes and preserve them.
3. Treat source code and test results as evidence.
4. Update this record when work is paused or materially changes.
5. Never copy secrets into the handoff.
6. Do not mark a task complete merely because a previous AI said so.

---

## Failure and Recovery

### 1. Usage Limit Reached
1. Stop repeated attempts to use the blocked service.
2. Preserve local files and inspect Git status.
3. Record the observed limitation and any reported reset information.
4. Update AI_HANDOFF.md.
5. Continue local tests or unrelated deterministic tasks.
6. Resume using an available, permitted tool when practical.

### 2. AI Produces Incorrect or Incomplete Code
1. Do not accept the result automatically.
2. Inspect the diff.
3. Run focused tests and static checks where available.
4. Record the exact error and reproduction steps.
5. Ask for a targeted correction rather than rewriting the project.
6. Keep the change unmerged until it passes the agreed checks.

### 3. Two AI Changes Conflict
1. Stop editing the conflicting files.
2. Preserve each agent's changes on its own branch or worktree.
3. Compare the diffs and shared interfaces.
4. Choose a compatible design and document the decision.
5. Integrate one change at a time.
6. Run contract and integration tests.

Never resolve conflicts by blindly overwriting another change.

### 4. Documentation Conflicts With Source Code
1. Inspect the implementation and related tests.
2. Identify which statements are outdated or unverified.
3. Record the discrepancy.
4. Update documentation only after verifying the intended behaviour.
5. Do not silently change a public contract.

### 5. Dependency or Python Compatibility Failure
1. Preserve the current environment.
2. Capture the exact error and package versions.
3. Check package support for the selected Python version.
4. Prefer an isolated virtual environment.
5. Test a compatible alternative before changing project-wide settings.
6. Avoid unnecessary system-wide installations.

### 6. Internet or Provider Unavailable
1. Distinguish a local failure from a provider failure.
2. Preserve pending work.
3. Run offline checks that remain meaningful.
4. Use mocks for external APIs and hardware during tests.
5. Do not report an external action as successful without evidence.

### 7. Accidental File Loss or Dangerous Git State
1. Stop destructive operations.
2. Inspect `git status` and recent commits.
3. Preserve uncommitted files before attempting recovery.
4. Review recovery commands before executing them.
5. Never run reset, clean, or force-push commands without understanding
   their consequences and obtaining appropriate authorization.

### 8. Security Incident
1. Stop exposing the affected credential.
2. Remove the secret from active files and prevent further disclosure.
3. Revoke or rotate the affected credential through its provider.
4. Check repository history if the secret was committed.
5. Do not claim a secret is fully removed from history without verifying
   the cleanup process.

### Recovery Completion Criteria
A failure is resolved only when:
- The cause or current limitation is documented.
- Local changes are preserved.
- Relevant checks have been executed.
- Remaining risks are stated.
- The handoff record identifies the next action.
