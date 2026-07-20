"""
ingest.py

Reads documents from Azure Blob Storage,
creates chunks,
generates embeddings using Azure OpenAI,
uploads them to Azure AI Search.
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.storage.blob import BlobServiceClient

from utils import prepare_chunks

# -----------------------------
# Load Environment Variables
# -----------------------------

load_dotenv()

# -----------------------------
# Azure OpenAI Client
# -----------------------------

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

EMBEDDING_MODEL = os.getenv("EMBEDDING_DEPLOYMENT")

# -----------------------------
# Azure AI Search Client
# -----------------------------

search_client = SearchClient(
    endpoint=os.getenv("SEARCH_ENDPOINT"),
    index_name=os.getenv("SEARCH_INDEX"),
    credential=AzureKeyCredential(os.getenv("SEARCH_API_KEY"))
)

# -----------------------------
# Azure Blob Storage Client
# -----------------------------

blob_service_client = BlobServiceClient.from_connection_string(
    os.getenv("AZURE_STORAGE_CONNECTION_STRING")
)

container_client = blob_service_client.get_container_client(
    os.getenv("BLOB_CONTAINER_NAME")
)

# -----------------------------
# Read Documents from Blob Storage
# -----------------------------

def read_documents():

    documents = []

    print("\nReading documents from Azure Blob Storage...\n")

    for blob in container_client.list_blobs():

        print(f"Downloading : {blob.name}")

        blob_client = container_client.get_blob_client(blob.name)

        content = blob_client.download_blob().readall().decode("utf-8")

        documents.append(
            {
                "filename": blob.name,
                "content": content
            }
        )

    return documents


# -----------------------------
# Generate Embedding
# -----------------------------

def generate_embedding(text):

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response.data[0].embedding


# -----------------------------
# Upload Documents
# -----------------------------

def upload_documents(documents):

    print("\nUploading documents to Azure AI Search...\n")

    result = search_client.upload_documents(documents)

    success = 0

    for item in result:

        if item.succeeded:
            success += 1

    print("=" * 50)
    print(f"Uploaded {success}/{len(documents)} documents")
    print("=" * 50)


# -----------------------------
# Main
# -----------------------------

def main():

    print("=" * 60)
    print("Loading Documents")
    print("=" * 60)

    documents = read_documents()

    print(f"Documents Loaded : {len(documents)}")

    chunks = prepare_chunks(documents)

    print(f"Chunks Created : {len(chunks)}")

    embedded_chunks = []

    print("\nGenerating Embeddings...\n")

    for i, chunk in enumerate(chunks):

        embedding = generate_embedding(chunk["content"])

        embedded_chunks.append(
            {
                "id": str(i),
                "content": chunk["content"],
                "source": chunk["filename"],
                "embedding": embedding
            }
        )

        print(f"Processed Chunk {i+1}/{len(chunks)}")

    print("\nEmbedding Generation Completed")

    upload_documents(embedded_chunks)

    print("\nCompleted Successfully")


if __name__ == "__main__":
    main()
