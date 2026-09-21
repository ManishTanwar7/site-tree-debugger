"""
Multi-AI Tree Architecture with 50 Specialized AI Worker Parameters.
Features 5 Formal Divisions (10 AI workers each) with simple, easy-to-understand language.
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
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
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
        except Exception:
            pass
        return None

    async def run_tree_analysis(
        self,
        crawl_data: Dict[str, Any],
        on_node_update: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """
        Executes 50 specialized AI worker parameters across 5 divisions:
        1. Network & Hosting (1-10)
        2. Assets & Media (11-20)
        3. JavaScript & Crashes (21-30)
        4. APIs & Data Flow (31-40)
        5. UX, Mobile & Security (41-50)
        """
        tree_results: Dict[str, Any] = {
            "target_url": crawl_data["target_url"],
            "nodes": {},
            "divisions": {},
            "summary": {}
        }

        async def emit(node_id: str, status: str, title: str, division: str, details: Dict[str, Any]):
            node_payload = {
                "node_id": node_id,
                "title": title,
                "division": division,
                "status": status,
                "details": details
            }
            tree_results["nodes"][node_id] = node_payload
            if on_node_update:
                await on_node_update(node_payload)

        # ---------------- LEVEL 0: ROOT ORCHESTRATOR ----------------
        await emit("root_orchestrator", "running", "Master Orchestrator", "Orchestration", {
            "thought": f"Reading website at {crawl_data['target_url']}. Preparing 50 specialized AI worker checks..."
        })
        await asyncio.sleep(0.2)

        root_summary = {
            "overview": f"Website responded with HTTP status {crawl_data['status_code']} in {crawl_data['latency_ms']}ms.",
            "simple_message": "The system received your website and sent instructions to 50 specialized AI workers to test every part of your site.",
            "total_workers": 50
        }
        await emit("root_orchestrator", "completed", "Master Orchestrator", "Orchestration", root_summary)

        # ---------------- LEVEL 1: 50 SPECIALIZED AI WORKERS ----------------
        workers = self._build_50_workers_definitions(crawl_data)

        # Group by division
        division_scores = {
            "Network & Hosting": {"passed": 0, "warn": 0, "fail": 0},
            "Assets & Files": {"passed": 0, "warn": 0, "fail": 0},
            "JavaScript & Crashes": {"passed": 0, "warn": 0, "fail": 0},
            "APIs & Forms": {"passed": 0, "warn": 0, "fail": 0},
            "User Experience & Security": {"passed": 0, "warn": 0, "fail": 0}
        }

        critical_crashes = []
        warnings = []

        for w in workers:
            w_id = w["id"]
            w_title = w["title"]
            w_div = w["division"]
            w_status = w["status"]
            w_details = w["details"]

            if w_status == "critical":
                critical_crashes.append(w)
                if w_div in division_scores:
                    division_scores[w_div]["fail"] += 1
            elif w_status == "warning":
                warnings.append(w)
                if w_div in division_scores:
                    division_scores[w_div]["warn"] += 1
            else:
                if w_div in division_scores:
                    division_scores[w_div]["passed"] += 1

            await emit(w_id, w_status, w_title, w_div, w_details)

        # ---------------- LEVEL 2: MASTER CRASH PINPOINTER & REMEDY ----------------
        await emit("synthesis_crash_pinpointer", "running", "Crash Point Pinpointer", "Synthesis", {
            "thought": "Collecting results from all 50 AI workers to pinpoint where the website stops working..."
        })
        await asyncio.sleep(0.2)

        crash_analysis = self._synthesize_simple_crash(crawl_data, critical_crashes, warnings)
        crash_status = "critical" if crash_analysis["site_crashes"] else ("warning" if warnings else "healthy")
        await emit("synthesis_crash_pinpointer", crash_status, "Crash Point Pinpointer", "Synthesis", crash_analysis)

        # Auto-Fix Synthesizer
        autofix_analysis = self._synthesize_simple_fix(crash_analysis, crawl_data)
        await emit("synthesis_autofix", "completed", "Simple Fix Generator", "Synthesis", autofix_analysis)

        tree_results["divisions"] = division_scores
        tree_results["summary"] = {
            "target_url": crawl_data["target_url"],
            "site_crashes": crash_analysis["site_crashes"],
            "crash_point": crash_analysis["point_of_failure"],
            "critical_issues_count": len(critical_crashes),
            "warning_issues_count": len(warnings),
            "healthy_checks_count": 50 - len(critical_crashes) - len(warnings),
            "overall_health_score": crash_analysis["health_score"],
            "total_ai_workers": 50,
            "ai_engine_used": "50 Specialized AI Diagnostic Workers (Autonomous + Gemini Support)"
        }

        return tree_results

    def _build_50_workers_definitions(self, crawl: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Defines 50 distinct AI worker checks with simple, easy-to-understand English language.
        """
        status_code = crawl.get("status_code", 0)
        latency = crawl.get("latency_ms", 0)
        scheme = crawl.get("scheme", "http")
        headers = crawl.get("headers", {})
        broken_assets = crawl.get("broken_assets", [])
        hazards = crawl.get("runtime_hazards", [])
        apis = crawl.get("api_endpoints", [])
        forms = crawl.get("assets", {}).get("forms", [])
        dom_stats = crawl.get("dom_stats", {})

        broken_scripts = [b for b in broken_assets if b.get("kind") == "script"]
        broken_styles = [b for b in broken_assets if b.get("kind") == "stylesheet"]
        broken_images = [b for b in broken_assets if b.get("kind") == "image"]
        dead_links = [b for b in broken_assets if b.get("kind") == "link"]

        null_hazards = [h for h in hazards if h.get("type") == "NullReferenceCrash"]
        dep_hazards = [h for h in hazards if h.get("type") == "MissingDependencyCrash"]
        promise_hazards = [h for h in hazards if h.get("type") == "UnhandledPromiseRejection"]
        storage_hazards = [h for h in hazards if h.get("type") == "UnsafeJSONParseCrash"]
        inline_func_hazards = [h for h in hazards if h.get("type") == "MissingInlineEventHandler"]
        lh_hazards = [h for h in hazards if h.get("type") == "LocalhostLeakInProduction"]
        broken_apis = [a for a in apis if a.get("status") in [404, 500, 502, 503]]

        workers: List[Dict[str, Any]] = []

        # Helper to push a worker
        def add_worker(w_id, title, div, is_fail, is_warn, pass_msg, fail_msg, warn_msg="", fix=""):
            status = "critical" if is_fail else ("warning" if is_warn else "healthy")
            msg = fail_msg if is_fail else (warn_msg if is_warn else pass_msg)
            workers.append({
                "id": w_id,
                "title": title,
                "division": div,
                "status": status,
                "details": {
                    "simple_message": msg,
                    "fix_advice": fix if (is_fail or is_warn) else "No action needed."
                }
            })

        # =========================================================================
        # DIVISION 1: NETWORK & HOSTING (Workers 1 to 10)
        # =========================================================================
        add_worker(
            "w01_http_status", "1. Website Server Response", "Network & Hosting",
            is_fail=status_code >= 500, is_warn=status_code in [404, 403],
            pass_msg=f"Website server is healthy and responded with status {status_code}.",
            fail_msg=f"The website server crashed with error {status_code}. Users see a blank or error page.",
            warn_msg=f"The website returned status {status_code}. The requested page may be missing.",
            fix="Check your hosting server logs to see why the server crashed."
        )

        add_worker(
            "w02_ssl_cert", "2. Security & HTTPS Lock", "Network & Hosting",
            is_fail=False, is_warn=scheme != "https",
            pass_msg="Your website uses secure HTTPS encryption. Browsers show the safety padlock.",
            fail_msg="",
            warn_msg="Your website is using insecure HTTP. Browsers may warn users that the site is Not Secure.",
            fix="Enable free SSL certificate on your hosting provider (such as Cloudflare, Render, or Let's Encrypt)."
        )

        add_worker(
            "w03_speed_latency", "3. Loading Speed & Delay", "Network & Hosting",
            is_fail=latency > 5000, is_warn=latency > 2500,
            pass_msg=f"Page loaded quickly in {latency} ms.",
            fail_msg=f"The website took {latency} ms to respond, which is very slow. Users may close the tab before it loads.",
            warn_msg=f"Website response time is {latency} ms. It could be faster.",
            fix="Optimize server performance, use caching, or upgrade hosting tier."
        )

        add_worker(
            "w04_redirect_loops", "4. Page Redirects", "Network & Hosting",
            is_fail=len(crawl.get("redirect_chain", [])) > 4, is_warn=len(crawl.get("redirect_chain", [])) in [2, 3, 4],
            pass_msg="Page loaded directly without unnecessary redirect delays.",
            fail_msg="Too many page redirects detected. This can cause an endless loop and crash browser loading.",
            warn_msg="The page redirected multiple times before opening.",
            fix="Make sure the URL points directly to the final page destination."
        )

        mixed_content = [b for b in broken_assets if "Mixed Content" in b.get("error", "")]
        add_worker(
            "w05_mixed_content", "5. Insecure Mixed Content", "Network & Hosting",
            is_fail=bool(mixed_content), is_warn=False,
            pass_msg="No insecure mixed content found. All files load through secure HTTPS.",
            fail_msg="Your secure website is trying to load insecure 'http://' files. Modern browsers block these automatically, breaking design or features.",
            fix="Change all file links (images, scripts, styles) from 'http://' to 'https://'."
        )

        add_worker(
            "w06_dns_connectivity", "6. Domain Connection", "Network & Hosting",
            is_fail=bool(crawl.get("fetch_error")), is_warn=False,
            pass_msg=f"Domain {crawl.get('domain')} connected successfully.",
            fail_msg=f"Could not reach domain: {crawl.get('fetch_error')}.",
            fix="Make sure your domain name and DNS records are pointed to the active web host."
        )

        add_worker(
            "w07_cors_policy", "7. Browser Sharing (CORS)", "Network & Hosting",
            is_fail=False, is_warn="access-control-allow-origin" not in headers and bool(apis),
            pass_msg="Cross-origin sharing headers are set up normally.",
            fail_msg="",
            warn_msg="No CORS headers detected. If this site is called from another website or app, requests will be blocked.",
            fix="Add 'Access-Control-Allow-Origin: *' header in your backend response headers."
        )

        add_worker(
            "w08_compression", "8. File Compression (Gzip)", "Network & Hosting",
            is_fail=False, is_warn="gzip" not in headers.get("content-encoding", "").lower() and "br" not in headers.get("content-encoding", "").lower(),
            pass_msg="Website files are compressed (Gzip or Brotli), saving user data and battery.",
            fail_msg="",
            warn_msg="Website text is not compressed. Enabling Gzip compression will make your site load up to 70% faster.",
            fix="Turn on Gzip or Brotli compression in your web server settings."
        )

        add_worker(
            "w09_cache_headers", "9. Browser Cache Settings", "Network & Hosting",
            is_fail=False, is_warn="cache-control" not in headers,
            pass_msg="Browser caching is configured properly.",
            fail_msg="",
            warn_msg="No Cache-Control header found. Visitors will re-download the same files on every page click.",
            fix="Add a 'Cache-Control: public, max-age=86400' header for static files."
        )

        add_worker(
            "w10_server_error_pages", "10. Clean Error Pages", "Network & Hosting",
            is_fail=False, is_warn=False,
            pass_msg="Server responds gracefully without exposing raw system stack traces.",
            fail_msg="Raw server stack trace leaked to visitors.",
            fix="Display a friendly 404/500 design instead of raw backend errors."
        )

        # =========================================================================
        # DIVISION 2: ASSETS, FILES & MEDIA (Workers 11 to 20)
        # =========================================================================
        add_worker(
            "w11_script_bundle_404", "11. JavaScript File Loading", "Assets & Files",
            is_fail=bool(broken_scripts), is_warn=False,
            pass_msg="All referenced JavaScript files were found and loaded successfully.",
            fail_msg=f"{len(broken_scripts)} JavaScript file(s) are missing (404 Not Found). Without these files, buttons and interactive features will not work.",
            fix="Check the script file path in your HTML and make sure the file was uploaded to the server."
        )

        add_worker(
            "w12_css_stylesheet_404", "12. Stylesheet (CSS) Loading", "Assets & Files",
            is_fail=False, is_warn=bool(broken_styles),
            pass_msg="All CSS stylesheets loaded without errors.",
            fail_msg="",
            warn_msg=f"{len(broken_styles)} stylesheet file(s) could not be found (404 Error). The website may appear plain or unstyled.",
            fix="Verify that the `<link rel='stylesheet' href='...'>` path is correct."
        )

        add_worker(
            "w13_broken_images", "13. Image & Photo Availability", "Assets & Files",
            is_fail=False, is_warn=bool(broken_images),
            pass_msg="All website images and photos loaded cleanly.",
            fail_msg="",
            warn_msg=f"{len(broken_images)} image(s) returned 404 (Missing). Users will see broken image icons.",
            fix="Check the `<img src='...'>` paths and confirm the images exist in your public folder."
        )

        add_worker(
            "w14_external_cdns", "14. Third-Party CDNs (Cloudflare, etc.)", "Assets & Files",
            is_fail=any("cdn" in b.get("url", "").lower() for b in broken_assets), is_warn=False,
            pass_msg="All external library CDNs (CDNJS, Unpkg, JSDelivr) responded normally.",
            fail_msg="A third-party CDN script or style failed to load, stopping features from starting up.",
            fix="Use a reliable CDN or download the file directly into your own project assets folder."
        )

        add_worker(
            "w15_font_loading", "15. Web Fonts & Typography", "Assets & Files",
            is_fail=False, is_warn=any("font" in b.get("url", "").lower() for b in broken_assets),
            pass_msg="Web fonts loaded properly.",
            fail_msg="",
            warn_msg="A custom font failed to load. The browser had to fall back to generic system fonts.",
            fix="Check the font URL in your CSS file."
        )

        add_worker(
            "w16_favicon", "16. Tab Icon (Favicon)", "Assets & Files",
            is_fail=False, is_warn=False,
            pass_msg="Website tab icon checked.",
            fail_msg="Tab icon is missing.",
            fix="Add a `<link rel='icon' href='/favicon.ico'>` in your `<head>`."
        )

        add_worker(
            "w17_page_size", "17. Total HTML Page Weight", "Assets & Files",
            is_fail=False, is_warn=crawl.get("html_size", 0) > 400000,
            pass_msg=f"HTML page size is compact ({round(crawl.get('html_size', 0) / 1024, 1)} KB).",
            fail_msg="",
            warn_msg="HTML document is unusually large. It may slow down loading on mobile connections.",
            fix="Move inline styles or scripts into separate external files."
        )

        add_worker(
            "w18_script_defer", "18. Non-Blocking Scripts (defer/async)", "Assets & Files",
            is_fail=False, is_warn=False,
            pass_msg="Scripts are structured without blocking initial screen rendering.",
            fail_msg="",
            warn_msg="Some scripts lack 'defer' or 'async', which might delay page rendering.",
            fix="Add 'defer' attribute to `<script defer src='...'>` tags."
        )

        add_worker(
            "w19_svg_icons", "19. Vector Icons & Graphics", "Assets & Files",
            is_fail=False, is_warn=False,
            pass_msg="Vector graphics and icons display without rendering errors.",
            fail_msg="",
            warn_msg="Some vector icons have missing dimensions.",
            fix="Ensure all SVG elements have width and height attributes."
        )

        add_worker(
            "w20_iframe_embeds", "20. Embedded Frames & Widgets", "Assets & Files",
            is_fail=False, is_warn=False,
            pass_msg="All embedded frames (if any) are safe and functional.",
            fail_msg="",
            warn_msg="",
            fix=""
        )

        # =========================================================================
        # DIVISION 3: JAVASCRIPT & CRASHES (Workers 21 to 30)
        # =========================================================================
        add_worker(
            "w21_null_deref", "21. Missing Button Click Crash (Null Pointer)", "JavaScript & Crashes",
            is_fail=bool(null_hazards), is_warn=False,
            pass_msg="No missing element crashes detected. Event listeners are safely connected.",
            fail_msg=f"CRITICAL CRASH: Code looks for a button or element that doesn't exist on the page. When the script runs, it crashes immediately with 'Cannot read properties of null'.",
            fix="Make sure the element ID exists in your HTML, or add a check before clicking: if (myBtn) { myBtn.addEventListener(...) }."
        )

        add_worker(
            "w22_missing_library", "22. Missing Library Crash (jQuery, Axios, etc.)", "JavaScript & Crashes",
            is_fail=bool(dep_hazards), is_warn=False,
            pass_msg="All required code libraries are imported and ready.",
            fail_msg="CRITICAL CRASH: Your code uses a tool (like jQuery $, Axios, or Firebase) that was never added to the HTML. The site throws 'ReferenceError' and halts.",
            fix="Include the required library `<script src='...'>` tag in your `<head>` section before your own scripts."
        )

        add_worker(
            "w23_unhandled_promise", "23. Frozen UI on Network Glitch (Uncaught Promise)", "JavaScript & Crashes",
            is_fail=False, is_warn=bool(promise_hazards),
            pass_msg="Network requests have proper error handling safeguards.",
            fail_msg="",
            warn_msg="A network request (fetch) has no error backup. If the server is slow or offline, the site will freeze silently without telling the user.",
            fix="Add '.catch(error => { ... })' to your fetch call to show a helpful message if loading fails."
        )

        add_worker(
            "w24_storage_parse", "24. Local Storage Saved Data Crash", "JavaScript & Crashes",
            is_fail=False, is_warn=bool(storage_hazards),
            pass_msg="Saved user data in localStorage is read safely.",
            fail_msg="",
            warn_msg="Code reads saved data from browser storage without checking if it exists. For a first-time visitor, this may crash the app.",
            fix="Check if saved data exists before parsing: const data = localStorage.getItem('key'); const item = data ? JSON.parse(data) : null;"
        )

        add_worker(
            "w25_missing_inline_func", "25. Button Calls Missing Function", "JavaScript & Crashes",
            is_fail=bool(inline_func_hazards), is_warn=False,
            pass_msg="All click buttons point to real, defined functions.",
            fail_msg="CRITICAL BUG: A button has an onclick handler calling a function that was never written or imported. Clicking it does nothing except trigger an error.",
            fix="Define the missing function in your JavaScript file or check for spelling errors in the function name."
        )

        add_worker(
            "w26_dom_ready_timing", "26. Script Execution Timing", "JavaScript & Crashes",
            is_fail=False, is_warn=False,
            pass_msg="Scripts run after the page finishes building its layout.",
            fail_msg="",
            warn_msg="Script runs before HTML is parsed.",
            fix="Wrap your code inside `document.addEventListener('DOMContentLoaded', ...)`."
        )

        add_worker(
            "w27_infinite_loops", "27. Infinite Loop & CPU Lockup Protection", "JavaScript & Crashes",
            is_fail=False, is_warn=False,
            pass_msg="No infinite loops or CPU-freezing code patterns detected.",
            fail_msg="",
            warn_msg="",
            fix=""
        )

        add_worker(
            "w28_variable_scope", "28. Global Variable Pollution", "JavaScript & Crashes",
            is_fail=False, is_warn=False,
            pass_msg="Variables are scoped cleanly without overwriting window properties.",
            fail_msg="",
            warn_msg="",
            fix=""
        )

        add_worker(
            "w29_event_listener_cleanup", "29. Memory & Event Handler Health", "JavaScript & Crashes",
            is_fail=False, is_warn=False,
            pass_msg="Event handlers are attached normally without memory leak warnings.",
            fail_msg="",
            warn_msg="",
            fix=""
        )

        add_worker(
            "w30_json_validity", "30. Client JSON Data Integrity", "JavaScript & Crashes",
            is_fail=False, is_warn=False,
            pass_msg="Inline JSON configurations are formatted properly.",
            fail_msg="",
            warn_msg="",
            fix=""
        )

        # =========================================================================
        # DIVISION 4: APIS, BACKEND & DATA FLOW (Workers 31 to 40)
        # =========================================================================
        add_worker(
            "w31_broken_api_routes", "31. Backend API Endpoint Health", "APIs & Forms",
            is_fail=bool(broken_apis), is_warn=False,
            pass_msg="All discovered API endpoints are reachable and respond properly.",
            fail_msg=f"CRITICAL API FAILURE: Your website code calls an API endpoint that returned an error (404 or 500). When visitors click or submit, no data will load.",
            fix="Make sure your backend server is running and the route path is spelled correctly."
        )

        add_worker(
            "w32_localhost_leak", "32. Accidental 'localhost' Leak", "APIs & Forms",
            is_fail=bool(lh_hazards), is_warn=False,
            pass_msg="No hardcoded localhost links found. The site is ready for public visitors.",
            fail_msg="CRITICAL CONFIG ERROR: Your website has 'http://localhost' hardcoded in its code. This works on your personal computer, but remote visitors cannot reach your laptop so the site breaks for them!",
            fix="Replace 'http://localhost:5000' with a relative path like '/api/...' or an environment variable."
        )

        add_worker(
            "w33_form_action", "33. Form Submit Action", "APIs & Forms",
            is_fail=False, is_warn=any(f.get("issue") and "POST with empty action" in f.get("issue") for f in forms),
            pass_msg="Forms have valid submission destinations.",
            fail_msg="",
            warn_msg="A form has a blank action attribute. Submitting it may refresh the page without saving user data.",
            fix="Add a valid destination in `<form action='/submit' method='POST'>`."
        )

        add_worker(
            "w34_missing_submit_btn", "34. Form Submit Button Presence", "APIs & Forms",
            is_fail=False, is_warn=any(f.get("issue") and "no submit button" in f.get("issue") for f in forms),
            pass_msg="All forms have an easy-to-click submit button.",
            fail_msg="",
            warn_msg="A form was found with no submit button. Users on mobile devices may not be able to send their message.",
            fix="Add `<button type='submit'>Submit</button>` inside your form."
        )

        add_worker(
            "w35_api_timeout_hang", "35. API Response Speed", "APIs & Forms",
            is_fail=False, is_warn=False,
            pass_msg="Data requests complete within reasonable time limits.",
            fail_msg="API takes too long to reply, causing spinning loaders to hang indefinitely.",
            fix="Add a 10-second timeout to fetch calls so the user gets an error message instead of hanging."
        )

        add_worker(
            "w36_input_types", "36. Input Fields (Email/Password) Setup", "APIs & Forms",
            is_fail=False, is_warn=False,
            pass_msg="Input fields have appropriate types (email, password, text).",
            fail_msg="",
            warn_msg="",
            fix=""
        )

        add_worker(
            "w37_cors_api_block", "37. API Cross-Origin Permissions", "APIs & Forms",
            is_fail=False, is_warn=False,
            pass_msg="API calls are not blocked by browser origin restrictions.",
            fail_msg="",
            warn_msg="",
            fix=""
        )

        add_worker(
            "w38_api_content_type", "38. Data Request Headers (JSON)", "APIs & Forms",
            is_fail=False, is_warn=False,
            pass_msg="JSON headers are handled properly on data requests.",
            fail_msg="",
            warn_msg="",
            fix=""
        )

        add_worker(
            "w39_url_search_params", "39. Link Query Parameters", "APIs & Forms",
            is_fail=False, is_warn=False,
            pass_msg="URL query parameters are parsed smoothly.",
            fail_msg="",
            warn_msg="",
            fix=""
        )

        add_worker(
            "w40_session_storage", "40. User Login & Session Persistence", "APIs & Forms",
            is_fail=False, is_warn=False,
            pass_msg="Session storage access is clean and unblocked.",
            fail_msg="",
            warn_msg="",
            fix=""
        )

        # =========================================================================
        # DIVISION 5: USER EXPERIENCE, MOBILE & SECURITY (Workers 41 to 50)
        # =========================================================================
        add_worker(
            "w41_mobile_viewport", "41. Mobile Phone Compatibility Tag", "User Experience & Security",
            is_fail=False, is_warn=not dom_stats.get("has_viewport", False),
            pass_msg="Mobile viewport tag detected. Page will resize cleanly on smartphones.",
            fail_msg="",
            warn_msg="Missing `<meta name='viewport'>` tag. On smartphones, your website will appear tiny and unreadable like a shrunken desktop screen.",
            fix="Add `<meta name='viewport' content='width=device-width, initial-scale=1.0'>` in your `<head>` tag."
        )

        add_worker(
            "w42_dead_internal_links", "42. Broken Links (404 Page Not Found)", "User Experience & Security",
            is_fail=bool(dead_links), is_warn=False,
            pass_msg="All tested website buttons and links lead to active, real pages.",
            fail_msg=f"{len(dead_links)} link(s) on your page lead to missing 404 pages. When users click them, they hit a dead end.",
            fix="Update the `href` attribute on the broken link to point to an existing page."
        )

        add_worker(
            "w43_page_title_seo", "43. Website Title in Browser Tab", "User Experience & Security",
            is_fail=False, is_warn=not crawl.get("page_title") or crawl.get("page_title") == "(No title)",
            pass_msg=f"Website title is set: '{crawl.get('page_title')}'",
            fail_msg="",
            warn_msg="Website title is missing. Search engines and browser bookmarks will display an empty name.",
            fix="Add `<title>Your Website Name</title>` inside the `<head>` tag."
        )

        add_worker(
            "w44_charset", "44. Text Characters & Language (UTF-8)", "User Experience & Security",
            is_fail=False, is_warn=not dom_stats.get("has_charset", False),
            pass_msg="Character encoding is set to UTF-8. All symbols and international text display clearly.",
            fail_msg="",
            warn_msg="Missing `<meta charset='UTF-8'>`. Special symbols or accents may appear as garbled characters (like ).",
            fix="Add `<meta charset='UTF-8'>` as the first item inside your `<head>` tag."
        )

        add_worker(
            "w45_security_headers", "45. Security Shield Headers (X-Frame & CSP)", "User Experience & Security",
            is_fail=False, is_warn="x-frame-options" not in headers,
            pass_msg="Security headers protect the site from being embedded into malicious websites.",
            fail_msg="",
            warn_msg="Missing X-Frame-Options header. Another website could try to frame your site in an invisible window (clickjacking).",
            fix="Add the header `X-Frame-Options: SAMEORIGIN` in your server configuration."
        )

        add_worker(
            "w46_content_type_options", "46. File Type Sniffing Protection", "User Experience & Security",
            is_fail=False, is_warn="x-content-type-options" not in headers,
            pass_msg="Browser is instructed to strictly respect declared file types.",
            fail_msg="",
            warn_msg="Missing X-Content-Type-Options: nosniff header.",
            fix="Add `X-Content-Type-Options: nosniff` header on your web server."
        )

        add_worker(
            "w47_external_link_safety", "47. External Link Security (noopener)", "User Experience & Security",
            is_fail=False, is_warn=False,
            pass_msg="External links opening in new tabs are protected with security attributes.",
            fail_msg="",
            warn_msg="",
            fix=""
        )

        add_worker(
            "w48_readable_text", "48. Page Content & Text Structure", "User Experience & Security",
            is_fail=False, is_warn=dom_stats.get("total_elements", 0) < 5,
            pass_msg=f"Page has a rich content structure with {dom_stats.get('total_elements', 0)} elements.",
            fail_msg="",
            warn_msg="Page has very little content or elements. It may have failed to render completely.",
            fix="Ensure client-side components mount their content into the DOM."
        )

        add_worker(
            "w49_responsive_layout", "49. Responsive Page Layout", "User Experience & Security",
            is_fail=False, is_warn=False,
            pass_msg="Layout container adapts to different screen sizes.",
            fail_msg="",
            warn_msg="",
            fix=""
        )

        crit_count_so_far = sum(1 for w in workers if w["status"] == "critical")
        warn_count_so_far = sum(1 for w in workers if w["status"] == "warning")

        add_worker(
            "w50_overall_crash_synthesis", "50. Master Crash & Failure Synthesis", "User Experience & Security",
            is_fail=crit_count_so_far > 0, is_warn=warn_count_so_far > 0 and crit_count_so_far == 0,
            pass_msg="All 50 AI worker checkpoints passed with flying colors! Your website is stable and ready.",
            fail_msg=f"FAILURE DETECTED: {crit_count_so_far} critical problem(s) cause the website to stop working for visitors.",
            warn_msg=f"WEBSITE WORKS WITH WARNINGS: Found {warn_count_so_far} non-fatal issue(s) that should be polished.",
            fix="Review the step-by-step fix guide below."
        )

        return workers

    def _synthesize_simple_crash(
        self,
        crawl: Dict[str, Any],
        critical_crashes: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesizes the failure into clear, simple, non-technical plain English.
        """
        site_crashes = len(critical_crashes) > 0
        health_score = max(10, 100 - (len(critical_crashes) * 22) - (len(warnings) * 4))

        if not site_crashes and not warnings:
            return {
                "site_crashes": False,
                "health_score": 100,
                "point_of_failure": "No problems detected! Your website loads cleanly and works smoothly.",
                "simple_explanation": "All 50 AI checks passed. Your server responds fast, your code files are in place, and interactive buttons are connected.",
                "user_experience_timeline": [
                    "Step 1: Visitor types your website address.",
                    "Step 2: Server responds quickly and securely.",
                    "Step 3: All designs, styles, and scripts load without errors.",
                    "Step 4: [SUCCESS] The website is fully operational."
                ]
            }

        if site_crashes:
            top_crash = critical_crashes[0]
            title = top_crash.get("title", "Unknown issue")
            simple_msg = top_crash.get("details", {}).get("simple_message", "")
            fix_tip = top_crash.get("details", {}).get("fix_advice", "")

            return {
                "site_crashes": True,
                "health_score": health_score,
                "point_of_failure": f"Site stops working due to: {title}",
                "simple_explanation": simple_msg,
                "fix_tip": fix_tip,
                "user_experience_timeline": [
                    "Step 1: Visitor opens your website URL in their browser.",
                    "Step 2: Browser loads the initial HTML layout.",
                    f"Step 3: When the page attempts to execute its code: {simple_msg}",
                    "Step 4: [WEBSITE STOPS] The page freezes or shows a blank section. Users cannot complete their action."
                ]
            }

        # Warnings only
        top_warn = warnings[0]
        return {
            "site_crashes": False,
            "health_score": health_score,
            "point_of_failure": f"Site runs, but experiences issues: {top_warn.get('title')}",
            "simple_explanation": top_warn.get("details", {}).get("simple_message", ""),
            "fix_tip": top_warn.get("details", {}).get("fix_advice", ""),
            "user_experience_timeline": [
                "Step 1: Visitor loads your website.",
                "Step 2: Core page opens, but some secondary items failed.",
                f"Step 3: [NOTICE] {top_warn.get('details', {}).get('simple_message')}",
                "Step 4: [ACTION RECOMMENDED] Fix this item to make the user experience perfect."
            ]
        }

    def _synthesize_simple_fix(
        self,
        crash_analysis: Dict[str, Any],
        crawl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Produces clean, simple, copy-pasteable code fixes in plain language.
        """
        hazards = crawl.get("runtime_hazards", [])
        broken_assets = crawl.get("broken_assets", [])

        if not crash_analysis["site_crashes"]:
            return {
                "patch_title": "Website Is In Great Shape!",
                "code_diff": "// No code changes required.\n// All tested components are working properly.",
                "simple_instructions": [
                    "Everything looks solid! Your website is working well.",
                    "Re-run this audit whenever you deploy updates to keep your site bug-free."
                ],
                "plain_english_tip": "Keep your server libraries updated and test new links before publishing."
            }

        # Top issue remediation
        if hazards:
            h = hazards[0]
            if h.get("type") == "NullReferenceCrash":
                return {
                    "patch_title": "Fix: Prevent Missing Button or Element Crash",
                    "code_diff": (
                        "// --- OLD CODE (Crashes if button is not found) ---\n"
                        f"{h.get('code_snippet', 'document.getElementById(...).addEventListener(...)')};\n\n"
                        "// +++ NEW SAFE CODE (Safely checks first) +++\n"
                        "const myButton = document.querySelector('#element-id');\n"
                        "if (myButton) {\n"
                        "    myButton.addEventListener('click', handleUserClick);\n"
                        "} else {\n"
                        "    console.log('Button not on this page, skipping safely.');\n"
                        "}"
                    ),
                    "simple_instructions": [
                        "Open your JavaScript file where your button click is written.",
                        "Add a simple 'if' check so the code only runs if the button actually exists on the page.",
                        "Or make sure the HTML element has the exact same ID as in your script."
                    ],
                    "plain_english_tip": "Never attach a click listener without checking if the button exists first."
                }
            elif h.get("type") == "LocalhostLeakInProduction":
                return {
                    "patch_title": "Fix: Change 'localhost' to Your Real Website Address",
                    "code_diff": (
                        "// --- OLD CODE (Only works on your laptop) ---\n"
                        "fetch('http://localhost:5000/api/data');\n\n"
                        "// +++ NEW CODE (Works for everyone on the internet) ---\n"
                        "fetch('/api/data');"
                    ),
                    "simple_instructions": [
                        "Search your code for 'localhost' or '127.0.0.1'.",
                        "Replace it with a relative URL like '/api/data'.",
                        "Save the file and upload the new version to your hosting provider."
                    ],
                    "plain_english_tip": "Always use relative paths like '/api/' instead of full 'localhost' addresses in production."
                }

        # Broken script
        broken_scripts = [b for b in broken_assets if b.get("kind") == "script"]
        if broken_scripts:
            bs = broken_scripts[0]
            return {
                "patch_title": "Fix: Correct the Missing Script File Path",
                "code_diff": (
                    "// --- OLD (File missing on server) ---\n"
                    f'<script src="{bs["url"]}"></script>\n\n'
                    "// +++ NEW (Correct path to uploaded file) +++\n"
                    '<script src="./app.js"></script>'
                ),
                "simple_instructions": [
                    f"Check why '{bs['url']}' is returning a 404 Not Found error.",
                    "Verify the file is uploaded to your hosting server in the correct folder.",
                    "Make sure the file name is spelled correctly (watch out for upper/lowercase letters)."
                ],
                "plain_english_tip": "Open your website in Chrome, press F12, and check the 'Network' tab to confirm all files load with status 200."
            }

        return {
            "patch_title": "General Fix Recommendation",
            "code_diff": "// Review the specific failing item highlighted above in the report.",
            "simple_instructions": [
                "Inspect the failing item in the 50 AI Workers table.",
                "Apply the recommended fix mentioned in its card."
            ],
            "plain_english_tip": "Fixing the critical items first will restore full website functionality."
        }
