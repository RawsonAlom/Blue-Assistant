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

---

## Module Contracts (consolidated)

Version: 0.1
Status: Proposed
Implementation Status: Not implemented

### 1. Purpose

This document defines the intended interfaces between BLUE modules.

Different AI coding agents may implement different modules, but they
must use the same approved contracts when integrating their work.

These contracts describe intended behaviour, not existing functionality.
No interface should be treated as implemented until source code and
tests verify it.

### 2. General Rules

1. Use Python type hints for public interfaces.
2. Use documented request and response structures.
3. Use async interfaces for operations that involve network or I/O
   when appropriate.
4. Keep vendor-specific formats inside integration adapters.
5. Do not pass raw microphone audio to the reasoning module.
6. Do not allow the reasoning module to execute tools directly.
7. Validate action names and arguments before execution.
8. Represent failures explicitly.
9. Do not silently change a public interface.
10. Update contract tests and documentation when an interface changes.

### 3. Shared Message Contracts

#### 3.1 UserMessage

Purpose:
Represent one normalized user request, independent of its input source.

Required fields:

- `text`: recognized or typed user text, as a string.
- `session_id`: identifier for the current conversation session.
- `source`: input source, initially `text` or `voice`.

Optional field:

- `metadata`: non-sensitive contextual information needed for handling
  the request. It must not contain credentials or unrestricted secrets.

Responsibilities:

- The input adapter produces a valid UserMessage.
- The coordinator validates the message.
- The reasoning module receives the normalized message.
- Raw audio and UI-specific objects remain outside this contract.

#### 3.2 ActionRequest

Purpose:
Represent a proposed operation that a registered skill may support.

Required fields:

- `name`: registered skill or action identifier.
- `arguments`: structured arguments validated against that action's schema.

Optional fields:

- `reason`: short explanation of why the action was proposed.
- `risk_level`: proposed risk classification, such as `low`, `medium`,
  or `high`.

Rules:

- An ActionRequest is a proposal, not proof of authorization.
- The caller must not trust the model's risk classification.
- The skill registry independently determines permissions and requirements.
- Unknown action names and invalid arguments must be rejected.
- High-risk or destructive operations require appropriate confirmation.

#### 3.3 AssistantResponse

Purpose:
Represent the result produced by the reasoning module.

Required fields:

- `text`: user-facing response text.

Optional field:

- `actions`: a list of proposed ActionRequest objects.

Rules:

- A response without actions is an ordinary conversational answer.
- Proposed actions must not execute automatically merely because
  they appear in an AssistantResponse.
- The coordinator handles validation, authorization, execution,
  result processing, and the final user-facing response.
- Provider-specific response objects must be normalized before
  reaching other modules.

#### 3.4 ActionResult

Purpose:
Represent the actual outcome of an action execution attempt.

Required fields:

- `action_name`: the action being reported.
- `status`: one of `success`, `failure`, `denied`, or `unknown`.
- `message`: a concise result or error explanation.

Optional field:

- `data`: structured, non-sensitive result details.

Rules:

- Only the execution layer reports the action outcome.
- A proposed action is not a successful action.
- If execution outcome cannot be verified, report `unknown`.
- Do not report success when execution failed or was not attempted.

### 4. Voice Module Contract

Module responsibility:
Handle speech input and speech output without implementing reasoning.

Expected operations:

- Capture or receive audio through an available input adapter.
- Transcribe audio into text.
- Return a normalized user request through the coordinator.
- Receive the final AssistantResponse.
- Convert its text to speech when voice output is enabled.
- Report recognition, playback, and device errors explicitly.

The voice module must not:
- Decide which unrestricted shell command to execute.
- Call hardware controls directly.
- Contain provider-specific reasoning logic.
- Modify Memory storage directly.

The voice module may use replaceable wake-word, speech recognition,
and text-to-speech implementations.

### 5. Core Brain Contract

Module responsibility:
Interpret the request and produce an answer or a structured action proposal.

Conceptual interface:

`respond(message, context) -> AssistantResponse`

Input:
- A validated UserMessage.
- Relevant conversation context.
- Relevant retrieved information supplied through approved interfaces.

Output:
- A valid AssistantResponse.

Rules:
- Do not execute tools directly.
- Do not access device pins or invoke unrestricted shell commands.
- Use provider-neutral internal interfaces.
- Distinguish known facts from assumptions.
- Request clarification when essential information is missing.
- Return proposed actions through the agreed structure.
- Handle model failures and malformed provider responses explicitly.

### 6. Coordinator Contract

Module responsibility:
Coordinate the end-to-end request lifecycle.

Expected responsibilities:

