import pytest
import os
import re
from pydantic import ValidationError
from agentlens.contracts.models import AgentToolEvent, Run, AgentConfig, ReplayRecord

# Reusable safe synthetic data
VALID_EVENT_DATA = {
    "seq": 1,
    "type": "tool_execution",
    "timestamp_ms": 1695034800000,
    "tool": "get_order",
    "arguments": {"order_id": "8271"},
    "status": "success",
    "result": {"status": "shipped"},
    "latency_ms": 150
}

VALID_RUN_DATA = {
    "run_id": "run-xyz-123",
    "agent_version": "v1.0.0",
    "prompt_version": "p-2023-09-01",
    "request": "Where is order #8271?",
    "events": [VALID_EVENT_DATA],
    "tool_calls": 1,
    "tokens": 150,
    "latency_ms": 200,
    "errors": [],
    "outcome": "success",
    "detected_failures": []
}

VALID_CONFIG_DATA = {
    "agent_version": "v1.0.0",
    "prompt_version": "p-2023-09-01",
    "retry_limit": 2,
    "fallback_enabled": True
}

VALID_REPLAY_DATA = {
    "run_id": "run-xyz-123",
    "prompt": "Where is order #8271?",
    "agent_version": "v1.0.0",
    "prompt_version": "p-2023-09-01",
    "failure_mode": "timeout",
    "tool_calls": [VALID_EVENT_DATA],
    "mocked_responses": {"get_order": "timeout_error"},
    "expected_behavior": "retry_loop",
    "original_incident_id": "inc-456"
}

def test_p1_t01_valid_run():
    """P1-T01 - Valid Run"""
    run = Run(**VALID_RUN_DATA)
    assert run.run_id == "run-xyz-123"

def test_p1_t02_missing_run_field():
    """P1-T02 - Missing Run Field"""
    invalid_data = VALID_RUN_DATA.copy()
    del invalid_data["outcome"]
    with pytest.raises(ValidationError):
        Run(**invalid_data)

def test_p1_t03_valid_agent_tool_event():
    """P1-T03 - Valid AgentToolEvent"""
    event = AgentToolEvent(**VALID_EVENT_DATA)
    assert event.seq == 1

def test_p1_t04_invalid_agent_tool_event():
    """P1-T04 - Invalid AgentToolEvent"""
    invalid_data = VALID_EVENT_DATA.copy()
    del invalid_data["latency_ms"]
    with pytest.raises(ValidationError):
        AgentToolEvent(**invalid_data)

def test_p1_t05_valid_agent_config():
    """P1-T05 - Valid AgentConfig"""
    config = AgentConfig(**VALID_CONFIG_DATA)
    assert config.retry_limit == 2

def test_p1_t06_retry_limit_validation():
    """P1-T06 - Retry Limit Validation"""
    invalid_data = VALID_CONFIG_DATA.copy()
    invalid_data["retry_limit"] = -1
    with pytest.raises(ValidationError):
        AgentConfig(**invalid_data)

def test_p1_t07_fallback_configuration():
    """P1-T07 - Fallback Configuration"""
    config = AgentConfig(**VALID_CONFIG_DATA)
    assert config.fallback_enabled is True

def test_p1_t08_agent_version():
    """P1-T08 - Agent Version"""
    config = AgentConfig(**VALID_CONFIG_DATA)
    assert hasattr(config, 'agent_version')
    assert config.agent_version == "v1.0.0"

def test_p1_t09_prompt_version():
    """P1-T09 - Prompt Version"""
    config = AgentConfig(**VALID_CONFIG_DATA)
    assert hasattr(config, 'prompt_version')
    assert config.prompt_version == "p-2023-09-01"

def test_p1_t10_valid_replay_record():
    """P1-T10 - Valid ReplayRecord"""
    replay = ReplayRecord(**VALID_REPLAY_DATA)
    assert replay.run_id == "run-xyz-123"

def test_p1_t11_invalid_replay_record():
    """P1-T11 - Invalid ReplayRecord"""
    invalid_data = VALID_REPLAY_DATA.copy()
    del invalid_data["failure_mode"]
    with pytest.raises(ValidationError):
        ReplayRecord(**invalid_data)

def test_p1_t12_secret_safety():
    """P1-T12 - Secret Safety"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    banned_words = [r"api[_-]?key", r"password\s*=", r"secret\s*="]
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py') and file != 'test_contracts.py':
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    for pattern in banned_words:
                        assert not re.search(pattern, content), f"Potential secret found in {file_path}"
