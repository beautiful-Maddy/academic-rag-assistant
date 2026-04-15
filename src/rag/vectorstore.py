from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from src.config import OPENAI_EMBEDDING_MODEL, CHROMA_PATH

def build_vectorstore(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    return vectorstore

def load_vectorstore():
    embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )