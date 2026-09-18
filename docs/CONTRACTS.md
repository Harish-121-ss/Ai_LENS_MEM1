# AgentLens Member 1 - Shared Contracts

This document defines the canonical Phase 1 shared data contracts for the AgentLens AI reliability engineering layer.

## Overview
These schemas represent the execution evidence, agent configuration, and replay data needed to evaluate AI reliability. They are strictly validated using Pydantic.

## Schemas

### 1. `Run`
Represents a single execution of the AI support agent.
- `run_id` (str): Unique identifier for the run.
- `agent_version` (str): The version of the agent code used.
- `prompt_version` (str): The version of the prompt instructions used.
- `request` (str): The user input or trigger.
- `events` (List[AgentToolEvent]): Sequential list of tool events that occurred.
- `tool_calls` (int): Total number of tool calls made.
- `tokens` (int): Total tokens consumed (if applicable).
- `latency_ms` (int): Total execution latency.
- `errors` (List[str]): Any top-level execution errors.
- `outcome` (str): Final outcome status (e.g., success, failure).
- `detected_failures` (List[str]): Failures identified during the run.

### 2. `AgentToolEvent`
Represents a single tool invocation within a Run.
- `seq` (int): Sequence order of the event.
- `type` (str): Event type classification.
- `timestamp_ms` (int): When the event occurred.
- `tool` (str): Name of the tool invoked.
- `arguments` (Dict[str, Any]): The arguments passed to the tool.
- `status` (str): Execution status of the tool (e.g., success, error).
- `result` (Any): The output returned by the tool.
- `latency_ms` (int): Tool execution duration.

### 3. `AgentConfig`
Controls the behavior and versioning of the agent.
- `agent_version` (str): The version of the agent.
- `prompt_version` (str): The version of the prompt.
- `retry_limit` (int): Maximum number of allowed retries (must be >= 0).
- `fallback_enabled` (bool): Whether fallback behavior is active.

### 4. `ReplayRecord`
Stores all necessary context to reproduce a specific scenario deterministically.
- `run_id` (str): ID of the original run.
- `prompt` (str): The original prompt/request used.
- `agent_version` (str): The exact agent version required.
- `prompt_version` (str): The exact prompt version required.
- `failure_mode` (str): The type of failure being replayed (e.g., timeout, wrong_tool).
- `tool_calls` (List[Dict[str, Any]]): The tool sequence expected.
- `mocked_responses` (Dict[str, Any]): Responses to substitute for external dependencies.
- `expected_behavior` (str): The behavior expected to occur during replay.
- `original_incident_id` (str): Link back to the incident being reproduced.

## Versioning Strategy
`agent_version` and `prompt_version` must be provided on every `Run`, `AgentConfig`, and `ReplayRecord`. This guarantees traceability. During testing, explicit string literals (e.g., "v1.0.0") are used.

## Validation
Validation is enforced via Pydantic on instantiation. 
- Required fields cannot be omitted.
- `retry_limit` in `AgentConfig` cannot be negative.
- Types are strictly checked.

## Consumption Instructions
### For Member 2 (Detectors / Observability)
Consume `Run` and `AgentToolEvent` payloads. Rely on `seq`, `tool`, and `status` to construct the canonical event timeline for failure detection. Do not expect runtime failure logic in these payloads—they only contain execution *evidence*.

### For Member 3 (Chaos / Replay)
Consume `ReplayRecord` to reconstruct controlled environments. Substitute external tool calls using the `mocked_responses` mapping. Replay execution should compare actual tool event sequences against the `tool_calls` list in the record.

### For Member 4 (UI / Platform)
Consume the `Run` schema. Expose `events` on the frontend trace viewer. Use `agent_version` and `prompt_version` to label before/after comparison dashboards.

---

# Phase 2: Support Tools

The four support tools below rely entirely on synthetic data and deterministic behavior. They act as the controlled interface for the AI agent to operate against.

## 1. get_order
- **Name**: `get_order`
- **Purpose**: Retrieve synthetic order information by its ID.
- **Category**: `READ`
- **Input**: `{ "order_id": "string" }`
- **Output**: Structured dictionary containing order details (e.g., items, total, status, customer_id).
- **Errors**: `VALIDATION_FAILED` (bad input), `NOT_FOUND` (unknown order).
- **Deterministic Behavior**: Identical ID always yields the exact same synthetic order.
- **Synthetic-Data Assumptions**: Assumes the existence of canonical order `#8271`. Does not hit a real DB.

## 2. get_customer
- **Name**: `get_customer`
- **Purpose**: Retrieve synthetic customer information by customer ID.
- **Category**: `READ`
- **Input**: `{ "customer_id": "string" }`
- **Output**: Structured dictionary containing customer details (e.g., name, email).
- **Errors**: `VALIDATION_FAILED`, `NOT_FOUND`.
- **Deterministic Behavior**: Yields the same customer for the same ID.
- **Synthetic-Data Assumptions**: Safe data only (e.g., "Jane Doe").

## 3. get_order_history
- **Name**: `get_order_history`
- **Purpose**: Retrieve a list of past orders for a specific customer.
- **Category**: `READ`
- **Input**: `{ "customer_id": "string" }`
- **Output**: Structured dictionary mapping the customer ID to a list of past order IDs.
- **Errors**: `VALIDATION_FAILED`, `NOT_FOUND`.
- **Deterministic Behavior**: Does not generate random history; returns a static predefined list.
- **Synthetic-Data Assumptions**: Exists only for the predefined synthetic customer.

## 4. cancel_order
- **Name**: `cancel_order`
- **Purpose**: Represent a controlled order cancellation action.
- **Category**: `WRITE/ACTION`
- **Input**: `{ "order_id": "string" }`
- **Output**: Success dictionary confirming cancellation.
- **Errors**: `VALIDATION_FAILED`, `NOT_FOUND`, `NOT_CANCELLABLE` (if the order is already shipped).
- **Deterministic Behavior**: Purely simulates success/failure deterministically based on static data rules without actual state mutation.
- **Synthetic-Data Assumptions**: Safe isolation; cannot trigger any external side effects or real cancellations.
