# README

Example use case: Extract financial and contextual entities from business and financial text.

More details: Search for 7 entities: Company, Date, Location, Money, Person, Product and Quantity from 32 text snippets drawn from business or financial news, reports, or announcements. The process can extract multiple entities from a single type and none from another type.

## Data

This is a sample of the bigger dataset [Cleanlab/fire-financial-ner-extraction](https://huggingface.co/datasets/Cleanlab/fire-financial-ner-extraction) (2k+ records) used by [CleanLab benchmark tool](https://github.com/cleanlab/structured-output-benchmark). Unlike the 2 other examples, this one is based on a real experiment of data extraction by LLM runs by this "data label-auditing" company, hence giving a good comparison point.
In the other hand, the product of the extraction is not usable as-is (the experiment makes no attempt to link the extracted entities between each-other and extract ideas). IMO it can only be used to compare LLM extraction approach. 

Below are some preparation work done on the data, given here for tracking and transparency, not required to run the example.

### Dataset Reduction

Reducing the dataset to 32 to be able to run the example quickly and keep human overview of the results. The dataset comes with the ground truth for each record (see [ground_truth.jsonl](documents/dataset.ground_truth.jsonl)) provided by the same company: "To enable more reliable assessment of models, we provide [...] rigorously cleaned and validated benchmarks".

### Dataset Preparation

The dataset and ground truth data was provided in CSV format, file provided [here](documents/fire_financial_ner_extraction.32.csv) for reference. For the usage here it was converted to JSONL and split into 2 files: [dataset.jsonl](./dataset.jsonl) and [ground_truth.jsonl](documents/ground_truth.jsonl) with a python script

- `python extract.py fire_financial_ner_extraction.32.csv ground_truth > ./documents/ground_truth.jsonl`
- `python extract.py fire_financial_ner_extraction.32.csv text > dataset.jsonl`

**extract.py**:
```python
import ast
import csv
import json
import sys

VALID_ATTRS = ("text", "ground_truth")


def main():
    if len(sys.argv) != 3 or sys.argv[2] not in VALID_ATTRS:
        print(f"Usage: {sys.argv[0]} <csv_file> <{' | '.join(VALID_ATTRS)}>", file=sys.stderr)
        sys.exit(1)

    attr = sys.argv[2]

    with open(sys.argv[1], newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            if attr == "text":
                obj = {"id": str(i), "text": row["text"]}
            else:
                obj = {"id": str(i), **ast.literal_eval(row["ground_truth"])}
            print(json.dumps(obj))


if __name__ == "__main__":
    main()

```


## Prompt

The [prompt](PROMPT.default.md) is vastly inspired by the [system prompt](https://github.com/cleanlab/structured-output-benchmark/blob/main/financial_entities/get_responses.ipynb) of the original benchmark tool. 

