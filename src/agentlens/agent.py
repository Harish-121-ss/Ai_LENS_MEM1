import uuid
import time
import re
from typing import Tuple, Dict, Any
from agentlens.contracts.models import Run, AgentConfig, AgentToolEvent
from agentlens.tools.api import get_order, cancel_order

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
            tokens += 25
            
            # --- FAILING SCENARIO B: WRONG TOOL ---
            if self.config.agent_version.endswith("-fail-wrongtool"):
                start_ms = int(time.time() * 1000)
                tool_latency = 50
                tool_result = cancel_order(order_id)
                
                event_status = tool_result.get("status", tool_result.get("error", "error"))
                event = AgentToolEvent(
                    seq=1,
                    type="tool_execution",
                    timestamp_ms=start_ms,
                    tool="cancel_order",
                    arguments={"order_id": order_id},
                    status=event_status,
                    result=tool_result,
                    latency_ms=tool_latency
                )
                events.append(event)
                tokens += 15
                
                response_text = "I executed a cancellation instead of looking up the order."
                outcome = "failure"
                
            # --- FAILING SCENARIO A: TIMEOUT LOOP ---
            elif self.config.agent_version.endswith("-fail-timeout"):
                loop_count = min(self.config.retry_limit + 1, 10)  # Bound execution strictly
                seq = 1
                for _ in range(loop_count):
                    start_ms = int(time.time() * 1000)
                    tool_latency = 50
                    
                    # Simulated timeout deterministic result
                    tool_result = {"error": "TIMEOUT", "message": "Connection timed out"}
                    
                    event = AgentToolEvent(
                        seq=seq,
                        type="tool_execution",
                        timestamp_ms=start_ms,
                        tool="get_order",
                        arguments={"order_id": order_id},
                        status="TIMEOUT",
                        result=tool_result,
                        latency_ms=tool_latency
                    )
                    events.append(event)
                    seq += 1
                
                response_text = "I'm sorry, I couldn't reach the order system."
                outcome = "failure"
                tokens += (15 * loop_count)
                
            # --- HUMAN FIX: GRACEFUL TIMEOUT RETRY ---
            elif self.config.agent_version.endswith("-fix-timeout"):
                max_attempts = self.config.retry_limit + 1
                seq = 1
                success = False
                
                for attempt in range(max_attempts):
                    start_ms = int(time.time() * 1000)
                    tool_latency = 50
                    
                    # Simulated timeout deterministic result for all attempts
                    tool_result = {"error": "TIMEOUT", "message": "Connection timed out"}
                    
                    event = AgentToolEvent(
                        seq=seq,
                        type="tool_execution",
                        timestamp_ms=start_ms,
                        tool="get_order",
                        arguments={"order_id": order_id},
                        status="TIMEOUT",
                        result=tool_result,
                        latency_ms=tool_latency
                    )
                    events.append(event)
                    seq += 1
                    tokens += 15
                    
                    # If it were successful, we'd break and set success=True here
                
                if not success:
                    if self.config.fallback_enabled:
                        response_text = "I'm sorry, our systems are currently unavailable. Please try again later."
                    else:
                        response_text = "I'm sorry, I couldn't reach the order system."
                    outcome = "failure"
                
            # --- NORMAL SCENARIO ---
            else:
                start_ms = int(time.time() * 1000)
                tool_latency = 50
                tool_result = get_order(order_id)
                
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
                tokens += 15
                
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
            
        total_latency_ms = 120
        
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
