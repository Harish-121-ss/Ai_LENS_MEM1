import pytest
from agentlens.contracts.models import AgentConfig, Run
from agentlens.agent import SupportAgent

@pytest.fixture
def fix_config():
    return AgentConfig(
        agent_version="v1.1.0-fix-timeout",
        prompt_version="p-2023-09-01",
        retry_limit=2,
        fallback_enabled=True
    )

def test_p5_t01_fixed_configuration_exists(fix_config):
    """P5-T01: Fixed configuration exists."""
    assert fix_config is not None

def test_p5_t02_explicitly_uses_retry_limit_2(fix_config):
    """P5-T02: Fixed configuration explicitly uses retry_limit = 2."""
    assert fix_config.retry_limit == 2

def test_p5_t03_explicitly_enables_fallback(fix_config):
    """P5-T03: Fixed configuration explicitly enables fallback."""
    assert fix_config.fallback_enabled is True

def test_p5_t04_controlled_timeout_executes_via_fixed_config(fix_config):
    """P5-T04: The same controlled timeout scenario can execute using the fixed config."""
    agent = SupportAgent(fix_config)
    r, run = agent.run("Where is order #8271?")
    assert run.tool_calls > 0

def test_p5_t05_get_order_timeout_represented_correctly(fix_config):
    """P5-T05: get_order TIMEOUT is represented correctly."""
    agent = SupportAgent(fix_config)
    r, run = agent.run("Where is order #8271?")
    assert run.events[0].tool == "get_order"
    assert run.events[0].status == "TIMEOUT"

def test_p5_t06_performs_no_more_than_2_retries(fix_config):
    """P5-T06: The fixed configuration performs no more than 2 retries."""
    agent = SupportAgent(fix_config)
    r, run = agent.run("Where is order #8271?")
    # 1 initial + 2 retries = 3 tool calls max
    assert run.tool_calls == 3

def test_p5_t07_total_tool_attempts_remain_bounded(fix_config):
    """P5-T07: Total tool attempts remain bounded."""
    agent = SupportAgent(fix_config)
    r, run = agent.run("Where is order #8271?")
    assert run.tool_calls == fix_config.retry_limit + 1

def test_p5_t08_cannot_enter_infinite_loop(fix_config):
    """P5-T08: Fixed execution cannot enter an infinite loop."""
    agent = SupportAgent(fix_config)
    r, run = agent.run("Where is order #8271?")
    assert len(run.events) <= 10 # strict absolute bound

def test_p5_t09_fallback_invoked_after_retry_exhaustion(fix_config):
    """P5-T09: Fallback is invoked after retry exhaustion."""
    agent = SupportAgent(fix_config)
    r, run = agent.run("Where is order #8271?")
    assert "systems are currently unavailable" in r
    assert run.outcome == "failure"

def test_p5_t10_fallback_produces_useful_deterministic_response(fix_config):
    """P5-T10: Fallback produces a useful deterministic response."""
    agent = SupportAgent(fix_config)
    r, run = agent.run("Where is order #8271?")
    assert r == "I'm sorry, our systems are currently unavailable. Please try again later."

def test_p5_t11_execution_produces_valid_run(fix_config):
    """P5-T11: Fixed execution produces a valid Run."""
    agent = SupportAgent(fix_config)
    r, run = agent.run("Where is order #8271?")
    assert isinstance(run, Run)

def test_p5_t12_all_generated_tool_events_are_valid(fix_config):
    """P5-T12: All generated tool events are valid AgentToolEvents."""
    agent = SupportAgent(fix_config)
    r, run = agent.run("Where is order #8271?")
    from agentlens.contracts.models import AgentToolEvent
    for event in run.events:
        assert isinstance(event, AgentToolEvent)

def test_p5_t13_agent_version_identifies_fixed_configuration(fix_config):
    """P5-T13: agent_version identifies the fixed configuration."""
    agent = SupportAgent(fix_config)
    r, run = agent.run("Where is order #8271?")
    assert run.agent_version == "v1.1.0-fix-timeout"

def test_p5_t14_prompt_version_identifies_fixed_configuration(fix_config):
    """P5-T14: prompt_version identifies the fixed configuration."""
    agent = SupportAgent(fix_config)
    r, run = agent.run("Where is order #8271?")
    assert run.prompt_version == "p-2023-09-01"

def test_p5_t15_reproducible_behavior(fix_config):
    """P5-T15: Repeated identical executions produce reproducible behavior."""
    agent = SupportAgent(fix_config)
    r1, run1 = agent.run("Where is order #8271?")
    r2, run2 = agent.run("Where is order #8271?")
    assert r1 == r2
    assert run1.tool_calls == run2.tool_calls
    assert run1.outcome == run2.outcome
