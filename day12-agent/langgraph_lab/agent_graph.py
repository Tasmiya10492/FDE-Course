"""YOUR TASK, part 2 (day 12): build the SAME agent as a LangGraph graph.

Run the tests any time:   uv run pytest -q -k graph

LangGraph is an open-source (MIT) Python library for stateful agents. The ideas:

    STATE          the data that flows through the graph (messages and an audit list)
    NODES          plain functions that read the state and return changes to it
    EDGES          which node runs next; a CONDITIONAL edge chooses the next node
    CHECKPOINTER   saves the state after each step so a graph can pause and resume
    INTERRUPT      pauses the graph and waits for a human; resume with Command(resume=...)

Read, in this order:
  https://docs.langchain.com/oss/python/langgraph/quickstart
  https://docs.langchain.com/oss/python/langgraph/interrupts
  https://docs.langchain.com/oss/python/langgraph/errors/GRAPH_RECURSION_LIMIT

The picture to build:

    START -> llm_call --(model asked for tools?)--> tool_node -> llm_call ...
                      \\--(no)--> END
"""

"""Day 12: the same tool-using agent implemented with LangGraph.

Run graph tests with:
    uv run pytest -q -k graph
"""

import operator
import time
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from llm import ChatModel
from tools import Tool, build_tools, validate_arguments


class AgentState(TypedDict):
    """Data passed between LangGraph nodes."""

    messages: Annotated[list[dict], operator.add]
    audit: Annotated[list[str], operator.add]
    total_tokens: int
    estimated_cost_usd: float
    start_time: float
    max_seconds: float
    max_total_tokens: int
    max_output_tokens: int
    max_cost_usd: float | None
    input_cost_per_million: float
    output_cost_per_million: float


def build_graph(
    model: ChatModel,
    tools: dict[str, Tool] | None = None,
):
    """Build and compile the tool-using agent graph."""

    available_tools = tools if tools is not None else build_tools()

    def llm_call(state: AgentState):
        """Call the model while enforcing execution budgets."""

        # 1. Check the execution-time budget before calling the model.
        if time.monotonic() - state["start_time"] >= state["max_seconds"]:
            return {
                "messages": [
                    {
                        "role": "assistant",
                        "content": "Stopped: time limit reached.",
                    }
                ],
                "audit": ["agent: time limit reached"],
            }

        # 2. Check the remaining token budget.
        remaining_tokens = state["max_total_tokens"] - state["total_tokens"]

        if remaining_tokens <= 0:
            return {
                "messages": [
                    {
                        "role": "assistant",
                        "content": "Stopped: token budget reached.",
                    }
                ],
                "audit": ["agent: token budget reached"],
            }

        # 3. Check the cost budget before calling the model.
        if state["max_cost_usd"] is not None and state["estimated_cost_usd"] >= state["max_cost_usd"]:
            return {
                "messages": [
                    {
                        "role": "assistant",
                        "content": "Stopped: cost budget reached.",
                    }
                ],
                "audit": ["agent: cost budget reached"],
            }

        # 4. Ask the model to answer or select a tool.
        reply = model.chat(
            state["messages"],
            [tool.schema() for tool in available_tools.values()],
            max_tokens=min(
                state["max_output_tokens"],
                remaining_tokens,
            ),
        )

        # 5. Extract usage information from the model response.
        usage = reply.get("usage") or {}

        prompt_tokens = int(usage.get("prompt_tokens") or 0)
        completion_tokens = int(usage.get("completion_tokens") or 0)

        call_tokens = int(usage.get("total_tokens") or prompt_tokens + completion_tokens)

        new_total_tokens = state["total_tokens"] + call_tokens

        # 6. Calculate the estimated cost of this model call.
        new_cost = (
            prompt_tokens * state["input_cost_per_million"]
            + completion_tokens * state["output_cost_per_million"]
        ) / 1_000_000

        estimated_cost = state["estimated_cost_usd"] + new_cost

        # 7. Remove usage metadata before adding the message to history.
        message = {key: value for key, value in reply.items() if key != "usage"}

        # 8. Check the time again because the model call may be slow.
        time_limit_reached = time.monotonic() - state["start_time"] >= state["max_seconds"]

        audit = []

        # 9. Record token and cost usage in the audit log.
        if usage:
            audit.append(
                f"usage: prompt={prompt_tokens}, "
                f"completion={completion_tokens}, "
                f"total={call_tokens}, "
                f"estimated_cost_usd={estimated_cost:.8f}"
            )

        # 10. If a limit has been reached, discard any tool calls
        # from this response. Do not execute them.
        if time_limit_reached:
            message = {
                "role": "assistant",
                "content": "Stopped: time limit reached.",
            }
            audit.append("agent: time limit reached")

        elif new_total_tokens >= state["max_total_tokens"]:
            message = {
                "role": "assistant",
                "content": "Stopped: token budget reached.",
            }
            audit.append("agent: token budget reached")

        elif state["max_cost_usd"] is not None and estimated_cost >= state["max_cost_usd"]:
            message = {
                "role": "assistant",
                "content": "Stopped: cost budget reached.",
            }
            audit.append("agent: cost budget reached")

        return {
            "messages": [message],
            "total_tokens": new_total_tokens,
            "estimated_cost_usd": estimated_cost,
            "audit": audit,
        }

    def tool_node(state: AgentState):
        """Validate and execute requested tools."""

        reply = state["messages"][-1]
        messages = []
        audit = []

        for call in reply.get("tool_calls") or []:
            name = call.get("name", "")
            call_id = call.get("id", "")
            arguments = call.get("arguments", {})
            result = ""

            tool = available_tools.get(name)

            # 1. Reject unknown tools.
            if tool is None:
                result = f"Unknown tool: {name}"
                audit.append(f"{name}: error: unknown tool")

            # 2. Reject arguments that are not objects.
            elif not isinstance(arguments, dict):
                result = "Invalid arguments: expected an object."
                audit.append(f"{name}: invalid arguments")

            else:
                # 3. Validate the arguments against the tool schema.
                problem = validate_arguments(tool, arguments)

                if problem:
                    result = f"Invalid arguments: {problem}"
                    audit.append(f"{name}: invalid arguments: {problem}")

                # 4. Side-effect tools require human approval.
                elif tool.needs_approval:
                    approved = interrupt(
                        {
                            "tool": name,
                            "arguments": arguments,
                            "preview": tool.preview(arguments),
                        }
                    )

                    if not approved:
                        result = "Action denied by human."
                        audit.append(f"{name}: denied by human")

                    else:
                        try:
                            result = tool.run(arguments)
                            audit.append(f"{name}: ran with {arguments}")

                        except Exception as exc:  # noqa: BLE001
                            result = f"Tool error: {exc}"
                            audit.append(f"{name}: error: {exc}")

                # 5. Read-only tools do not require approval.
                else:
                    try:
                        result = tool.run(arguments)
                        audit.append(f"{name}: ran with {arguments}")

                    except Exception as exc:  # noqa: BLE001
                        result = f"Tool error: {exc}"
                        audit.append(f"{name}: error: {exc}")

            # 6. Return the tool result to the model as a message.
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": name,
                    "content": str(result),
                }
            )

        return {
            "messages": messages,
            "audit": audit,
        }

    def should_continue(state: AgentState):
        """Choose whether to execute tools or finish the graph."""

        last_message = state["messages"][-1]

        # No tool calls means the model has finished.
        if not last_message.get("tool_calls"):
            return END

        # Stop if the execution-time budget has expired.
        if time.monotonic() - state["start_time"] >= state["max_seconds"]:
            return END

        # Stop if the token budget has been reached.
        if state["total_tokens"] >= state["max_total_tokens"]:
            return END

        # Stop if the cost budget has been reached.
        if state["max_cost_usd"] is not None and state["estimated_cost_usd"] >= state["max_cost_usd"]:
            return END

        return "tool_node"

    # Define the graph.
    builder = StateGraph(AgentState)

    builder.add_node("llm_call", llm_call)
    builder.add_node("tool_node", tool_node)

    # START -> model -> conditional route.
    builder.add_edge(START, "llm_call")
    builder.add_conditional_edges("llm_call", should_continue)

    # After tool execution, ask the model again.
    builder.add_edge("tool_node", "llm_call")

    # Compile with a checkpointer so interrupted runs can resume.
    return builder.compile(checkpointer=InMemorySaver())


