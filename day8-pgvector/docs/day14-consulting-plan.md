# Day 14 – Consulting Practice Plan

## 1. Confirmed Requirements

- Build a Knowledge Assistant web page using FastAPI, Jinja2 and HTMX.
- Allow employees to submit HR policy questions through a web form.
- Display generated answers with supporting citations.
- Show loading feedback while a question is being processed.
- Display clear error messages when a request cannot be processed.
- Escape untrusted content to prevent cross-site scripting (XSS).
- Protect form submissions using CSRF validation.
- Configure security headers, including Content Security Policy.
- Support keyboard navigation and accessible form labels.
- Validate user input and handle empty or oversized questions.

## 2. Suggestions

- Improve the presentation of answers and citations for readability.
- Provide clear guidance when the assistant cannot find an answer.
- Continue testing the interface with different HR policy questions.
- Consider adding authenticated user access and role-based permissions in a future iteration.
- Gather feedback from employees to identify usability improvements.

## 3. Risks and Caveats

- The assistant may not always find sufficient information to answer a question.
- Generated answers must be checked against the cited HR policy documents.
- Incorrect or outdated policy documents may lead to inaccurate answers.
- The current web interface uses a fixed Employee role and does not provide a complete login or user-management system.
- The application requires a valid session secret and secure deployment configuration.
- The interface depends on the availability of the backend, database and language model.
- Users should consult HR for clarification when an answer is uncertain or incomplete.

## 4. Acceptance Tests

| No. | Test scenario | Expected result |
|---|---|---|
| 1 | Open the Knowledge Assistant page. | The page loads successfully and displays the question form. |
| 2 | Submit a valid HR policy question. | The application displays an answer and supporting citations. |
| 3 | Submit an empty question. | The application displays a clear validation error. |
| 4 | Submit a question longer than 2,000 characters. | The application rejects the question and explains the character limit. |
| 5 | Submit a question without a valid CSRF token. | The application rejects the request. |
| 6 | Submit content containing a script tag. | The content is HTML-escaped and is not executed as a script. |
| 7 | Submit content containing malicious HTML in citation fields. | The HTML is escaped and is not executed by the browser. |
| 8 | Check the response security headers. | CSP and other configured security headers are present. |
| 9 | Navigate through the form using the keyboard. | The fields and Submit button are accessible, with visible focus indicators. |
| 10 | Submit a question and wait for the response. | A loading indicator is displayed while processing. |
| 11 | Trigger an application error. | A clear error message is displayed to the user. |
| 12 | Ask a question whose answer is not supported by the available policy documents. | The assistant abstains instead of inventing an answer. |
| 13 | Access the static CSS and JavaScript files. | The required static resources load successfully. |
| 14 | View the page at different screen sizes. | The interface remains usable and readable. |

### Acceptance Criteria

The implementation is accepted when the required page, question submission, answer and citation display, validation, security protections and accessibility behaviours work as expected, and the relevant automated and browser tests pass.
