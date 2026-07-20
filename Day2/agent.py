import os
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AzureAISearchTool

# Load .env
load_dotenv()

# Configuration
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")
MODEL = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

# Connect to Azure AI Foundry
project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

# Connect Azure AI Search Index
search = AzureAISearchTool(
    index_connection={
        "endpoint": SEARCH_ENDPOINT,
        "index_name": SEARCH_INDEX,
    }
)

# Create Agent
agent = project.agents.create_agent(
    name="blob-rag-agent",
    model=MODEL,
    instructions="""
You are a helpful AI Assistant.

Always answer from the Azure AI Search knowledge base.

If the answer is not found, say:
'I could not find that information in the knowledge base.'
""",
    tools=search.definitions,
    tool_resources=search.resources,
)

print(f"Agent Created: {agent.id}")

# Create Conversation Thread
thread = project.agents.create_thread()

print(f"Thread Created: {thread.id}")

# Conversation Loop
while True:

    question = input("\nYou: ")

    if question.lower() == "exit":
        break

    # Add user message
    project.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=question,
    )

    # Run agent
    run = project.agents.create_run(
        thread_id=thread.id,
        agent_id=agent.id,
    )

    # Wait until completed
    project.agents.process_run(run, thread)

    # Read latest assistant response
    messages = project.agents.list_messages(thread.id)

    for message in reversed(messages.data):

        if message.role == "assistant":

            print("\nAssistant:")

            for part in message.content:
                if hasattr(part, "text"):
                    print(part.text.value)

            break
