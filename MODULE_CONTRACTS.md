# BLUE — Module Contracts

Version: 0.1
Status: Proposed
Implementation Status: Not implemented

## 1. Purpose

This document defines the intended interfaces between BLUE modules.

Different AI coding agents may implement different modules, but they
must use the same approved contracts when integrating their work.

These contracts describe intended behaviour, not existing functionality.
No interface should be treated as implemented until source code and
tests verify it.

## 2. General Rules

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

## 3. Shared Message Contracts

### 3.1 UserMessage

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

### 3.2 ActionRequest

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

### 3.3 AssistantResponse

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

### 3.4 ActionResult

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

## 4. Voice Module Contract

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

## 5. Core Brain Contract

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

## 6. Coordinator Contract

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

## 7. AI Provider Contract

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

## 8. Memory Contract

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

## 9. Skill Registry and Execution Contract

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

## 10. Device Gateway Contract

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

## 11. Scheduler Contract

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

## 12. Dashboard Contract

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

## 13. Error Handling

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

## 14. Contract Testing Requirements

Before integrating modules, tests should verify:

1. Valid messages can cross the interface.
2. Invalid inputs are rejected.
3. Provider responses are normalized.
4. Unknown actions cannot execute.
5. Confirmation requirements are enforced.
6. Tool failures do not become false success reports.
7. Voice output can consume a final response.
8. Modules can be tested with mocks instead of paid APIs or real hardware.

## 15. Change Control

A contract change must include:

- The reason for the change.
- The affected modules.
- Backward compatibility considerations.
- Updated interface documentation.
- Updated or new contract tests.
- The implementation tasks required from other modules.

Do not silently change public signatures or data fields.

## 16. Open Decisions

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
