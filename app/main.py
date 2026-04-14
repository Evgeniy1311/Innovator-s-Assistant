from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from app.models import UserRequest, FinalReport, HypothesisIdea, ValidationResult
from app.services.llm_service import (
    analyze_topic_and_recommend_count,
    generate_ideas_batch,
    validate_hypothesis
)
from app.services.patent_search import search_patents
from app.services.paper_search import search_papers

app = FastAPI(
    title="Innovator's Assistant API",
    description="Генерация и валидация научных гипотез с помощью ИИ",
    version="0.2.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Innovator's Assistant API is running"}

async def validate_one(hyp: HypothesisIdea) -> ValidationResult:
    """Проверяет одну гипотезу (поиск патентов + статей + вызов LLM)."""
    patents = await search_patents(hyp.title, limit=5)
    patents_text = "\n".join([
        f"- Патент {p['id']}: {p['title']}\n  Аннотация: {p['abstract']}"
        for p in patents
    ]) if patents else "Патентов не найдено"
    
    papers = await search_papers(hyp.title, limit=5)
    papers_text = "\n".join([
        f"- Статья {p['id']}: {p['title']}\n  Аннотация: {p['abstract']}"
        for p in papers
    ]) if papers else "Статей не найдено"
    
    return await validate_hypothesis(hyp, patents_text, papers_text)

async def validate_remaining_ideas(ideas: list[HypothesisIdea]):
    """Фоновая задача: валидация оставшихся идей."""
    for i, hyp in enumerate(ideas):
        try:
            result = await validate_one(hyp)
            print(f"Валидация {i+1}/{len(ideas)}: {hyp.title} - {result.novelty_score}")
        except Exception as e:
            print(f"Ошибка валидации идеи '{hyp.title}': {e}")

@app.post("/generate", response_model=FinalReport)
async def generate_and_validate(request: UserRequest, background_tasks: BackgroundTasks):
    # 1. Анализируем запрос и получаем рекомендованное количество идей
    recommended_count = await analyze_topic_and_recommend_count(request)
    
    # 2. Генерируем идеи (пакетами)
    hypotheses = await generate_ideas_batch(request, total_ideas=recommended_count)
    
    # 3. Синхронно валидируем первые 10 идей для немедленного отображения
    first_batch = hypotheses[:10]
    validation_results = []
    for hyp in first_batch:
        try:
            res = await validate_one(hyp)
        except Exception as e:
            print(f"Ошибка валидации: {e}")
            res = ValidationResult(
                query_used=hyp.title,
                similar_patents_count=0,
                similar_papers_count=0,
                novelty_score="Unknown",
                risks="Ошибка при проверке",
                top_references=[]
            )
        validation_results.append(res)
    
    # 4. Отправляем остальные идеи в фоновую обработку (если их больше 10)
    if len(hypotheses) > 10:
        background_tasks.add_task(validate_remaining_ideas, hypotheses[10:])
    
    # 5. Формируем отчёт
    summary = f"Пользователь интересуется: {request.free_text_interests[:200]}...\n"
    summary += f"Области: {', '.join(request.domains) if request.domains else 'не указаны'}\n"
    summary += f"Навыки: {', '.join(request.skills) if request.skills else 'не указаны'}\n"
    summary += f"Рекомендовано идей: {recommended_count}. Сгенерировано: {len(hypotheses)}. Показаны первые 10 с полной валидацией, остальные в обработке."
    
    return FinalReport(
        user_context_summary=summary,
        generated_hypotheses=hypotheses,
        validation_report=validation_results
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)