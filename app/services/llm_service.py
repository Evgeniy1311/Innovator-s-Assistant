import json
import asyncio
from typing import List
from openai import AsyncOpenAI, RateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings
from app.models import HypothesisIdea, ValidationResult, UserRequest
from app.core.prompts import (
    IDEA_GENERATION_PROMPT,
    VALIDATION_PROMPT,
    IDEA_GENERATION_BATCH_PROMPT,
    TOPIC_ANALYSIS_PROMPT
)

client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)

def _normalize_feasibility(item: dict) -> None:
    """Приводит feasibility_assessment к строке."""
    feas = item.get("feasibility_assessment")
    if feas is None:
        item["feasibility_assessment"] = "Не указано"
    elif not isinstance(feas, str):
        item["feasibility_assessment"] = str(feas)

async def analyze_topic_and_recommend_count(request: UserRequest) -> int:
    prompt = TOPIC_ANALYSIS_PROMPT.format(
        free_text=request.free_text_interests,
        domains=", ".join(request.domains) if request.domains else "не указаны",
        skills=", ".join(request.skills) if request.skills else "не указаны"
    )
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    data = json.loads(response.choices[0].message.content)
    count = int(data.get("recommended_ideas", 30))
    return max(5, min(count, 250))

async def generate_ideas(request: UserRequest, n_ideas: int = 3) -> List[HypothesisIdea]:
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
        _normalize_feasibility(item)
        ideas.append(HypothesisIdea(**item))
    return ideas

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=30),
    retry=retry_if_exception_type(RateLimitError)
)
async def _generate_single_batch(request: UserRequest, n_ideas: int) -> List[HypothesisIdea]:
    prompt = IDEA_GENERATION_BATCH_PROMPT.format(
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
        temperature=0.9,
        response_format={"type": "json_object"}
    )
    data = json.loads(response.choices[0].message.content)
    ideas = []
    for item in data.get("ideas", []):
        _normalize_feasibility(item)
        try:
            ideas.append(HypothesisIdea(**item))
        except Exception as e:
            print(f"Пропущена идея из-за ошибки валидации: {e}")
    return ideas

async def generate_ideas_batch(
    request: UserRequest,
    total_ideas: int,
    batch_size: int = 10
) -> List[HypothesisIdea]:
    num_batches = (total_ideas + batch_size - 1) // batch_size
    tasks = [_generate_single_batch(request, batch_size) for _ in range(num_batches)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_ideas = []
    for res in results:
        if isinstance(res, Exception):
            print(f"Ошибка в пакете: {res}")
            continue
        all_ideas.extend(res)
    return all_ideas[:total_ideas]

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