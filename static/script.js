// static/script.js
let currentPage = 1;
const itemsPerPage = 10;
let allHypotheses = [];
let allValidations = [];

document.getElementById('ideaForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = submitBtn.querySelector('.spinner');
    const resultsSection = document.getElementById('results');
    const errorSection = document.getElementById('error');
    
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    btnText.style.display = 'none';
    spinner.style.display = 'inline-block';
    submitBtn.disabled = true;
    
    try {
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
        
        if (!response.ok) throw new Error(`Ошибка сервера: ${response.status}`);
        
        const data = await response.json();
        allHypotheses = data.generated_hypotheses;
        allValidations = data.validation_report;
        currentPage = 1;
        displayPaginated();
        resultsSection.style.display = 'block';
        
    } catch (error) {
        console.error('Ошибка:', error);
        errorSection.textContent = `Произошла ошибка: ${error.message}`;
        errorSection.style.display = 'block';
    } finally {
        btnText.style.display = 'inline';
        spinner.style.display = 'none';
        submitBtn.disabled = false;
    }
});

function displayPaginated() {
    const summaryDiv = document.getElementById('summary');
    const hypothesesContainer = document.getElementById('hypotheses');
    const paginationDiv = document.getElementById('pagination') || createPaginationContainer();
    
    const totalPages = Math.ceil(allHypotheses.length / itemsPerPage);
    const start = (currentPage - 1) * itemsPerPage;
    const end = Math.min(start + itemsPerPage, allHypotheses.length);
    
    // Обновляем сводку
    summaryDiv.textContent = `Сгенерировано идей: ${allHypotheses.length}. Показаны идеи ${start+1}–${end}. Валидация выполнена для первых 10.`;
    
    // Рендерим карточки текущей страницы
    hypothesesContainer.innerHTML = '';
    for (let i = start; i < end; i++) {
        const hyp = allHypotheses[i];
        const validation = (i < allValidations.length) ? allValidations[i] : null;
        hypothesesContainer.appendChild(createCard(hyp, validation, i+1));
    }
    
    // Рендерим кнопки пагинации
    renderPagination(paginationDiv, totalPages);
}

function createCard(hyp, validation, index) {
    const card = document.createElement('div');
    card.className = 'hypothesis-card';
    
    let validationHtml = '';
    if (validation) {
        const noveltyClass = validation.novelty_score === 'High' ? 'novelty-high' :
                           (validation.novelty_score === 'Medium' ? 'novelty-medium' : 'novelty-low');
        validationHtml = `
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
    } else {
        validationHtml = `<p style="margin-top: 1rem; color: #6b7280;"><em>Валидация в очереди...</em></p>`;
    }
    
    card.innerHTML = `
        <div class="hypothesis-title">${index}. ${hyp.title}</div>
        <div class="hypothesis-description">${hyp.description}</div>
        <div><strong>Аспект новизны:</strong> ${hyp.novelty_aspect}</div>
        <div><strong>Реализуемость:</strong> ${hyp.feasibility_assessment}</div>
        ${validationHtml}
    `;
    return card;
}

function createPaginationContainer() {
    const container = document.createElement('div');
    container.id = 'pagination';
    container.style.cssText = 'display: flex; justify-content: center; gap: 0.5rem; margin-top: 2rem;';
    document.querySelector('.results-section').appendChild(container);
    return container;
}

function renderPagination(container, totalPages) {
    container.innerHTML = '';
    for (let i = 1; i <= totalPages; i++) {
        const btn = document.createElement('button');
        btn.textContent = i;
        btn.style.cssText = 'padding: 0.5rem 1rem; border: 1px solid #e5e7eb; background: white; border-radius: 0.25rem; cursor: pointer;';
        if (i === currentPage) {
            btn.style.background = '#4f46e5';
            btn.style.color = 'white';
            btn.style.borderColor = '#4f46e5';
        }
        btn.addEventListener('click', () => {
            currentPage = i;
            displayPaginated();
            window.scrollTo({ top: document.querySelector('.results-section').offsetTop, behavior: 'smooth' });
        });
        container.appendChild(btn);
    }
}