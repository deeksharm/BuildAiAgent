"""
search.py

Generates an embedding for the user's question
and performs vector search in Azure AI Search.
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

# -------------------------------------
# Load Environment Variables
# -------------------------------------

load_dotenv()

# -------------------------------------
# Azure OpenAI Client
# -------------------------------------

openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

EMBEDDING_MODEL = os.getenv("EMBEDDING_DEPLOYMENT")

# -------------------------------------
# Azure AI Search Client
# -------------------------------------

search_client = SearchClient(
    endpoint=os.getenv("SEARCH_ENDPOINT"),
    index_name=os.getenv("SEARCH_INDEX"),
    credential=AzureKeyCredential(os.getenv("SEARCH_API_KEY"))
)


def generate_query_embedding(question):
    """
    Convert the user question into an embedding.
    """

    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=question
    )

    return response.data[0].embedding


def search_documents(question, top_k=3):
    """
    Perform vector search.
    """

    question_embedding = generate_query_embedding(question)

    vector_query = VectorizedQuery(
        vector=question_embedding,
        k_nearest_neighbors=top_k,
        fields="embedding"
    )

    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=[
            "id",
            "content",
            "source"
        ]
    )

    documents = []

    for result in results:

        documents.append(
            {
                "id": result["id"],
                "source": result["source"],
                "content": result["content"]
            }
        )

    return documents


def main():

    print("=" * 60)
    print("Azure AI Search")
    print("=" * 60)

    while True:

        question = input("\nAsk a question (type exit): ")

        if question.lower() == "exit":
            break

        documents = search_documents(question)

        print("\nRelevant Chunks\n")

        if len(documents) == 0:

            print("No documents found.")

            continue

        for i, doc in enumerate(documents, start=1):

            print("=" * 60)
            print(f"Result {i}")
            print("=" * 60)

            print("Source :", doc["source"])
            print()
            print(doc["content"])
            print()


if __name__ == "__main__":
    main()
