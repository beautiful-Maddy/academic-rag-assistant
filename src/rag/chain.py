from typing import Dict, Any
from langchain_openai import ChatOpenAI

from src.config import OPENAI_MODEL
from src.utils.prompts import RAG_PROMPT

def ask_rag(question: str, vectorstore, history: str) -> Dict[str, Any]:
    if vectorstore is None:
        return {
            "answer": "Le moteur RAG n'est pas encore chargé. Veuillez indexer ou charger les documents.",
            "sources": []
        }

    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    docs = retriever.invoke(question)

    if not docs:
        return {
            "answer": "Je n'ai trouvé aucun passage pertinent dans les notes de cours.",
            "sources": []
        }

    context_parts = []
    sources = []

    for doc in docs:
        source = doc.metadata.get("source", "source inconnue")
        page = doc.metadata.get("page", None)

        if page is not None:
            source_label = f"{source} - page {page + 1}"
        else:
            source_label = source

        context_parts.append(f"[Source: {source_label}]\n{doc.page_content}")

        if source_label not in sources:
            sources.append(source_label)

    context = "\n\n".join(context_parts)

    llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)
    prompt = RAG_PROMPT.format(
        history=history,
        context=context,
        question=question
    )
    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "sources": sources
    }