/**
 * SiteTree Debugger - Formal Professional Edition
 * 50 Specialized AI Worker Parameters with Simple Plain-English Explanations.
 */

// State
let currentAuditId = null;
let currentAuditData = null;
let currentWorkersList = [];
let activeDivisionFilter = "all";

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

// 50 AI Workers Static Registry for initial skeleton
const WORKERS_REGISTRY = [
    // Division 1: Network & Hosting (1-10)
    { id: "w01_http_status", title: "1. Website Server Response", division: "Network & Hosting", icon: "fa-solid fa-server" },
    { id: "w02_ssl_cert", title: "2. Security & HTTPS Lock", division: "Network & Hosting", icon: "fa-solid fa-lock" },
    { id: "w03_speed_latency", title: "3. Loading Speed & Delay", division: "Network & Hosting", icon: "fa-solid fa-gauge-high" },
    { id: "w04_redirect_loops", title: "4. Page Redirects", division: "Network & Hosting", icon: "fa-solid fa-arrow-turn-down" },
    { id: "w05_mixed_content", title: "5. Insecure Mixed Content", division: "Network & Hosting", icon: "fa-solid fa-triangle-exclamation" },
    { id: "w06_dns_connectivity", title: "6. Domain Connection", division: "Network & Hosting", icon: "fa-solid fa-globe" },
    { id: "w07_cors_policy", title: "7. Browser Sharing (CORS)", division: "Network & Hosting", icon: "fa-solid fa-share-nodes" },
    { id: "w08_compression", title: "8. File Compression (Gzip)", division: "Network & Hosting", icon: "fa-solid fa-file-zipper" },
    { id: "w09_cache_headers", title: "9. Browser Cache Settings", division: "Network & Hosting", icon: "fa-solid fa-clock" },
    { id: "w10_server_error_pages", title: "10. Clean Error Pages", division: "Network & Hosting", icon: "fa-solid fa-shield" },

    // Division 2: Assets & Files (11-20)
    { id: "w11_script_bundle_404", title: "11. JavaScript File Loading", division: "Assets & Files", icon: "fa-brands fa-js" },
    { id: "w12_css_stylesheet_404", title: "12. Stylesheet (CSS) Loading", division: "Assets & Files", icon: "fa-solid fa-palette" },
    { id: "w13_broken_images", title: "13. Image & Photo Availability", division: "Assets & Files", icon: "fa-solid fa-image" },
    { id: "w14_external_cdns", title: "14. Third-Party CDNs", division: "Assets & Files", icon: "fa-solid fa-cloud-arrow-down" },
    { id: "w15_font_loading", title: "15. Web Fonts & Typography", division: "Assets & Files", icon: "fa-solid fa-font" },
    { id: "w16_favicon", title: "16. Tab Icon (Favicon)", division: "Assets & Files", icon: "fa-solid fa-star" },
    { id: "w17_page_size", title: "17. Total HTML Page Weight", division: "Assets & Files", icon: "fa-solid fa-weight-scale" },
    { id: "w18_script_defer", title: "18. Non-Blocking Scripts", division: "Assets & Files", icon: "fa-solid fa-bolt" },
    { id: "w19_svg_icons", title: "19. Vector Icons & Graphics", division: "Assets & Files", icon: "fa-solid fa-shapes" },
    { id: "w20_iframe_embeds", title: "20. Embedded Frames & Widgets", division: "Assets & Files", icon: "fa-solid fa-window-restore" },

    // Division 3: JavaScript & Crashes (21-30)
    { id: "w21_null_deref", title: "21. Missing Button Click Crash", division: "JavaScript & Crashes", icon: "fa-solid fa-arrow-pointer" },
    { id: "w22_missing_library", title: "22. Missing Library Crash", division: "JavaScript & Crashes", icon: "fa-solid fa-box-open" },
    { id: "w23_unhandled_promise", title: "23. Frozen UI on Network Glitch", division: "JavaScript & Crashes", icon: "fa-solid fa-snowflake" },
    { id: "w24_storage_parse", title: "24. Local Storage Saved Data Crash", division: "JavaScript & Crashes", icon: "fa-solid fa-database" },
    { id: "w25_missing_inline_func", title: "25. Button Calls Missing Function", division: "JavaScript & Crashes", icon: "fa-solid fa-hand-pointer" },
    { id: "w26_dom_ready_timing", title: "26. Script Execution Timing", division: "JavaScript & Crashes", icon: "fa-solid fa-hourglass-start" },
    { id: "w27_infinite_loops", title: "27. Infinite Loop Protection", division: "JavaScript & Crashes", icon: "fa-solid fa-repeat" },
    { id: "w28_variable_scope", title: "28. Global Variable Scope", division: "JavaScript & Crashes", icon: "fa-solid fa-code" },
    { id: "w29_event_listener_cleanup", title: "29. Memory & Event Handlers", division: "JavaScript & Crashes", icon: "fa-solid fa-microchip" },
    { id: "w30_json_validity", title: "30. Client JSON Data Integrity", division: "JavaScript & Crashes", icon: "fa-solid fa-file-code" },

    // Division 4: APIs & Forms (31-40)
    { id: "w31_broken_api_routes", title: "31. Backend API Endpoint Health", division: "APIs & Forms", icon: "fa-solid fa-network-wired" },
    { id: "w32_localhost_leak", title: "32. Accidental 'localhost' Leak", division: "APIs & Forms", icon: "fa-solid fa-laptop-code" },
    { id: "w33_form_action", title: "33. Form Submit Action", division: "APIs & Forms", icon: "fa-solid fa-paper-plane" },
    { id: "w34_missing_submit_btn", title: "34. Form Submit Button Presence", division: "APIs & Forms", icon: "fa-solid fa-square-check" },
    { id: "w35_api_timeout_hang", title: "35. API Response Speed", division: "APIs & Forms", icon: "fa-solid fa-stopwatch" },
    { id: "w36_input_types", title: "36. Input Fields Setup", division: "APIs & Forms", icon: "fa-solid fa-keyboard" },
    { id: "w37_cors_api_block", title: "37. API Cross-Origin Permissions", division: "APIs & Forms", icon: "fa-solid fa-shield-virus" },
    { id: "w38_api_content_type", title: "38. Data Request Headers (JSON)", division: "APIs & Forms", icon: "fa-solid fa-brackets-curly" },
    { id: "w39_url_search_params", title: "39. Link Query Parameters", division: "APIs & Forms", icon: "fa-solid fa-magnifying-glass" },
    { id: "w40_session_storage", title: "40. User Login & Session Persistence", division: "APIs & Forms", icon: "fa-solid fa-user-shield" },

    // Division 5: User Experience & Security (41-50)
    { id: "w41_mobile_viewport", title: "41. Mobile Phone Compatibility Tag", division: "User Experience & Security", icon: "fa-solid fa-mobile-screen" },
    { id: "w42_dead_internal_links", title: "42. Broken Links (404 Not Found)", division: "User Experience & Security", icon: "fa-solid fa-link-slash" },
    { id: "w43_page_title_seo", title: "43. Website Title in Browser Tab", division: "User Experience & Security", icon: "fa-solid fa-window-maximize" },
    { id: "w44_charset", title: "44. Text Characters & Language (UTF-8)", division: "User Experience & Security", icon: "fa-solid fa-language" },
    { id: "w45_security_headers", title: "45. Security Shield Headers (X-Frame)", division: "User Experience & Security", icon: "fa-solid fa-shield-halved" },
    { id: "w46_content_type_options", title: "46. File Type Sniffing Protection", division: "User Experience & Security", icon: "fa-solid fa-file-shield" },
    { id: "w47_external_link_safety", title: "47. External Link Security", division: "User Experience & Security", icon: "fa-solid fa-arrow-up-right-from-square" },
    { id: "w48_readable_text", title: "48. Page Content & Text Structure", division: "User Experience & Security", icon: "fa-solid fa-align-left" },
    { id: "w49_responsive_layout", title: "49. Responsive Page Layout", division: "User Experience & Security", icon: "fa-solid fa-table-columns" },
    { id: "w50_overall_crash_synthesis", title: "50. Master Crash & Failure Synthesis", division: "User Experience & Security", icon: "fa-solid fa-circle-nodes" }
];

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    initDivisionFilters();
    initSettings();
    initHistory();
    renderInitialWorkersSkeleton();
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

