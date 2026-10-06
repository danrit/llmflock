"""
Build the schema-following instructions automatically added to the user prompt.

Given the JSON schema produced by `schema_dsl()`, this module builds:
- `<human_json_schema_rules>`: a plain-english, bullet-point explanation of
  the expected response format.
- `<json_example_1>`, `<json_example_2>`, `<json_example_3>`: three
  deterministic, schema-valid example JSON payloads.

Note: ai-agent-generated with requirements and examples provided.
"""
import hashlib
import json
from typing import Any

from jsonschema import validate

from llmflock.concise_schema.lookup_tables import bools, ints, floats, strs

TYPE_WORDS = {
    'boolean': 'Boolean',
    'integer': 'Whole Number',
    'number': 'Number',
    'string': 'Text',
}

NUM_EXAMPLES = 3
# Fixed example index used to demonstrate a null value for nullable fields.
NULL_EXAMPLE_INDEX = 2


def _field_type_and_nullable(field_schema: dict) -> tuple[str, bool]:
    """Unwrap a `schema_dsl()` field type declaration, eg `["integer", "null"]`,
    into its (actual_type, nullable) parts."""
    field_type = field_schema['type']
    if isinstance(field_type, list):
        nullable = 'null' in field_type
        actual_type = next(t for t in field_type if t != 'null')
    else:
        nullable = False
        actual_type = field_type
    return actual_type, nullable


def _schema_hash(schema: dict) -> str:
    return hashlib.sha256(
        json.dumps(schema, sort_keys=True).encode('utf-8')).hexdigest()


def _seed(schema_hash: str, *parts: Any) -> int:
    seed_str = ':'.join([schema_hash, *(str(part) for part in parts)])
    return int(hashlib.md5(seed_str.encode('utf-8')).hexdigest(), 16)


def _generate_value(schema_hash: str, field_name: str, field_type: str,
                     nullable: bool, example_index: int,
                     element_index: int | None) -> Any:
    if nullable and example_index == NULL_EXAMPLE_INDEX:
        return None

    seed = _seed(schema_hash, field_name, example_index, element_index)

    if field_type == 'boolean':
        return bools[seed % len(bools)]
    elif field_type == 'integer':
        return ints[seed % len(ints)]
    elif field_type == 'number':
        return floats[seed % len(floats)]
    elif field_type == 'string':
        left = strs['left'][seed % len(strs['left'])]
        right = strs['right'][(seed // len(strs['left'])) % len(strs['right'])]
        return f'{left} {right}'
    else:
        raise ValueError(
            f"Unsupported field type for example generation: {field_type!r}")


def _properties_of(schema: dict) -> dict:
    """The `properties` object to iterate over, whether `schema` is a plain
    object schema or an array-wrapped one (`--schema-multi`)."""
    if schema.get('type') == 'array':
        return schema['items']['properties']
    return schema['properties']


def _human_rules_for_properties(properties: dict) -> str:
    bullets = []
    for field_name, field_schema in properties.items():
        field_type, nullable = _field_type_and_nullable(field_schema)
        type_word = TYPE_WORDS[field_type]
        bullet = (f'- `{field_name}` and assign it the related answer as a '
                  f'data type `{type_word}`')
        if nullable:
            bullet += ' or a null value'
        description = field_schema.get('description')
        if description:
            bullet += f': {description}'
        bullets.append(bullet)
    return '\n'.join(bullets)


def build_human_json_schema_rules(schema: dict) -> str:
    """Build the `<human_json_schema_rules>` token: a plain-english
    explanation of the response format required by `schema`."""
    if schema.get('type') == 'array':
        header = 'an Array where each element is an Object having the key(s):'
    else:
        header = 'an Object having the key(s):'

    return f'{header}\n\n{_human_rules_for_properties(_properties_of(schema))}'


def _generate_object_example(schema_hash: str, properties: dict,
                              example_index: int,
                              element_index: int | None = None) -> dict:
    example = {}
    for field_name, field_schema in properties.items():
        field_type, nullable = _field_type_and_nullable(field_schema)
        example[field_name] = _generate_value(
            schema_hash, field_name, field_type, nullable, example_index,
            element_index)
    return example


def build_json_examples(schema: dict) -> list[str]:
    """Build the `<json_example_1>`, `<json_example_2>`, `<json_example_3>`
    tokens: 3 deterministic, schema-valid JSON payloads.

    For a `--schema-multi` (array) schema, example N contains N array
    elements, so the examples also demonstrate that the array length varies.
    """
    schema_hash = _schema_hash(schema)
    is_multi = schema.get('type') == 'array'
    properties = _properties_of(schema)

    examples = []
    for example_index in range(1, NUM_EXAMPLES + 1):
        if is_multi:
            data = [
                _generate_object_example(schema_hash, properties,
                                         example_index, element_index)
                for element_index in range(1, example_index + 1)
            ]
        else:
            data = _generate_object_example(schema_hash, properties,
                                            example_index)

        validate(instance=data, schema=schema)
        examples.append(json.dumps(data, indent=2))

    return examples


def build_schema_prompt(user_prompt: str, schema: dict, template: str) -> str:
    """Compose the full prompt (user instruction + schema-following
    directives) from `template` (`config.prompt_schema_default`), replacing
    its `{user_prompt}`, `<human_json_schema_rules>` and `<json_example_N>`
    tokens.

    Uses plain string replacement rather than `str.format()`: the generated
    JSON examples contain `{`/`}` characters that `.format()` would otherwise
    try to interpret as format fields. The resulting `content` is later
    passed through `.format()` again in `cli.build_prompt()` (to substitute
    dataset/document variables), so the injected human rules and JSON
    examples have their braces escaped (`{{`/`}}`) to survive that pass
    unchanged.
    """
    def escape_braces(text: str) -> str:
        return text.replace('{', '{{').replace('}', '}}')

    prompt = template.replace('{user_prompt}', user_prompt)
    prompt = prompt.replace('<human_json_schema_rules>',
                           escape_braces(build_human_json_schema_rules(schema)))
    for index, example in enumerate(build_json_examples(schema), start=1):
        prompt = prompt.replace(f'<json_example_{index}>', escape_braces(example))
    return prompt
