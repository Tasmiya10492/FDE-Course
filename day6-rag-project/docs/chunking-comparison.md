
## Results

| Method | Total questions | Successful Hit@3 | Hit@3 rate |
|---|---:|---:|---:|
| Fixed-size | 10 | 8 | 80% |
| Sentence-based | 10 | 8 | 80% |
| Paragraph-based | 10 | 10 | 100% |

## Observations

1. Fixed-size chunking successfully retrieved the expected policy in 8 out of 10 questions.
2. Sentence-based chunking also achieved 8 out of 10.
3. Paragraph-based chunking achieved 10 out of 10.
4. Paragraph-based chunking preserved useful policy context for this particular dataset.
5. Fixed-size and sentence-based chunking missed the expected policy for HR003 and HR004.

## Conclusion

Paragraph-based chunking performed best in this experiment, achieving a 100% Hit@3 retrieval rate across the 10 evaluation questions.

It appears that keeping policy paragraphs together helped ChromaDB retrieve the relevant policy information.

This result is specific to the current synthetic HR policy dataset and evaluation questions. Further testing with different documents would be needed before selecting it as a general-purpose chunking strategy.
