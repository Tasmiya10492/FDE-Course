# Multimodal Invoice Extraction Experiment

## 1. Objective

The objective was to test whether a multimodal Large Language Model (LLM) could extract structured invoice information from both a normal invoice image and a scanned PDF page.

## 2. Environment

- Provider: Ollama
- Model: qwen3.5:2b
- Temperature: 0
- Seed: 42
- Output validation: Pydantic
- Image processing: Pillow
- PDF conversion: PyMuPDF

## 3. Input Files

| Input | Format | Processing |
|---|---|---|
| invoice.png | PNG image | Sent directly to the vision model |
| invoice_scan.pdf | Scanned PDF | Converted into a PNG image using PyMuPDF |

## 4. Extracted Results

### Invoice 1 – Normal Image

- Invoice number: INV-2026-0417
- Invoice date: 2026-03-14
- Due date: 2026-04-13
- Vendor: Brightwater Supplies Ltd (invented)
- Customer: Demo Customer Co (invented)
- Subtotal: 17,900
- Tax rate: 18%
- Tax amount: 3,222
- Total due: 21,122
- Items: 3

### Invoice 2 – Scanned PDF

- Invoice number: INV-2026-0533
- Invoice date: 2026-03-14
- Due date: 2026-04-13
- Vendor: Harbourlight Stationers (invented)
- Customer: Demo Customer Co (invented)
- Subtotal: 22,700
- Tax rate: 18%
- Tax amount: 4,086
- Total due: 26,786
- Items: 2

## 5. Validation

Both extracted responses were successfully validated using the Pydantic InvoiceData schema.

The extracted invoice fields and line items were manually compared against the original images. The values matched the visible source information.

Currency was returned as null because no currency was visibly specified in the documents.

## 6. Security Considerations

- The invoice content was treated as untrusted input.
- The prompt instructed the model not to follow instructions embedded in invoice documents.
- The model was instructed not to invent missing information.
- Missing optional values were represented as null.
- Pydantic validation was used to enforce the expected output structure.

## 7. Conclusion

The multimodal model successfully extracted structured invoice data from both a regular image and a scanned PDF page.

The experiment demonstrated how a scanned document can be converted into an image and passed to a vision-capable LLM for structured extraction.

Pydantic validation helped ensure that the extracted response followed the expected invoice schema.