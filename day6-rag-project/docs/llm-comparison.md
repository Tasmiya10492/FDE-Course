# Local LLM vs Hosted LLM Comparison

## Objective

Compare a small local language model with a hosted language model using the same question and retrieved policy context.

## Models

- Local model: Qwen 3.5 2B using Ollama
- Hosted model: ChatGPT

## Test question

An employee's paternity leave request has been approved, but they no longer need it. What steps should they follow to cancel it, and who reviews the cancellation?

## Retrieved context

The RAG system retrieved information from HR005 and HR010.

Relevant retrieved information:
- Employees who no longer need approved leave should submit a cancellation request through the HR portal.
- The employee should check the HR portal to confirm that the leave cancellation has been approved.

The retrieved context did not include the sentence identifying the reporting manager as the reviewer.

## Results

| Evaluation | Local Qwen 3.5 2B | Hosted ChatGPT |
|---|---|---|
| Generated an answer | No; returned an empty response | Yes |
| Identified the cancellation process | Not evaluated because the response was empty | Yes |
| Explained how to confirm cancellation | Not evaluated | Yes |
| Avoided inventing the reviewer | Not evaluated | Yes; stated that the retrieved context did not identify the reviewer |

## Observation

For this test, the local model returned an empty response even though relevant policy information was retrieved. The hosted model generated a useful answer using the same context and correctly identified that the reviewer information was missing.

This demonstrates a difference in observed output for this test. It does not prove that model size alone caused the local model's empty response.

## Possible reasons for the difference

- The local model may have generation or response-handling limitations.
- Model size and capability can affect complex response generation.
- Model configuration and inference behaviour may also affect output.

These are possible explanations, not confirmed causes.

## Conclusion

The hosted model performed better in this particular test because it generated a relevant response while the local model returned an empty response. More tests would be needed to make a general performance comparison.