# LLM Prompt

## Instruction

{user_prompt}

## Formatting the response 

Format the answer in the response in JSON inside a JSON Markdown fenced code block: an Object having the key(s):

- `start` and assign it the related answer as a data type `Number` or a null value
- `end` and assign it the related answer as a data type `Number` or a null value

### Examples:

_example 1_:

```json
{{
  "start": 56,
  "end": 123
}}
```

_example 2_:

```json
{{
  "start": 142,
  "end": null
}}
```
