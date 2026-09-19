import pytest
from agentlens import SupportAgent, AgentConfig, Run

def test_public_entry_point():
    config = AgentConfig(
        agent_version="v1.0",
        prompt_version="p1",
        retry_limit=3,
        fallback_enabled=True
    )
    agent = SupportAgent(config)
    assert agent is not None

def test_deterministic_normal_execution():
    config = AgentConfig(agent_version="v1.0", prompt_version="p1", retry_limit=3, fallback_enabled=True)
    agent = SupportAgent(config)
    response, run = agent.run("Where is order #8271?")
    assert run.outcome == "success"
    assert len(run.events) == 1
    assert run.events[0].tool == "get_order"

def test_deterministic_failure_execution():
    config = AgentConfig(agent_version="v1.0-fail-timeout", prompt_version="p1", retry_limit=3, fallback_enabled=True)
    agent = SupportAgent(config)
    response, run = agent.run("Where is order #8271?")
    assert run.outcome == "failure"
    assert len(run.events) == 4 # 1 initial + 3 retries = 4

def test_bounded_retry_behavior():
    config = AgentConfig(agent_version="v1.0-fail-timeout", prompt_version="p1", retry_limit=1, fallback_enabled=True)
    agent = SupportAgent(config)
    response, run = agent.run("Where is order #8271?")
    assert run.outcome == "failure"
    assert len(run.events) == 2 # 1 initial + 1 retry

def test_fallback_behavior():
    config = AgentConfig(agent_version="v1.0-fix-timeout", prompt_version="p1", retry_limit=1, fallback_enabled=True)
    agent = SupportAgent(config)
    response, run = agent.run("Where is order #8271?")
    assert "our systems are currently unavailable" in response.lower()
    assert run.outcome == "failure"
    assert len(run.events) == 2

def test_malformed_input_handling():
    config = AgentConfig(agent_version="v1.0", prompt_version="p1", retry_limit=3, fallback_enabled=True)
    agent = SupportAgent(config)
    response, run = agent.run("Hello there!")
    assert run.tool_calls == 0
    assert "only help with order lookups" in response.lower()

def test_local_offline_operation():
    config = AgentConfig(agent_version="v1.0", prompt_version="p1", retry_limit=3, fallback_enabled=True)
    agent = SupportAgent(config)
    response, run = agent.run("Where is order #8271?")
    assert "success" == run.outcome