function initDivisionFilters() {
    const filterBtns = document.querySelectorAll(".div-filter-btn");
    filterBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            filterBtns.forEach(b => {
                b.className = "div-filter-btn px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200 hover:bg-slate-200 cursor-pointer";
            });
            btn.className = "div-filter-btn px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-50 text-blue-800 border border-blue-200 cursor-pointer";
            activeDivisionFilter = btn.getAttribute("data-filter");
            applyDivisionFilter();
        });
    });
}

function applyDivisionFilter() {
    const cards = document.querySelectorAll(".ai-worker-card");
    cards.forEach(c => {
        const div = c.getAttribute("data-division");
        if (activeDivisionFilter === "all" || div === activeDivisionFilter) {
            c.classList.remove("hidden");
        } else {
            c.classList.add("hidden");
        }
    });
}

function renderInitialWorkersSkeleton() {
    aiWorkersGrid.innerHTML = "";
    currentWorkersList = [];

    WORKERS_REGISTRY.forEach(w => {
        const card = document.createElement("div");
        card.id = `worker-${w.id}`;
        card.setAttribute("data-division", w.division);
        card.className = "ai-worker-card rounded-lg p-3.5 flex flex-col justify-between text-left transition shadow-xs";
        card.onclick = () => openWorkerModal(w.id);

        card.innerHTML = `
            <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                    <span class="w-7 h-7 rounded-md bg-slate-100 text-slate-600 flex items-center justify-center text-xs worker-icon">
                        <i class="${w.icon}"></i>
                    </span>
                    <span class="text-[11px] font-medium text-slate-500">${w.division}</span>
                </div>
                <span class="worker-badge text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium">READY</span>
            </div>
            <div>
                <h5 class="font-bold text-xs text-slate-900 truncate">${w.title}</h5>
                <p class="worker-msg text-xs text-slate-600 mt-1 line-clamp-2">Waiting to inspect site...</p>
            </div>
            <div class="worker-action text-[11px] text-blue-700 font-medium mt-2 flex items-center gap-1">
                <span>View Details</span> <i class="fa-solid fa-angle-right text-[9px]"></i>
            </div>
        `;

        aiWorkersGrid.appendChild(card);
        currentWorkersList.push({
            id: w.id,
            title: w.title,
            division: w.division,
            icon: w.icon,
            status: "ready",
            details: { simple_message: "Waiting for scan...", fix_advice: "No action needed." }
        });
    });
}

