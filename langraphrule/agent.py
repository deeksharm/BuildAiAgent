"""
LangGraph agentic AI wired to Azure AI Foundry (Azure OpenAI).

Architecture: classic ReAct-style tool-calling loop built with LangGraph's
StateGraph, so you can see and customize every part of the control flow
(instead of hiding it behind create_react_agent).

Flow:
    START -> agent (LLM decides: answer or call a tool)
          -> [conditional] -> tools (execute tool calls) -> agent (loop back)
          -> [conditional] -> END (LLM produced a final answer)

Run:
    python agent.py
"""

import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

# ---------------------------------------------------------------------------
# 1. Define tools
#    Replace these with real integrations: an internal API, a database
#    lookup, a search service, etc. Each tool needs a clear docstring —
#    the LLM reads it to decide when to call the tool.
# ---------------------------------------------------------------------------


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city name."""
    # Stub — swap in a real weather API call.
    fake_data = {
        "seattle": "58°F, light rain",
        "austin": "94°F, sunny",
        "new york": "71°F, partly cloudy",
    }
    return fake_data.get(city.lower(), f"No weather data found for {city}.")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '12 * (4 + 3)'."""
    try:
        # NOTE: eval() is fine for a local demo only. In production, use a
        # safe math parser (e.g. `numexpr` or `asteval`) instead of eval().
        allowed_chars = set("0123456789+-*/(). ")
        if not set(expression) <= allowed_chars:
            return "Error: expression contains disallowed characters."
        return str(eval(expression))
    except Exception as e:
        return f"Error evaluating expression: {e}"


tools = [get_weather, calculator]

# ---------------------------------------------------------------------------
# 2. Configure the Azure AI Foundry model
# ---------------------------------------------------------------------------

llm = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    temperature=0,
)

llm_with_tools = llm.bind_tools(tools)


# ---------------------------------------------------------------------------
# 3. Define graph state
# ---------------------------------------------------------------------------


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ---------------------------------------------------------------------------
# 4. Define nodes
# ---------------------------------------------------------------------------


def agent_node(state: AgentState) -> AgentState:
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


tool_node = ToolNode(tools)

# ---------------------------------------------------------------------------
# 5. Build the graph
# ---------------------------------------------------------------------------

graph_builder = StateGraph(AgentState)
graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "agent")
# tools_condition inspects the last message: if it has tool_calls, route to
# "tools"; otherwise route to END.
graph_builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
graph_builder.add_edge("tools", "agent")

graph = graph_builder.compile()


# ---------------------------------------------------------------------------
# 6. Run it
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Azure AI Foundry + LangGraph agent. Type 'exit' to quit.\n")

    conversation_state = {"messages": []}

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break

        conversation_state["messages"].append(HumanMessage(content=user_input))
        result = graph.invoke(conversation_state)
        conversation_state = result

        final_message = result["messages"][-1]
        print(f"Agent: {final_message.content}\n")
