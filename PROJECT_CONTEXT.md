# BLUE / JARVIS — Project Context

## 1. Project Vision

BLUE is a modular personal AI assistant inspired by
Tony Stark's JARVIS.

The long-term goal is to build an assistant that can
communicate naturally, reason about tasks, remember
useful information, use approved tools, control compatible
devices, and report the actual results of its actions.

This is a long-term project. Build it incrementally.
Reliability is more important than the number of features.

## 2. Main Goals

- Voice interaction and natural conversations
- Bangla, Banglish, and English support
- A modular reasoning and task-planning system
- Short-term context and user-controlled long-term memory
- Extensible skills and external tool integrations
- Smart-home control using compatible ESP32 devices
- A web dashboard for interaction and status
- Task scheduling, notifications, and error reporting
- Automated tests, logs, and recoverable changes
- Optional offline functionality where practical

## 3. Development Environment

- Operating system: Ubuntu 26.04.1 LTS
- Processor: Intel Core i5, 2nd generation
- Installed RAM: approximately 10 GB
- Primary storage: 128 GB SSD
- Available disk space at initial inspection: approximately 62 GB
- Python detected: 3.14.4
- Git detected: 2.53.0
- VS Code detected: 1.141.0

Keep resource usage low. Check Python package compatibility
before selecting dependencies. Do not install large local
AI models unless there is a justified need.

## 4. Development Method

- VS Code is the main development environment.
- Git is the source-control system.
- Work in small, verifiable steps.
- Test a change before considering it complete.
- Preserve a recoverable checkpoint before risky changes.
- Do not begin dependent work while a required step is incomplete.
- Keep documentation synchronized with the implementation.
- Never claim that a command or test succeeded unless it was run
  and the result was checked.

## 5. Multi-AI Development

Different AI assistants may help with architecture, coding,
review, testing, documentation, and debugging.

Every AI working on this project must:

1. Read the relevant project documentation.
2. Inspect the current source code before proposing changes.
3. Understand relevant neighbouring modules and their interfaces.
4. Check the current Git state and existing work.
5. State assumptions and identify unresolved questions.
6. Stay within the assigned task and file scope.
7. Report files changed, tests run, actual results, and remaining work.
8. Update the handoff notes when a task is completed or interrupted.

This repository is the shared source of truth. Separate AI chat
conversations are not assumed to share memory or local files.

## 6. Free-Tier Usage Constraints

- Do not assume that any AI service provides unlimited usage.
- Do not hardcode a fixed message quota or assume a reset time.
- Record reported usage restrictions and reset information when
  it is available from the service.
- Prefer precise prompts, focused context, and local testing.
- Use deterministic local tools for formatting and tests where possible.
- Preserve progress before an AI task is interrupted.
- Never rely on bypassing service usage limits through automated
  account rotation.
- Distinguish free web-chat access from API access and IDE-agent access.
  These are not automatically interchangeable.
- Keep the project functional without requiring every AI service
  to be available at the same time.

## 7. Architecture Principles

- Separate voice, reasoning, memory, tools, hardware, and UI.
- Define interfaces before connecting independently developed modules.
- Use provider adapters so model providers can be changed where practical.
- Do not tightly couple core logic to one AI vendor.
- Validate tool arguments and handle failures explicitly.
- Keep secrets out of source control and generated context reports.
- Require appropriate approval for sensitive or destructive actions.
- Verify real-world actions before reporting success.

## 8. Current Project State

- Project directory: Blue Assistant Project
- Git repository initialized
- Main branch created
- Git identity configured locally for this repository
- Initial commit: 5884382
- Initial .gitignore committed
- Application modules have not yet been implemented.

## 9. Next Planning Tasks

Before implementing application features:

1. Define repository-wide AI instructions.
2. Design the architecture and module contracts.
3. Define Git-based collaboration and integration rules.
4. Design project status, task tracking, and AI handoff files.
5. Design a usage-aware workflow for free AI tools.
6. Establish local validation and testing commands.
7. Select compatible dependencies before installation.

Do not treat proposed architecture or future features as implemented.
Update this document when verified project facts change.
