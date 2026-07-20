
"""
app.py

Main RAG Application

Workflow:
User Question
    ↓
Azure AI Search
    ↓
Relevant Chunks
    ↓
GPT-4.1-mini
    ↓
Answer
"""

import os

from dotenv import load_dotenv
from openai import AzureOpenAI

from search import search_documents

# Load environment variables
load_dotenv()

# Azure OpenAI Client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

CHAT_MODEL = os.getenv("CHAT_DEPLOYMENT")


def ask_rag(question):
    """
    Retrieve relevant documents and ask GPT.
    """

    # Retrieve relevant chunks
    documents = search_documents(question)

    context = ""

    for doc in documents:
        context += f"\nSource: {doc['source']}\n"
        context += doc["content"]
        context += "\n\n"

    prompt = f"""
You are an AI assistant.

Answer ONLY from the provided context.

If the answer is not available,
reply:

"I couldn't find that information in the documents."

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You answer only using the provided context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


def main():

    print("=" * 60)
    print("Enterprise RAG Chatbot")
    print("=" * 60)

    while True:

        question = input("\nAsk a question (type 'exit' to quit): ")

        if question.lower() == "exit":
            break

        print("\nSearching documents...")

        answer = ask_rag(question)

        print("\nAnswer")
        print("-" * 60)
        print(answer)


if __name__ == "__main__":
    main()
