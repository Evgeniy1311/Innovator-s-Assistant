from fastapi import FastAPI
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
        patents_text = "\n".join([
            f"- Патент {p['id']}: {p['title']}\n  Аннотация: {p['abstract']}"
            for p in patents
        ]) if patents else "Патентов не найдено"
        
        # Поиск научных статей
        papers = await search_papers(hyp.title, limit=5)
        papers_text = "\n".join([
            f"- Статья {p['id']}: {p['title']}\n  Аннотация: {p['abstract']}"
            for p in papers
        ]) if papers else "Статей не найдено"
        
        # Валидация с использованием найденного контекста
        validation = await validate_hypothesis(hyp, patents_text, papers_text)
        validation_results.append(validation)
    
    # 3. Формирование итогового отчёта
    summary = f"Пользователь интересуется: {request.free_text_interests[:200]}...\n"
    summary += f"Области: {', '.join(request.domains) if request.domains else 'не указаны'}\n"
    summary += f"Навыки: {', '.join(request.skills) if request.skills else 'не указаны'}"
    
    return FinalReport(
        user_context_summary=summary,
        generated_hypotheses=hypotheses,
        validation_report=validation_results
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
