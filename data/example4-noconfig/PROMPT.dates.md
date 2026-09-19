# LLM Prompt

## Instruction

{user_prompt}

## Formatting the response 

Format the answer in the response as JSON Object inside a JSON Markdown fenced code block: use the keys

- `start` and assign it the answer as a data type `Number`
- `end` and assign it the answer as a data type `Number`

### Examples:

_example 1_:

```json
{{
  "start": 56,
  "end": 123,
}}
```

_example 2_:

```json
{{
  "start": 56,
  "end": -6979,
}}
```
