document.addEventListener('DOMContentLoaded', () => {
    // Basic setup
    const pathParts = window.location.pathname.split('/');
    const problemId = pathParts[pathParts.length - 1] || pathParts[pathParts.length - 2];
    
    let currentProblem = null;
    let currentLanguage = 'python';
    let editor = null;
    let currentHintLevel = 0;

    // Elements
    const elProbTitle = document.getElementById('prob-title');
    const elProbDiff = document.getElementById('prob-diff');
    const elProbStmt = document.getElementById('prob-stmt');
    const elProbExamples = document.getElementById('prob-examples');
    const elHintDots = document.getElementById('hint-dots');
    const elHintContainer = document.getElementById('hint-container');
    const btnHint = document.getElementById('btn-hint');
    const btnRun = document.getElementById('btn-run');
    const runSpinner = document.getElementById('run-spinner');
    const resultsSection = document.getElementById('results-section');
    const langBtns = document.querySelectorAll('#lang-toggle button');
    const btnReset = document.getElementById('btn-reset');
    
    // Init Editor
    initMonaco();

    // Fetch Problem Data
    fetchProblemData();

    // Mobile Panel Toggle
    const mobileToggle = document.getElementById('mobile-toggle');
    const leftPanel = document.getElementById('left-panel');
    let panelOpen = false;
    
    if (mobileToggle) {
        mobileToggle.addEventListener('click', () => {
            panelOpen = !panelOpen;
            if (panelOpen) {
                leftPanel.classList.remove('-translate-x-full');
            } else {
                leftPanel.classList.add('-translate-x-full');
            }
        });
        
        // Hide panel by default on mobile
        if (window.innerWidth < 768) {
            leftPanel.classList.add('-translate-x-full');
        }
    }

    async function fetchProblemData() {
        try {
            const res = await fetch(`/dsa/problems/${problemId}`);
            if (res.ok) {
                currentProblem = await res.json();
                populateLeftPanel();
                if (editor) {
                    setEditorContent();
                }
            } else {
                elProbTitle.textContent = "Problem Not Found";
            }
        } catch (e) {
            console.error(e);
            elProbTitle.textContent = "Data Error";
        }
    }

    function populateLeftPanel() {
        // Title & Badge
        elProbTitle.textContent = currentProblem.title;
        elProbDiff.textContent = currentProblem.difficulty;
        
        if(currentProblem.difficulty === 'beginner') elProbDiff.className = "text-[11px] font-bold px-2.5 py-1 rounded-md border text-green-400 bg-green-500/10 border-green-500/20 uppercase tracking-widest shadow-sm ring-1 ring-green-500/30";
        else if(currentProblem.difficulty === 'intermediate') elProbDiff.className = "text-[11px] font-bold px-2.5 py-1 rounded-md border text-blue-400 bg-blue-500/10 border-blue-500/20 uppercase tracking-widest shadow-sm ring-1 ring-blue-500/30";
        else elProbDiff.className = "text-[11px] font-bold px-2.5 py-1 rounded-md border text-purple-400 bg-purple-500/10 border-purple-500/20 uppercase tracking-widest shadow-sm ring-1 ring-purple-500/30";

        // Body
        elProbStmt.innerHTML = currentProblem.problem_statement.replace(/\n/g, '<br>');

        // Examples
        elProbExamples.innerHTML = '';
        if (currentProblem.examples) {
            currentProblem.examples.forEach((ex, i) => {
                const exDiv = document.createElement('div');
                exDiv.className = "text-sm bg-[#1A1D24] border border-gray-800 rounded-xl overflow-hidden shadow-sm";
                exDiv.innerHTML = `
                    <div class="px-4 py-2 bg-gray-900 border-b border-gray-800 font-bold text-gray-400 text-xs uppercase tracking-wider">Example ${i+1}</div>
                    <div class="p-4 space-y-3">
                        <div>
                            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1">Input</span>
                            <div class="bg-[#0F1117] border border-gray-800 rounded-lg p-3 font-mono text-gray-300 text-xs overflow-x-auto whitespace-pre hover:border-gray-700 transition-colors">${ex.input}</div>
                        </div>
                        <div>
                            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1">Output</span>
                            <div class="bg-[#0F1117] border border-gray-800 rounded-lg p-3 font-mono text-teal-400 font-bold text-xs overflow-x-auto whitespace-pre hover:border-gray-700 transition-colors">${ex.output}</div>
                        </div>
                        ${ex.explanation ? `<div class="pt-2 border-t border-gray-800 max-w-full text-gray-400 leading-relaxed"><span class="font-bold text-gray-300">Explanation:</span> ${ex.explanation}</div>` : ''}
                    </div>
                `;
                elProbExamples.appendChild(exDiv);
            });
        }
    }

    function initMonaco() {
        require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' }});
        require(['vs/editor/editor.main'], function() {
            // Define custom theme
            monaco.editor.defineTheme('hireverse', {
                base: 'vs-dark',
                inherit: true,
                rules: [],
                colors: {
                    'editor.background': '#0F1117',
                    'editor.lineHighlightBackground': '#1A1D24',
                    'editorIndentGuide.background': '#1A1D24',
                    'editorSuggestWidget.background': '#1A1D24',
                }
            });
            
            editor = monaco.editor.create(document.getElementById('editor-container'), {
                value: '',
                language: 'python',
                theme: 'hireverse',
                automaticLayout: true,
                minimap: { enabled: false },
                fontSize: 14,
                fontFamily: "'Fira Code', 'Menlo', 'Monaco', 'Courier New', monospace",
                scrollBeyondLastLine: false,
                roundedSelection: true,
                padding: { top: 24, bottom: 24 },
                renderLineHighlight: "all",
                quickSuggestions: true,
                scrollbar: {
                    horizontalScrollbarSize: 8,
                    verticalScrollbarSize: 8,
                }
            });
            
            if (currentProblem) setEditorContent();
            
            // Re-layout on window resize
            window.addEventListener('resize', () => {
                editor.layout();
            });
            
            // Editor resize observer
            const resizeObserver = new ResizeObserver(() => {
                editor.layout();
            });
            resizeObserver.observe(document.getElementById('editor-container'));
        });
    }

    function setEditorContent() {
        if (!editor || !currentProblem) return;
        const code = currentLanguage === 'python' ? currentProblem.python_signature : currentProblem.java_signature;
        editor.setValue(code || '');
        monaco.editor.setModelLanguage(editor.getModel(), currentLanguage);
    }

    // Reset button
    if (btnReset) {
        btnReset.addEventListener('click', () => {
            if (confirm("Reset current language code to starting template?")) {
                setEditorContent();
            }
        });
    }

    // Language Toggle
    langBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            currentLanguage = e.target.getAttribute('data-lang');
            langBtns.forEach(b => {
                b.className = "px-5 py-1.5 text-sm rounded-md bg-transparent text-gray-400 hover:text-gray-200 font-bold transition-all";
            });
            e.target.className = "px-5 py-1.5 text-sm rounded-md bg-teal-600 text-white font-bold transition-all shadow-md";
            
            // Only reset content if changing language, you wouldn't want to lose logic
            // But since this is a simple impl, we swap out
            setEditorContent();
        });
    });

    // Run Tests
    btnRun.addEventListener('click', async () => {
        const code = editor.getValue();
        if (!code.trim()) return;

        btnRun.disabled = true;
        btnRun.classList.add('opacity-50', 'cursor-not-allowed');
        runSpinner.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        try {
            const res = await fetch('/dsa/submit', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    problem_id: parseInt(problemId),
                    language: currentLanguage,
                    code: code
                })
            });

            const data = await res.json();
            if (res.ok) {
                renderResults(data);
                resultsSection.classList.remove('hidden');
                
                // Hide mobile panel on output so they can see results
                if (window.innerWidth < 768 && panelOpen) {
                     leftPanel.classList.add('-translate-x-full');
                     panelOpen = false;
                }
                
                // scroll to results slowly
                setTimeout(() => {
                    resultsSection.scroll({ top: 0, behavior: 'smooth' });
                }, 100);
            } else {
                alert("Submission error: " + (data.detail || "Unknown error"));
            }
        } catch (e) {
            alert("Network error. Please try again.");
        } finally {
            btnRun.disabled = false;
            btnRun.classList.remove('opacity-50', 'cursor-not-allowed');
            runSpinner.classList.add('hidden');
        }
    });

    function getComplexityColorMap(c) {
        const lower = c.toLowerCase();
        if (lower.includes('1') || lower.includes('log n')) return 'bg-green-500/10 text-green-400 border-green-500/30 shadow-[0_0_10px_rgba(74,222,128,0.1)]';
        if (lower.includes('o(n)') && !lower.includes('n²')) return 'bg-blue-500/10 text-blue-400 border-blue-500/30 shadow-[0_0_10px_rgba(96,165,250,0.1)]';
        return 'bg-red-500/10 text-red-400 border-red-500/30 shadow-[0_0_10px_rgba(248,113,113,0.1)]';
    }

    function renderResults(data) {
        // Update Score Chip
        document.getElementById('dsa-score-chip').innerHTML = `<svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg> Score: <span class="text-white font-extrabold text-base ml-1">${data.dsa_score || 0}/100</span>`;
        if (document.getElementById('mobile-dsa-score')) {
            document.getElementById('mobile-dsa-score').textContent = `${data.dsa_score || 0}/100`;
        }

        // Stats Bar
        const sBar = document.getElementById('res-stats-bar');
        if (data.status === 'pass') {
            sBar.className = "px-6 py-4 rounded-xl mb-8 flex flex-col md:flex-row md:justify-between items-start md:items-center font-mono text-sm font-bold border bg-green-500/10 border-green-500/30 text-green-400 shadow-[0_0_20px_rgba(34,197,94,0.1)] transition-all";
        } else if (data.status === 'fail') {
            sBar.className = "px-6 py-4 rounded-xl mb-8 flex flex-col md:flex-row md:justify-between items-start md:items-center font-mono text-sm font-bold border bg-red-500/10 border-red-500/30 text-red-400 shadow-[0_0_20px_rgba(239,68,68,0.1)] transition-all";
        } else {
            sBar.className = "px-6 py-4 rounded-xl mb-8 flex flex-col md:flex-row md:justify-between items-start md:items-center font-mono text-sm font-bold border bg-yellow-500/10 border-yellow-500/30 text-yellow-500 shadow-[0_0_20px_rgba(234,179,8,0.1)] transition-all";
        }
        
        sBar.innerHTML = `
            <div class="flex items-center flex-wrap gap-4">
                <span class="flex items-center gap-2 text-base">
                    ${data.status === 'pass' ? '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>' : ''}
                    ${data.passed_cases}/${data.total_cases} Passed
                </span>
                <span class="text-gray-600 hidden md:inline">|</span>
                <span class="text-gray-300 font-medium bg-gray-900/50 px-3 py-1 rounded-md border border-gray-700/50">Runtime: <span class="text-white">${data.runtime_ms}ms</span></span>
                <span class="text-gray-300 font-medium bg-gray-900/50 px-3 py-1 rounded-md border border-gray-700/50">Memory: <span class="text-white">${(data.memory_kb / 1024).toFixed(1)}MB</span></span>
            </div>
            <div class="uppercase tracking-widest font-black text-lg mt-3 md:mt-0 opacity-80">${data.status}</div>
        `;

        // Complexity
        const crow = document.getElementById('complexity-row');
        const tcClass = getComplexityColorMap(data.time_complexity);
        const scClass = getComplexityColorMap(data.space_complexity);
        crow.innerHTML = `
            <div class="px-4 py-1.5 rounded-lg border text-sm font-mono font-bold ${tcClass} flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                Time: ${data.time_complexity}
            </div>
            <div class="px-4 py-1.5 rounded-lg border text-sm font-mono font-bold ${scClass} flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                Space: ${data.space_complexity}
            </div>
        `;

        // Cases
        const tlist = document.getElementById('test-cases-list');
        tlist.innerHTML = '';
        if (data.per_case_results && data.per_case_results.length > 0) {
            data.per_case_results.forEach(tc => {
                const el = document.createElement('div');
                el.className = `p-5 rounded-2xl bg-[#0F1117] border shadow-sm ${tc.passed ? 'border-gray-800' : 'border-red-500/30'}`;
                
                const icon = tc.passed 
                    ? `<div class="bg-green-500/20 p-1.5 rounded-full text-green-500"><svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg></div>` 
                    : `<div class="bg-red-500/20 p-1.5 rounded-full text-red-500"><svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg></div>`;

                if (tc.hidden) {
                    el.innerHTML = `
                        <div class="flex items-center gap-4">
                            ${icon}
                            <span class="text-white font-bold tracking-wide">Hidden Test ${tc.case_id}</span>
                            <span class="ml-auto text-xs font-black px-2.5 py-1 rounded bg-gray-900 border border-gray-800 uppercase tracking-widest ${tc.passed ? 'text-green-500' : 'text-red-500'}">${tc.passed ? 'Passed' : 'Failed'}</span>
                        </div>
                        ${tc.error ? `<div class="mt-4 p-4 bg-red-500/10 text-red-400 font-mono text-sm rounded-xl border border-red-500/20 overflow-x-auto whitespace-pre">${tc.error}</div>` : ''}
                    `;
                } else {
                    el.innerHTML = `
                        <div class="flex items-center gap-4 mb-5">
                            ${icon}
                            <span class="text-white font-bold tracking-wide">Test Case ${tc.case_id}</span>
                            <span class="ml-auto text-xs font-black px-2.5 py-1 rounded bg-gray-900 border border-gray-800 uppercase tracking-widest ${tc.passed ? 'text-green-500' : 'text-red-500'}">${tc.passed ? 'Passed' : 'Failed'}</span>
                        </div>
                        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
                            <div class="bg-[#1A1D24] rounded-xl p-3 border border-gray-800 shadow-inner">
                                <div class="text-[11px] text-gray-500 mb-2 font-black uppercase tracking-widest">Input</div>
                                <div class="font-mono text-xs text-gray-300 break-all whitespace-pre">${tc.input || '-'}</div>
                            </div>
                            <div class="bg-[#1A1D24] rounded-xl p-3 border border-gray-800 shadow-inner">
                                <div class="text-[11px] text-gray-500 mb-2 font-black uppercase tracking-widest">Expected</div>
                                <div class="font-mono text-xs text-teal-400 font-bold break-all whitespace-pre">${tc.expected || '-'}</div>
                            </div>
                            <div class="bg-[#1A1D24] rounded-xl p-3 border overflow-hidden relative shadow-inner ${tc.passed ? 'border-gray-800' : 'border-red-500/30'}">
                                <div class="text-[11px] text-gray-500 mb-2 font-black uppercase tracking-widest">Output</div>
                                <div class="font-mono text-xs ${tc.passed ? 'text-gray-300' : 'text-red-400 font-bold'} break-all whitespace-pre">${tc.actual || '-'}</div>
                            </div>
                        </div>
                        ${tc.error ? `<div class="mt-4 p-4 bg-red-500/10 text-red-400 font-mono text-sm font-bold rounded-xl border border-red-500/20 overflow-x-auto whitespace-pre">${tc.error}</div>` : ''}
                    `;
                }
                tlist.appendChild(el);
            });
        }

        // Follow Up
        const fcard = document.getElementById('follow-up-card');
        const ftext = document.getElementById('follow-up-text');
        if (data.status === 'pass' && data.follow_up_question) {
            ftext.textContent = data.follow_up_question;
            fcard.classList.remove('hidden');
        } else {
            fcard.classList.add('hidden');
        }

        // AI Feedback
        if (data.ai_feedback) {
            document.getElementById('ai-feedback-body').textContent = data.ai_feedback;
        } else {
            document.getElementById('ai-feedback-body').textContent = "Analysis complete, but AI feedback generation failed.";
        }
    }

    // Hint Logic
    btnHint.addEventListener('click', async () => {
        if (currentHintLevel >= 4) return;
        
        const code = editor ? editor.getValue() : '';
        const levelToRequest = currentHintLevel + 1;
        
        btnHint.disabled = true;
        const oldText = btnHint.innerHTML;
        btnHint.innerHTML = `<svg class="animate-spin h-4 w-4 text-amber-500" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Resolving Hint...`;

        try {
            const res = await fetch('/dsa/hint', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    problem_id: parseInt(problemId),
                    code: code,
                    level: levelToRequest
                })
            });

            const data = await res.json();
            if (res.ok) {
                currentHintLevel = data.level;
                
                // Update dots
                const dots = elHintDots.children;
                for (let i = 0; i < 4; i++) {
                    if (i < currentHintLevel) {
                        dots[i].className = "w-2.5 h-2.5 rounded-full bg-amber-500 border-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.5)] transition-all";
                    } else {
                        dots[i].className = "w-2.5 h-2.5 rounded-full border border-gray-600 transition-all";
                    }
                }
                
                // Appeand hint text
                const hEl = document.createElement('div');
                hEl.className = "mt-4 p-4 bg-gradient-to-br from-amber-500/10 to-amber-900/10 border-l-4 border-l-amber-500 rounded-xl text-sm leading-relaxed whitespace-pre-wrap flex flex-col gap-2 shadow-sm animate-fade-in";
                
                const safeHint = data.hint.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                
                hEl.innerHTML = `
                <span class="text-amber-500 font-black uppercase tracking-widest text-[10px] flex items-center gap-1.5"><svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z"></path></svg> Level ${currentHintLevel} Revelation</span>
                <span class="text-gray-200 font-medium">${safeHint}</span>
                `;
                elHintContainer.appendChild(hEl);

                // Update button
                if (currentHintLevel >= 4) {
                    btnHint.innerHTML = "Max Hints Reached";
                    btnHint.className = "flex justify-center items-center gap-2 px-5 py-2.5 border-2 border-gray-700 bg-gray-800/50 text-gray-500 rounded-xl text-sm transition-all font-bold w-full cursor-not-allowed";
                } else {
                    btnHint.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg> Drop Next Hint (Level ${currentHintLevel + 1})`;
                }

            } else {
                alert("Failed to get hint: " + (data.detail || "Unknown error"));
                btnHint.innerHTML = oldText;
            }
        } catch (e) {
            alert("Network error fetching hint.");
            btnHint.innerHTML = oldText;
        } finally {
            if (currentHintLevel < 4) {
                btnHint.disabled = false;
            }
        }
    });
});