1. Accept and validate a UserMessage.
2. Load relevant conversation context.
3. Request relevant memory when appropriate.
4. Call the reasoning interface.
5. Validate proposed actions.
6. Obtain any required user confirmation.
7. Execute approved actions through the registered skill system.
8. Return verified results to the reasoning layer when needed.
9. Produce the final AssistantResponse.
10. Update relevant task and conversation records.

The coordinator must not treat model output as trusted executable code.

### 7. AI Provider Contract

Module responsibility:
Hide vendor-specific model APIs behind a replaceable interface.

Expected capabilities:

- Accept a normalized model request.
- Return a normalized model response.
- Support timeout and error handling.
- Report rate-limit or quota errors when the provider exposes them.
- Keep provider credentials outside source code.
- Permit configuration of the selected provider.

Provider-specific SDK objects must not leak into core business logic.

Access to a provider API must be configured independently of any
free web-chat subscription. Free chat access does not imply API access.

### 8. Memory Contract

Module responsibility:
Persist and retrieve approved information.

Expected operations:

- Store a supported memory record.
- Retrieve relevant memories for a query or session.
- Retrieve session history when required.
- Update or delete memory records when requested and authorized.

Rules:
- Keep short-term conversation context distinct from long-term memory.
- Do not save every utterance as a permanent user memory.
- Validate stored data.
- Avoid storing credentials or unnecessary sensitive data.
- Make memory retrieval optional where it is not required.
- Report storage or retrieval failures explicitly.

SQLite is the initial preferred storage candidate, pending implementation
and dependency review.

### 9. Skill Registry and Execution Contract

Module responsibility:
Expose a controlled set of supported actions.

Expected capabilities:

- Register supported actions.
- Describe each action's accepted arguments.
- Validate incoming ActionRequest objects.
- Determine authorization and confirmation requirements.
- Execute only registered, approved actions.
- Return an ActionResult.
- Apply timeouts and handle execution errors.

Rules:
- Never expose unrestricted arbitrary command execution to the model.
- Reject unknown actions.
- Reject invalid or unexpected arguments.
- Check authorization independently of model-generated text.
- Use mocks for testing skills that affect external systems.

### 10. Device Gateway Contract

Module responsibility:
Communicate with supported hardware through a controlled interface.

Expected capabilities:

- Identify registered devices.
- Send supported commands after authorization.
- Query device status when supported.
- Report connectivity and command failures.
- Return actual or clearly labelled estimated state.

The device gateway is the only application module that should handle
the device-specific communication protocol.

An ActionResult may be `success` only when the system has sufficient
evidence that the requested operation succeeded.

Real hardware integration must remain optional during unit tests.

### 11. Scheduler Contract

Module responsibility:
Manage persistent reminders and approved scheduled routines.

Expected capabilities:

- Create a supported scheduled task.
- List, update, or cancel a task.
- Execute eligible tasks at the configured time.
- Persist tasks across application restarts.
- Record execution status and failures.

Rules:
- Validate scheduling inputs.
- Define timezone handling explicitly during implementation.
- Avoid duplicate execution where feasible.
- Do not schedule sensitive external actions without appropriate approval.

### 12. Dashboard Contract

Module responsibility:
Present a user interface without owning core business logic.

Expected capabilities:

- Submit text requests.
- Present assistant responses.
- Present relevant action status.
- Show device state and task status where supported.
- Expose settings and permission controls.

The dashboard must use documented application interfaces.
It must not access internal database structures directly.

### 13. Error Handling

Modules must distinguish expected failures from successful results.

Relevant error categories include:

- Invalid input
- Unsupported operation
- Provider unavailable
- Provider rate limited
- Request timeout
- Memory access failure
- Permission denied
- Missing confirmation
- Device disconnected
- Action execution failure

Errors should be converted into useful internal results and safe,
understandable user-facing messages.

Sensitive details and credentials must not be exposed in error messages.

### 14. Contract Testing Requirements

Before integrating modules, tests should verify:

1. Valid messages can cross the interface.
2. Invalid inputs are rejected.
3. Provider responses are normalized.
4. Unknown actions cannot execute.
5. Confirmation requirements are enforced.
6. Tool failures do not become false success reports.
7. Voice output can consume a final response.
8. Modules can be tested with mocks instead of paid APIs or real hardware.

### 15. Change Control

A contract change must include:

- The reason for the change.
- The affected modules.
- Backward compatibility considerations.
- Updated interface documentation.
- Updated or new contract tests.
- The implementation tasks required from other modules.

Do not silently change public signatures or data fields.

### 16. Open Decisions

The following details remain open until the detailed design phase:

- Exact Python data types and class locations.
- Whether shared schemas use dataclasses or another appropriate method.
- Exact async method signatures.
- Provider timeout and retry policies.
- Persistent task schema.
- Device authentication and message format.
- Voice streaming and interruption interface.
- API versioning strategy.

Resolve these decisions before independently implementing
modules that depend on the relevant interface.
