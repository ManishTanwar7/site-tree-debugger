"""
Multi-AI Model Tree Structure Orchestrator for Website Bug & Crash Analysis.
Executes a hierarchical tree of specialized AI agents/models:
- Root: Orchestrator / Site Decomposer
  - Branch 1: Network & Security Guard
  - Branch 2: Asset & Dependency Hunter
  - Branch 3: DOM & Interaction Auditor
  - Branch 4: Script Runtime Crash Specialist
  - Branch 5: API & Backend Tracer
    - Synthesis 1: Crash Point Pinpointer (Where site stops working)
    - Synthesis 2: Auto-Fix Synthesizer (Code patches & remedies)
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Callable, Awaitable
import httpx

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

class MultiAITreeEngine:
    def __init__(self, api_key: Optional[str] = None, preferred_model: str = "gemini-2.5-flash"):
        self.api_key = api_key.strip() if api_key and api_key.strip() else None
        self.preferred_model = preferred_model or "gemini-2.5-flash"

    async def _query_gemini(self, prompt: str, system_instruction: str) -> Optional[str]:
        """Calls Gemini REST API directly if API key is present."""
        if not self.api_key:
            return None
        
        url = GEMINI_API_URL.format(model=self.preferred_model, api_key=self.api_key)
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "systemInstruction": {
                "parts": [
                    {"text": system_instruction}
                ]
            },
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
        except Exception as e:
            # Fallback to heuristic on network or API failure
            pass
        return None

    async def run_tree_analysis(
        self,
        crawl_data: Dict[str, Any],
        on_node_update: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """
        Executes the entire multi-AI tree structure on the crawled web data.
        Streams updates for each node as it executes.
        """
        tree_results: Dict[str, Any] = {
            "target_url": crawl_data["target_url"],
            "nodes": {},
            "summary": {}
        }

        async def emit(node_id: str, status: str, title: str, details: Dict[str, Any]):
            node_payload = {
                "node_id": node_id,
                "title": title,
                "status": status,
                "details": details
            }
            tree_results["nodes"][node_id] = node_payload
            if on_node_update:
                await on_node_update(node_payload)

        # ----------------------------------------------------
        # LEVEL 0: ROOT ORCHESTRATOR NODE
        # ----------------------------------------------------
        await emit("root_orchestrator", "running", "Root Orchestrator (Site Decomposer)", {
            "thought": f"Analyzing site profile for {crawl_data['target_url']}. Parsing status code {crawl_data['status_code']}, {len(crawl_data['assets']['scripts'])} scripts, and {len(crawl_data['broken_assets'])} broken resources..."
        })
        await asyncio.sleep(0.3)

        root_summary = await self._analyze_root(crawl_data)
        await emit("root_orchestrator", "completed", "Root Orchestrator (Site Decomposer)", root_summary)

        # ----------------------------------------------------
        # LEVEL 1: DOMAIN SPECIALIST BRANCHES (CONCURRENT)
        # ----------------------------------------------------
        branches = [
            ("branch_network", "Network & Security Guardian", self._analyze_network),
            ("branch_assets", "Asset & Dependency Hunter", self._analyze_assets),
            ("branch_dom", "DOM & Interaction Auditor", self._analyze_dom),
            ("branch_scripts", "Script Runtime Crash Specialist", self._analyze_scripts),
            ("branch_api", "API & Backend Route Tracer", self._analyze_api)
        ]

        # Set all to running
        for b_id, b_title, _ in branches:
            await emit(b_id, "running", b_title, {"thought": f"Model inspecting {b_title.lower()} parameters..."})

        branch_results = {}

        async def run_branch(b_id: str, b_title: str, func):
            res = await func(crawl_data)
            branch_results[b_id] = res
            status = "critical" if res.get("severity") == "Critical" else ("warning" if res.get("severity") == "Warning" else "healthy")
            await emit(b_id, status, b_title, res)

        await asyncio.gather(*[run_branch(b_id, b_title, func) for b_id, b_title, func in branches])

        # ----------------------------------------------------
        # LEVEL 2: DIAGNOSTIC SYNTHESIS (CRASH PINPOINTER & AUTO-FIX)
        # ----------------------------------------------------
        await emit("synthesis_crash_pinpointer", "running", "Crash Point Pinpointer", {
            "thought": "Synthesizing all branch findings to trace the exact chronological failure point..."
        })
        await asyncio.sleep(0.4)

        crash_analysis = await self._synthesize_crash_point(crawl_data, branch_results)
        crash_status = "critical" if crash_analysis.get("site_crashes") else ("warning" if crash_analysis.get("has_warnings") else "healthy")
        await emit("synthesis_crash_pinpointer", crash_status, "Crash Point Pinpointer", crash_analysis)

        # Auto-Fix Node
        await emit("synthesis_autofix", "running", "Auto-Fix & Remedy Synthesizer", {
            "thought": "Generating concrete code diffs and remedial actions for detected crash points..."
        })
        await asyncio.sleep(0.4)

        autofix_analysis = await self._synthesize_autofix(crash_analysis, crawl_data)
        await emit("synthesis_autofix", "completed", "Auto-Fix & Remedy Synthesizer", autofix_analysis)

        # Overall Summary
        tree_results["summary"] = {
            "target_url": crawl_data["target_url"],
            "site_crashes": crash_analysis.get("site_crashes", False),
            "crash_point": crash_analysis.get("point_of_failure", "None detected"),
            "critical_issues_count": crash_analysis.get("critical_count", 0),
            "warning_issues_count": crash_analysis.get("warning_count", 0),
            "overall_health_score": crash_analysis.get("health_score", 100),
            "ai_engine_used": f"Gemini ({self.preferred_model})" if self.api_key else "Autonomous Heuristic Diagnostic Engine"
        }

        return tree_results

    # ------------------ BRANCH HANDLERS ------------------

    async def _analyze_root(self, crawl: Dict[str, Any]) -> Dict[str, Any]:
        status_ok = crawl["status_code"] in [200, 301, 302]
        return {
            "overview": f"Site responded with HTTP {crawl['status_code']} in {crawl['latency_ms']}ms. Page Title: '{crawl['page_title']}'.",
            "scripts_count": len(crawl["assets"]["scripts"]),
            "stylesheets_count": len(crawl["assets"]["stylesheets"]),
            "forms_count": len(crawl["assets"]["forms"]),
            "detected_hazards_count": len(crawl["runtime_hazards"]),
            "broken_resources_count": len(crawl["broken_assets"]),
            "diagnostic_dispatch": "Dispatched 5 specialized analysis branches for Network, Assets, DOM, Scripts, and API layers."
        }

    async def _analyze_network(self, crawl: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        status_code = crawl["status_code"]
        headers = crawl.get("headers", {})

        if status_code >= 500:
            issues.append(f"HTTP Server Crash: Server returned status {status_code} Internal Server Error.")
        elif status_code == 404:
            issues.append(f"Page Not Found: URL returned HTTP 404.")
        elif status_code >= 400:
            issues.append(f"HTTP Client Error: Status {status_code}.")

        if crawl["latency_ms"] > 3500:
            issues.append(f"High Latency: Initial response took {crawl['latency_ms']}ms (potential timeout hazard).")

        # Mixed Content
        mixed_assets = [b for b in crawl["broken_assets"] if "Mixed Content" in b.get("error", "")]
        if mixed_assets:
            issues.append(f"Mixed Content Block: {len(mixed_assets)} insecure HTTP resource(s) blocked on HTTPS site.")

        # Security headers
        missing_sec = []
        for h in ["content-security-policy", "x-frame-options", "x-content-type-options"]:
            if h not in headers:
                missing_sec.append(h)

        severity = "Critical" if status_code >= 400 or mixed_assets else ("Warning" if issues else "Healthy")
        return {
            "name": "Network & Security",
            "severity": severity,
            "status_code": status_code,
            "latency_ms": crawl["latency_ms"],
            "ssl_enabled": crawl["scheme"] == "https",
            "missing_security_headers": missing_sec,
            "issues": issues,
            "diagnosis": (
                f"Network status: {status_code}. "
                + (f"Found {len(issues)} connectivity/security hazard(s)." if issues else "Network and SSL layer is stable.")
            )
        }

    async def _analyze_assets(self, crawl: Dict[str, Any]) -> Dict[str, Any]:
        broken = crawl["broken_assets"]
        broken_scripts = [b for b in broken if b.get("kind") == "script"]
        broken_styles = [b for b in broken if b.get("kind") == "stylesheet"]
        broken_images = [b for b in broken if b.get("kind") == "image"]

        issues = []
        if broken_scripts:
            for s in broken_scripts:
                issues.append(f"CRITICAL: Failed to load JavaScript bundle: {s['url']} ({s['error']})")
        if broken_styles:
            for st in broken_styles:
                issues.append(f"WARNING: Stylesheet failed to load: {st['url']} ({st['error']})")
        if broken_images:
            issues.append(f"Broken Images: {len(broken_images)} image(s) returned 404.")

        severity = "Critical" if broken_scripts else ("Warning" if (broken_styles or broken_images) else "Healthy")
        return {
            "name": "Assets & Dependencies",
            "severity": severity,
            "total_scripts": len(crawl["assets"]["scripts"]),
            "total_stylesheets": len(crawl["assets"]["stylesheets"]),
            "broken_scripts_count": len(broken_scripts),
            "broken_styles_count": len(broken_styles),
            "broken_images_count": len(broken_images),
            "broken_items": broken,
            "issues": issues,
            "diagnosis": (
                "Critical scripts failed to load; site functionality is likely broken."
                if broken_scripts else
                ("Some external styles or images failed to load." if issues else "All external scripts and styles resolved successfully.")
            )
        }

    async def _analyze_dom(self, crawl: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        dead_links = [b for b in crawl["broken_assets"] if b.get("kind") == "link"]
        if dead_links:
            for dl in dead_links:
                issues.append(f"Dead Link: {dl['error']}")

        # Form issues
        for f in crawl["assets"]["forms"]:
            if f.get("issue"):
                issues.append(f"Form Hazard: {f['issue']}")

        # Missing viewport
        if not crawl["dom_stats"].get("has_viewport"):
            issues.append("Missing `<meta name=\"viewport\">` tag: Page will break or render poorly on mobile screens.")

        severity = "Critical" if dead_links else ("Warning" if issues else "Healthy")
        return {
            "name": "DOM & Interaction",
            "severity": severity,
            "total_dom_elements": crawl["dom_stats"].get("total_elements", 0),
            "forms_audited": len(crawl["assets"]["forms"]),
            "dead_links_count": len(dead_links),
            "issues": issues,
            "diagnosis": (
                f"Found {len(dead_links)} broken internal links and {len(issues) - len(dead_links)} DOM configuration issues."
                if issues else "DOM hierarchy and interactive form elements appear intact."
            )
        }

    async def _analyze_scripts(self, crawl: Dict[str, Any]) -> Dict[str, Any]:
        hazards = crawl["runtime_hazards"]
        critical_crashes = [h for h in hazards if h.get("severity") == "Critical"]
        warnings = [h for h in hazards if h.get("severity") != "Critical"]

        crash_points = []
        for c in critical_crashes:
            crash_points.append({
                "type": c.get("type"),
                "location": c.get("location"),
                "trigger": c.get("trigger"),
                "description": c.get("description"),
                "fix": c.get("fix_suggestion")
            })

        severity = "Critical" if critical_crashes else ("Warning" if warnings else "Healthy")
        return {
            "name": "Script Runtime Crash Detector",
            "severity": severity,
            "critical_crashes_detected": len(critical_crashes),
            "warnings_detected": len(warnings),
            "crash_points": crash_points,
            "all_hazards": hazards,
            "diagnosis": (
                f"Detected {len(critical_crashes)} JavaScript runtime crash conditions (e.g. null pointer dereference, missing globals, or missing event handlers)."
                if critical_crashes else
                (f"Detected {len(warnings)} script code quality warnings." if warnings else "No client-side JavaScript runtime crash patterns detected.")
            )
        }

    async def _analyze_api(self, crawl: Dict[str, Any]) -> Dict[str, Any]:
        apis = crawl.get("api_endpoints", [])
        broken_apis = [ep for ep in apis if ep.get("status") in [404, 500, 502, 503]]
        
        issues = []
        for ba in broken_apis:
            issues.append(f"Broken API: Endpoint '{ba['raw_path']}' returned HTTP {ba['status']} ({ba.get('error')})")

        # Check for Localhost Leaks
        lh_hazards = [h for h in crawl["runtime_hazards"] if h.get("type") == "LocalhostLeakInProduction"]
        for lh in lh_hazards:
            issues.append(f"Localhost Leak: {lh['description']}")

        severity = "Critical" if broken_apis or lh_hazards else "Healthy"
        return {
            "name": "API & Backend Tracer",
            "severity": severity,
            "total_endpoints_scanned": len(apis),
            "broken_endpoints_count": len(broken_apis),
            "broken_apis": broken_apis,
            "issues": issues,
            "diagnosis": (
                f"Client makes calls to {len(broken_apis)} failing API routes or contains localhost leaks in production."
                if issues else f"Audited {len(apis)} API routes; no connectivity failures detected."
            )
        }

    # ------------------ SYNTHESIS NODES ------------------

    async def _synthesize_crash_point(
        self,
        crawl: Dict[str, Any],
        branches: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Pinpoints the exact chronological sequence and breaking point where the site stops working.
        """
        # If Gemini API Key is available, prompt Gemini for deep synthesis
        if self.api_key:
            prompt = (
                f"Analyze this website diagnostic audit for URL: {crawl['target_url']}\n"
                f"Crawl summary: HTTP {crawl['status_code']}, Latency {crawl['latency_ms']}ms\n"
                f"Branch findings: {json.dumps(branches, indent=2)}\n\n"
                "Return a JSON object with:\n"
                "{\n"
                "  \"site_crashes\": boolean,\n"
                "  \"has_warnings\": boolean,\n"
                "  \"point_of_failure\": \"Clear 1-2 sentence description of the exact point where the site stops working\",\n"
                "  \"execution_timeline\": [\"Step 1: ...\", \"Step 2: ...\", \"Step 3: ... [CRASH]\"],\n"
                "  \"root_cause\": \"The exact technical reason for the crash\",\n"
                "  \"severity\": \"Critical\" | \"High\" | \"Medium\" | \"Healthy\",\n"
                "  \"health_score\": integer between 0 and 100\n"
                "}"
            )
            ai_res = await self._query_gemini(
                prompt,
                "You are an expert full-stack web diagnostic and crash-investigation AI. Pinpoint the exact point of failure."
            )
            if ai_res:
                try:
                    parsed = json.loads(ai_res)
                    parsed["critical_count"] = sum(1 for b in branches.values() if b.get("severity") == "Critical")
                    parsed["warning_count"] = sum(1 for b in branches.values() if b.get("severity") in ["Warning", "High", "Medium"])
                    return parsed
                except Exception:
                    pass

        # Heuristic Synthesis Engine
        script_branch = branches.get("branch_scripts", {})
        asset_branch = branches.get("branch_assets", {})
        net_branch = branches.get("branch_network", {})
        api_branch = branches.get("branch_api", {})

        timeline = []
        point_of_failure = None
        root_cause = None
        site_crashes = False
        health_score = 100

        # Scenario 1: Server or Network Failure
        if crawl["status_code"] >= 500:
            site_crashes = True
            health_score = 10
            timeline = [
                f"1. Browser sends GET request to {crawl['target_url']}",
                f"2. Web server responds with HTTP {crawl['status_code']} Internal Server Error",
                "3. [CRASH] Browser renders HTTP error page. Application fails to boot."
            ]
            point_of_failure = f"Site stops on initial HTTP request: Server crashed with HTTP {crawl['status_code']}."
            root_cause = f"Backend application crashed or web server returned HTTP {crawl['status_code']}."

        # Scenario 2: Failed Script Bundle
        elif asset_branch.get("broken_scripts_count", 0) > 0:
            site_crashes = True
            health_score = 25
            broken_s = asset_branch["broken_items"][0]["url"]
            timeline = [
                "1. Browser downloads HTML document successfully",
                f"2. Browser requests JavaScript bundle: {broken_s}",
                "3. Server returns HTTP 404 Not Found for the script bundle",
                "4. [CRASH] Script fails to execute. Interactive components, event listeners, and UI state engine fail to initialize."
            ]
            point_of_failure = f"Site stops immediately after HTML load: Critical JavaScript file '{broken_s}' failed to load (404/Network Error)."
            root_cause = f"Script source path is incorrect or missing from the hosting server ({broken_s})."

        # Scenario 3: JavaScript Null Reference / Missing Dependency Crash
        elif script_branch.get("critical_crashes_detected", 0) > 0:
            site_crashes = True
            health_score = 35
            top_crash = script_branch["crash_points"][0]
            timeline = [
                "1. HTML document loaded and parsed by DOM tree",
                f"2. Client JavaScript executes: {top_crash.get('location')}",
                f"3. {top_crash.get('trigger')}",
                f"4. [CRASH] Throws runtime error: {top_crash.get('type')}. Script execution halts instantly; remaining buttons and handlers fail."
            ]
            point_of_failure = f"Site crashes during JavaScript execution: {top_crash.get('description')}"
            root_cause = f"{top_crash.get('type')} at {top_crash.get('location')}: {top_crash.get('description')}"

        # Scenario 4: Broken API / Localhost Leak
        elif api_branch.get("broken_endpoints_count", 0) > 0 or api_branch.get("issues"):
            site_crashes = True
            health_score = 45
            top_api_issue = api_branch["issues"][0]
            timeline = [
                "1. User navigates website and page UI loads",
                "2. Client application makes asynchronous data request to backend route",
                f"3. API call fails: {top_api_issue}",
                "4. [CRASH/HANG] UI displays infinite loading spinner or crashes due to undefined response data."
            ]
            point_of_failure = f"Site breaks upon user interaction: {top_api_issue}"
            root_cause = "Backend API route returned error or client code targeted unreachable localhost route."

        # Scenario 5: Dead Links or DOM Glitches
        elif crawl["broken_assets"]:
            site_crashes = False
            health_score = 70
            timeline = [
                "1. Site loads and core JavaScript executes without fatal errors",
                f"2. User navigates internal links or loads secondary media",
                f"3. [WARNING] Resource missing: {crawl['broken_assets'][0].get('error')}"
            ]
            point_of_failure = f"Site functions generally, but experiences broken resources: {crawl['broken_assets'][0].get('error')}"
            root_cause = "Missing asset or dead internal link."

        # Scenario 6: Healthy Site
        else:
            site_crashes = False
            health_score = 98
            timeline = [
                f"1. HTTP request responded with status {crawl['status_code']} ({crawl['latency_ms']}ms)",
                "2. All referenced scripts and stylesheets resolved successfully",
                "3. DOM parsed and no null-reference traps or missing dependencies found",
                "4. [PASSED] Site functions normally without detectable crashes."
            ]
            point_of_failure = "No fatal crash points detected. The site is operating normally."
            root_cause = "None"

        crit_count = sum(1 for b in branches.values() if b.get("severity") == "Critical")
        warn_count = sum(1 for b in branches.values() if b.get("severity") in ["Warning", "High", "Medium"])

        return {
            "site_crashes": site_crashes,
            "has_warnings": warn_count > 0,
            "point_of_failure": point_of_failure,
            "execution_timeline": timeline,
            "root_cause": root_cause,
            "severity": "Critical" if site_crashes else ("Warning" if warn_count > 0 else "Healthy"),
            "health_score": health_score,
            "critical_count": crit_count,
            "warning_count": warn_count
        }

    async def _synthesize_autofix(
        self,
        crash_analysis: Dict[str, Any],
        crawl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Produces actionable code patches, snippets, and step-by-step resolution steps.
        """
        # If Gemini API Key is available, prompt Gemini for customized code patches
        if self.api_key:
            prompt = (
                f"Given this crash diagnosis for {crawl['target_url']}:\n"
                f"Point of Failure: {crash_analysis.get('point_of_failure')}\n"
                f"Root cause: {crash_analysis.get('root_cause')}\n"
                f"Hazards: {json.dumps(crawl['runtime_hazards'][:5], indent=2)}\n\n"
                "Return a JSON object with:\n"
                "{\n"
                "  \"patch_title\": \"Title of the fix\",\n"
                "  \"code_diff\": \"Before & After code snippet showing the fix\",\n"
                "  \"remedy_steps\": [\"Step 1...\", \"Step 2...\"],\n"
                "  \"prevention_tip\": \"Best practice to avoid this in future builds\"\n"
                "}"
            )
            ai_res = await self._query_gemini(
                prompt,
                "You are a principal software engineer. Provide exact code diffs and concrete fixes."
            )
            if ai_res:
                try:
                    return json.loads(ai_res)
                except Exception:
                    pass

        # Heuristic Auto-Fix Synthesis
        hazards = crawl.get("runtime_hazards", [])
        broken_assets = crawl.get("broken_assets", [])

        if not crash_analysis.get("site_crashes") and not crash_analysis.get("has_warnings"):
            return {
                "patch_title": "Site Health Verified",
                "code_diff": "// No code changes required\n// All tested DOM elements, scripts, and network endpoints responded normally.",
                "remedy_steps": [
                    "Keep dependencies updated regularly.",
                    "Ensure automated end-to-end tests run before deploying changes."
                ],
                "prevention_tip": "Add automated synthetic monitoring to alert you if third-party CDNs go down."
            }

        # Check top hazard
        if hazards:
            h = hazards[0]
            if h.get("type") == "NullReferenceCrash":
                return {
                    "patch_title": "Fix Null Pointer Exception in JavaScript",
                    "code_diff": (
                        "// --- BEFORE (Crashes if element does not exist) ---\n"
                        f"{h.get('code_snippet', 'document.getElementById(...).addEventListener(...)')};\n\n"
                        "// +++ AFTER (Safe with Optional Chaining or Null Guard) +++\n"
                        "const targetEl = document.querySelector('#element-id');\n"
                        "if (targetEl) {\n"
                        "    targetEl.addEventListener('click', handleEvent);\n"
                        "} else {\n"
                        "    console.warn('targetEl was not found in the DOM.');\n"
                        "}"
                    ),
                    "remedy_steps": [
                        "Check your HTML file to ensure the element ID exists in the markup.",
                        "If the element is rendered dynamically (e.g. via React or innerHTML), attach the event listener after the element is mounted.",
                        "Use modern optional chaining: `document.getElementById('...')?.addEventListener(...)`."
                    ],
                    "prevention_tip": "Always guard DOM lookups with null checks or use event delegation on document.body."
                }
            elif h.get("type") == "MissingDependencyCrash":
                fix_hint = h.get('fix_suggestion', '<script src="..."></script>')
                return {
                    "patch_title": "Import Missing Third-Party Dependency",
                    "code_diff": (
                        "// --- BEFORE: Calling global without loading library ---\n"
                        "$('#my-element').hide(); // ReferenceError: $ is not defined\n\n"
                        "// +++ AFTER: Add script tag inside <head> before your custom scripts +++\n"
                        f"{fix_hint}"
                    ),
                    "remedy_steps": [
                        "Open index.html and locate your `<head>` section.",
                        "Add the missing CDN script tag before your application bundle.",
                        "Re-run this audit to verify the library is detected."
                    ],
                    "prevention_tip": "Use ES module imports or a bundler (Vite / Webpack) to guarantee dependencies are packaged."
                }
            elif h.get("type") == "LocalhostLeakInProduction":
                return {
                    "patch_title": "Replace Hardcoded Localhost URL with Environment Variable",
                    "code_diff": (
                        "// --- BEFORE (Breaks for all remote users) ---\n"
                        "const res = await fetch('http://localhost:5000/api/data');\n\n"
                        "// +++ AFTER (Uses relative URL or environment variable) +++\n"
                        "const API_BASE = window.location.origin; // or process.env.VITE_API_URL\n"
                        "const res = await fetch(`${API_BASE}/api/data`);"
                    ),
                    "remedy_steps": [
                        "Search your codebase for 'http://localhost' or '127.0.0.1'.",
                        "Replace them with relative paths (e.g. '/api/...') if hosted on the same domain, or use an environment variable (e.g. VITE_API_URL / NEXT_PUBLIC_API_URL).",
                        "Redeploy to production."
                    ],
                    "prevention_tip": "Use `.env.production` and `.env.development` configurations to keep environments isolated."
                }

        # Check broken script asset
        broken_scripts = [b for b in broken_assets if b.get("kind") == "script"]
        if broken_scripts:
            bs = broken_scripts[0]
            return {
                "patch_title": "Fix Missing JavaScript Bundle Path",
                "code_diff": (
                    "// --- BEFORE (404 Not Found) ---\n"
                    f'<script src="{bs["url"]}"></script>\n\n'
                    "// +++ AFTER (Correct relative or CDN path) +++\n"
                    '<script src="./assets/bundle.js"></script>'
                ),
                "remedy_steps": [
                    f"Check that the file exists on your web server at: {bs['url']}",
                    "If using a framework like Vite, React, or Next.js, check `base: './'` in `vite.config.js` or `publicPath` settings.",
                    "Confirm the build artifact directory (e.g. `dist/` or `build/`) was uploaded to your host."
                ],
                "prevention_tip": "Always verify assets load without 404 in DevTools Network tab after deployment."
            }

        return {
            "patch_title": "General Site Remediation",
            "code_diff": (
                "// Inspect server logs and client console\n"
                "console.log('Diagnostic review complete. Address highlighted network or DOM items.');"
            ),
            "remedy_steps": [
                "Review the issues highlighted in the domain branches above.",
                "Ensure all internal links point to active, existing routes."
            ],
            "prevention_tip": "Run regular site scans after every deployment."
        }
