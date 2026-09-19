# Member 1 Integration Quickstart

This document provides Member 4 (Project Integration) with everything needed to consume the Member 1 (Agent Engineering) component of AgentLens.

## What Member 1 Provides
Member 1 provides a deterministic, synthetically-mocked customer support agent. It guarantees reproducible execution paths for normal operations, failures (timeout loops, wrong tool selection), and fixed fallback operations.

## Public Entry Point
The ONLY authorized public entry point is exposed via `agentlens`:

```python
from agentlens import SupportAgent, AgentConfig, Run, AgentToolEvent, ReplayRecord
```

## Required Inputs
To initialize the agent, you must provide an `AgentConfig`. To run a request, you must provide a string.

```python
config = AgentConfig(
    agent_version="v1.0.0",
    prompt_version="p-2023-09-01",
    retry_limit=3,
    fallback_enabled=True
)
agent = SupportAgent(config)
response_text, run_record = agent.run("Where is order #8271?")
```

## Expected Outputs
The `.run()` method returns a tuple:
1. `response_text` (str): The natural language response meant for the user.
2. `run_record` (Run): A structured Pydantic model containing the complete execution trace, which serves as the evidence payload for Member 2.

## How to Execute Scenarios

### 1. Normal Scenario
```python
config = AgentConfig(agent_version="v1.0.0", prompt_version="p1", retry_limit=3, fallback_enabled=True)
agent = SupportAgent(config)
response, run = agent.run("Where is order #8271?")
# Outcome: success
```

### 2. Timeout/Failure Scenario
```python
config = AgentConfig(agent_version="v1.0.0-fail-timeout", prompt_version="p1", retry_limit=3, fallback_enabled=True)
agent = SupportAgent(config)
response, run = agent.run("Where is order #8271?")
# Outcome: failure (contains retry loop)
```

### 3. Fixed Scenario
```python
config = AgentConfig(agent_version="v1.0.0-fix-timeout", prompt_version="p1", retry_limit=2, fallback_enabled=True)
agent = SupportAgent(config)
response, run = agent.run("Where is order #8271?")
# Outcome: failure (but bounded retries and graceful fallback message)
```

## How Output Connects to Shared Contracts
The `run_record` object returned by `agent.run()` is exactly the `agentlens.contracts.models.Run` contract required by Member 2. 
You can pass this `run_record` directly to Member 2's `agentlens.engine.orchestrator.run_reliability_pipeline(run_record)`.

## What NOT to Import
- Do NOT import internal implementation details like `agentlens.agent.SupportAgent` directly (use the top-level package).
- Do NOT import `agentlens.tools.*`
- Do NOT import `agentlens.fixtures`

## How to Run Member 1 Tests
We use pytest for unit and integration testing.

```bash
# From the member 1 repository root
pytest -q
```
