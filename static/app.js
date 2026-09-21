/**
 * SiteTree Debugger - High-Density 2,000 AI Verification Grid
 * Instant search, division filtering, status filtering, and fast pagination across 2,000 parameters.
 */

// State
let currentAuditId = null;
let currentAuditData = null;
let allWorkers = [];
let filteredWorkers = [];
let currentPage = 1;
const PAGE_SIZE = 48; // 48 items per page = 42 pages for 2,000 items

let activeDivision = "all";
let activeStatus = "all";
let searchQuery = "";

// DOM Elements
const auditForm = document.getElementById("audit-form");
const targetUrlInput = document.getElementById("target-url-input");
const btnAnalyze = document.getElementById("btn-analyze");
const btnDemoUrl = document.getElementById("btn-demo-url");
const liveStatusBar = document.getElementById("live-status-bar");
const liveStatusText = document.getElementById("live-status-text");
const liveStatusSub = document.getElementById("live-status-sub");
const resultsWrapper = document.getElementById("results-wrapper");
const aiWorkersGrid = document.getElementById("ai-workers-grid");
const crashSpotlightCard = document.getElementById("crash-spotlight-card");
const autofixCard = document.getElementById("autofix-card");

// Search & Filter Inputs
const paramSearchInput = document.getElementById("param-search-input");
const statusFilterCritCount = document.getElementById("status-filter-crit-count");
const statusFilterWarnCount = document.getElementById("status-filter-warn-count");

// Pagination elements
const btnPagePrev = document.getElementById("btn-page-prev");
const btnPageNext = document.getElementById("btn-page-next");
const gridPageNum = document.getElementById("grid-page-num");
const gridShowingText = document.getElementById("grid-showing-text");

const btnPagePrevBottom = document.getElementById("btn-page-prev-bottom");
const btnPageNextBottom = document.getElementById("btn-page-next-bottom");
const gridPageNumBottom = document.getElementById("grid-page-num-bottom");
const gridShowingTextBottom = document.getElementById("grid-showing-text-bottom");

// Metrics
const metricHealthScore = document.getElementById("metric-health-score");
const metricHealthIcon = document.getElementById("metric-health-icon");
const metricCriticalCount = document.getElementById("metric-critical-count");
const metricWarningCount = document.getElementById("metric-warning-count");
const metricPassedCount = document.getElementById("metric-passed-count");

// Modal
const nodeModal = document.getElementById("node-modal");
const btnCloseNodeModal = document.getElementById("btn-close-node-modal");
const modalNodeTitle = document.getElementById("modal-node-title");
const modalNodeStatus = document.getElementById("modal-node-status");
const modalNodeIcon = document.getElementById("modal-node-icon");
const modalNodeContent = document.getElementById("modal-node-content");

// History Drawer
const historyDrawer = document.getElementById("history-drawer");
const btnOpenHistory = document.getElementById("btn-open-history");
const btnCloseHistory = document.getElementById("btn-close-history");
const historyList = document.getElementById("history-list");

// Settings Modal
const settingsModal = document.getElementById("settings-modal");
const btnOpenSettings = document.getElementById("btn-open-settings");
const btnCloseSettings = document.getElementById("btn-close-settings");
const btnCancelSettings = document.getElementById("btn-cancel-settings");
const settingsForm = document.getElementById("settings-form");
const settingGeminiKey = document.getElementById("setting-gemini-key");
const settingModel = document.getElementById("setting-model");

// Exports
const btnExportMd = document.getElementById("btn-export-md");
const btnExportJson = document.getElementById("btn-export-json");

// Helper to determine endpoints safely
function getEndpoints() {
    const proto = window.location.protocol;
    const host = window.location.host;
    
    if (proto === "file:" || !host || host === "") {
        return {
            httpBase: "http://127.0.0.1:8000",
            wsBase: "ws://127.0.0.1:8000"
        };
    }
    
    const wsProto = proto === "https:" ? "wss:" : "ws:";
    return {
        httpBase: window.location.origin,
        wsBase: `${wsProto}//${host}`
    };
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    initFilters();
    initPagination();
    initSettings();
    initHistory();
});

