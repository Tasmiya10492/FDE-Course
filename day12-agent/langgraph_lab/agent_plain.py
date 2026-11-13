"""YOUR TASK, part 1 (day 12): build the agent loop in plain Python.

An agent is a loop:
    ask the model -> does it want a tool? -> run the tool
    -> give the result back -> repeat

The loop needs hard limits, and anything that changes data
needs human approval.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass, field

from llm import ChatModel
from memory import get_conversation, get_user_memory, save_conversation
from tools import Tool, build_tools, validate_arguments


@dataclass
class AgentResult:
    answer: str
    steps: int
    stopped_by: str = "answer"
    audit: list[str] = field(default_factory=list)
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


def run_agent(
    question: str,
    model: ChatModel,
    approve: Callable[[str], bool],
    tools: dict[str, Tool] | None = None,
    max_steps: int = 6,
    max_seconds: float = 30.0,
    user_id: str | None = None,
    thread_id: str | None = None,
    max_output_tokens: int = 500,
    max_total_tokens: int = 4000,
    max_cost_usd: float | None = None,
    input_cost_per_million: float = 0.0,
    output_cost_per_million: float = 0.0,
) -> AgentResult:

    # Validate limits and pricing configuration.
    if max_steps <= 0:
        raise ValueError("max_steps must be positive.")

    if max_seconds <= 0:
        raise ValueError("max_seconds must be positive.")

    if max_output_tokens <= 0 or max_total_tokens <= 0:
        raise ValueError("Token limits must be positive.")

    if max_cost_usd is not None and max_cost_usd <= 0:
        raise ValueError("max_cost_usd must be positive.")

    if max_cost_usd is not None and (input_cost_per_million <= 0 or output_cost_per_million <= 0):
        raise ValueError("Cost rates must be positive when max_cost_usd is set.")

    available_tools = tools if tools is not None else build_tools()

    audit = []
    steps = 0
    total_tokens = 0
    estimated_cost_usd = 0.0
    start_time = time.monotonic()

    # Load previous conversation only when both IDs are supplied.
    use_memory = bool(user_id and thread_id)

    if use_memory:
        messages = get_conversation(user_id, thread_id)

        # Add relevant user memory only when starting a new thread.
        if not messages:
            facts = get_user_memory(user_id)

            if facts:
                messages.append(
                    {
                        "role": "system",
                        "content": "Relevant user memory: " + "; ".join(facts),
                    }
                )

        messages.append({"role": "user", "content": question})

    else:
        messages = [{"role": "user", "content": question}]

    # Save the conversation whenever the agent finishes.
    def finish(answer: str, stopped_by: str) -> AgentResult:
        if use_memory:
            save_conversation(user_id, thread_id, messages)

        return AgentResult(
            answer=answer,
            steps=steps,
            stopped_by=stopped_by,
            audit=audit,
            total_tokens=total_tokens,
            estimated_cost_usd=round(estimated_cost_usd, 8),
        )

    # Main agent loop.
    while steps < max_steps:
        # Check hard limits before making another model request.
        if time.monotonic() - start_time >= max_seconds:
            return finish("Stopped: time limit reached.", "time_limit")

        if total_tokens >= max_total_tokens:
            return finish("Stopped: token budget reached.", "token_limit")

        if max_cost_usd is not None and estimated_cost_usd >= max_cost_usd:
            return finish("Stopped: cost budget reached.", "cost_limit")

        steps += 1

        # Ask the model what to do next.
        try:
            reply = model.chat(
                messages,
                [tool.schema() for tool in available_tools.values()],
                max_tokens=min(
                    max_output_tokens,
                    max_total_tokens - total_tokens,
                ),
            )

        except Exception as exc:  # noqa: BLE001
            audit.append(f"model: error: {exc}")
            return finish(f"Model error: {exc}", "answer")

        # Extract usage metadata separately from the chat message.
        usage = reply.get("usage") or {}

        # Do not put usage metadata into the conversation history.
        messages.append({key: value for key, value in reply.items() if key != "usage"})

        prompt_tokens = int(usage.get("prompt_tokens") or 0)
        completion_tokens = int(usage.get("completion_tokens") or 0)

        call_tokens = int(usage.get("total_tokens") or (prompt_tokens + completion_tokens))

        total_tokens += call_tokens

        # Estimate cost using the configured provider pricing.
        estimated_cost_usd += (
            prompt_tokens * input_cost_per_million + completion_tokens * output_cost_per_million
        ) / 1_000_000

        # Log usage only when the provider supplies usage information.
        if usage:
            audit.append(
                f"usage: prompt={prompt_tokens}, "
                f"completion={completion_tokens}, "
                f"total={call_tokens}, "
                f"estimated_cost_usd={estimated_cost_usd:.8f}"
            )

        # Stop before executing tools or making another model request.
        if total_tokens >= max_total_tokens:
            return finish("Stopped: token budget reached.", "token_limit")

        if max_cost_usd is not None and estimated_cost_usd >= max_cost_usd:
            return finish("Stopped: cost budget reached.", "cost_limit")

        # Check whether the model wants to call tools.
        tool_calls = reply.get("tool_calls") or []

        # No tool calls means the model has produced its final answer.
        if not tool_calls:
            return finish(reply.get("content", ""), "answer")

        # Execute each requested tool.
        for call in tool_calls:
            name = call.get("name", "")
            call_id = call.get("id", "")
            arguments = call.get("arguments", {})
            result = ""

            tool = available_tools.get(name)

            if tool is None:
                result = f"Unknown tool: {name}"
                audit.append(f"{name}: error: unknown tool")

            elif not isinstance(arguments, dict):
                result = "Invalid arguments: expected an object."
                audit.append(f"{name}: invalid arguments")

            else:
                problem = validate_arguments(tool, arguments)

                if problem:
                    result = f"Invalid arguments: {problem}"
                    audit.append(f"{name}: invalid arguments: {problem}")

                # Side-effect tools require human approval.
                elif tool.needs_approval:
                    try:
                        approved = approve(tool.preview(arguments))

                    except Exception as exc:  # noqa: BLE001
                        approved = False
                        result = f"Approval error: {exc}"

                    if not approved:
                        if not result:
                            result = "Action denied by human."

                        audit.append(f"{name}: denied")

                    else:
                        try:
                            result = tool.run(arguments)
                            audit.append(f"{name}: ran with {arguments}")

                        except Exception as exc:  # noqa: BLE001
                            result = f"Tool error: {exc}"
                            audit.append(f"{name}: error: {exc}")

                # Read-only tools can run without human approval.
                else:
                    try:
                        result = tool.run(arguments)
                        audit.append(f"{name}: ran with {arguments}")

                    except Exception as exc:  # noqa: BLE001
                        result = f"Tool error: {exc}"
                        audit.append(f"{name}: error: {exc}")

            # Return the tool result to the model in the next loop.
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": name,
                    "content": str(result),
                }
            )

            # Check the time limit after tool execution too.
            if time.monotonic() - start_time >= max_seconds:
                return finish("Stopped: time limit reached.", "time_limit")

    return finish("Stopped: step limit reached.", "step_limit")
