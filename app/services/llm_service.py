import json
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
