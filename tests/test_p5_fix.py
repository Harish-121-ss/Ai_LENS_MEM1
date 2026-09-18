import pytest
from agentlens.contracts.models import AgentConfig, Run
from agentlens.agent import SupportAgent

@pytest.fixture
def fix_config():
    return AgentConfig(
        agent_version="v1.1.0-fix-timeout",
        prompt_version="p-2023-09-01",
        retry_limit=2, # Initial call + 2 retries = 3 calls total
        fallback_enabled=True
    )

@pytest.fixture
def fix_config_no_fallback():
    return AgentConfig(
        agent_version="v1.1.0-fix-timeout",
        prompt_version="p-2023-09-01",
        retry_limit=1,
        fallback_enabled=False
    )

def test_p5_graceful_retry_limit(fix_config):
    """Test that the fix bounds retries exactly to retry_limit + 1."""
    agent = SupportAgent(fix_config)
    r, run = agent.run("Where is order #8271?")
    
    # retry_limit is 2, meaning 1 initial attempt + 2 retries = 3 total tool calls.
    assert run.tool_calls == 3
    assert len(run.events) == 3
    
    for event in run.events:
        assert event.tool == "get_order"
        assert event.status == "TIMEOUT"

def test_p5_fallback_response(fix_config):
    """Test that the agent provides a graceful fallback response."""
    agent = SupportAgent(fix_config)
    r, run = agent.run("Where is order #8271?")
    
    assert "systems are currently unavailable" in r
    assert run.outcome == "failure"

def test_p5_no_fallback_response(fix_config_no_fallback):
    """Test response when fallback is disabled."""
    agent = SupportAgent(fix_config_no_fallback)
    r, run = agent.run("Where is order #8271?")
    
    assert "couldn't reach the order system" in r
    assert run.outcome == "failure"

def test_p5_run_schema_compliance(fix_config):
    """Test that the fixed execution produces a valid Run object."""
    agent = SupportAgent(fix_config)
    r, run = agent.run("Where is order #8271?")
    
    assert isinstance(run, Run)
    assert run.agent_version == "v1.1.0-fix-timeout"
    assert run.run_id is not None
