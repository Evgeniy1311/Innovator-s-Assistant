import httpx

async def search_papers(query: str, limit: int = 5) -> list[dict]:
    """
    Поиск научных статей через Semantic Scholar API (бесплатно, без ключа).
    Возвращает список словарей с полями title, abstract, paperId.
    """
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,paperId"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
        papers = []
        for paper in data.get("data", []):
            papers.append({
                "title": paper.get("title", ""),
                "abstract": paper.get("abstract", ""),
                "id": paper.get("paperId", "")
            })
        return papers
    except Exception as e:
        print(f"Ошибка при поиске научных статей: {e}")
        return []