function updateWorkerCard(nodeId, status, details = {}) {
    const card = document.getElementById(`worker-${nodeId}`);
    if (!card) return;

    const badge = card.querySelector(".worker-badge");
    const msg = card.querySelector(".worker-msg");
    const icon = card.querySelector(".worker-icon");

    // Reset styles
    card.classList.remove("border-rose-300", "border-amber-300", "border-emerald-300", "bg-rose-50/40", "bg-amber-50/40");

    const wItem = currentWorkersList.find(x => x.id === nodeId);
    if (wItem) {
        wItem.status = status;
        wItem.details = details;
    }

    if (status === "critical") {
        card.classList.add("border-rose-300", "bg-rose-50/30");
        badge.className = "worker-badge text-[10px] px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 font-bold";
        badge.textContent = "CRITICAL FAIL";
        icon.className = "w-7 h-7 rounded-md bg-rose-100 text-rose-700 flex items-center justify-center text-xs worker-icon";
        msg.textContent = details.simple_message || "Critical failure found.";
        msg.className = "worker-msg text-xs text-rose-900 font-medium mt-1 line-clamp-2";
    } else if (status === "warning") {
        card.classList.add("border-amber-300", "bg-amber-50/30");
        badge.className = "worker-badge text-[10px] px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 font-bold";
        badge.textContent = "WARNING";
        icon.className = "w-7 h-7 rounded-md bg-amber-100 text-amber-700 flex items-center justify-center text-xs worker-icon";
        msg.textContent = details.simple_message || "Warning found.";
        msg.className = "worker-msg text-xs text-amber-900 font-medium mt-1 line-clamp-2";
    } else {
        badge.className = "worker-badge text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold";
        badge.textContent = "PASSED";
        icon.className = "w-7 h-7 rounded-md bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs worker-icon";
        msg.textContent = details.simple_message || "Passed inspection.";
        msg.className = "worker-msg text-xs text-slate-700 mt-1 line-clamp-2";
    }
}