def start(
    graph,
    question: str,
    thread_id: str,
    max_steps: int = 10,
    max_seconds: float = 30.0,
    max_output_tokens: int = 500,
    max_total_tokens: int = 4000,
    max_cost_usd: float | None = None,
    input_cost_per_million: float = 0.0,
    output_cost_per_million: float = 0.0,
) -> dict:
    """Start a new graph execution."""

    # Validate execution limits.
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

    # LangGraph uses this configuration for checkpointing and recursion.
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": max_steps,
    }

    # Initial state for this conversation.
    initial_state = {
        "messages": [
            {
                "role": "user",
                "content": question,
            }
        ],
        "audit": [],
        "total_tokens": 0,
        "estimated_cost_usd": 0.0,
        "start_time": time.monotonic(),
        "max_seconds": max_seconds,
        "max_total_tokens": max_total_tokens,
        "max_output_tokens": max_output_tokens,
        "max_cost_usd": max_cost_usd,
        "input_cost_per_million": input_cost_per_million,
        "output_cost_per_million": output_cost_per_million,
    }

    # Execute the graph.
    # GraphRecursionError is intentionally allowed to propagate.
    result = graph.invoke(initial_state, config)

    # If a tool needs approval, return the approval request.
    if result.get("__interrupt__"):
        request = result["__interrupt__"][0].value

        return {
            "status": "needs_approval",
            "request": request,
        }

    # Return the final result.
    return {
        "status": "done",
        "answer": result["messages"][-1].get("content", ""),
        "audit": result.get("audit", []),
        "total_tokens": result.get("total_tokens", 0),
        "estimated_cost_usd": result.get(
            "estimated_cost_usd",
            0.0,
        ),
    }


def resume(
    graph,
    thread_id: str,
    approved: bool,
    max_steps: int = 10,
) -> dict:
    """Resume an interrupted graph after human approval or denial."""

    if max_steps <= 0:
        raise ValueError("max_steps must be positive.")

    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": max_steps,
    }

    # Resume the paused node with the human's decision.
    result = graph.invoke(
        Command(resume=approved),
        config,
    )

    # The graph may pause again if another tool needs approval.
    if result.get("__interrupt__"):
        request = result["__interrupt__"][0].value

        return {
            "status": "needs_approval",
            "request": request,
        }

    return {
        "status": "done",
        "answer": result["messages"][-1].get("content", ""),
        "audit": result.get("audit", []),
        "total_tokens": result.get("total_tokens", 0),
        "estimated_cost_usd": result.get(
            "estimated_cost_usd",
            0.0,
        ),
    }
