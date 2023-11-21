# Knowledge Base Assistant

### Purpose

This project is an exploration of [OpenAI's Assistant API](https://platform.openai.com/docs/assistants/overview) -
trying to evaluate the strengths and weaknesses.

1. Is an Assistant easier to use
   than [Llama Index](https://llamahub.ai/)/[Langchain](https://python.langchain.com/docs/get_started/introduction)?
2. Does an Assistant provide more accurate answers
   than [Llama Index](https://llamahub.ai/)/[Langchain](https://python.langchain.com/docs/get_started/introduction)?

### Context

This project is based off the existing [Knowledge Base Demo](https://github.com/focused-labs/ai-knowledge-base-demo).

### Data Inputs:

1. Our external Notion wiki
2. Our public website: [Focused Labs](https://focusedlabs.io/)

### Run

1. A Open AI API account (api key). You can sign up [at Open AI's website](https://platform.openai.com/signup).
2. Python (and your favorite IDE). We are using python v3.10.7.

#### Update `.env`

```
OPENAI_API_KEY = "<Open AI API Token>"
```

#### Run the test

Run the code blocks in `sandbox.ipynb`

This will result in an `accuracy_test_results.csv` file. You can open this and evaluate the accuracy of the answers. 