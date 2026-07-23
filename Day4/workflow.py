Paste your LangGraph workflow code.
from typing import TypedDict

from langgraph.graph import StateGraph, END

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

from dotenv import load_dotenv

from openai import AzureOpenAI

import os

# -----------------------------
# LOAD ENV VARIABLES
# -----------------------------

load_dotenv()

# -----------------------------
# AZURE OPENAI
# -----------------------------

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# -----------------------------
# AZURE AI SEARCH
# -----------------------------

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
    credential=AzureKeyCredential(
        os.getenv("AZURE_SEARCH_KEY")
    )
)

# -----------------------------
# STATE
# -----------------------------

class BankingState(TypedDict):

    user_input: str

    retrieved_context: str

    final_result: str

# -----------------------------
# RETRIEVAL NODE
# -----------------------------

def retrieval_node(state):

    query = state["user_input"]

    results = search_client.search(
        search_text=query,
        top=3
    )

    context = ""

    for result in results:

        if "chunk" in result:

            context += result["chunk"] + "\n\n"

        elif "content" in result:

            context += result["content"] + "\n\n"

    return {

        "retrieved_context": context
    }

# -----------------------------
# ANALYSIS NODE
# -----------------------------

def analysis_node(state):

    prompt = f"""
You are an Enterprise Banking AI Assistant.

Answer ONLY using the banking policy context below.

If information is unavailable,
say:
"Information not available in banking policies."

=============================
BANKING POLICY CONTEXT
=============================

{state['retrieved_context']}

=============================
USER QUESTION
=============================

{state['user_input']}
"""

    response = client.chat.completions.create(

        model=deployment,

        messages=[

            {
                "role": "system",
                "content": "You are a professional banking AI assistant."
            },

            {
                "role": "user",
                "content": prompt
            }

        ],

        temperature=0.3
    )

    answer = response.choices[0].message.content

    return {

        "final_result": answer
    }

# -----------------------------
# LANGGRAPH WORKFLOW
# -----------------------------

workflow = StateGraph(BankingState)

workflow.add_node(
    "retrieval",
    retrieval_node
)

workflow.add_node(
    "analysis",
    analysis_node
)

workflow.set_entry_point(
    "retrieval"
)

workflow.add_edge(
    "retrieval",
    "analysis"
)

workflow.add_edge(
    "analysis",
    END
)

# -----------------------------
# COMPILE GRAPH
# -----------------------------

graph = workflow.compile()
