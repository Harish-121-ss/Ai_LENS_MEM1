from pydantic import BaseModel, ValidationError
from typing import Dict, Any, Optional
from agentlens.tools.data import CUSTOMERS, ORDERS, ORDER_HISTORY

# Input Models for Validation
class GetOrderInput(BaseModel):
    order_id: str

class GetCustomerInput(BaseModel):
    customer_id: str

class GetOrderHistoryInput(BaseModel):
    customer_id: str

class CancelOrderInput(BaseModel):
    order_id: str

def get_order(order_id: str) -> Dict[str, Any]:
    """Retrieve an order by ID (READ intent)."""
    try:
        validated = GetOrderInput(order_id=order_id)
    except ValidationError as e:
        return {"error": "VALIDATION_FAILED", "details": str(e)}
        
    order = ORDERS.get(validated.order_id)
    if not order:
        return {"error": "NOT_FOUND", "message": f"Order {validated.order_id} not found."}
    return {"status": "SUCCESS", "data": order}

def get_customer(customer_id: str) -> Dict[str, Any]:
    """Retrieve a customer by ID (READ intent)."""
    try:
        validated = GetCustomerInput(customer_id=customer_id)
    except ValidationError as e:
        return {"error": "VALIDATION_FAILED", "details": str(e)}
        
    customer = CUSTOMERS.get(validated.customer_id)
    if not customer:
        return {"error": "NOT_FOUND", "message": f"Customer {validated.customer_id} not found."}
    return {"status": "SUCCESS", "data": customer}

def get_order_history(customer_id: str) -> Dict[str, Any]:
    """Retrieve order history for a customer (READ intent)."""
    try:
        validated = GetOrderHistoryInput(customer_id=customer_id)
    except ValidationError as e:
        return {"error": "VALIDATION_FAILED", "details": str(e)}
        
    history = ORDER_HISTORY.get(validated.customer_id)
    if not history:
        return {"error": "NOT_FOUND", "message": f"History for {validated.customer_id} not found."}
    return {"status": "SUCCESS", "data": history}

def cancel_order(order_id: str) -> Dict[str, Any]:
    """Cancel an order by ID (WRITE/ACTION intent)."""
    try:
        validated = CancelOrderInput(order_id=order_id)
    except ValidationError as e:
        return {"error": "VALIDATION_FAILED", "details": str(e)}
        
    order = ORDERS.get(validated.order_id)
    if not order:
        return {"error": "NOT_FOUND", "message": f"Order {validated.order_id} not found."}
        
    if not order.get("cancellable"):
        return {"error": "NOT_CANCELLABLE", "message": f"Order {validated.order_id} cannot be cancelled."}
        
    # Simulate deterministic action without actual state mutation (since it's a test support tool)
    return {"status": "SUCCESS", "message": f"Order {validated.order_id} cancelled successfully."}