// Demo URL Button
btnDemoUrl.addEventListener("click", () => {
    const { httpBase } = getEndpoints();
    targetUrlInput.value = `${httpBase}/api/demo-broken-site`;
    auditForm.dispatchEvent(new Event("submit"));
});

// Form Submission
auditForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const url = targetUrlInput.value.trim();
    if (!url) return;

    startAudit(url);
});

function initFilters() {
    // Instant Search
    paramSearchInput.addEventListener("input", (e) => {
        searchQuery = e.target.value.toLowerCase().trim();
        currentPage = 1;
        applyFiltersAndRender();
    });

    // Status Filter Buttons
    const statusBtns = document.querySelectorAll(".status-filter-btn");
    statusBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            statusBtns.forEach(b => {
                b.className = "status-filter-btn px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200 hover:bg-slate-200 cursor-pointer";
            });
            btn.className = "status-filter-btn px-2.5 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-800 border border-blue-200 cursor-pointer";
            activeStatus = btn.getAttribute("data-status");
            currentPage = 1;
            applyFiltersAndRender();
        });
    });

    // Division Filter Buttons
    const divBtns = document.querySelectorAll(".div-filter-btn");
    divBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            divBtns.forEach(b => {
                b.className = "div-filter-btn px-2.5 py-1 rounded-md text-[11px] font-medium bg-slate-100 text-slate-700 border border-slate-200 hover:bg-slate-200 cursor-pointer";
            });
            btn.className = "div-filter-btn px-2.5 py-1 rounded-md text-[11px] font-medium bg-blue-50 text-blue-800 border border-blue-200 cursor-pointer";
            activeDivision = btn.getAttribute("data-filter");
            currentPage = 1;
            applyFiltersAndRender();
        });
    });
}

function initPagination() {
    const goPrev = () => {
        if (currentPage > 1) {
            currentPage--;
            renderGridPage();
        }
    };
    const goNext = () => {
        const maxPages = Math.ceil(filteredWorkers.length / PAGE_SIZE) || 1;
        if (currentPage < maxPages) {
            currentPage++;
            renderGridPage();
        }
    };

    btnPagePrev.addEventListener("click", goPrev);
    btnPageNext.addEventListener("click", goNext);
    btnPagePrevBottom.addEventListener("click", goPrev);
    btnPageNextBottom.addEventListener("click", goNext);
}

function applyFiltersAndRender() {
    filteredWorkers = allWorkers.filter(w => {
        // Division filter
        if (activeDivision !== "all" && w.division !== activeDivision) {
            return false;
        }
        // Status filter
        if (activeStatus !== "all" && w.status !== activeStatus) {
            return false;
        }
        // Search query
        if (searchQuery) {
            const inTitle = w.title.toLowerCase().includes(searchQuery);
            const inMsg = (w.details?.simple_message || "").toLowerCase().includes(searchQuery);
            const inDiv = (w.division || "").toLowerCase().includes(searchQuery);
            if (!inTitle && !inMsg && !inDiv) {
                return false;
            }
        }
        return true;
    });

    renderGridPage();
}

