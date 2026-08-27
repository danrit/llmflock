# LLM Prompt

Consider the following financial news text:

```text
{text}
```

Identify and extract entities into the following categories: Provided here with some examples:

- **Company**: {{Apple Inc.; Uber; Bank of America}}
- **Date**: {{June 2nd, 2010; quarter ended 2021; last week; prior year; Wednesday}}
- **Location**: {{California; Paris; 1280 W 12th Blvd; Americas; Europe}}
- **Money**: {{$76.3 million; $4 Bn; Rs 33.80 crore; 1.2 BTC}}
- **Person**: {{Meg Whitman; Mr. Baker; Warren Buffet}}
- **Product**: {{iPhone; Tesla model X; cloud services; Microsoft Windows 10; laptops; medical equipment; computer software; online classes; eye surgery}}
- **Quantity**: {{15%; 25,000 units; 2.75in; 100 tons}}

For each category:
- Extract all relevant entities as a list of strings, preserving the wording from the text
- Use null if no entities are found in that category
- Only extract entities that are explicitly mentioned in the text itself, do not make inferences or reason about what entities might be implied based on URLs, domain names, or other indirect references
- Extract individual items rather than compound or ranged entities (e.g., if a range or compound entity is mentioned, extract each individual item separately)

Return the extracted information as a JSON object with all categories included.

Format the data in the response as a JSON Markdown fenced code block.

Example:

For the following financial text

```text
BYD and its partner , privately held Megha Engineering and Infrastructures submitted a proposal to the Indian government in April to jointly build electric cars in India , Reuters reported earlier this month.
```

The expected result is:

```json
{{
  "Company": ["BYD", "Megha Engineering and Infrastructures", "Reuters"],
  "Date": ["April", "this month"],
  "Location": ["Indian", "India"],
  "Money": null,
  "Person": null,
  "Product": ["electric cars"],
  "Quantity": null
}}
```
