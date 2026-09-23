# LLM Prompt

## Instruction

{user_prompt}

## Formatting the response

Format the answer in the response in JSON inside a JSON Markdown fenced code block: an Array where each element is an Object having the key(s):

- `name` and assign it the related answer as a data type `Text`

### Examples:

_example 1_:

```json
[
    {{
      "name": "gracious wheat"
    }}
]
```

_example 2_:

```json
[
    {{
      "name": "happy cactus"
    }},
    {{
      "name": "elegant mint"
    }}
]
```

_example 3_:

```json
[
    {{
      "name": "heuristic lavender"
    }},
    {{
      "name": "epic poppy"
    }},
    {{
      "name": "compassionate wheat"
    }}
]
```
