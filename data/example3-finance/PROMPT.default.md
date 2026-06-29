# LLM Prompt

Consider the following financial news text:

```text
{content_text}
```

Identify and extract entities into the following categories:

- **Company**
  - Definition: Denotes the official or unofficial name of a registered company or a brand.
  - Example entities: {Apple Inc.; Uber; Bank of America}
- **Date**
  - Definition: Represents a specific time period, whether explicitly mentioned (e.g., "year ended March 2020") or implicitly referred to (e.g., "last month"), in the past, present, or future.
  - Example entities: {June 2nd, 2010; quarter ended 2021; last week; prior year; Wednesday}
- **Location**
  -  Definition: Represents geographical locations, such as political regions, countries, states, cities, roads, or any other location, even when used as adjectives.
  - Example entities: {California; Paris; 1280 W 12th Blvd; Americas; Europe}
- **Money**
  - Definition: Denotes a monetary value expressed in any world currency, including digital currencies.
  - Example entities: {$76.3 million; $4 Bn; Rs 33.80 crore; 1.2 BTC}
- **Person**
  - Definition: Represents the name of an individual.
  - Example entities: {Meg Whitman; Mr. Baker; Warren Buffet}
- **Product**
  - Definition: Refers to any physical object or service manufactured or provided by a company to consumers, excluding references to businesses or sectors within the financial context.
  - Example entities: {iPhone; Tesla model X; cloud services; Microsoft Windows 10; laptops; medical equipment; computer software; online classes; eye surgery}
- **Quantity**
  - Definition: Represents any numeric value that is not categorized as Money, such as percentages, numbers, measurements (e.g., weight, length), or other similar quantities. Note that unit of measurements are also part of the entity.
  - Example entities: {15%; 25,000 units; 2.75in; 100 tons}

For each category:
- Extract all relevant entities as a list of strings, preserving the wording from the text
- Use null if no entities are found in that category
- Only extract entities that are explicitly mentioned in the text itself, do not make inferences or reason about what entities might be implied based on URLs, domain names, or other indirect references
- Extract individual items rather than compound or ranged entities (e.g., if a range or compound entity is mentioned, extract each individual item separately)

Return the extracted information as a JSON object with all categories included.

Format the data in the response as a JSON Markdown fenced code block:

Example output:

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
