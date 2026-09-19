/**
 * SiteTree Debugger Frontend Engine
 * Dual-Transport: Real-time WebSocket + Automatic HTTP REST Fallback,
 * Interactive visual tree renderer, timeline pinpointer, and bug matrix.
 */

// State
let currentAuditId = null;
let currentAuditData = null;
let currentNodesState = {};

// DOM Elements
const auditForm = document.getElementById("audit-form");
const targetUrlInput = document.getElementById("target-url-input");
const btnAnalyze = document.getElementById("btn-analyze");
const btnDemoUrl = document.getElementById("btn-demo-url");
const liveStatusBar = document.getElementById("live-status-bar");
const liveStatusText = document.getElementById("live-status-text");
const liveStatusSub = document.getElementById("live-status-sub");
const resultsWrapper = document.getElementById("results-wrapper");
const treeVisualizer = document.getElementById("ai-tree-visualizer");
const crashSpotlightCard = document.getElementById("crash-spotlight-card");
const autofixCard = document.getElementById("autofix-card");

// Metrics
const metricHealthScore = document.getElementById("metric-health-score");
const metricHealthIcon = document.getElementById("metric-health-icon");
const metricCriticalCount = document.getElementById("metric-critical-count");
const metricWarningCount = document.getElementById("metric-warning-count");
const metricLatency = document.getElementById("metric-latency");

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
    
    // If opened via file:/// or host is empty, fallback to local backend port 8000
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

// Define Tree Architecture Layout
const TREE_STRUCTURE = [
    {
        level: 0,
        label: "Root Level: Site Decomposer",
        nodes: [
            { id: "root_orchestrator", title: "Root Orchestrator", icon: "fa-solid fa-brain", role: "Site Intake & Task Decomposition" }
        ]
    },
    {
        level: 1,
        label: "Domain Specialist Branches (Concurrent AI Models)",
        nodes: [
            { id: "branch_network", title: "Network & Security", icon: "fa-solid fa-shield-halved", role: "HTTP, SSL, CORS & Headers" },
            { id: "branch_assets", title: "Asset & Dependencies", icon: "fa-solid fa-boxes-stacked", role: "Script & Style 404s" },
            { id: "branch_dom", title: "DOM & Interaction", icon: "fa-solid fa-window-maximize", role: "Forms & Dead Links" },
            { id: "branch_scripts", title: "Script Runtime Crash", icon: "fa-brands fa-js", role: "Null Derefs & Exceptions" },
            { id: "branch_api", title: "API & Backend Tracer", icon: "fa-solid fa-server", role: "XHR/Fetch Connectivity" }
        ]
    },
    {
        level: 2,
        label: "Diagnostic Synthesis & Auto-Remediation",
        nodes: [
            { id: "synthesis_crash_pinpointer", title: "Crash Point Pinpointer", icon: "fa-solid fa-crosshairs", role: "Traces Exact Point of Failure" },
            { id: "synthesis_autofix", title: "Auto-Fix Synthesizer", icon: "fa-solid fa-screwdriver-wrench", role: "Produces Code Patches" }
        ]
    }
];

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initSettings();
    initHistory();
    renderInitialTreeSkeleton();
});

// Demo URL Handler
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

