# LLM Prompt

## Instruction

{count_question}

## Formatting the response 

Format the answer in the response as JSON Object inside a JSON Markdown fenced code block: use the key `count` and assign it the answer as a data type `Number`

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
