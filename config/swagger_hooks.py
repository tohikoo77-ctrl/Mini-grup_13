def _json_body(schema, example=None):
    body = {
        "required": True,
        "content": {
            "application/json": {
                "schema": schema,
            }
        },
    }
    if example is not None:
        body["content"]["application/json"]["example"] = example
    return body


# Known write endpoints that drf-spectacular cannot infer (APIView, drf-yasg stubs).
_PATH_BODY_RULES = (
    ("login", _json_body(
        {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
                "username": {"type": "string"},
                "password": {"type": "string", "format": "password"},
            },
            "required": ["password"],
        },
        {"email": "user@example.com", "password": "your-password"},
    )),
    ("register", _json_body(
        {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "password": {"type": "string", "format": "password"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "phone_number": {"type": "string", "example": "+998901234567"},
                "role": {"type": "string", "enum": ["admin", "customer", "seller"]},
                "address": {"type": "string"},
            },
            "required": ["username", "email", "password"],
        },
        {
            "username": "john",
            "email": "john@example.com",
            "password": "securepass123",
        },
    )),
    ("verify", _json_body(
        {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
                "code": {"type": "string"},
            },
            "required": ["email", "code"],
        },
        {"email": "user@example.com", "code": "123456"},
    )),
    ("resend", _json_body(
        {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
            },
            "required": ["email"],
        },
        {"email": "user@example.com"},
    )),
    ("forgot", _json_body(
        {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
            },
            "required": ["email"],
        },
        {"email": "user@example.com"},
    )),
    ("reset", _json_body(
        {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
                "code": {"type": "string"},
                "new_password": {"type": "string", "format": "password"},
            },
            "required": ["email", "code", "new_password"],
        },
    )),
    ("change-password", _json_body(
        {
            "type": "object",
            "properties": {
                "old_password": {"type": "string", "format": "password"},
                "new_password": {"type": "string", "format": "password"},
                "password": {"type": "string", "format": "password"},
            },
            "required": ["new_password"],
        },
        {"old_password": "oldpass", "new_password": "newpass"},
    )),
    ("password", _json_body(
        {
            "type": "object",
            "properties": {
                "old_password": {"type": "string", "format": "password"},
                "new_password": {"type": "string", "format": "password"},
            },
            "required": ["new_password"],
        },
    )),
    ("username", _json_body(
        {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
            },
            "required": ["username"],
        },
        {"username": "new_username"},
    )),
    ("profile", _json_body(
        {
            "type": "object",
            "properties": {
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "phone_number": {"type": "string"},
                "address": {"type": "string"},
            },
        },
    )),
    ("compare", _json_body(
        {
            "type": "object",
            "properties": {
                "product_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                },
            },
            "required": ["product_ids"],
        },
        {"product_ids": [1, 2]},
    )),
    ("toggle", _json_body(
        {
            "type": "object",
            "properties": {
                "product_id": {"type": "integer"},
            },
            "required": ["product_id"],
        },
        {"product_id": 1},
    )),
    ("checkout", _json_body(
        {
            "type": "object",
            "properties": {
                "address": {"type": "string"},
                "payment_method": {"type": "string"},
            },
        },
    )),
)

_DEFAULT_WRITE_BODY = _json_body(
    {
        "type": "object",
        "additionalProperties": True,
        "description": "Request JSON body",
    }
)


def _match_body(path_name, operation_id):
    name = f"{path_name} {operation_id}".lower()
    for keyword, body in _PATH_BODY_RULES:
        if keyword in name:
            return body
    return _DEFAULT_WRITE_BODY


def add_write_method_request_bodies(result, generator, request, public):
    """Ensure POST, PUT, and PATCH operations expose an editable JSON request body."""
    for path, path_item in result.get("paths", {}).items():
        path_name = path.lower()
        for method_name, operation in path_item.items():
            if method_name.lower() not in {"post", "put", "patch"}:
                continue
            if operation.get("requestBody"):
                continue

            operation_id = operation.get("operationId", "")
            operation["requestBody"] = _match_body(path_name, operation_id)

    return result


# Backward-compatible alias used in settings.
add_verify_resend_request_bodies = add_write_method_request_bodies
