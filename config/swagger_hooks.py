def add_verify_resend_request_bodies(result, generator, request, public):
    verify_body = {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "format": "email"},
                        "code": {"type": "string"},
                    },
                    "required": ["email", "code"],
                }
            }
        },
    }
    resend_body = {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "format": "email"},
                    },
                    "required": ["email"],
                }
            }
        },
    }

    for path, path_item in result.get("paths", {}).items():
        path_name = path.lower()
        for method_name, operation in path_item.items():
            if method_name.lower() not in {"post", "put", "patch"}:
                continue

            operation_id = operation.get("operationId", "").lower()
            name = f"{path_name} {operation_id}"

            if "resend" in name:
                operation["requestBody"] = resend_body
            elif "verify" in name:
                operation["requestBody"] = verify_body

    return result
