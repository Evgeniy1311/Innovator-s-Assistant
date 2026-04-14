// script.js
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