// Start Audit (Dual-Transport: WebSocket with seamless HTTP REST Fallback)
function startAudit(url) {
    btnAnalyze.disabled = true;
    liveStatusBar.classList.remove("hidden");
    resultsWrapper.classList.remove("hidden");
    liveStatusText.textContent = `Running 50 AI worker parameters on: ${url}`;
    liveStatusSub.textContent = "Checking network, assets, code crashes, APIs, and mobile readiness...";

    renderInitialWorkersSkeleton();

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
            console.warn("WebSocket timeout. Seamlessly falling back to HTTP REST audit.");
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
                    liveStatusText.textContent = "Inspecting website code & resources...";
                    liveStatusSub.textContent = msg.message;
                } else if (msg.type === "crawl_completed") {
                    liveStatusText.textContent = "Evaluating 50 specialized AI parameters...";
                    liveStatusSub.textContent = "Testing for buttons, scripts, links, and crash traps...";
                } else if (msg.type === "node_update") {
                    const node = msg.node;
                    updateWorkerCard(node.node_id, node.status, node.details);
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
    liveStatusSub.textContent = "Running 50 AI worker parameters via REST engine...";

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

        // Update each worker card
        const nodes = fullData.tree_data?.nodes || {};
        for (const [nid, node] of Object.entries(nodes)) {
            updateWorkerCard(nid, node.status, node.details);
        }

        liveStatusBar.classList.add("hidden");
        btnAnalyze.disabled = false;
        currentAuditId = data.audit_id;
        currentAuditData = fullData;
        renderAuditReport(fullData);
        refreshHistory();
    } catch (err) {
        liveStatusText.textContent = `Audit notice: ${err.message}`;
        liveStatusSub.textContent = `Make sure the server is running at ${httpBase}.`;
        btnAnalyze.disabled = false;
    }
}

// Render Complete Audit Report with Simple Plain-English
function renderAuditReport(data) {
    const summary = data.summary || {};
    const tree = data.tree_data?.nodes || {};
    const crashNode = tree.synthesis_crash_pinpointer?.details || {};
    const autofixNode = tree.synthesis_autofix?.details || {};

    // 1. Health Score Cards
    const score = summary.overall_health_score ?? 100;
    metricHealthScore.textContent = `${score}/100`;
    metricCriticalCount.textContent = summary.critical_issues_count ?? 0;
    metricWarningCount.textContent = summary.warning_issues_count ?? 0;
    metricPassedCount.textContent = `${summary.healthy_checks_count ?? 50}/50`;

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

    // 2. CRASH POINT SPOTLIGHT BANNER (SIMPLE PLAIN ENGLISH)
    renderSimpleCrashSpotlight(summary.site_crashes, crashNode);

    // 3. Simple Fix Card
    renderSimpleAutoFix(autofixNode);

    applyDivisionFilter();
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
            <span class="text-xs text-slate-500">50 AI Workers Evaluated</span>
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
            <pre id="code-diff-content" class="overflow-x-auto whitespace-pre">${escapeHtml(fix.code_diff || '// All tests passed. No code change needed.')}</pre>
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
function openWorkerModal(workerId) {
    const w = currentWorkersList.find(x => x.id === workerId);
    if (!w) return;

    modalNodeTitle.textContent = w.title;
    modalNodeStatus.textContent = w.status.toUpperCase();
    modalNodeIcon.className = `w-10 h-10 rounded-lg flex items-center justify-center text-lg ${w.status === 'critical' ? 'bg-rose-50 text-rose-600' : (w.status === 'warning' ? 'bg-amber-50 text-amber-600' : 'bg-emerald-50 text-emerald-600')}`;
    modalNodeIcon.innerHTML = `<i class="${w.icon}"></i>`;

    const details = w.details || {};
    modalNodeContent.innerHTML = `
        <div class="space-y-3">
            <div>
                <span class="text-xs font-bold text-slate-900">What this AI worker checked:</span>
                <p class="text-xs text-slate-700 mt-0.5">${escapeHtml(details.simple_message || 'Inspected site parameters.')}</p>
            </div>
            ${details.fix_advice ? `
                <div class="p-3 rounded-lg bg-slate-50 border border-slate-200">
                    <span class="text-xs font-bold text-blue-800">How to Fix This:</span>
                    <p class="text-xs text-slate-700 mt-0.5">${escapeHtml(details.fix_advice)}</p>
                </div>
            ` : ''}
            <div class="text-[11px] text-slate-500">
                Division: <span class="font-medium text-slate-700">${w.division}</span>
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
                <p class="text-[11px] text-slate-500 truncate">${escapeHtml(item.crash_point || 'Passed all checks')}</p>
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

        renderInitialWorkersSkeleton();
        const nodes = data.tree_data?.nodes || {};
        for (const [nid, node] of Object.entries(nodes)) {
            updateWorkerCard(nid, node.status, node.details);
        }

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
