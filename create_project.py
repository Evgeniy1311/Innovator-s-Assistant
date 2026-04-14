#!/usr/bin/env python3
"""
Скрипт для создания структуры проекта "Innovator's Assistant"
Запуск: python create_project.py
"""

import os

# Содержимое файлов
FILES = {
    "requirements.txt": """fastapi==0.115.6
uvicorn[standard]==0.30.6
pydantic==2.9.2
python-dotenv==1.0.1
openai==1.55.0
langchain==0.3.7
langchain-openai==0.2.6
langchain-community==0.3.5
httpx==0.27.2
faiss-cpu==1.9.0
tiktoken==0.7.0
pypdf==4.3.1
python-multipart==0.0.12
""",

    ".env": """# === Конфигурация LLM ===
# По умолчанию настроено на Groq (бесплатно, быстро, требует регистрации)
# Получить ключ: https://console.groq.com/keys

OPENAI_API_KEY=gsk_ваш_ключ_от_groq
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.3-70b-versatile

# Альтернативные настройки:
# Для OpenAI (платно):
# OPENAI_API_KEY=sk-ваш_ключ_openai
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_MODEL=gpt-4o-mini

# Для локального Ollama (бесплатно, без интернета):
# OPENAI_API_KEY=not-needed
# OPENAI_BASE_URL=http://localhost:11434/v1
# OPENAI_MODEL=gemma3:12b

# Для GigaChat API (Cloud.ru):
# OPENAI_API_KEY=ваш_ключ_gigachat
# OPENAI_BASE_URL=https://gigachat.devices.sberbank.ru/api/v1
# OPENAI_MODEL=GigaChat-2-Max
""",

    ".gitignore": """# Виртуальное окружение
venv/
env/
.env

# Python
__pycache__/
*.py[cod]
*.so
.Python

# IDE
.vscode/
.idea/
*.swp

# Локальные настройки
*.local
.env.local

# Логи
logs/
*.log
""",

    "app/__init__.py": '"""Пакет приложения "Ассистент Инноватора"."""\n',

    "app/config.py": """import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

settings = Settings()
""",

    "app/models.py": """from pydantic import BaseModel, Field
from typing import List, Optional

class UserRequest(BaseModel):
    free_text_interests: str = Field(..., description="Свободное описание научных интересов")
    domains: List[str] = Field(default=[], description="Научные области (напр. AI, Biology)")
    skills: List[str] = Field(default=[], description="Ключевые навыки")
    experience_years: Optional[int] = Field(None, description="Опыт в годах")
    education_level: Optional[str] = Field(None, description="Уровень образования")

class HypothesisIdea(BaseModel):
    title: str
    description: str
    novelty_aspect: str
    feasibility_assessment: str

class ValidationResult(BaseModel):
    query_used: str
    similar_patents_count: int
    similar_papers_count: int
    novelty_score: str  # "High", "Medium", "Low"
    risks: str
    top_references: List[str]

class FinalReport(BaseModel):
    user_context_summary: str
    generated_hypotheses: List[HypothesisIdea]
    validation_report: List[ValidationResult]
""",

    "app/core/__init__.py": '"""Ядро приложения: промпты и вспомогательные схемы."""\n',

    "app/core/prompts.py": '''# Промпт для генерации идей
IDEA_GENERATION_PROMPT = \'\'\'Ты — эксперт по научным исследованиям и инновациям.
На основе профиля пользователя предложи {n_ideas} конкретных гипотез для научного проекта.
Каждая идея должна обладать научной новизной и быть реализуемой с учетом компетенций пользователя.

Профиль пользователя:
- Интересы (свободное описание): {free_text}
- Научные области: {domains}
- Навыки: {skills}
- Опыт (лет): {experience}
- Образование: {education}

Требования к ответу:
1. Ответ должен быть в формате JSON с ключом "ideas", содержащим массив объектов.
2. Каждый объект должен иметь поля:
   - "title": краткое название идеи
   - "description": подробное описание идеи (2-3 предложения)
   - "novelty_aspect": в чем заключается научная новизна
   - "feasibility_assessment": оценка реализуемости с данными компетенциями

Будь конкретен и избегай общих фраз.\'\'\'

# Промпт для валидации гипотезы на основе найденных аналогов
VALIDATION_PROMPT = \'\'\'Ты — эксперт по патентному поиску и анализу научной литературы.
Оцени уровень новизны следующей научной гипотезы, сравнив её с предоставленными данными о существующих патентах и научных статьях.

Гипотеза:
- Название: {title}
- Описание: {description}

Найденные патенты (до 5 наиболее релевантных):
{patents}

Найденные научные статьи (до 5 наиболее релевантных):
{papers}

Твоя задача:
1. Оценить, насколько гипотеза пересекается с существующими решениями.
2. Определить уровень новизны: "High" (высокая, аналогов мало или нет), "Medium" (средняя, есть частичные совпадения), "Low" (низкая, идея уже реализована).
3. Выделить основные риски реализации (технические, патентные, научные).
4. Указать до 3 наиболее релевантных ссылок (патентные номера или названия статей).

Ответ должен быть в формате JSON со следующими полями:
- "similar_patents_count": число найденных патентов, которые ты считаешь релевантными
- "similar_papers_count": число найденных статей, которые ты считаешь релевантными
- "novelty_score": "High", "Medium" или "Low"
- "risks": текстовое описание рисков (1-2 предложения)
- "top_references": массив строк с идентификаторами или названиями документов
\'\'\'
''',

    "app/core/schemas.py": """# Дополнительные схемы для внутреннего использования (при необходимости)
from pydantic import BaseModel
from typing import Optional

class PatentDocument(BaseModel):
    patent_id: str
    title: str
    abstract: Optional[str] = None

class PaperDocument(BaseModel):
    paper_id: str
    title: str
    abstract: Optional[str] = None
""",

    "app/services/__init__.py": '"""Сервисы для работы с LLM, патентами и научными статьями."""\n',

    "app/services/llm_service.py": '''import json
from openai import AsyncOpenAI
from app.config import settings
from app.models import HypothesisIdea, ValidationResult, UserRequest
from app.core.prompts import IDEA_GENERATION_PROMPT, VALIDATION_PROMPT

client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)

async def generate_ideas(request: UserRequest, n_ideas: int = 3) -> list[HypothesisIdea]:
    prompt = IDEA_GENERATION_PROMPT.format(
        n_ideas=n_ideas,
        free_text=request.free_text_interests,
        domains=", ".join(request.domains) if request.domains else "не указаны",
        skills=", ".join(request.skills) if request.skills else "не указаны",
        experience=request.experience_years or "не указано",
        education=request.education_level or "не указано"
    )
    
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    data = json.loads(content)
    
    ideas = []
    for item in data.get("ideas", []):
        ideas.append(HypothesisIdea(**item))
    return ideas

async def validate_hypothesis(
    hypothesis: HypothesisIdea,
    patents_context: str = "",
    papers_context: str = ""
) -> ValidationResult:
    prompt = VALIDATION_PROMPT.format(
        title=hypothesis.title,
        description=hypothesis.description,
        patents=patents_context or "Информация о патентах не найдена.",
        papers=papers_context or "Информация о научных статьях не найдена."
    )
    
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    data = json.loads(content)
    
    return ValidationResult(
        query_used=hypothesis.title,
        similar_patents_count=data.get("similar_patents_count", 0),
        similar_papers_count=data.get("similar_papers_count", 0),
        novelty_score=data.get("novelty_score", "Medium"),
        risks=data.get("risks", ""),
        top_references=data.get("top_references", [])
    )
''',

    "app/services/patent_search.py": '''import httpx
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
''',

    "app/services/paper_search.py": '''import httpx

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
''',

    "app/main.py": '''from fastapi import FastAPI
from app.models import UserRequest, FinalReport
from app.services.llm_service import generate_ideas, validate_hypothesis
from app.services.patent_search import search_patents
from app.services.paper_search import search_papers

app = FastAPI(
    title="Innovator's Assistant API",
    description="Генерация и валидация научных гипотез с помощью ИИ",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Innovator's Assistant API is running"}

@app.post("/generate", response_model=FinalReport)
async def generate_and_validate(request: UserRequest):
    # 1. Генерация гипотез
    hypotheses = await generate_ideas(request)
    
    # 2. Для каждой гипотезы выполняем поиск аналогов и валидацию
    validation_results = []
    for hyp in hypotheses:
        # Поиск патентов
        patents = await search_patents(hyp.title, limit=5)
        patents_text = "\\n".join([
            f"- Патент {p['id']}: {p['title']}\\n  Аннотация: {p['abstract']}"
            for p in patents
        ]) if patents else "Патентов не найдено"
        
        # Поиск научных статей
        papers = await search_papers(hyp.title, limit=5)
        papers_text = "\\n".join([
            f"- Статья {p['id']}: {p['title']}\\n  Аннотация: {p['abstract']}"
            for p in papers
        ]) if papers else "Статей не найдено"
        
        # Валидация с использованием найденного контекста
        validation = await validate_hypothesis(hyp, patents_text, papers_text)
        validation_results.append(validation)
    
    # 3. Формирование итогового отчёта
    summary = f"Пользователь интересуется: {request.free_text_interests[:200]}...\\n"
    summary += f"Области: {', '.join(request.domains) if request.domains else 'не указаны'}\\n"
    summary += f"Навыки: {', '.join(request.skills) if request.skills else 'не указаны'}"
    
    return FinalReport(
        user_context_summary=summary,
        generated_hypotheses=hypotheses,
        validation_report=validation_results
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
}

def create_directories():
    """Создаём необходимые папки"""
    dirs = [
        "app",
        "app/core",
        "app/services"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"  + Папка {d} создана")

def write_files():
    """Записываем все файлы"""
    for path, content in FILES.items():
        full_path = os.path.join(os.getcwd(), path)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  + Файл {path} создан")

if __name__ == "__main__":
    print("=== Создание структуры проекта Innovator's Assistant ===\n")
    create_directories()
    print()
    write_files()
    print("\n=== Готово! ===\n")
    print("Следующие шаги:")
    print("1. Убедитесь, что виртуальное окружение активировано (должно быть (venv) в начале строки)")
    print("2. Установите зависимости: pip install -r requirements.txt")
    print("3. Отредактируйте файл .env и вставьте ваш API-ключ от Groq")
    print("4. Запустите сервер: uvicorn app.main:app --reload")
    print("5. Откройте http://localhost:8000/docs")