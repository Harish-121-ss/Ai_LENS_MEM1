from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AgentToolEvent(BaseModel):
    seq: int
    type: str
    timestamp_ms: int
    tool: str
    arguments: Dict[str, Any]
    status: str
    result: Any
    latency_ms: int

class Run(BaseModel):
    run_id: str
    agent_version: str
    prompt_version: str
    request: str
    events: List[AgentToolEvent]
    tool_calls: int
    tokens: int
    latency_ms: int
    errors: List[str]
    outcome: str
    detected_failures: List[str]

class AgentConfig(BaseModel):
    agent_version: str
    prompt_version: str
    retry_limit: int = Field(ge=0)
    fallback_enabled: bool

class ReplayRecord(BaseModel):
    run_id: str
    prompt: str
    agent_version: str
    prompt_version: str
    failure_mode: str
    tool_calls: List[Dict[str, Any]]
    mocked_responses: Dict[str, Any]
    expected_behavior: str
    original_incident_id: str
