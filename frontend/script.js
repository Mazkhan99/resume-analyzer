document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('resume-file');
    const fileNameDisplay = document.getElementById('file-name');
    const form = document.getElementById('analyzer-form');
    const submitBtn = document.getElementById('submit-btn');
    const resultsPanel = document.getElementById('results-panel');
    const errorToast = document.getElementById('error-message');

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileNameDisplay.textContent = e.target.files[0].name;
            fileNameDisplay.style.color = 'var(--accent-primary)';
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        resultsPanel.classList.add('hidden');
        errorToast.classList.add('hidden');
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;

        try {
            const formData = new FormData(form);
            const response = await fetch('/analyze', { method: 'POST', body: formData });
            const data = await response.json();

            if (!response.ok) throw new Error(data.error || 'Failed to analyze');
            renderResults(data);
        } catch (error) {
            errorToast.textContent = error.message;
            errorToast.classList.remove('hidden');
        } finally {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    });

    function renderResults(data) {
        resultsPanel.classList.remove('hidden');

        // Circular Score
        animateCircularScore(data.match_score);

        // Progress Bars
        document.getElementById('val-skill').textContent = `${data.skill_score}%`;
        setTimeout(() => { document.getElementById('bar-skill').style.width = `${data.skill_score}%`; }, 100);
        
        document.getElementById('val-keyword').textContent = `${data.similarity_score}%`;
        setTimeout(() => { document.getElementById('bar-keyword').style.width = `${data.similarity_score}%`; }, 100);
        
        // Tags
        renderTags('critical-skills-container', data.critical_missing_skills, 'critical');
        renderTags('missing-skills-container', data.missing_skills, 'missing');
        renderTags('found-skills-container', data.skills_found, 'found');

        // Feedback & Suggestions
        renderList('suggestions-list', data.suggestions);
        renderList('feedback-issues', data.resume_feedback.issues);
        renderList('feedback-rec', data.resume_feedback.recommendations);
        
        resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function renderTags(containerId, items, typeClass) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        if (!items || items.length === 0) {
            if(typeClass !== 'found') container.innerHTML = '<span style="color: var(--text-secondary); font-size: 0.85rem;">None</span>';
            return;
        }
        items.forEach(item => {
            const span = document.createElement('span');
            span.className = `tag ${typeClass}`;
            span.textContent = item;
            container.appendChild(span);
        });
    }

    function renderList(ulId, items) {
        const ul = document.getElementById(ulId);
        ul.innerHTML = '';
        items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            ul.appendChild(li);
        });
    }

    function animateCircularScore(target) {
        const circle = document.getElementById('score-circle');
        const text = document.getElementById('score-text');
        let current = 0;
        const targetNum = parseFloat(target);
        if (isNaN(targetNum)) return;
        
        let color = 'var(--danger)';
        if (targetNum >= 75) color = 'var(--success)';
        else if (targetNum >= 50) color = 'var(--warning)';

        const timer = setInterval(() => {
            current += targetNum / 50;
            if (current >= targetNum) { current = targetNum; clearInterval(timer); }
            text.textContent = `${Math.round(current)}%`;
            text.style.color = color;
            circle.style.background = `conic-gradient(${color} ${current * 3.6}deg, var(--glass-bg) 0deg)`;
        }, 20);
    }
});
