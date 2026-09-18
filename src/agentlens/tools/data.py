# Synthetic Database for Phase 2 Support Tools
# Contains no real PII, credentials, or secrets.

CUSTOMERS = {
    "CUST-100": {
        "customer_id": "CUST-100",
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "status": "active"
    }
}

ORDERS = {
    "8271": {
        "order_id": "8271",
        "customer_id": "CUST-100",
        "status": "processing",
        "items": [
            {"item_id": "SKU-A1", "name": "Wireless Mouse", "quantity": 1}
        ],
        "total_amount": 29.99,
        "cancellable": True
    },
    "9001": {
        "order_id": "9001",
        "customer_id": "CUST-100",
        "status": "shipped",
        "items": [
            {"item_id": "SKU-B2", "name": "Mechanical Keyboard", "quantity": 1}
        ],
        "total_amount": 89.99,
        "cancellable": False
    }
}

ORDER_HISTORY = {
    "CUST-100": {
        "customer_id": "CUST-100",
        "orders": [
            "8271",
            "9001"
        ]
    }
}

# Intent mapping definitions
TOOL_INTENTS = {
    "get_order": "READ",
    "get_customer": "READ",
    "get_order_history": "READ",
    "cancel_order": "WRITE/ACTION"
}