function renderGridPage() {
    const total = filteredWorkers.length;
    const maxPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    if (currentPage > maxPages) currentPage = maxPages;

    const startIdx = (currentPage - 1) * PAGE_SIZE;
    const endIdx = Math.min(total, startIdx + PAGE_SIZE);
    const pageItems = filteredWorkers.slice(startIdx, endIdx);

    const infoText = total === 0 ? "No matching parameters found" : `Showing ${startIdx + 1}–${endIdx} of ${total.toLocaleString()} AI Parameters`;
    gridShowingText.textContent = infoText;
    gridShowingTextBottom.textContent = infoText;

    const pageText = `${currentPage} / ${maxPages}`;
    gridPageNum.textContent = pageText;
    gridPageNumBottom.textContent = pageText;

    btnPagePrev.disabled = currentPage <= 1;
    btnPageNext.disabled = currentPage >= maxPages;
    btnPagePrevBottom.disabled = currentPage <= 1;
    btnPageNextBottom.disabled = currentPage >= maxPages;

    aiWorkersGrid.innerHTML = "";

    if (pageItems.length === 0) {
        aiWorkersGrid.innerHTML = `<div class="col-span-full py-8 text-center text-xs text-slate-500">No parameters match your search query. Try typing another keyword.</div>`;
        return;
    }

    pageItems.forEach(w => {
        const card = document.createElement("div");
        card.id = `worker-${w.id}`;
        card.className = `ai-worker-card rounded-lg p-3 flex flex-col justify-between text-left transition shadow-xs ${w.status === 'critical' ? 'border-rose-300 bg-rose-50/30' : (w.status === 'warning' ? 'border-amber-300 bg-amber-50/30' : '')}`;
        card.onclick = () => openWorkerModal(w);

        let badgeClass = "bg-emerald-100 text-emerald-800";
        let badgeLabel = "PASSED";
        if (w.status === "critical") {
            badgeClass = "bg-rose-100 text-rose-800 font-bold";
            badgeLabel = "FAIL";
        } else if (w.status === "warning") {
            badgeClass = "bg-amber-100 text-amber-800 font-bold";
            badgeLabel = "WARN";
        }

        card.innerHTML = `
            <div class="flex items-center justify-between mb-1.5">
                <span class="text-[10px] font-medium text-slate-500 truncate max-w-[140px]">${w.division}</span>
                <span class="text-[9px] px-1.5 py-0.5 rounded-full font-mono ${badgeClass}">${badgeLabel}</span>
            </div>
            <div>
                <h5 class="font-bold text-xs text-slate-900 truncate">${escapeHtml(w.title)}</h5>
                <p class="text-[11px] ${w.status === 'critical' ? 'text-rose-900 font-medium' : (w.status === 'warning' ? 'text-amber-900' : 'text-slate-600')} mt-1 line-clamp-2">
                    ${escapeHtml(w.details?.simple_message || 'Parameter check passed.')}
                </p>
            </div>
            <div class="text-[10px] text-blue-700 font-medium mt-2 flex items-center justify-between">
                <span>View Details</span>
                <i class="fa-solid fa-angle-right text-[8px]"></i>
            </div>
        `;

        aiWorkersGrid.appendChild(card);
    });
}

// Start Audit (Dual-Transport: WebSocket with seamless HTTP REST Fallback)
function startAudit(url) {
    btnAnalyze.disabled = true;
    liveStatusBar.classList.remove("hidden");
    resultsWrapper.classList.remove("hidden");
    liveStatusText.textContent = `Deploying 2,000 AI parameter verification grid on: ${url}`;
    liveStatusSub.textContent = "Testing network, scripts, DOM, crashes, APIs, mobile viewports, and security...";

    const { httpBase, wsBase } = getEndpoints();

    if (window.location.protocol === "file:" || typeof WebSocket === "undefined") {
        runHttpAudit(url, httpBase);
        return;
    }

    let wsHandshakeSuccess = false;
    let wsTimedOut = false;
    let socket = null;

    const wsWatchdog = setTimeout(() => {
        if (!wsHandshakeSuccess) {
            wsTimedOut = true;
            if (socket) {
                try { socket.close(); } catch (e) {}
            }
            console.warn("WebSocket timeout. Seamlessly running 2,000 AI parameters via HTTP REST.");
            runHttpAudit(url, httpBase);
        }
    }, 2000);

    try {
        const wsUrl = `${wsBase}/ws/analyze`;
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            liveStatusText.textContent = `Inspecting website: ${url}`;
            socket.send(JSON.stringify({ url }));
        };

        socket.onmessage = (event) => {
            wsHandshakeSuccess = true;
            clearTimeout(wsWatchdog);

            try {
                const msg = JSON.parse(event.data);

                if (msg.type === "crawl_started") {
                    liveStatusText.textContent = "Crawling site assets & building 2,000 AI parameter matrix...";
                    liveStatusSub.textContent = msg.message;
                } else if (msg.type === "crawl_completed") {
                    liveStatusText.textContent = "Evaluating 2,000 specialized AI parameter checkpoints...";
                    liveStatusSub.textContent = "Calculating failure points across 10 master divisions...";
                } else if (msg.type === "audit_completed") {
                    liveStatusBar.classList.add("hidden");
                    btnAnalyze.disabled = false;
                    currentAuditId = msg.audit_id;
                    currentAuditData = msg.full_data;
                    renderAuditReport(msg.full_data);
                    refreshHistory();
                } else if (msg.type === "error") {
                    liveStatusText.textContent = `Inspection notice: ${msg.message}`;
                    btnAnalyze.disabled = false;
                }
            } catch (err) {
                console.error("Error parsing WebSocket message:", err);
            }
        };

        socket.onerror = () => {
            if (!wsHandshakeSuccess && !wsTimedOut) {
                clearTimeout(wsWatchdog);
                runHttpAudit(url, httpBase);
            }
        };

        socket.onclose = () => {
            if (!wsHandshakeSuccess && !wsTimedOut) {
                clearTimeout(wsWatchdog);
                runHttpAudit(url, httpBase);
            }
        };
    } catch (err) {
        clearTimeout(wsWatchdog);
        runHttpAudit(url, httpBase);
    }
}

