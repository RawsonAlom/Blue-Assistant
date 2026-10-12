# BLUE — System Architecture

Version: 0.1
Status: Proposed
Architecture Style: Modular Monolith

## 1. Architectural Goal

BLUE is a modular personal AI assistant inspired by JARVIS.

The system must support multiple interfaces, replaceable AI providers,
persistent memory, registered skills, voice interaction, and future
smart-home integration.

The architecture must be understandable by different AI coding agents
working on separate modules.

Architecture documents describe intended design. Actual implementation
status must be verified against source code and tests.

## 2. Core Design Decisions

1. Start with one Python application and clearly separated modules.
2. Do not introduce microservices without a demonstrated need.
3. Keep business logic independent of specific AI providers.
4. Keep voice recognition and speech synthesis independent of reasoning.
5. Use explicit interfaces and structured data between modules.
6. Keep initial storage lightweight and local.
7. Make external integrations optional and replaceable.
8. Prefer deterministic code for predictable operations.
9. Never let an LLM execute arbitrary commands without validation
   and authorization.
10. Add features incrementally and test each integration boundary.

## 3. System Layers

### Layer A — User Interfaces

Responsibilities:
- Accept text input.
- Accept voice input through the voice pipeline.
- Present assistant responses and task status.
- Display device status and relevant history.
- Provide settings and permission controls.

Possible interfaces:
- Local web dashboard
- Voice interface
- Optional command-line interface for development

Interfaces must call application services instead of implementing
business logic themselves.

### Layer B — Application Coordinator

Responsibilities:
- Create and manage conversation sessions.
- Normalize incoming requests.
- Pass requests to the reasoning interface.
- Coordinate memory retrieval and response handling.
- Dispatch validated action requests through the skill registry.
- Track task state, errors, and completion results.

This layer coordinates modules; it must not contain all feature logic.

### Layer C — Core Intelligence

Responsibilities:
- Interpret user requests.
- Use relevant conversation context.
- Decide whether to answer or request a tool action.
- Plan multi-step tasks when needed.
- Select tools through the registered skill interface.
- Interpret tool results and produce a final response.

Core intelligence must depend on provider-neutral interfaces,
not directly on a particular vendor SDK.

The LLM proposes actions. Ordinary application code validates,
authorizes, and executes them.

### Layer D — AI Provider Adapters

Responsibilities:
- Provide a common interface for compatible model providers.
- Convert internal requests to provider-specific formats.
- Normalize responses and tool-call proposals.
- Handle timeouts, failures, and rate limits.
- Support provider selection through explicit configuration.

A provider adapter may use an API only when valid credentials and
the required access are available.

A free ChatGPT or Claude web-chat account does not automatically
provide API access to the running BLUE application.

Development AI tools and runtime AI providers are separate concerns.

### Layer E — Memory and Persistence

Responsibilities:
- Store conversation and task records where appropriate.
- Store user-approved long-term memories.
- Retrieve relevant notes and context.
- Store persistent reminders and scheduled tasks.
- Support inspecting, editing, and deleting stored memories.

Start with SQLite for structured persistent data.

Add semantic or vector search only when an actual requirement
justifies its complexity and resource cost.

Do not treat every conversation message as a permanent memory.

### Layer F — Skill Registry and Tool Execution

Responsibilities:
- Register available skills and their input schemas.
- Validate arguments before executing a skill.
- Enforce authorization and confirmation requirements.
- Apply timeouts and handle execution failures.
- Return structured results to the coordinator.
- Record relevant action history.

Example skill categories:
- Reminders and timers
- Files and document search
- Web research
- Supported desktop actions
- Smart-home controls
- Developer utilities

Skills must not expose unrestricted shell execution to the LLM.

### Layer G — Voice Pipeline

Responsibilities:
- Receive microphone audio.
- Detect a wake word when supported.
- Convert speech to text.
- pass recognized text to the application coordinator.
- Convert the final response to speech.
- Handle interruption, silence, and recognition errors.

Keep wake-word detection, speech recognition, and speech synthesis
as separate replaceable components.

Begin with a simple push-to-talk or explicit recording flow if this
makes the first implementation easier to test.

Continuous listening and interruption support can be added later.

### Layer H — Device Gateway

Responsibilities:
- Communicate with registered devices such as ESP32 boards.
- Validate supported device commands.
- Report known device state and connection status.
- Handle communication failure and timeouts.
- Authenticate device communication where supported.

The LLM must never directly control hardware pins.
All device actions must pass through validated skill interfaces
and the device gateway.

Use a mock device implementation before testing real hardware.

### Layer I — Scheduling and Notifications

