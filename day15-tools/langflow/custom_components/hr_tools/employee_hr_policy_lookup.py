"""Langflow component for the employee HR policy API."""

import json
import os
import urllib.error
import urllib.request
from typing import ClassVar

from lfx.custom.custom_component.component import Component
from lfx.io import MessageTextInput, Output
from lfx.schema.message import Message


class EmployeeHRPolicyLookup(Component):
    display_name = "Employee HR Policy Lookup"
    description = "Ask the authenticated FastAPI employee HR policy assistant."
    documentation = ""
    icon = "shield-check"
    name = "EmployeeHRPolicyLookup"

    inputs: ClassVar[list[MessageTextInput]] = [
        MessageTextInput(
            name="question",
            display_name="Question",
            info="The employee's HR policy question.",
            required=True,
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(
            name="answer",
            display_name="Answer",
            method="lookup",
        ),
    ]

    def lookup(self) -> Message:
        api_key = os.getenv("EMPLOYEE_API_KEY")

        if not api_key:
            raise ValueError("EMPLOYEE_API_KEY is not configured in the Langflow environment.")

        question = str(self.question).strip()

        if not question:
            raise ValueError("Please enter a question.")

        if len(question) > 2000:
            raise ValueError("The question must be 2,000 characters or fewer.")

        request_body = json.dumps({"question": question, "limit": 3}).encode("utf-8")

        request = urllib.request.Request(
            url="http://host.docker.internal:8000/ask",
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310
                result = json.loads(response.read().decode("utf-8"))

        except urllib.error.HTTPError as exc:
            raise RuntimeError(
                f"FastAPI returned HTTP {exc.code}. Check API authentication and the FastAPI logs."
            ) from None

        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not connect to FastAPI: {exc.reason}") from None

        answer = result.get("answer", "No answer was returned.")
        citations = result.get("citations", [])

        citation_text = json.dumps(
            citations,
            ensure_ascii=False,
            indent=2,
        )

        self.status = "Employee HR policy lookup completed."

        return Message(text=f"{answer}\n\nSources:\n{citation_text}")
