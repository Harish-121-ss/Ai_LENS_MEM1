import os
import json
from agentlens.agent import SupportAgent
from agentlens.contracts.models import AgentConfig, ReplayRecord
from agentlens.identifiers import (
    NORMAL_ORDER_LOOKUP,
    TIMEOUT_RETRY_LOOP,
    WRONG_TOOL,
    FIXED_TIMEOUT_FALLBACK
)

def generate_fixtures():
    # Make sure fixtures directory exists
    fixtures_dir = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures")
    os.makedirs(fixtures_dir, exist_ok=True)
    
    scenarios = [
        {
            "id": NORMAL_ORDER_LOOKUP,
            "config": AgentConfig(
                agent_version="v1.0.0",
                prompt_version="p-2023-09-01",
                retry_limit=4,
                fallback_enabled=True
            ),
            "expected_behavior": "Executes get_order successfully and returns processing status.",
            "mocked_responses": {"get_order": {"status": "SUCCESS", "data": {"order_id": "8271", "status": "processing"}}}
        },
        {
            "id": TIMEOUT_RETRY_LOOP,
            "config": AgentConfig(
                agent_version="v1.0.0-fail-timeout",
                prompt_version="p-2023-09-01",
                retry_limit=3, # 1 + 3 retries = 4 calls minimum
                fallback_enabled=True
            ),
            "expected_behavior": "Repeatedly calls get_order due to timeout.",
            "mocked_responses": {"get_order": {"error": "TIMEOUT", "message": "Connection timed out"}}
        },
        {
            "id": WRONG_TOOL,
            "config": AgentConfig(
                agent_version="v1.0.0-fail-wrongtool",
                prompt_version="p-2023-09-01",
                retry_limit=2,
                fallback_enabled=True
            ),
            "expected_behavior": "Intentionally selects cancel_order instead of get_order.",
            "mocked_responses": {"cancel_order": {"status": "SUCCESS", "data": {"message": "Simulated cancellation"}}}
        },
        {
            "id": FIXED_TIMEOUT_FALLBACK,
            "config": AgentConfig(
                agent_version="v1.1.0-fix-timeout",
                prompt_version="p-2023-09-01",
                retry_limit=2,
                fallback_enabled=True
            ),
            "expected_behavior": "Calls get_order exactly retry_limit+1 times and invokes fallback.",
            "mocked_responses": {"get_order": {"error": "TIMEOUT", "message": "Connection timed out"}}
        }
    ]
    
    for scenario in scenarios:
        agent = SupportAgent(scenario["config"])
        request_text = "Where is order #8271?"
        response_text, run_record = agent.run(request_text)
        
        # Build ReplayRecord
        tool_calls_summary = [
            {"seq": ev.seq, "tool": ev.tool, "arguments": ev.arguments} 
            for ev in run_record.events
        ]
        
        replay_record = ReplayRecord(
            run_id=run_record.run_id,
            prompt=request_text,
            agent_version=scenario["config"].agent_version,
            prompt_version=scenario["config"].prompt_version,
            failure_mode=scenario["id"],
            tool_calls=tool_calls_summary,
            mocked_responses=scenario["mocked_responses"],
            expected_behavior=scenario["expected_behavior"],
            original_incident_id=f"INC-{scenario['id']}"
        )
        
        # Save to disk
        payload = {
            "run": run_record.model_dump(),
            "replay": replay_record.model_dump()
        }
        
        # Name explicit files for BEFORE/AFTER
        filename = f"{scenario['id']}.json"
        if scenario['id'] == TIMEOUT_RETRY_LOOP:
            filename = "BEFORE_TIMEOUT_RETRY_LOOP.json"
        elif scenario['id'] == FIXED_TIMEOUT_FALLBACK:
            filename = "AFTER_FIXED_TIMEOUT_FALLBACK.json"
            
        filepath = os.path.join(fixtures_dir, filename)
        with open(filepath, "w") as f:
            json.dump(payload, f, indent=2)

if __name__ == "__main__":
    generate_fixtures()
