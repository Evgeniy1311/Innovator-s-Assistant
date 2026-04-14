import httpx
import json
import asyncio
from typing import List, Dict, Any

async def search_patents(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Поиск патентов через PatentsView API (бесплатно, без ключа).
    Возвращает список словарей с полями title, abstract, id.
    """
    url = "https://api.patentsview.org/patents/"
    query_json = {
        "_or": [
            {"_text_any": {"patent_title": query}},
            {"_text_any": {"patent_abstract": query}}
        ]
    }
    params = {
        "q": json.dumps(query_json),
        "f": ["patent_title", "patent_abstract", "patent_id"],
        "o": json.dumps({"page": 1, "per_page": limit})
    }

    for attempt in range(3):
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
            print(f"Ошибка при поиске патентов (попытка {attempt+1}): {e}")
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)  # 1, 2, 4 сек
    return []