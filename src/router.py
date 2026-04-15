import json
from typing import Any, Dict

from langchain_openai import ChatOpenAI

from src.config import OPENAI_MODEL
from src.rag.chain import ask_rag
from src.rag.quiz import generate_quiz
from src.tools.calculator_tool import calculate
from src.tools.web_search_tool import web_search
from src.tools.todo_tool import add_task, list_tasks, remove_task
from src.utils.prompts import CHAT_PROMPT, AGENT_ROUTER_PROMPT


def fallback_route(question: str) -> Dict[str, str]:
    q = question.lower()

    if "quiz" in q or "qcm" in q or "questions de révision" in q:
        topic = question
        for prefix in [
            "Crée un quiz sur",
            "crée un quiz sur",
            "génère un quiz sur",
            "génère un quiz à partir de",
            "fais-moi un quiz sur",
            "fais moi un quiz sur",
        ]:
            topic = topic.replace(prefix, "")
        return {
            "route": "quiz",
            "reason": "fallback keyword quiz",
            "tool_input": topic.strip(" :.?")
        }

    if "ajoute" in q and ("todo" in q or "tâche" in q or "liste" in q):
        task = question
        for prefix in [
            "Ajoute à ma todo :",
            "ajoute à ma todo :",
            "Ajoute à ma todo",
            "ajoute à ma todo",
            "ajoute une tâche :",
            "Ajoute une tâche :",
            "ajoute une tâche",
            "Ajoute une tâche",
        ]:
            task = task.replace(prefix, "")
        return {
            "route": "todo_add",
            "reason": "fallback keyword todo add",
            "tool_input": task.strip()
        }

    if "affiche" in q and ("todo" in q or "tâches" in q or "liste" in q):
        return {
            "route": "todo_list",
            "reason": "fallback keyword todo list",
            "tool_input": ""
        }

    if ("supprime" in q or "retire" in q or "enlève" in q) and "tâche" in q:
        digits = "".join(ch for ch in question if ch.isdigit())
        return {
            "route": "todo_remove",
            "reason": "fallback keyword todo remove",
            "tool_input": digits
        }

    if any(op in q for op in ["+", "-", "*", "/"]) or "calcule" in q or "combien fait" in q:
        expr = question.lower().replace("calcule", "").replace("combien fait", "").strip(" ?=")
        return {
            "route": "calculator",
            "reason": "fallback keyword calculator",
            "tool_input": expr
        }

    if "web" in q or "internet" in q or "recherche" in q:
        query = question
        for prefix in [
            "Recherche web",
            "recherche web",
            "cherche sur le web",
            "Cherche sur le web",
            "cherche sur internet",
            "Cherche sur internet",
            "recherche sur internet",
        ]:
            query = query.replace(prefix, "")
        return {
            "route": "web_search",
            "reason": "fallback keyword web",
            "tool_input": query.strip(" :.?")
        }

    if any(k in q for k in ["cours", "chapitre", "notes", "document", "pdf", "selon le cours", "résume", "explique"]):
        return {
            "route": "rag",
            "reason": "fallback keyword rag",
            "tool_input": question
        }

    return {
        "route": "chat",
        "reason": "fallback default chat",
        "tool_input": question
    }


def agent_decide(question: str) -> Dict[str, str]:
    llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)

    prompt = AGENT_ROUTER_PROMPT.format(question=question)
    response = llm.invoke(prompt)

    try:
        decision = json.loads(response.content)

        if not isinstance(decision, dict):
            raise ValueError("JSON invalide")

        route = decision.get("route", "chat")
        reason = decision.get("reason", "aucune raison fournie")
        tool_input = decision.get("tool_input", question)

        allowed_routes = {
            "rag",
            "quiz",
            "calculator",
            "web_search",
            "todo_add",
            "todo_list",
            "todo_remove",
            "chat",
        }

        if route not in allowed_routes:
            raise ValueError(f"Route non autorisée : {route}")

        if tool_input is None:
            tool_input = ""

        return {
            "route": route,
            "reason": reason,
            "tool_input": str(tool_input).strip()
        }

    except Exception:
        return fallback_route(question)


def route_question(question: str, vectorstore, history: str) -> Dict[str, Any]:
    decision = agent_decide(question)

    route = decision["route"]
    reason = decision["reason"]
    tool_input = decision["tool_input"]

    if route == "rag":
        result = ask_rag(tool_input or question, vectorstore, history)
        return {
            "mode": "RAG",
            "decision_reason": reason,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    if route == "quiz":
        result = generate_quiz(tool_input or question, vectorstore, num_questions=5)
        return {
            "mode": "Quiz Generator",
            "decision_reason": reason,
            "answer": result["quiz"],
            "sources": result["sources"]
        }

    if route == "calculator":
        return {
            "mode": "Tool: Calculator",
            "decision_reason": reason,
            "answer": calculate(tool_input),
            "sources": []
        }

    if route == "web_search":
        return {
            "mode": "Tool: Web Search",
            "decision_reason": reason,
            "answer": web_search(tool_input),
            "sources": []
        }

    if route == "todo_add":
        return {
            "mode": "Tool: Todo",
            "decision_reason": reason,
            "answer": add_task(tool_input),
            "sources": []
        }

    if route == "todo_list":
        return {
            "mode": "Tool: Todo",
            "decision_reason": reason,
            "answer": list_tasks(),
            "sources": []
        }

    if route == "todo_remove":
        if not tool_input.isdigit():
            return {
                "mode": "Tool: Todo",
                "decision_reason": reason,
                "answer": "Merci d'indiquer le numéro de la tâche à supprimer.",
                "sources": []
            }

        return {
            "mode": "Tool: Todo",
            "decision_reason": reason,
            "answer": remove_task(int(tool_input)),
            "sources": []
        }

    llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0.3)
    prompt = CHAT_PROMPT.format(history=history, question=question)
    response = llm.invoke(prompt)

    return {
        "mode": "Chat",
        "decision_reason": reason,
        "answer": response.content,
        "sources": []
    }