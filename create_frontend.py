#!/usr/bin/env python3
"""
Скрипт для создания статического веб-интерфейса проекта "Innovator's Assistant"
Запуск: python create_frontend.py
"""

import os

# Содержимое файлов
FILES = {
    "static/index.html": """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ассистент Инноватора</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🧠 Ассистент Инноватора</h1>
            <p class="subtitle">Генерация и валидация научных гипотез с помощью ИИ</p>
        </header>

        <main>
            <section class="input-section">
                <h2>Расскажите о ваших интересах и компетенциях</h2>
                <form id="ideaForm">
                    <div class="form-group">
                        <label for="interests">Научные интересы (свободное описание) *</label>
                        <textarea id="interests" name="interests" rows="4" required placeholder="Например: Разработка методов объяснимого ИИ для медицинской диагностики рака лёгких по снимкам КТ"></textarea>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="domains">Научные области (через запятую)</label>
                            <input type="text" id="domains" name="domains" placeholder="AI, Medical Imaging, Explainable AI">
                        </div>
                        <div class="form-group">
                            <label for="skills">Ключевые навыки (через запятую)</label>
                            <input type="text" id="skills" name="skills" placeholder="Python, PyTorch, Deep Learning">
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="experience">Опыт (лет)</label>
                            <input type="number" id="experience" name="experience" min="0" step="1" placeholder="5">
                        </div>
                        <div class="form-group">
                            <label for="education">Образование</label>
                            <select id="education" name="education">
                                <option value="">Не указано</option>
                                <option value="Bachelor">Бакалавр</option>
                                <option value="Master">Магистр</option>
                                <option value="PhD">Кандидат наук (PhD)</option>
                                <option value="PostDoc">Доктор наук / Постдок</option>
                            </select>
                        </div>
                    </div>

                    <button type="submit" id="submitBtn" class="primary-btn">
                        <span class="btn-text">Сгенерировать и проверить идеи</span>
                        <span class="spinner" style="display: none;"></span>
                    </button>
                </form>
            </section>

            <section class="results-section" id="results" style="display: none;">
                <h2>Результаты</h2>
                <div id="summary" class="summary-box"></div>
                <div id="hypotheses" class="hypotheses-container"></div>
            </section>

            <section id="error" class="error-section" style="display: none;"></section>
        </main>
    </div>
    <script src="/static/script.js"></script>
</body>
</html>
""",

    "static/style.css": """/* style.css */
:root {
    --primary: #4f46e5;
    --primary-dark: #4338ca;
    --success: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-600: #4b5563;
    --gray-800: #1f2937;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    background: var(--gray-50);
    color: var(--gray-800);
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1rem;
}

header {
    text-align: center;
    margin-bottom: 2.5rem;
}

h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--gray-800);
    margin-bottom: 0.5rem;
}

.subtitle {
    color: var(--gray-600);
    font-size: 1.1rem;
}

.input-section, .results-section {
    background: white;
    border-radius: 1rem;
    padding: 2rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
}

.form-group {
    margin-bottom: 1.5rem;
}

label {
    display: block;
    font-weight: 500;
    margin-bottom: 0.5rem;
    color: var(--gray-800);
}

textarea, input[type="text"], input[type="number"], select {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 1px solid var(--gray-200);
    border-radius: 0.5rem;
    font-size: 1rem;
    transition: border-color 0.15s;
}

textarea:focus, input:focus, select:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

.primary-btn {
    background: var(--primary);
    color: white;
    border: none;
    padding: 0.875rem 2rem;
    border-radius: 0.5rem;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.15s;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.primary-btn:hover:not(:disabled) {
    background: var(--primary-dark);
}

.primary-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.spinner {
    width: 1.25rem;
    height: 1.25rem;
    border: 2px solid rgba(255,255,255,0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.summary-box {
    background: var(--gray-100);
    padding: 1.25rem;
    border-radius: 0.5rem;
    margin-bottom: 2rem;
    white-space: pre-wrap;
}

.hypothesis-card {
    background: white;
    border: 1px solid var(--gray-200);
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.hypothesis-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--gray-800);
}

.hypothesis-description {
    margin-bottom: 1rem;
    color: var(--gray-600);
}

.novelty-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
}

.novelty-high { background: #dcfce7; color: #166534; }
.novelty-medium { background: #fef9c3; color: #854d0e; }
.novelty-low { background: #fee2e2; color: #991b1b; }

.risks {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--gray-200);
}

.references {
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: var(--gray-600);
}

.error-section {
    background: #fee2e2;
    color: #991b1b;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #fecaca;
}

@media (max-width: 640px) {
    .form-row { grid-template-columns: 1fr; }
    h1 { font-size: 2rem; }
}
""",

    "static/script.js": """// script.js
document.getElementById('ideaForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = submitBtn.querySelector('.spinner');
    const resultsSection = document.getElementById('results');
    const errorSection = document.getElementById('error');
    
    // Сброс предыдущих результатов и ошибок
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Показываем спиннер
    btnText.style.display = 'none';
    spinner.style.display = 'inline-block';
    submitBtn.disabled = true;
    
    try {
        // Сбор данных формы
        const interests = document.getElementById('interests').value.trim();
        const domainsInput = document.getElementById('domains').value.trim();
        const skillsInput = document.getElementById('skills').value.trim();
        const experience = document.getElementById('experience').value;
        const education = document.getElementById('education').value;
        
        const payload = {
            free_text_interests: interests,
            domains: domainsInput ? domainsInput.split(',').map(s => s.trim()) : [],
            skills: skillsInput ? skillsInput.split(',').map(s => s.trim()) : [],
            experience_years: experience ? parseInt(experience) : null,
            education_level: education || null
        };
        
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        console.error('Ошибка:', error);
        errorSection.textContent = `Произошла ошибка: ${error.message}. Попробуйте обновить страницу и повторить.`;
        errorSection.style.display = 'block';
    } finally {
        btnText.style.display = 'inline';
        spinner.style.display = 'none';
        submitBtn.disabled = false;
    }
});

function displayResults(data) {
    const resultsSection = document.getElementById('results');
    const summaryDiv = document.getElementById('summary');
    const hypothesesContainer = document.getElementById('hypotheses');
    
    // Отображаем сводку
    summaryDiv.textContent = data.user_context_summary;
    
    // Очищаем и заполняем гипотезы
    hypothesesContainer.innerHTML = '';
    
    data.generated_hypotheses.forEach((hyp, index) => {
        const validation = data.validation_report[index];
        
        const card = document.createElement('div');
        card.className = 'hypothesis-card';
        
        // Новизна
        const noveltyClass = validation.novelty_score === 'High' ? 'novelty-high' :
                           (validation.novelty_score === 'Medium' ? 'novelty-medium' : 'novelty-low');
        
        card.innerHTML = `
            <div class="hypothesis-title">${hyp.title}</div>
            <div class="hypothesis-description">${hyp.description}</div>
            <div><strong>Аспект новизны:</strong> ${hyp.novelty_aspect}</div>
            <div><strong>Реализуемость:</strong> ${hyp.feasibility_assessment}</div>
            <div style="margin-top: 1rem;">
                <span class="novelty-badge ${noveltyClass}">Новизна: ${validation.novelty_score}</span>
                <span style="margin-left: 1rem;">Патентов: ${validation.similar_patents_count}, Статей: ${validation.similar_papers_count}</span>
            </div>
            <div class="risks"><strong>Риски:</strong> ${validation.risks}</div>
            ${validation.top_references.length ? `
                <div class="references">
                    <strong>Релевантные источники:</strong>
                    <ul>${validation.top_references.map(ref => `<li>${ref}</li>`).join('')}</ul>
                </div>
            ` : ''}
        `;
        
        hypothesesContainer.appendChild(card);
    });
    
    resultsSection.style.display = 'block';
}
"""
}

def create_directories():
    os.makedirs("static", exist_ok=True)
    print("  + Папка static создана")

def write_files():
    for path, content in FILES.items():
        full_path = os.path.join(os.getcwd(), path)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  + Файл {path} создан")

if __name__ == "__main__":
    print("=== Создание веб-интерфейса ===\n")
    create_directories()
    write_files()
    print("\n=== Готово! ===")
    print("Теперь запустите сервер и откройте http://localhost:8000/static/index.html")