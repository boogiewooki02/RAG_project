from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

vector_store = Chroma(
    collection_name="card_info",
    embedding_function=embedding_model,
    persist_directory="../data/chroma_db",
)

retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)