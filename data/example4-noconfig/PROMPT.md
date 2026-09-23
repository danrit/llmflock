# LLM Prompt

## Instruction

{user_prompt}

## Formatting the response 

Format the answer in the response in JSON inside a JSON Markdown fenced code block: an Object having the key(s):

- `count` and assign it the related answer as a data type `Number`

### Examples:

_example 1_:

```json
{{
  "count": 0,
}}
```

_example 2_:

```json
{{
  "count": 2,
}}
```
