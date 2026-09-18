"""
Selected utilities functions from simonw/llm

Based on the original implementation by Simon Willison in simonw/llm
Source: https://github.com/simonw/llm/blob/a463c6318f65a48ae185733a0655dca7bb00c3e1/llm/utils.py
"""

from typing import Any

def schema_dsl(schema_dsl: str, multi: bool = False) -> dict[str, Any]:
    """
    Build a JSON schema from a concise schema string.

    Args:
        schema_dsl: A string representing a schema in the concise format.
            Can be comma-separated or newline-separated.
        multi: Boolean, return a schema for an "items" array of these

    Returns:
        A dictionary representing the JSON schema.
    """
    # Type mapping dictionary
    type_mapping = {
        "int": "integer",
        "float": "number",
        "bool": "boolean",
        "str": "string",
    }

    # Initialize the schema dictionary with required elements
    json_schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    # Check if the schema is newline-separated or comma-separated
    if "\n" in schema_dsl:
        fields = [field.strip() for field in schema_dsl.split("\n") if field.strip()]
    else:
        fields = [field.strip() for field in schema_dsl.split(",") if field.strip()]

    # Process each field
    for field in fields:
        # Extract field name, type, and description
        if ":" in field:
            field_info, description = field.split(":", 1)
            description = description.strip()
        else:
            field_info = field
            description = ""

        # Process field name and type
        field_parts = field_info.strip().split()
        if not field_parts:
            raise ValueError(
                f"Invalid schema DSL: field {field!r} is missing a name before ':'"
            )
        field_name = field_parts[0].strip()

        # Default type is string
        field_type = "string"

        # If type is specified, use it
        if len(field_parts) > 1:
            type_indicator = field_parts[1].strip()
            try:
                field_type = type_mapping[type_indicator]
            except KeyError:
                # 'from None' hides the internal mapping KeyError from the
                # user-facing traceback:
                raise ValueError(
                    f"Invalid schema DSL: unknown type {type_indicator!r} "
                    f"for field {field_name!r}"
                ) from None

        if field_name in json_schema["properties"]:
            raise ValueError(f"Invalid schema DSL: duplicate field name {field_name!r}")

        # Add field to properties
        json_schema["properties"][field_name] = {"type": field_type}

        # Add description if provided
        if description:
            json_schema["properties"][field_name]["description"] = description

        # Add field to required list
        json_schema["required"].append(field_name)

    if multi:
        return multi_schema(json_schema)
    else:
        return json_schema

def multi_schema(schema: dict) -> dict:
    "Wrap JSON schema in an 'items': [] array"
    return {
        "type": "object",
        "properties": {"items": {"type": "array", "items": schema}},
        "required": ["items"],
    }


