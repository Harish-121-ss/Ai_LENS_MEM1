import uuid
import time
import re
from typing import Tuple, Dict, Any
from agentlens.contracts.models import Run, AgentConfig, AgentToolEvent
from agentlens.tools.api import get_order

class SupportAgent:
    def __init__(self, config: AgentConfig):
        self.config = config

    def run(self, request: str) -> Tuple[str, Run]:
        """
        Executes a customer support request deterministically.
        Returns the human-readable response and the Run execution record.
        """
        run_id = f"run-{uuid.uuid4().hex[:8]}"
        events = []
        errors = []
        tokens = 0
        outcome = "success"
        detected_failures = []
        response_text = ""
        
        # Simple intent detection: Order lookup
        order_match = re.search(r"order #?(\w+)", request, re.IGNORECASE)
        
        if order_match:
            order_id = order_match.group(1)
            intent = "READ"  # Intent classification
            
            # Simulated token usage for reasoning
            tokens += 25
            
            # Execute tool
            start_ms = int(time.time() * 1000)
            # Simulated latency (deterministic mock latency)
            tool_latency = 50
            
            # Call the tool
            tool_result = get_order(order_id)
            
            # Record Event
            event_status = tool_result.get("status", tool_result.get("error", "error"))
            event = AgentToolEvent(
                seq=1,
                type="tool_execution",
                timestamp_ms=start_ms,
                tool="get_order",
                arguments={"order_id": order_id},
                status=event_status,
                result=tool_result,
                latency_ms=tool_latency
            )
            events.append(event)
            tokens += 15 # response parsing tokens
            
            if tool_result.get("status") == "SUCCESS":
                order_data = tool_result["data"]
                status = order_data.get("status", "unknown")
                response_text = f"Order {order_id} is {status}."
            else:
                error_type = tool_result.get("error", "UNKNOWN")
                if error_type == "NOT_FOUND":
                    response_text = f"I'm sorry, I couldn't find order {order_id}."
                else:
                    response_text = "I encountered an error looking up your order."
                    errors.append(error_type)
                    outcome = "failure"
        else:
            # Fallback for unrecognizable request
            response_text = "I'm sorry, I can only help with order lookups right now."
            tokens += 10
            
        total_latency_ms = 120 # deterministic total agent latency
        
        # Build Run
        run_record = Run(
            run_id=run_id,
            agent_version=self.config.agent_version,
            prompt_version=self.config.prompt_version,
            request=request,
            events=events,
            tool_calls=len(events),
            tokens=tokens,
            latency_ms=total_latency_ms,
            errors=errors,
            outcome=outcome,
            detected_failures=detected_failures
        )
        
        return response_text, run_record
