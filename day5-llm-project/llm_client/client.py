import time

import httpx

from llm_client.config import Settings, get_settings
from llm_client.exceptions import (
    LLMAPIError,
    LLMConnectionError,
)
from llm_client.models import LLMResponse, TokenUsage


class LLMClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> LLMResponse:

        models = [
            self.settings.model,
            *self.settings.fallback_model_list,
        ]

        last_error = None

        for model in models:
            try:
                return self._send_request(messages, model, temperature, seed)

            except LLMAPIError as error:
                last_error = error

                if error.status_code not in (429, 500, 502, 503, 504):
                    raise

            except LLMConnectionError as error:
                last_error = error

        raise last_error or LLMAPIError("No models available")

    def _send_request(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float,
        seed: int | None = None,
    ) -> LLMResponse:

        url = f"{self.settings.base_url.rstrip('/')}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        if seed is not None:
            payload["seed"] = seed

        if self.settings.provider == "ollama":
            payload["reasoning_effort"] = "none"

        for attempt in range(self.settings.max_retries + 1):
            try:
                response = httpx.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.settings.timeout,
                )

                if response.status_code in (429, 500, 502, 503, 504):
                    response.raise_for_status()

                response.raise_for_status()

                data = response.json()

                choice = data["choices"][0]
                message = choice["message"]

                usage_data = data.get("usage")

                usage = (
                    TokenUsage(
                        prompt_tokens=usage_data.get("prompt_tokens"),
                        completion_tokens=usage_data.get("completion_tokens"),
                        total_tokens=usage_data.get("total_tokens"),
                    )
                    if usage_data
                    else None
                )

                return LLMResponse(
                    content=message.get("content") or "",
                    model=data.get("model", model),
                    usage=usage,
                    finish_reason=choice.get("finish_reason"),
                )

            except httpx.HTTPStatusError as error:
                status = error.response.status_code

                if status not in (429, 500, 502, 503, 504):
                    raise LLMAPIError(
                        f"LLM API returned HTTP {status}",
                        status_code=status,
                    ) from error

                if attempt == self.settings.max_retries:
                    raise LLMAPIError(
                        f"LLM API failed after retries: HTTP {status}",
                        status_code=status,
                    ) from error

                time.sleep(2**attempt)

            except (httpx.TimeoutException, httpx.ConnectError) as error:
                if attempt == self.settings.max_retries:
                    raise LLMConnectionError(
                        "Unable to connect to the LLM server."
                    ) from error

                time.sleep(2**attempt)

        raise LLMAPIError("LLM request failed")