Responsibilities:
- Store scheduled tasks persistently.
- Execute approved reminders and routines.
- Recover pending tasks after application restarts where possible.
- Report failures and missed executions accurately.

Start with simple scheduled jobs. Add a dedicated background worker
only when the actual workload requires it.

### Layer J — Observability and Safety

Responsibilities:
- Record application errors and meaningful lifecycle events.
- Track task identifiers, status, duration, and retry attempts.
- Track known AI provider availability and reported usage limits.
- Avoid recording secrets or unnecessary sensitive content.
- Require confirmation for sensitive or destructive operations.
- Distinguish proposed, running, successful, failed, and unknown actions.

Never report that a real-world operation succeeded without evidence
from the relevant integration.

## 4. Request Flow

The intended request flow is:

1. A user submits text or voice.
2. The interface converts it into a normalized user message.
3. The coordinator loads relevant session context.
4. The memory interface retrieves relevant information when needed.
5. The reasoning interface produces an answer or a structured action
   proposal.
6. The skill registry validates and authorizes any action.
7. The selected skill executes the action and returns a result.
8. The coordinator passes relevant results back to the reasoning layer.
9. The final response is returned to the interface.
10. Voice output is generated when requested.
11. Relevant status and history are persisted.

If an action requires confirmation, execution pauses until approval.

If a tool fails, the failure must be handled explicitly rather than
being presented as a successful operation.

## 5. Intended Module Boundaries

- `core/`: reasoning interfaces, planning, orchestration, routing
- `voice/`: wake word, speech recognition, speech synthesis, sessions
- `memory/`: database access, memory storage and retrieval
- `skills/`: registered actions and their validation
- `integrations/`: AI provider adapters and external services
- `devices/`: device registry, communication, and device state
- `web/`: dashboard and user-facing web assets
- `scheduler/`: persistent scheduling and task dispatch
- `contracts/`: shared message schemas and public interfaces
- `tests/`: unit, contract, integration, and safety tests
- `scripts/`: development, verification, and context utilities
- `docs/`: detailed technical documentation

These are intended boundaries. The final folder structure may be
adjusted after the interfaces and implementation plan are reviewed.

## 6. Module Communication Rules

1. Use documented function interfaces and structured data.
2. Avoid circular imports between modules.
3. Keep vendor-specific request formats inside provider adapters.
4. Keep UI components independent of storage internals.
5. Keep device protocols inside the device gateway.
6. Use typed data structures where practical.
7. Represent expected failures explicitly.
8. Do not change a shared interface silently.
9. Update related tests and documentation when a contract changes.
10. Prefer simple direct calls inside the initial application.
    Introduce queues or event buses only when justified.

## 7. Resource Constraints

The primary development computer has approximately:
- 10 GB RAM
- Intel Core i5, 2nd generation
- 128 GB SSD
- Ubuntu Linux

Design for modest hardware:
- Avoid mandatory large local language models.
- Avoid running unnecessary background services.
- Keep caches, models, logs, and dependencies under control.
- Use cloud-assisted reasoning where appropriate.
- Keep essential deterministic commands separate from cloud AI.
- Check dependency compatibility before installation.

## 8. Multi-AI Development Rules

Different AI assistants may develop or review different modules.

Before coding, every agent must:
- Read repository-wide instructions and project context.
- Inspect the actual code of relevant neighbouring modules.
- Check shared contracts, tests, Git state, and recent changes.
- Identify conflicts between proposed work and existing interfaces.
- Describe its scope and expected changes before major implementation.

Agents must not assume that another module is complete simply
because documentation describes it.

Independent changes must be reviewed and tested before integration.

## 9. Testing Strategy

Use separate levels of verification:

1. Unit tests for isolated functions and components.
2. Contract tests for module interfaces and data schemas.
3. Integration tests for communication between modules.
4. Safety tests for permissions and invalid actions.
5. Mock-based tests for external APIs and hardware.
6. End-to-end tests for complete user request flows.

Tests must not require real hardware or paid AI access by default.
External-service tests can be optional and clearly marked.

## 10. Architecture Decisions Still Open

The following decisions must be investigated before implementation:
- Supported Python version and dependency compatibility
- Web framework and local API design
- Shared contract schemas
- AI provider adapter interface
- Voice and audio dependency selection
- Wake-word engine
- Scheduler implementation
- Device communication protocol
- Memory schema and retrieval strategy
- Local testing and static analysis tools
- Secure configuration and permission model

Do not install dependencies or implement all planned modules merely
because they appear in this document.

## 11. Current Implementation Status

This document describes a proposed architecture only.

The application modules, provider adapters, voice pipeline, memory
system, dashboard, skills, and device gateway are not yet implemented.

Verify every future completion claim against actual source code
and test results.