function renderInitialTreeSkeleton() {
    treeVisualizer.innerHTML = "";

    TREE_STRUCTURE.forEach((tier, tierIdx) => {
        const tierWrapper = document.createElement("div");
        tierWrapper.className = "w-full flex flex-col items-center space-y-2";

        const label = document.createElement("div");
        label.className = "text-[11px] font-mono text-slate-400 uppercase tracking-wider";
        label.textContent = tier.label;
        tierWrapper.appendChild(label);

        const nodesRow = document.createElement("div");
        nodesRow.className = "flex flex-wrap justify-center gap-3 w-full";

        tier.nodes.forEach(n => {
            const card = document.createElement("div");
            card.id = `node-${n.id}`;
            card.className = "tree-node rounded-xl p-3 w-56 flex flex-col justify-between text-left transition border border-darkborder";
            card.onclick = () => openNodeModal(n.id);

            card.innerHTML = `
                <div class="flex items-center justify-between mb-2">
                    <div class="w-8 h-8 rounded-lg bg-slate-800 text-slate-400 flex items-center justify-center node-icon">
                        <i class="${n.icon}"></i>
                    </div>
                    <span class="node-badge text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">IDLE</span>
                </div>
                <div>
                    <h5 class="font-bold text-xs text-white truncate">${n.title}</h5>
                    <p class="text-[11px] text-slate-400 truncate">${n.role}</p>
                </div>
                <div class="node-status-text text-[10px] text-slate-400 mt-2 truncate">Waiting for input...</div>
            `;
            nodesRow.appendChild(card);
            currentNodesState[n.id] = { title: n.title, icon: n.icon, status: "idle", details: {} };
        });

        tierWrapper.appendChild(nodesRow);

        // Connector line between tiers
        if (tierIdx < TREE_STRUCTURE.length - 1) {
            const conn = document.createElement("div");
            conn.className = "w-0.5 h-6 bg-slate-700/80 my-1";
            tierWrapper.appendChild(conn);
        }

        treeVisualizer.appendChild(tierWrapper);
    });
}

function updateNodeVisual(nodeId, status, details = {}) {
    const card = document.getElementById(`node-${nodeId}`);
    if (!card) return;

    const badge = card.querySelector(".node-badge");
    const statusText = card.querySelector(".node-status-text");
    const iconBox = card.querySelector(".node-icon");

    card.classList.remove("tree-node-running", "border-rose-500", "border-amber-500", "border-emerald-500", "border-indigo-500");

    if (currentNodesState[nodeId]) {
        currentNodesState[nodeId].status = status;
        currentNodesState[nodeId].details = details;
    }

    if (status === "running") {
        card.classList.add("tree-node-running");
        badge.className = "node-badge text-[10px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 font-mono animate-pulse";
        badge.textContent = "RUNNING";
        iconBox.className = "w-8 h-8 rounded-lg bg-indigo-600/20 text-indigo-400 flex items-center justify-center node-icon";
        statusText.textContent = details.thought || "Analyzing telemetry...";
        statusText.className = "node-status-text text-[10px] text-indigo-300 mt-2 truncate";
    } else if (status === "critical") {
        card.classList.add("border-rose-500");
        badge.className = "node-badge text-[10px] px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-400 font-mono";
        badge.textContent = "CRASH / BUG";
        iconBox.className = "w-8 h-8 rounded-lg bg-rose-600/20 text-rose-400 flex items-center justify-center node-icon";
        statusText.textContent = details.diagnosis || details.point_of_failure || "Critical hazard detected";
        statusText.className = "node-status-text text-[10px] text-rose-400 mt-2 truncate";
    } else if (status === "warning") {
        card.classList.add("border-amber-500");
        badge.className = "node-badge text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 font-mono";
        badge.textContent = "WARNING";
        iconBox.className = "w-8 h-8 rounded-lg bg-amber-600/20 text-amber-400 flex items-center justify-center node-icon";
        statusText.textContent = details.diagnosis || "Warning items found";
        statusText.className = "node-status-text text-[10px] text-amber-400 mt-2 truncate";
    } else if (status === "healthy" || status === "completed") {
        card.classList.add("border-emerald-500");
        badge.className = "node-badge text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono";
        badge.textContent = "PASSED";
        iconBox.className = "w-8 h-8 rounded-lg bg-emerald-600/20 text-emerald-400 flex items-center justify-center node-icon";
        statusText.textContent = details.diagnosis || "All checks passed";
        statusText.className = "node-status-text text-[10px] text-emerald-400 mt-2 truncate";
    }
}

