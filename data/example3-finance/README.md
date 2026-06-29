# README

Example use case: Extract financial and contextual entities from business and financial text.

More details: Search for 7 entities: Company, Date, Location, Money, Person, Product and Quantity from 32 text snippets drawn from business or financial news, reports, or announcements. The process can extract multiple entities from a single type and none from another type.

This is a sample of the bigger dataset [Cleanlab/fire-financial-ner-extraction](https://huggingface.co/datasets/Cleanlab/fire-financial-ner-extraction) (2k+ records) used by [CleanLab benchmark tool](https://github.com/cleanlab/structured-output-benchmark). Unlike the 2 other examples, this one is based on a real experiment of data extraction by LLM runs by this "data label-auditing" company, hence giving a good comparison point.
In the other hand, the product of the extraction is not usable as-is (the experiment makes no attempt to link the extracted entities between each-other and extract ideas). IMO it can only be used to compare LLM extraction approach. 

Reducing the dataset to 32 to be able to run the example quickly and keep human overview of the results. The dataset comes with the ground truth for each record (see [ground_truth.jsonl](documents/dataset.ground_truth.jsonl)) provided by the same company: "To enable more reliable assessment of models, we provide [...] rigorously cleaned and validated benchmarks"


## Prompt

The [prompt](PROMPT.default.md) is vastly inspired by the [system prompt](https://github.com/cleanlab/structured-output-benchmark/blob/main/financial_entities/get_responses.ipynb) of the original benchmark tool. 

