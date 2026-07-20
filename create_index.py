"""
create_index.py

Creates an Azure AI Search Vector Index
"""

import os
from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential

from azure.search.documents.indexes import SearchIndexClient

from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile
)

# --------------------------------------
# Load Environment Variables
# --------------------------------------

load_dotenv()

SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
INDEX_NAME = os.getenv("SEARCH_INDEX")

# --------------------------------------
# Create Search Client
# --------------------------------------

credential = AzureKeyCredential(SEARCH_API_KEY)

index_client = SearchIndexClient(
    endpoint=SEARCH_ENDPOINT,
    credential=credential
)

# --------------------------------------
# Configure Vector Search
# --------------------------------------

vector_search = VectorSearch(

    algorithms=[
        HnswAlgorithmConfiguration(
            name="my-hnsw-config"
        )
    ],

    profiles=[
        VectorSearchProfile(
            name="my-vector-profile",
            algorithm_configuration_name="my-hnsw-config"
        )
    ]
)

# --------------------------------------
# Define Fields
# --------------------------------------

fields = [

    SimpleField(
        name="id",
        type=SearchFieldDataType.String,
        key=True
    ),

    SearchableField(
        name="content",
        type=SearchFieldDataType.String
    ),

    SearchableField(
        name="source",
        type=SearchFieldDataType.String
    ),

    SearchField(
        name="embedding",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),

        vector_search_dimensions=1536,

        vector_search_profile_name="my-vector-profile"
    )

]

# --------------------------------------
# Create Index
# --------------------------------------

index = SearchIndex(
    name=INDEX_NAME,
    fields=fields,
    vector_search=vector_search
)

try:

    index_client.create_index(index)

    print("=" * 60)
    print("Index Created Successfully")
    print("=" * 60)

except Exception as ex:

    print("=" * 60)
    print("Error")
    print("=" * 60)
    print(ex)