// Start Audit: Tries WebSocket, gracefully and automatically falls back to HTTP REST
function startAudit(url) {
    btnAnalyze.disabled = true;
    liveStatusBar.classList.remove("hidden");
    resultsWrapper.classList.remove("hidden");
    liveStatusText.textContent = `Connecting to audit engine for: ${url}`;
    liveStatusSub.textContent = "Initiating multi-model tree evaluation pipeline...";

    renderInitialTreeSkeleton();

    const { httpBase, wsBase } = getEndpoints();

    // If opened directly from file system (file:///) or WebSocket is unavailable, use HTTP REST immediately
    if (window.location.protocol === "file:" || typeof WebSocket === "undefined") {
        runHttpAudit(url, httpBase);
        return;
    }

    let wsHandshakeSuccess = false;
    let wsTimedOut = false;
    let socket = null;

    // Safety Watchdog: If WebSocket does not respond within 2 seconds, switch to HTTP REST API
    const wsWatchdog = setTimeout(() => {
        if (!wsHandshakeSuccess) {
            wsTimedOut = true;
            if (socket) {
                try { socket.close(); } catch (e) {}
            }
            console.warn("WebSocket watchdog triggered. Switching to HTTP REST engine.");
            runHttpAudit(url, httpBase);
        }
    }, 2000);

    try {
        const wsUrl = `${wsBase}/ws/analyze`;
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            liveStatusText.textContent = `Scraping & inspecting DOM: ${url}`;
            socket.send(JSON.stringify({ url }));
        };

        socket.onmessage = (event) => {
            wsHandshakeSuccess = true;
            clearTimeout(wsWatchdog);

            try {
                const msg = JSON.parse(event.data);

                if (msg.type === "crawl_started") {
                    liveStatusText.textContent = "Crawling website resources...";
                    liveStatusSub.textContent = msg.message;
                } else if (msg.type === "crawl_completed") {
                    const s = msg.crawl_summary;
                    liveStatusText.textContent = `Crawled ${s.scripts_found} scripts & ${s.broken_assets} broken assets. Launching Multi-AI Model Tree...`;
                    liveStatusSub.textContent = `HTTP ${s.status_code} • Latency: ${s.latency_ms}ms • Hazards: ${s.runtime_hazards}`;
                } else if (msg.type === "node_update") {
                    const node = msg.node;
                    updateNodeVisual(node.node_id, node.status, node.details);
                } else if (msg.type === "audit_completed") {
                    liveStatusBar.classList.add("hidden");
                    btnAnalyze.disabled = false;
                    currentAuditId = msg.audit_id;
                    currentAuditData = msg.full_data;
                    renderAuditReport(msg.full_data);
                    refreshHistory();
                } else if (msg.type === "error") {
                    liveStatusText.textContent = `Audit Error: ${msg.message}`;
                    liveStatusSub.textContent = "Please verify the URL is accessible and try again.";
                    btnAnalyze.disabled = false;
                }
            } catch (err) {
                console.error("Error parsing WebSocket message:", err);
            }
        };

        socket.onerror = (err) => {
            if (!wsHandshakeSuccess && !wsTimedOut) {
                clearTimeout(wsWatchdog);
                console.warn("WebSocket error detected. Seamlessly falling back to HTTP REST audit...");
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
        console.warn("WebSocket initialization exception:", err);
        runHttpAudit(url, httpBase);
    }
}

// HTTP REST Audit Engine (100% reliable fallback)
async function runHttpAudit(url, httpBase) {
    liveStatusText.textContent = `Auditing website via REST engine: ${url}`;
    liveStatusSub.textContent = "Crawling HTML, scripts, stylesheets, and evaluating AI decision tree...";

    // Animate nodes sequentially so the UI provides live visual feedback
    updateNodeVisual("root_orchestrator", "running", { thought: `Analyzing site profile for ${url}...` });
    
    const branchTimer = setTimeout(() => {
        ["branch_network", "branch_assets", "branch_dom", "branch_scripts", "branch_api"].forEach(bId => {
            updateNodeVisual(bId, "running", { thought: "Model inspecting parameters..." });
        });
    }, 400);

    const synthTimer = setTimeout(() => {
        updateNodeVisual("synthesis_crash_pinpointer", "running", { thought: "Pinpointing failure points..." });
        updateNodeVisual("synthesis_autofix", "running", { thought: "Synthesizing code fixes..." });
    }, 1200);

    try {
        const res = await fetch(`${httpBase}/api/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });

        clearTimeout(branchTimer);
        clearTimeout(synthTimer);

        if (!res.ok) {
            const errData = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
            throw new Error(errData.detail || `Server returned ${res.status}`);
        }

        const data = await res.json();
        const fullData = data.full_data || {};

        // Update each node in the tree with its real results
        const nodes = fullData.tree_data?.nodes || {};
        for (const [nid, node] of Object.entries(nodes)) {
            updateNodeVisual(nid, node.status, node.details);
        }

        liveStatusBar.classList.add("hidden");
        btnAnalyze.disabled = false;
        currentAuditId = data.audit_id;
        currentAuditData = fullData;
        renderAuditReport(fullData);
        refreshHistory();
    } catch (err) {
        clearTimeout(branchTimer);
        clearTimeout(synthTimer);
        liveStatusText.textContent = `Audit Failed: ${err.message}`;
        liveStatusSub.textContent = `Ensure the backend server is running at ${httpBase}. Click to retry.`;
        btnAnalyze.disabled = false;
        console.error("HTTP audit failed:", err);
    }
}

// Render Complete Audit Report
function renderAuditReport(data) {
    const summary = data.summary || {};
    const crawl = data.crawl_data || {};
    const tree = data.tree_data?.nodes || {};

    const crashNode = tree.synthesis_crash_pinpointer?.details || {};
    const autofixNode = tree.synthesis_autofix?.details || {};

    // 1. Metrics Strip
    const score = summary.overall_health_score ?? 100;
    metricHealthScore.textContent = `${score}/100`;
    metricCriticalCount.textContent = summary.critical_issues_count ?? 0;
    metricWarningCount.textContent = summary.warning_issues_count ?? 0;
    metricLatency.textContent = `${crawl.latency_ms || 0} ms`;

    if (score >= 80) {
        metricHealthIcon.className = "w-12 h-12 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-xl";
        metricHealthIcon.innerHTML = `<i class="fa-solid fa-heart-pulse"></i>`;
    } else if (score >= 50) {
        metricHealthIcon.className = "w-12 h-12 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center text-xl";
        metricHealthIcon.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i>`;
    } else {
        metricHealthIcon.className = "w-12 h-12 rounded-lg bg-rose-500/10 text-rose-400 flex items-center justify-center text-xl";
        metricHealthIcon.innerHTML = `<i class="fa-solid fa-skull-crossbones"></i>`;
    }

    // 2. CRASH POINT SPOTLIGHT BANNER
    renderCrashSpotlight(summary.site_crashes, crashNode);

    // 3. Auto-Fix Card
    renderAutoFixCard(autofixNode);

    // 4. Update Tabs
    renderTabsContent(crawl);
}

function renderCrashSpotlight(siteCrashes, crashNode) {
    const bannerClass = siteCrashes ? "crash-banner-critical" : (crashNode.has_warnings ? "crash-banner-warning" : "crash-banner-healthy");
    const badgeText = siteCrashes ? "🚨 POINT OF FAILURE: EXACT POINT WHERE SITE STOPS WORKING" : (crashNode.has_warnings ? "⚠️ WARNING: NON-FATAL GLITCHES DETECTED" : "✅ SITE HEALTHY: NO CRITICAL CRASHES DETECTED");
    const badgeColor = siteCrashes ? "bg-rose-500/20 text-rose-300 border-rose-500/40" : (crashNode.has_warnings ? "bg-amber-500/20 text-amber-300 border-amber-500/40" : "bg-emerald-500/20 text-emerald-300 border-emerald-500/40");

    let timelineHtml = "";
    if (crashNode.execution_timeline && crashNode.execution_timeline.length) {
        timelineHtml = `
            <div class="mt-4 space-y-2">
                <h5 class="text-xs font-mono uppercase text-slate-400 tracking-wider">Execution Failure Timeline:</h5>
                <div class="space-y-1.5">
                    ${crashNode.execution_timeline.map(step => {
                        const isCrash = step.includes("[CRASH]") || step.includes("error") || step.includes("hazard");
                        return `
                            <div class="flex items-start gap-2 text-xs">
                                <span class="mt-0.5 ${isCrash ? 'text-rose-400' : 'text-slate-400'}"><i class="${isCrash ? 'fa-solid fa-circle-xmark' : 'fa-solid fa-circle-check'}"></i></span>
                                <span class="${isCrash ? 'text-rose-200 font-semibold' : 'text-slate-300'}">${escapeHtml(step)}</span>
                            </div>
                        `;
                    }).join("")}
                </div>
            </div>
        `;
    }

    crashSpotlightCard.className = `rounded-2xl border p-6 shadow-xl transition ${bannerClass}`;
    crashSpotlightCard.innerHTML = `
        <div class="flex flex-wrap items-center justify-between gap-2">
            <span class="text-xs font-mono uppercase px-3 py-1 rounded-full border ${badgeColor} font-bold flex items-center gap-1.5">
                ${badgeText}
            </span>
            <span class="text-xs text-slate-400">Model: ${crashNode.name || 'Crash Pinpointer Model'}</span>
        </div>
        <div class="mt-3">
            <h3 class="text-lg font-bold text-white">${escapeHtml(crashNode.point_of_failure || 'Analysis completed.')}</h3>
            ${crashNode.root_cause ? `<p class="text-xs text-slate-300 mt-1"><span class="font-semibold text-rose-400">Root Cause:</span> ${escapeHtml(crashNode.root_cause)}</p>` : ''}
        </div>
        ${timelineHtml}
    `;
}

function renderAutoFixCard(fix) {
    if (!fix) return;

    let stepsHtml = "";
    if (fix.remedy_steps && fix.remedy_steps.length) {
        stepsHtml = fix.remedy_steps.map((s, idx) => `
            <li class="flex items-start gap-2">
                <span class="w-4 h-4 rounded-full bg-indigo-500/20 text-indigo-300 text-[10px] flex items-center justify-center font-mono mt-0.5">${idx + 1}</span>
                <span>${escapeHtml(s)}</span>
            </li>
        `).join("");
    }

    autofixCard.innerHTML = `
        <div class="flex flex-wrap items-center justify-between gap-2 border-b border-darkborder pb-4">
            <div>
                <h4 class="text-base font-bold text-white flex items-center gap-2">
                    <i class="fa-solid fa-wand-magic-sparkles text-indigo-400"></i> ${escapeHtml(fix.patch_title || 'Recommended Auto-Fix')}
                </h4>
                <p class="text-xs text-slate-400">Actionable code patch and step-by-step remedy to prevent site crashes.</p>
            </div>
            <button onclick="copyCodeDiff()" class="text-xs px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 transition flex items-center gap-1.5">
                <i class="fa-solid fa-copy"></i> Copy Code Fix
            </button>
        </div>

        <div class="relative rounded-xl overflow-hidden bg-slate-950 border border-slate-800 p-4 font-mono text-xs text-slate-200">
            <pre id="code-diff-content" class="overflow-x-auto whitespace-pre">${escapeHtml(fix.code_diff || '// No code modification required')}</pre>
        </div>

        ${stepsHtml ? `
            <div class="space-y-2 text-xs text-slate-300">
                <h5 class="font-bold text-white">Remediation Action Plan:</h5>
                <ul class="space-y-1.5">${stepsHtml}</ul>
            </div>
        ` : ''}

        ${fix.prevention_tip ? `
            <div class="rounded-lg bg-indigo-950/40 border border-indigo-800/40 p-3 text-xs text-indigo-200 flex items-start gap-2.5">
                <i class="fa-solid fa-lightbulb text-amber-400 mt-0.5"></i>
                <div>
                    <span class="font-bold text-white">Pro Prevention Tip:</span> ${escapeHtml(fix.prevention_tip)}
                </div>
            </div>
        ` : ''}
    `;
}

function copyCodeDiff() {
    const el = document.getElementById("code-diff-content");
    if (el) {
        navigator.clipboard.writeText(el.innerText).then(() => {
            alert("Code fix copied to clipboard!");
        });
    }
}

// Render Tabs Content
function renderTabsContent(crawl) {
    const hazards = crawl.runtime_hazards || [];
    const brokenAssets = crawl.broken_assets || [];
    const apis = crawl.api_endpoints || [];
    const forms = crawl.forms || [];

    document.getElementById("count-hazards").textContent = hazards.length;
    document.getElementById("count-assets").textContent = brokenAssets.length;
    document.getElementById("count-api").textContent = apis.length;
    document.getElementById("count-forms").textContent = forms.length;

    // Hazards
    const hazardsList = document.getElementById("hazards-list");
    if (hazards.length === 0) {
        hazardsList.innerHTML = `<p class="text-xs text-emerald-400 py-3">✅ No JavaScript null-dereferences, missing globals, or runtime crash traps detected!</p>`;
    } else {
        hazardsList.innerHTML = hazards.map(h => `
            <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
                <div class="flex items-center justify-between">
                    <span class="text-xs font-mono font-bold ${h.severity === 'Critical' ? 'text-rose-400' : 'text-amber-400'} flex items-center gap-1.5">
                        <i class="fa-solid fa-circle-exclamation"></i> ${escapeHtml(h.type)}
                    </span>
                    <span class="text-[10px] px-2 py-0.5 rounded font-mono ${h.severity === 'Critical' ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'}">${h.severity}</span>
                </div>
                <p class="text-xs text-slate-300">${escapeHtml(h.description)}</p>
                ${h.code_snippet ? `<pre class="bg-black/50 p-2 rounded text-[11px] font-mono text-rose-300 overflow-x-auto">${escapeHtml(h.code_snippet)}</pre>` : ''}
                <p class="text-[11px] text-slate-400"><span class="text-indigo-400 font-semibold">Trigger:</span> ${escapeHtml(h.trigger || 'On load')}</p>
                <p class="text-[11px] text-emerald-400"><span class="font-semibold">Suggested Fix:</span> ${escapeHtml(h.fix_suggestion || 'Add check')}</p>
            </div>
        `).join("");
    }

    // Broken Assets
    const assetsList = document.getElementById("assets-list");
    if (brokenAssets.length === 0) {
        assetsList.innerHTML = `<p class="text-xs text-emerald-400 py-3">✅ All referenced scripts, styles, and links responded without 404/500 errors.</p>`;
    } else {
        assetsList.innerHTML = brokenAssets.map(a => `
            <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                <div class="space-y-0.5 max-w-[80%]">
                    <div class="font-mono text-white truncate">${escapeHtml(a.url)}</div>
                    <div class="text-slate-400 text-[11px]">${escapeHtml(a.error)}</div>
                </div>
                <div class="text-right">
                    <span class="px-2 py-0.5 rounded font-mono text-[10px] ${a.severity === 'Critical' ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'}">${a.kind.toUpperCase()} • ${a.status || 'ERR'}</span>
                </div>
            </div>
        `).join("");
    }

    // API Routes
    const apiList = document.getElementById("api-list");
    if (apis.length === 0) {
        apiList.innerHTML = `<p class="text-xs text-slate-400 py-3">No client-side fetch/axios calls discovered in scripts.</p>`;
    } else {
        apiList.innerHTML = apis.map(ep => `
            <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                <div>
                    <div class="font-mono text-indigo-300">${escapeHtml(ep.raw_path)}</div>
                    <div class="text-[11px] text-slate-400 truncate">Called from: ${escapeHtml(ep.source)}</div>
                </div>
                <span class="px-2 py-0.5 rounded font-mono text-[10px] ${ep.status >= 400 ? 'bg-rose-500/20 text-rose-300' : (ep.status ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-400')}">
                    HTTP ${ep.status || 'UNTESTED'}
                </span>
            </div>
        `).join("");
    }

    // Forms
    const formsList = document.getElementById("forms-list");
    if (forms.length === 0) {
        formsList.innerHTML = `<p class="text-xs text-slate-400 py-3">No HTML forms found on page.</p>`;
    } else {
        formsList.innerHTML = forms.map((f, idx) => `
            <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1 text-xs">
                <div class="flex items-center justify-between">
                    <span class="font-bold text-white">Form #${idx + 1} (${f.method} ${f.action || '(Self)'})</span>
                    <span class="px-2 py-0.5 rounded font-mono text-[10px] ${f.has_submit ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'}">
                        ${f.has_submit ? 'HAS SUBMIT BTN' : 'NO SUBMIT BTN'}
                    </span>
                </div>
                ${f.issue ? `<p class="text-amber-400 text-[11px]">${escapeHtml(f.issue)}</p>` : `<p class="text-emerald-400 text-[11px]">Form structure valid with ${f.inputs_count} inputs.</p>`}
            </div>
        `).join("");
    }
}

// Open Node Modal
function openNodeModal(nodeId) {
    const node = currentNodesState[nodeId];
    if (!node) return;

    modalNodeTitle.textContent = node.title;
    modalNodeStatus.textContent = node.status || "IDLE";
    modalNodeIcon.className = `w-10 h-10 rounded-xl flex items-center justify-center text-lg ${node.status === 'critical' ? 'bg-rose-500/20 text-rose-400' : (node.status === 'warning' ? 'bg-amber-500/20 text-amber-400' : 'bg-indigo-500/20 text-indigo-400')}`;
    modalNodeIcon.innerHTML = `<i class="${node.icon}"></i>`;

    const details = node.details || {};
    let contentHtml = `
        <div>
            <span class="font-bold text-white">Model Diagnosis:</span>
            <p class="text-slate-300 mt-1">${escapeHtml(details.diagnosis || details.overview || details.point_of_failure || 'Diagnostic checks in progress...')}</p>
        </div>
    `;

    if (details.issues && details.issues.length) {
        contentHtml += `
            <div class="mt-3">
                <span class="font-bold text-rose-400">Issues Flagged:</span>
                <ul class="list-disc pl-4 space-y-1 mt-1 text-slate-300">
                    ${details.issues.map(iss => `<li>${escapeHtml(iss)}</li>`).join("")}
                </ul>
            </div>
        `;
    }

    if (details.crash_points && details.crash_points.length) {
        contentHtml += `
            <div class="mt-3">
                <span class="font-bold text-rose-400">Crash Points:</span>
                <div class="space-y-2 mt-1">
                    ${details.crash_points.map(cp => `
                        <div class="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                            <div class="font-bold text-rose-300">${escapeHtml(cp.type)}</div>
                            <div class="text-slate-400">${escapeHtml(cp.description)}</div>
                            <div class="text-emerald-400 mt-1">Fix: ${escapeHtml(cp.fix)}</div>
                        </div>
                    `).join("")}
                </div>
            </div>
        `;
    }

    modalNodeContent.innerHTML = contentHtml;
    nodeModal.classList.remove("hidden");
}

btnCloseNodeModal.addEventListener("click", () => nodeModal.classList.add("hidden"));
nodeModal.addEventListener("click", (e) => {
    if (e.target === nodeModal) nodeModal.classList.add("hidden");
});

// Tabs logic
function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => {
                b.classList.remove("border-indigo-500", "text-white");
                b.classList.add("border-transparent", "text-slate-400");
            });
            btn.classList.add("border-indigo-500", "text-white");
            btn.classList.remove("border-transparent", "text-slate-400");

            document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.add("hidden"));
            const target = btn.getAttribute("data-tab");
            const targetPane = document.getElementById(target);
            if (targetPane) targetPane.classList.remove("hidden");
        });
    });
}

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
            <div onclick="loadPastAudit('${item.id}')" class="p-3 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 cursor-pointer transition space-y-1">
                <div class="flex items-center justify-between text-xs">
                    <span class="font-bold text-white truncate max-w-[200px]">${escapeHtml(item.target_url)}</span>
                    <span class="font-mono text-[10px] px-1.5 py-0.5 rounded ${item.site_crashes ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'}">
                        ${item.health_score}/100
                    </span>
                </div>
                <p class="text-[11px] text-slate-400 truncate">${escapeHtml(item.crash_point || 'Clean run')}</p>
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

        // Populate tree visuals from stored nodes
        renderInitialTreeSkeleton();
        const nodes = data.tree_data?.nodes || {};
        for (const [nid, node] of Object.entries(nodes)) {
            updateNodeVisual(nid, node.status, node.details);
        }

        renderAuditReport(data);
    } catch (err) {
        alert("Failed to load audit record.");
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
