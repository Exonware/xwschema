"""
Create many XWSchema instances to test if construction + to_dict() are fast after import.
Timing summary you’ll see:
- First XWSchema() is slow (~1–1.3 s) due to first-use init (e.g. XWData path).
- Subsequent creates are fast (~0.15 ms each). to_dict() is fast (~0.01 ms each).
- Import adds ~1–1.5 s one-time at process start.
"""

import time
from exonware.xwschema import XWSchema
# Many schemas following the same pattern as person (id, properties, required)
SCHEMAS = [
    {
        "id": "xwschema.examples.person",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"],
    },
    {
        "id": "xwschema.examples.product",
        "properties": {
            "sku": {"type": "string"},
            "title": {"type": "string"},
            "price": {"type": "number"},
            "in_stock": {"type": "boolean"},
        },
        "required": ["sku", "title", "price"],
    },
    {
        "id": "xwschema.examples.order",
        "properties": {
            "order_id": {"type": "string"},
            "customer_id": {"type": "string"},
            "items": {"type": "array", "items": {"type": "string"}},
            "total": {"type": "number"},
        },
        "required": ["order_id", "customer_id", "total"],
    },
    {
        "id": "xwschema.examples.user",
        "properties": {
            "email": {"type": "string"},
            "username": {"type": "string"},
            "created_at": {"type": "string", "format": "date-time"},
        },
        "required": ["email"],
    },
    {
        "id": "xwschema.examples.address",
        "properties": {
            "street": {"type": "string"},
            "city": {"type": "string"},
            "postal_code": {"type": "string"},
            "country": {"type": "string"},
        },
        "required": ["city", "country"],
    },
    {
        "id": "xwschema.examples.invoice",
        "properties": {
            "invoice_no": {"type": "string"},
            "amount": {"type": "number"},
            "due_date": {"type": "string", "format": "date"},
            "paid": {"type": "boolean"},
        },
        "required": ["invoice_no", "amount"],
    },
    {
        "id": "xwschema.examples.customer",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "email": {"type": "string"},
            "address": {"type": "object"},
        },
        "required": ["id", "name", "email"],
    },
    {
        "id": "xwschema.examples.article",
        "properties": {
            "slug": {"type": "string"},
            "title": {"type": "string"},
            "body": {"type": "string"},
            "published": {"type": "boolean"},
        },
        "required": ["slug", "title"],
    },
    {
        "id": "xwschema.examples.event",
        "properties": {
            "name": {"type": "string"},
            "start": {"type": "string", "format": "date-time"},
            "end": {"type": "string", "format": "date-time"},
            "location": {"type": "string"},
        },
        "required": ["name", "start"],
    },
    {
        "id": "xwschema.examples.ticket",
        "properties": {
            "ticket_id": {"type": "string"},
            "event_id": {"type": "string"},
            "seat": {"type": "string"},
            "price": {"type": "number"},
        },
        "required": ["ticket_id", "event_id", "price"],
    },
    {
        "id": "xwschema.examples.review",
        "properties": {
            "rating": {"type": "integer"},
            "comment": {"type": "string"},
            "author_id": {"type": "string"},
        },
        "required": ["rating"],
    },
    {
        "id": "xwschema.examples.payment",
        "properties": {
            "method": {"type": "string", "enum": ["card", "bank", "paypal"]},
            "amount": {"type": "number"},
            "currency": {"type": "string"},
        },
        "required": ["method", "amount", "currency"],
    },
    {
        "id": "xwschema.examples.shipment",
        "properties": {
            "tracking_no": {"type": "string"},
            "carrier": {"type": "string"},
            "status": {"type": "string"},
            "estimated_delivery": {"type": "string", "format": "date"},
        },
        "required": ["tracking_no", "carrier"],
    },
    {
        "id": "xwschema.examples.category",
        "properties": {
            "name": {"type": "string"},
            "parent_id": {"type": ["string", "null"]},
            "slug": {"type": "string"},
        },
        "required": ["name", "slug"],
    },
    {
        "id": "xwschema.examples.tag",
        "properties": {"name": {"type": "string"}, "color": {"type": "string"}},
        "required": ["name"],
    },
    {
        "id": "xwschema.examples.config",
        "properties": {
            "key": {"type": "string"},
            "value": {"type": "string"},
            "environment": {"type": "string"},
        },
        "required": ["key", "value"],
    },
    {
        "id": "xwschema.examples.audit_log",
        "properties": {
            "action": {"type": "string"},
            "entity_type": {"type": "string"},
            "entity_id": {"type": "string"},
            "timestamp": {"type": "string", "format": "date-time"},
        },
        "required": ["action", "entity_type", "timestamp"],
    },
    {
        "id": "xwschema.examples.webhook",
        "properties": {
            "url": {"type": "string", "format": "uri"},
            "events": {"type": "array", "items": {"type": "string"}},
            "secret": {"type": "string"},
        },
        "required": ["url", "events"],
    },
    {
        "id": "xwschema.examples.api_key",
        "properties": {
            "key_prefix": {"type": "string"},
            "scopes": {"type": "array", "items": {"type": "string"}},
            "expires_at": {"type": "string", "format": "date-time"},
        },
        "required": ["key_prefix", "scopes"],
    },
    {
        "id": "xwschema.examples.session",
        "properties": {
            "session_id": {"type": "string"},
            "user_id": {"type": "string"},
            "expires_at": {"type": "string", "format": "date-time"},
        },
        "required": ["session_id", "user_id"],
    },
]


def main():
    n = len(SCHEMAS)
    # Time first schema vs rest (see if first-call is slow)
    t0 = time.perf_counter()
    first = XWSchema(schema=SCHEMAS[0])
    t1 = time.perf_counter()
    first_ms = (t1 - t0) * 1000
    t0 = time.perf_counter()
    rest = [XWSchema(schema=s) for s in SCHEMAS[1:]]
    t1 = time.perf_counter()
    rest_ms = (t1 - t0) * 1000
    schemas = [first] + rest
    create_ms = first_ms + rest_ms
    t0 = time.perf_counter()
    for s in schemas:
        s.to_dict()
    t1 = time.perf_counter()
    to_dict_ms = (t1 - t0) * 1000
    print(f"First XWSchema create:  {first_ms:.2f} ms")
    print(f"Next {n - 1} creates:   {rest_ms:.2f} ms ({rest_ms / (n - 1):.3f} ms each)")
    print(f"Created {n} XWSchema instances in {create_ms:.2f} ms ({create_ms / n:.3f} ms each)")
    print(f"Called to_dict() on all {n} in {to_dict_ms:.2f} ms ({to_dict_ms / n:.3f} ms each)")
    print(f"Total (create + to_dict): {create_ms + to_dict_ms:.2f} ms")
    print()
    # Show first schema output as before
    print("First schema (person) to_dict() sample:")
    print(schemas[0].to_dict())
if __name__ == "__main__":
    main()
