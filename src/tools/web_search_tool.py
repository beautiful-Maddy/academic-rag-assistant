from duckduckgo_search import DDGS

def web_search(query: str, max_results: int = 5) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return "Aucun résultat trouvé."

        formatted = []
        for i, result in enumerate(results, start=1):
            title = result.get("title", "Sans titre")
            body = result.get("body", "")
            href = result.get("href", "")
            formatted.append(f"{i}. {title}\n{body}\n{href}")

        return "\n\n".join(formatted)

    except Exception as e:
        return f"Erreur recherche web : {e}"