// HTTP REST Audit Engine
async function runHttpAudit(url, httpBase) {
    liveStatusText.textContent = `Inspecting website: ${url}`;
    liveStatusSub.textContent = "Running 2,000 AI parameter verification grid via REST engine...";

    try {
        const res = await fetch(`${httpBase}/api/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
            throw new Error(errData.detail || `Server error ${res.status}`);
        }

        const data = await res.json();
        const fullData = data.full_data || {};

        liveStatusBar.classList.add("hidden");
        btnAnalyze.disabled = false;
        currentAuditId = data.audit_id;
        currentAuditData = fullData;
        renderAuditReport(fullData);
        refreshHistory();
    } catch (err) {
        liveStatusText.textContent = `Audit notice: ${err.message}`;
        liveStatusSub.textContent = `Ensure server is running at ${httpBase}.`;
        btnAnalyze.disabled = false;
    }
}

// Render Complete Audit Report with Simple Plain-English
function renderAuditReport(data) {
    const summary = data.summary || {};
    const tree = data.tree_data?.nodes || {};
    const crashNode = tree.synthesis_crash_pinpointer?.details || {};
    const autofixNode = tree.synthesis_autofix?.details || {};

    // 1. Convert all 2,000 nodes into workers list
    allWorkers = [];
    let critCount = 0;
    let warnCount = 0;

    for (const [nid, node] of Object.entries(tree)) {
        if (nid.startsWith("param_")) {
            allWorkers.push({
                id: nid,
                title: node.title,
                division: node.division,
                status: node.status,
                details: node.details
            });
            if (node.status === "critical") critCount++;
            else if (node.status === "warning") warnCount++;
        }
    }

    statusFilterCritCount.textContent = critCount;
    statusFilterWarnCount.textContent = warnCount;

    // 2. Health Score Cards
    const score = summary.overall_health_score ?? 100;
    metricHealthScore.textContent = `${score}/100`;
    metricCriticalCount.textContent = summary.critical_issues_count ?? critCount;
    metricWarningCount.textContent = summary.warning_issues_count ?? warnCount;
    metricPassedCount.textContent = `${summary.total_ai_workers || allWorkers.length || 2000}`;

    if (score >= 80) {
        metricHealthIcon.className = "w-12 h-12 rounded-lg bg-emerald-50 text-emerald-600 border border-emerald-200 flex items-center justify-center text-xl";
        metricHealthIcon.innerHTML = `<i class="fa-solid fa-circle-check"></i>`;
    } else if (score >= 50) {
        metricHealthIcon.className = "w-12 h-12 rounded-lg bg-amber-50 text-amber-600 border border-amber-200 flex items-center justify-center text-xl";
        metricHealthIcon.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i>`;
    } else {
        metricHealthIcon.className = "w-12 h-12 rounded-lg bg-rose-50 text-rose-600 border border-rose-200 flex items-center justify-center text-xl";
        metricHealthIcon.innerHTML = `<i class="fa-solid fa-circle-xmark"></i>`;
    }

    // 3. CRASH POINT SPOTLIGHT BANNER (SIMPLE PLAIN ENGLISH)
    renderSimpleCrashSpotlight(summary.site_crashes, crashNode);

    // 4. Simple Fix Card
    renderSimpleAutoFix(autofixNode);

    // 5. Render Grid with filters and pagination
    currentPage = 1;
    applyFiltersAndRender();
}

function renderSimpleCrashSpotlight(siteCrashes, crashNode) {
    const bannerClass = siteCrashes ? "crash-banner-critical" : (crashNode.has_warnings ? "crash-banner-warning" : "crash-banner-healthy");
    const badgeText = siteCrashes ? "CRITICAL POINT OF FAILURE" : (crashNode.has_warnings ? "WEBSITE WORKING WITH WARNINGS" : "ALL SYSTEMS OPERATIONAL");
    const badgeClass = siteCrashes ? "bg-rose-100 text-rose-800 border-rose-200" : (crashNode.has_warnings ? "bg-amber-100 text-amber-800 border-amber-200" : "bg-emerald-100 text-emerald-800 border-emerald-200");

    let timelineHtml = "";
    if (crashNode.user_experience_timeline && crashNode.user_experience_timeline.length) {
        timelineHtml = `
            <div class="mt-4 pt-4 border-t border-slate-200/60 space-y-2">
                <h5 class="text-xs font-bold uppercase text-slate-700 tracking-wider">What Your Visitor Experiences (Step-by-Step):</h5>
                <div class="space-y-1.5">
                    ${crashNode.user_experience_timeline.map(step => {
                        const isFail = step.includes("[WEBSITE STOPS]") || step.includes("[CRASH]") || step.includes("error");
                        return `
                            <div class="flex items-start gap-2 text-xs">
                                <span class="mt-0.5 ${isFail ? 'text-rose-600 font-bold' : 'text-slate-500'}"><i class="${isFail ? 'fa-solid fa-circle-xmark' : 'fa-solid fa-circle-check text-emerald-600'}"></i></span>
                                <span class="${isFail ? 'text-rose-900 font-semibold' : 'text-slate-700'}">${escapeHtml(step)}</span>
                            </div>
                        `;
                    }).join("")}
                </div>
            </div>
        `;
    }

    crashSpotlightCard.className = `rounded-xl border p-6 shadow-sm transition ${bannerClass}`;
    crashSpotlightCard.innerHTML = `
        <div class="flex flex-wrap items-center justify-between gap-2">
            <span class="text-xs font-bold uppercase px-3 py-1 rounded-full border ${badgeClass}">
                ${badgeText}
            </span>
            <span class="text-xs text-slate-500 font-medium">2,000 AI Parameters Checked</span>
        </div>
        <div class="mt-3">
            <h3 class="text-base font-bold text-slate-900">${escapeHtml(crashNode.point_of_failure || 'Audit completed successfully.')}</h3>
            <p class="text-sm text-slate-700 mt-1">${escapeHtml(crashNode.simple_explanation || '')}</p>
            ${crashNode.fix_tip ? `<p class="text-xs text-blue-700 font-medium mt-2"><span class="font-bold">Simple Fix Tip:</span> ${escapeHtml(crashNode.fix_tip)}</p>` : ''}
        </div>
        ${timelineHtml}
    `;
}

function renderSimpleAutoFix(fix) {
    if (!fix) return;

    let instructionsHtml = "";
    if (fix.simple_instructions && fix.simple_instructions.length) {
        instructionsHtml = fix.simple_instructions.map((step, idx) => `
            <li class="flex items-start gap-2 text-xs text-slate-700">
                <span class="w-4 h-4 rounded-full bg-blue-100 text-blue-800 text-[10px] flex items-center justify-center font-bold mt-0.5">${idx + 1}</span>
                <span>${escapeHtml(step)}</span>
            </li>
        `).join("");
    }

    autofixCard.innerHTML = `
        <div class="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-4">
            <div>
                <h4 class="text-base font-bold text-slate-900 flex items-center gap-2">
                    <i class="fa-solid fa-wrench text-blue-600"></i> ${escapeHtml(fix.patch_title || 'Recommended Fix')}
                </h4>
                <p class="text-xs text-slate-500 mt-0.5">Simple, step-by-step instructions to prevent your site from crashing.</p>
            </div>
            <button onclick="copyCodeDiff()" class="text-xs px-3 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 transition flex items-center gap-1.5 font-medium cursor-pointer">
                <i class="fa-solid fa-copy"></i> Copy Safe Code
            </button>
        </div>

        <div class="relative rounded-lg overflow-hidden bg-slate-900 border border-slate-800 p-4 font-mono text-xs text-slate-100">
            <pre id="code-diff-content" class="overflow-x-auto whitespace-pre">${escapeHtml(fix.code_diff || '// All 2,000 tests passed. No code change needed.')}</pre>
        </div>

        ${instructionsHtml ? `
            <div class="space-y-2 pt-1">
                <h5 class="text-xs font-bold text-slate-900 uppercase tracking-wider">How to Apply This Fix (3 Simple Steps):</h5>
                <ul class="space-y-1.5">${instructionsHtml}</ul>
            </div>
        ` : ''}

        ${fix.plain_english_tip ? `
            <div class="rounded-lg bg-blue-50 border border-blue-200 p-3 text-xs text-blue-900 flex items-start gap-2.5">
                <i class="fa-solid fa-lightbulb text-amber-500 mt-0.5"></i>
                <div>
                    <span class="font-bold">Simple Advice:</span> ${escapeHtml(fix.plain_english_tip)}
                </div>
            </div>
        ` : ''}
    `;
}

function copyCodeDiff() {
    const el = document.getElementById("code-diff-content");
    if (el) {
        navigator.clipboard.writeText(el.innerText).then(() => {
            alert("Code snippet copied to clipboard!");
        });
    }
}

// Open Worker Details Modal
function openWorkerModal(w) {
    modalNodeTitle.textContent = w.title;
    modalNodeStatus.textContent = w.status.toUpperCase();
    modalNodeIcon.className = `w-10 h-10 rounded-lg flex items-center justify-center text-lg ${w.status === 'critical' ? 'bg-rose-50 text-rose-600' : (w.status === 'warning' ? 'bg-amber-50 text-amber-600' : 'bg-emerald-50 text-emerald-600')}`;
    modalNodeIcon.innerHTML = `<i class="${w.status === 'critical' ? 'fa-solid fa-circle-xmark' : (w.status === 'warning' ? 'fa-solid fa-triangle-exclamation' : 'fa-solid fa-circle-check')}"></i>`;

    const details = w.details || {};
    modalNodeContent.innerHTML = `
        <div class="space-y-3">
            <div>
                <span class="text-xs font-bold text-slate-900">What this AI parameter verified:</span>
                <p class="text-xs text-slate-700 mt-0.5">${escapeHtml(details.simple_message || 'Inspected site parameters.')}</p>
            </div>
            ${details.fix_advice ? `
                <div class="p-3 rounded-lg bg-slate-50 border border-slate-200">
                    <span class="text-xs font-bold text-blue-800">How to Fix This:</span>
                    <p class="text-xs text-slate-700 mt-0.5">${escapeHtml(details.fix_advice)}</p>
                </div>
            ` : ''}
            <div class="text-[11px] text-slate-500">
                Division: <span class="font-medium text-slate-700">${w.division}</span> &bull; Vector ID: <span class="font-mono text-slate-700">${w.id}</span>
            </div>
        </div>
    `;

    nodeModal.classList.remove("hidden");
}

btnCloseNodeModal.addEventListener("click", () => nodeModal.classList.add("hidden"));
nodeModal.addEventListener("click", (e) => {
    if (e.target === nodeModal) nodeModal.classList.add("hidden");
});

// History logic
function initHistory() {
    btnOpenHistory.addEventListener("click", () => {
        refreshHistory();
        historyDrawer.classList.remove("translate-x-full");
    });

    btnCloseHistory.addEventListener("click", () => {
        historyDrawer.classList.add("translate-x-full");
    });
}

async function refreshHistory() {
    const { httpBase } = getEndpoints();
    try {
        const res = await fetch(`${httpBase}/api/history`);
        const list = await res.json();

        if (!list || list.length === 0) {
            historyList.innerHTML = `<p class="text-xs text-slate-500 text-center py-6">No previous audits found.</p>`;
            return;
        }

        historyList.innerHTML = list.map(item => `
            <div onclick="loadPastAudit('${item.id}')" class="p-3 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200 cursor-pointer transition space-y-1">
                <div class="flex items-center justify-between text-xs">
                    <span class="font-bold text-slate-900 truncate max-w-[200px]">${escapeHtml(item.target_url)}</span>
                    <span class="font-medium text-[10px] px-2 py-0.5 rounded-full ${item.site_crashes ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800'}">
                        Score: ${item.health_score}/100
                    </span>
                </div>
                <p class="text-[11px] text-slate-500 truncate">${escapeHtml(item.crash_point || 'Passed 2,000 checks')}</p>
            </div>
        `).join("");
    } catch (err) {
        console.error("Failed to fetch history:", err);
    }
}

async function loadPastAudit(auditId) {
    const { httpBase } = getEndpoints();
    try {
        const res = await fetch(`${httpBase}/api/audit/${auditId}`);
        const data = await res.json();
        currentAuditId = auditId;
        currentAuditData = data;
        historyDrawer.classList.add("translate-x-full");
        resultsWrapper.classList.remove("hidden");
        targetUrlInput.value = data.target_url;

        renderAuditReport(data);
    } catch (err) {
        alert("Could not load past audit.");
    }
}

// Settings logic
function initSettings() {
    btnOpenSettings.addEventListener("click", async () => {
        const { httpBase } = getEndpoints();
        try {
            const res = await fetch(`${httpBase}/api/settings`);
            const data = await res.json();
            settingGeminiKey.value = data.gemini_api_key || "";
            settingModel.value = data.preferred_model || "gemini-2.5-flash";
        } catch (err) {}
        settingsModal.classList.remove("hidden");
    });

    const closeSettings = () => settingsModal.classList.add("hidden");
    btnCloseSettings.addEventListener("click", closeSettings);
    btnCancelSettings.addEventListener("click", closeSettings);
    settingsModal.addEventListener("click", (e) => {
        if (e.target === settingsModal) closeSettings();
    });

    settingsForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const { httpBase } = getEndpoints();
        const payload = {
            gemini_api_key: settingGeminiKey.value.trim(),
            preferred_model: settingModel.value
        };
        try {
            await fetch(`${httpBase}/api/settings`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            alert("Settings saved successfully!");
            closeSettings();
        } catch (err) {
            alert("Failed to save settings.");
        }
    });
}

// Exports
btnExportMd.addEventListener("click", () => {
    if (!currentAuditId) return;
    const { httpBase } = getEndpoints();
    window.open(`${httpBase}/api/export/${currentAuditId}?format=markdown`, "_blank");
});

btnExportJson.addEventListener("click", () => {
    if (!currentAuditId) return;
    const { httpBase } = getEndpoints();
    window.open(`${httpBase}/api/export/${currentAuditId}?format=json`, "_blank");
});

// Utilities
function escapeHtml(str) {
    if (typeof str !== "string") return str;
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
