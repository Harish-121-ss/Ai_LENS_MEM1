# Stage 7 Architecture Audit

## Current Directory Structure
- `src/agentlens/`: Core Member 1 source code
  - `agent.py`: Contains the `SupportAgent` execution logic.
  - `contracts/models.py`: Shared Pydantic data models (`Run`, `AgentToolEvent`, `AgentConfig`, etc.).
  - `fixtures.py`: Logic for generating deterministic `ReplayRecord` test data.
  - `identifiers.py`: Identifiers for canonical scenarios.
  - `tools/`: Synthetic tools implementation.
- `tests/`: Existing Member 1 test suite (`test_contracts.py`, `test_p2_tools.py`, etc.).
- `fixtures/`: Generated JSON fixture data for scenarios.

## Ownership and Frozen State
- **Member 1 Owns**: Support agent execution, tool interaction, failure injection, bounded retries, generating execution evidence (Run record).
- **Frozen**: Stages 1-6 are frozen. The shared contracts in `src/agentlens/contracts/models.py` MUST NOT be modified.

## Public Interfaces
- **Current Entry Point**: The primary agent entry point is `agentlens.agent.SupportAgent.run()`. We will create a stable, clean public interface wrapper (`__init__.py` or `api.py`) exposing the entry point.

## Dependencies
- Does NOT own or import Member 2 (reliability intelligence/detectors).
- Relies on pure Python execution (no external network dependencies in deterministic mode).

## Existing Tests
- Contains comprehensive historical tests (`test_p2_tools.py`, `test_p3_agent.py`, `test_p4_scenarios.py`, `test_p5_compliance.py`, `test_p5_fix.py`, `test_p6_handoff.py`).

## Integration Boundaries
- Member 1 generates a `Run` object containing `AgentToolEvent`s which will be consumed by Member 2.

## Files that MUST NOT be modified
- `src/agentlens/contracts/models.py` (Frozen Shared Contracts)
- `src/agentlens/agent.py` core frozen behaviors
- Historical test files (`tests/test_p*.py`) must not be deleted or rewritten unnecessarily.
