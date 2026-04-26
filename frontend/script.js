document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide icons
    lucide.createIcons();

    // --- Toast Notification ---
    function showToast(message, isError = true) {
        const toast = document.getElementById('toast');
        const icon = isError ? '<i data-lucide="alert-circle"></i>' : '<i data-lucide="check-circle"></i>';
        toast.innerHTML = `${icon} <span>${message}</span>`;
        toast.style.background = isError ? 'var(--error)' : 'var(--success)';
        lucide.createIcons();
        
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 4000);
    }

    // --- Color Logic ---
    function getColorForScore(score) {
        if (score >= 80) return 'var(--success)';
        if (score >= 50) return 'var(--warning)';
        return 'var(--error)';
    }

    // --- Tab Switching ---
    const tabs = document.querySelectorAll('.nav-item');
    const panes = document.querySelectorAll('.tab-pane');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            panes.forEach(p => p.classList.add('hidden'));
            
            tab.classList.add('active');
            const targetPane = document.getElementById(tab.dataset.tab);
            targetPane.classList.remove('hidden');
            targetPane.classList.add('active');
        });
    });

    // --- File Input UI ---
    const dropArea = document.getElementById('file-drop-area');
    const fileInput = document.getElementById('resume-file');
    const fileMsg = document.querySelector('.file-msg');

    if (fileInput && dropArea) {
        dropArea.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                fileMsg.textContent = e.target.files[0].name;
                dropArea.classList.add('has-file');
            } else {
                fileMsg.textContent = 'Click or drag file to upload';
                dropArea.classList.remove('has-file');
            }
        });
    }

    // --- Render Helpers ---
    function renderChips(containerId, items, typeClass) {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = '';
        
        if (!items || items.length === 0) {
            if(typeClass !== 'found') {
                container.innerHTML = '<span class="chip" style="color: var(--success); border-color: var(--success-bg); background: var(--success-bg)">No major gaps 🎯</span>';
            } else {
                container.innerHTML = '<span class="chip" style="opacity: 0.5;">None</span>';
            }
            return;
        }
        
        items.forEach(item => {
            const span = document.createElement('span');
            span.className = `chip ${typeClass}`;
            span.textContent = item;
            container.appendChild(span);
        });
    }

    function renderList(ulId, items) {
        const ul = document.getElementById(ulId);
        if (!ul) return;
        ul.innerHTML = '';
        
        if (!items || items.length === 0) {
            ul.innerHTML = '<li style="opacity: 0.5;">Looks good! No issues found.</li>';
            return;
        }
        
        items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            ul.appendChild(li);
        });
    }

    function animateCircularScore(targetScore, circleClass = '.circle', textId = 'score-text') {
        const circle = document.querySelector(circleClass);
        const percentageText = document.querySelector('.percentage');
        if (!circle || !percentageText) return;

        const score = parseFloat(targetScore) || 0;
        const color = getColorForScore(score);
        
        circle.setAttribute('stroke-dasharray', `${score}, 100`);
        circle.style.stroke = color;
        
        let current = 0;
        const step = score / 30; 
        
        const timer = setInterval(() => {
            current += step;
            if (current >= score) {
                current = score;
                clearInterval(timer);
            }
            percentageText.textContent = `${Math.round(current)}%`;
            percentageText.style.color = color;
        }, 30);
    }

    function animateBar(barId, valId, score) {
        const bar = document.getElementById(barId);
        const valText = document.getElementById(valId);
        if (!bar || !valText) return;
        
        const num = parseFloat(score) || 0;
        const color = getColorForScore(num);
        
        bar.style.background = color;
        setTimeout(() => { bar.style.width = `${num}%`; }, 100);
        valText.textContent = `${num}%`;
        valText.style.color = color;
    }

    // ==========================================
    // 1. SINGLE ANALYSIS LOGIC
    // ==========================================
    const singleForm = document.getElementById('analyze-form');
    const singleBtn = document.getElementById('analyze-btn');
    const singleResults = document.getElementById('results-panel');

    if (singleForm) {
        singleForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            singleResults.classList.add('hidden');
            singleBtn.classList.add('loading');
            singleBtn.disabled = true;

            try {
                const formData = new FormData(singleForm);
                const res = await fetch('/analyze', { method: 'POST', body: formData });
                const data = await res.json();

                if (!res.ok) throw new Error(data.error || 'Failed to analyze');
                
                renderSingleResults(data);
                showToast('Analysis complete!', false);
            } catch (err) {
                showToast(err.message);
            } finally {
                singleBtn.classList.remove('loading');
                singleBtn.disabled = false;
            }
        });
    }

    function renderSingleResults(data) {
        singleResults.classList.remove('hidden');

        animateCircularScore(data.match_score);
        animateBar('bar-skill', 'val-skill', data.skill_score);
        animateBar('bar-sim', 'val-sim', data.similarity_score);

        renderChips('chips-critical', data.critical_missing_skills, 'critical');
        renderChips('chips-missing', data.missing_skills, 'missing');
        renderChips('chips-found', data.skills_found, 'found');

        renderList('list-suggestions', data.suggestions);
        renderList('list-issues', data.resume_feedback?.issues);
        renderList('list-rec', data.resume_feedback?.recommendations);

        singleResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // ==========================================
    // 2. MULTI COMPARE LOGIC
    // ==========================================
    const addJobBtn = document.getElementById('add-job-btn');
    const jobsContainer = document.getElementById('jobs-container');
    const compareBtn = document.getElementById('compare-btn');
    const multiResults = document.getElementById('multi-results');
    const compareGrid = document.getElementById('compare-grid');

    if (addJobBtn) {
        addJobBtn.addEventListener('click', () => {
            const div = document.createElement('div');
            div.className = 'job-item glass-light';
            div.innerHTML = `
                <input type="text" class="job-title-input" placeholder="Job Title (e.g. Frontend Dev)" required>
                <textarea class="job-desc-input" rows="2" placeholder="Job description..." required></textarea>
                <button class="icon-btn text-error remove-job"><i data-lucide="trash-2"></i></button>
            `;
            jobsContainer.appendChild(div);
            lucide.createIcons();
            updateRemoveButtons();
        });
    }

    if (jobsContainer) {
        jobsContainer.addEventListener('click', (e) => {
            const btn = e.target.closest('.remove-job');
            if (btn) {
                btn.closest('.job-item').remove();
                updateRemoveButtons();
            }
        });
    }

    function updateRemoveButtons() {
        const items = jobsContainer.querySelectorAll('.job-item');
        items.forEach(item => {
            const btn = item.querySelector('.remove-job');
            if (items.length === 1) btn.classList.add('hidden');
            else btn.classList.remove('hidden');
        });
    }
    if (jobsContainer) updateRemoveButtons(); // initial state

    if (compareBtn) {
        compareBtn.addEventListener('click', async () => {
            const resumeText = document.getElementById('multi-resume').value;
            if (!resumeText.trim()) {
                showToast("Please provide the base resume text.");
                return;
            }

            const jobItems = jobsContainer.querySelectorAll('.job-item');
            const jobs = [];
            
            let valid = true;
            jobItems.forEach(item => {
                const title = item.querySelector('.job-title-input').value;
                const desc = item.querySelector('.job-desc-input').value;
                if (!title || !desc) valid = false;
                jobs.push({ title, desc });
            });

            if (!valid) {
                showToast("Please fill all Job Titles and Descriptions.");
                return;
            }

            multiResults.classList.add('hidden');
            compareBtn.classList.add('loading');
            compareBtn.disabled = true;

            try {
                // Run API sequentially for simplicity and stability
                const results = [];
                for (let i = 0; i < jobs.length; i++) {
                    const fd = new FormData();
                    fd.append('resume_text', resumeText);
                    fd.append('job_description', jobs[i].desc);

                    const res = await fetch('/analyze', { method: 'POST', body: fd });
                    const data = await res.json();
                    
                    if (!res.ok) throw new Error(`Job ${i+1}: ${data.error}`);
                    
                    results.push({
                        title: jobs[i].title,
                        score: data.match_score || 0,
                        found: data.skills_found || [],
                        missing: [...(data.critical_missing_skills || []), ...(data.missing_skills || [])]
                    });
                }

                renderMultiResults(results);
                showToast('Comparison complete!', false);
            } catch (err) {
                showToast(err.message);
            } finally {
                compareBtn.classList.remove('loading');
                compareBtn.disabled = false;
            }
        });
    }

    function renderMultiResults(results) {
        compareGrid.innerHTML = '';
        multiResults.classList.remove('hidden');

        // Sort desc by score
        results.sort((a, b) => b.score - a.score);
        
        results.forEach((res, index) => {
            const isBest = index === 0 && res.score > 0;
            const color = getColorForScore(res.score);
            
            const card = document.createElement('div');
            card.className = `compare-card ${isBest ? 'best-match' : ''}`;
            
            let badgeHtml = isBest ? `<div class="badge"><i data-lucide="trophy"></i> BEST MATCH</div>` : '';
            
            const foundHtml = res.found.slice(0, 5).map(s => `<span class="c-tag">${s}</span>`).join('');
            const foundCount = res.found.length > 5 ? `<span class="c-tag" style="opacity:0.5">+${res.found.length-5}</span>` : '';
            
            const missingHtml = res.missing.slice(0, 5).map(s => `<span class="c-tag" style="background:var(--error-bg);color:var(--error)">${s}</span>`).join('');
            const missingCount = res.missing.length > 5 ? `<span class="c-tag" style="opacity:0.5">+${res.missing.length-5}</span>` : '';

            card.innerHTML = `
                ${badgeHtml}
                <div class="c-title">${res.title}</div>
                <div class="c-score" style="color: ${color}">${res.score}%</div>
                
                <div class="c-section">
                    <h5>Matched Skills</h5>
                    <div class="c-tags">${foundHtml || '<span class="c-tag">None</span>'} ${foundCount}</div>
                </div>
                
                <div class="c-section">
                    <h5>Missing Skills</h5>
                    <div class="c-tags">${missingHtml || '<span class="c-tag" style="background:var(--success-bg);color:var(--success)">None 🎯</span>'} ${missingCount}</div>
                </div>
            `;
            
            compareGrid.appendChild(card);
        });
        
        lucide.createIcons();
        multiResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});
