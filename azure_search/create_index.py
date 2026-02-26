import os
from dotenv import load_dotenv
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
from azure.core.credentials import AzureKeyCredential
 
load_dotenv()
 
endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX")
 
credential = AzureKeyCredential(key)
index_client = SearchIndexClient(endpoint, credential)
 
# IMPORTANT: Embedding dimension
# text-embedding-3-small = 1536
VECTOR_DIMENSIONS = 1536
 
 
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
 
    SearchableField(
        name="content",
        type=SearchFieldDataType.String,
    ),
 
    SimpleField(
        name="source",
        type=SearchFieldDataType.String,
        filterable=True
    ),
 
    SimpleField(
        name="type",
        type=SearchFieldDataType.String,
        filterable=True
    ),
 
    # ✅ Correct Vector Field Definition
    SearchField(
        name="contentVector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=VECTOR_DIMENSIONS,
        vector_search_profile_name="my-vector-profile"
    )
]
 
 
# ✅ Vector configuration
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
 
index = SearchIndex(
    name=index_name,
    fields=fields,
    vector_search=vector_search
)
 
# Delete old index if exists (important when fixing schema)
try:
    index_client.delete_index(index_name)
    print("Old index deleted.")
except:
    pass
 
index_client.create_index(index)
print("✅ Index created successfully.")