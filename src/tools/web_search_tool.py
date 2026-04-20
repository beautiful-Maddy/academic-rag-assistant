from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

def web_search(query: str, max_results: int = 5) -> str:
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True 
        )

        # 👉 ICI
        answer = response.get("answer", "")

        results = response.get("results", [])

        if not results:
            return "Aucun résultat trouvé."

        formatted = []

        # 👉 on ajoute la réponse synthétique en haut
        if answer:
            formatted.append(f"🧠 Réponse rapide :\n{answer}\n")

        for i, result in enumerate(results, start=1):
            title = result.get("title", "Sans titre")
            content = result.get("content", "")
            url = result.get("url", "")

            formatted.append(f"{i}. {title}\n{content}\n{url}")

        return "\n\n".join(formatted)

    except Exception as e:
        return f"Erreur recherche web : {e}"