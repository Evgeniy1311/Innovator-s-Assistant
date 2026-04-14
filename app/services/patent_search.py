import httpx
import json

async def search_patents(query: str, limit: int = 5) -> list[dict]:
    """
    Поиск патентов через PatentsView API (бесплатно, без ключа).
    Возвращает список словарей с полями title, abstract, id.
    """
    url = "https://search.patentsview.org/api/v1/patent/"
    query_json = {
        "_or": [
            {"_text_any": {"patent_title": query}},
            {"_text_any": {"patent_abstract": query}}
        ]
    }
    params = {
        "q": json.dumps(query_json),
        "f": ["patent_title", "patent_abstract", "patent_id"],
        "o": {"page": 1, "per_page": limit}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
        patents = []
        for patent in data.get("patents", []):
            patents.append({
                "title": patent.get("patent_title", ""),
                "abstract": patent.get("patent_abstract", ""),
                "id": patent.get("patent_id", "")
            })
        return patents
    except Exception as e:
        print(f"Ошибка при поиске патентов: {e}")
        return []
