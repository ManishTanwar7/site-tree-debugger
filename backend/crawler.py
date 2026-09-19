"""
High-performance asynchronous website crawler and deep asset/runtime inspector.
Analyzes a URL to extract DOM, scripts, styles, API calls, and detects potential crash points.
"""

import asyncio
import re
import urllib.parse
from typing import Dict, List, Any, Optional
import httpx
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 SiteTreeDebugger/1.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

class SiteCrawler:
    def __init__(self, timeout: float = 12.0, max_assets: int = 25):
        self.timeout = timeout
        self.max_assets = max_assets

    def normalize_url(self, raw_url: str) -> str:
        raw_url = raw_url.strip()
        if not raw_url.startswith(("http://", "https://")):
            raw_url = "https://" + raw_url
        return raw_url

    async def inspect_url(self, target_url: str) -> Dict[str, Any]:
        """
        Comprehensive scan of a web address:
        - Fetches HTML, measures latency, inspects headers & SSL
        - Extracts scripts, stylesheets, links, forms, interactive elements
        - Concurrently checks asset health (404s, CORS, mixed content)
        - Scans scripts for runtime crash hazards (null-derefs, missing globals, API fails)
        """
        normalized_url = self.normalize_url(target_url)
        parsed_target = urllib.parse.urlparse(normalized_url)
        base_domain = f"{parsed_target.scheme}://{parsed_target.netloc}"

        report: Dict[str, Any] = {
            "target_url": normalized_url,
            "domain": parsed_target.netloc,
            "scheme": parsed_target.scheme,
            "status_code": 0,
            "latency_ms": 0,
            "headers": {},
            "redirect_chain": [],
            "network_ok": False,
            "page_title": "",
            "html_size": 0,
            "dom_stats": {},
            "assets": {
                "scripts": [],
                "stylesheets": [],
                "images": [],
                "forms": [],
                "links": []
            },
            "broken_assets": [],
            "api_endpoints": [],
            "runtime_hazards": [],
            "missing_dom_references": [],
            "raw_issues_count": 0,
            "fetch_error": None
        }

        async with httpx.AsyncClient(
            headers=DEFAULT_HEADERS,
            follow_redirects=True,
            verify=False,  # Allow inspecting self-signed/local certs for localhost testing
            timeout=httpx.Timeout(self.timeout)
        ) as client:
            # 1. Fetch Main Page
            start_time = asyncio.get_event_loop().time()
            try:
                response = await client.get(normalized_url)
                latency = round((asyncio.get_event_loop().time() - start_time) * 1000, 2)
                report["latency_ms"] = latency
                report["status_code"] = response.status_code
                report["headers"] = dict(response.headers)
                report["html_size"] = len(response.text)
                
                # Check redirect chain
                if response.history:
                    report["redirect_chain"] = [
                        {"url": str(r.url), "status": r.status_code} for r in response.history
                    ]
                
                if response.status_code >= 400:
                    report["fetch_error"] = f"Server returned HTTP error status {response.status_code}"
                    report["network_ok"] = False
                else:
                    report["network_ok"] = True

                html_content = response.text
            except Exception as e:
                latency = round((asyncio.get_event_loop().time() - start_time) * 1000, 2)
                report["latency_ms"] = latency
                report["fetch_error"] = f"Failed to connect to {normalized_url}: {str(e)}"
                report["network_ok"] = False
                return report

            # 2. Parse DOM with BeautifulSoup
            try:
                soup = BeautifulSoup(html_content, "html.parser")
            except Exception as e:
                soup = BeautifulSoup(html_content, "lxml")

            report["page_title"] = soup.title.string.strip() if soup.title and soup.title.string else "(No title)"

            # Extract all DOM element IDs and Classes
            existing_ids = set()
            existing_classes = set()
            for tag in soup.find_all(True):
                if tag.get("id"):
                    existing_ids.add(tag.get("id").strip())
                if tag.get("class"):
                    classes = tag.get("class")
                    if isinstance(classes, list):
                        existing_classes.update(c.strip() for c in classes)
                    elif isinstance(classes, str):
                        existing_classes.update(classes.split())

            report["dom_stats"] = {
                "total_elements": len(soup.find_all(True)),
                "total_ids": len(existing_ids),
                "total_classes": len(existing_classes),
                "has_viewport": bool(soup.find("meta", attrs={"name": "viewport"})),
                "has_charset": bool(soup.find("meta", attrs={"charset": True}) or soup.find("meta", attrs={"http-equiv": "Content-Type"}))
            }

            # 3. Extract Assets (Scripts, Styles, Images, Links, Forms)
            script_tags = soup.find_all("script")
            style_tags = soup.find_all("link", rel=lambda x: x and "stylesheet" in x.lower() if isinstance(x, str) else False)
            img_tags = soup.find_all("img")
            link_tags = soup.find_all("a", href=True)
            form_tags = soup.find_all("form")

            scripts_to_fetch = []
            inline_scripts = []

            for s in script_tags:
                src = s.get("src")
                if src:
                    full_src = urllib.parse.urljoin(normalized_url, src)
                    scripts_to_fetch.append({
                        "url": full_src,
                        "raw_src": src,
                        "async": s.get("async") is not None,
                        "defer": s.get("defer") is not None,
                        "type": s.get("type", "text/javascript")
                    })
                else:
                    if s.string and s.string.strip():
                        inline_scripts.append(s.string.strip())

            stylesheets_to_check = []
            for st in style_tags:
                href = st.get("href")
                if href:
                    stylesheets_to_check.append({
                        "url": urllib.parse.urljoin(normalized_url, href),
                        "raw_href": href
                    })

            images_to_check = []
            for img in img_tags:
                src = img.get("src")
                if src and not src.startswith("data:"):
                    images_to_check.append({
                        "url": urllib.parse.urljoin(normalized_url, src),
                        "alt": img.get("alt", "")
                    })

            # Inspect Forms
            for f in form_tags:
                action = f.get("action", "")
                method = f.get("method", "GET").upper()
                inputs = [inp.get("name") or inp.get("id") or inp.get("type") for inp in f.find_all("input")]
                has_submit = bool(f.find("input", type="submit") or f.find("button", type="submit") or f.find("button"))
                
                form_issue = None
                if not has_submit:
                    form_issue = "Form has no submit button or input, users may not be able to submit."
                elif not action and method == "POST":
                    form_issue = "Form uses POST with empty action attribute, may cause unexpected self-refresh or crash."
                
                report["assets"]["forms"].append({
                    "action": action,
                    "method": method,
                    "inputs_count": len(inputs),
                    "has_submit": has_submit,
                    "issue": form_issue
                })

            # Inspect Interactive Elements & Inline Event Handlers
            inline_handlers = []
            for tag in soup.find_all(True):
                for attr, val in tag.attrs.items():
                    if attr.startswith("on") and isinstance(val, str):
                        inline_handlers.append({
                            "tag": tag.name,
                            "id": tag.get("id"),
                            "event": attr,
                            "handler_code": val
                        })
            
            # 4. Concurrently Audit Assets (Broken scripts, 404 styles, images)
            assets_to_test = scripts_to_fetch[:self.max_assets] + stylesheets_to_check[:10] + images_to_check[:10]
            downloaded_scripts: List[Dict[str, Any]] = []

            async def check_asset(asset_item: Dict[str, Any], kind: str):
                url = asset_item["url"]
                # Detect mixed content
                if parsed_target.scheme == "https" and url.startswith("http://"):
                    report["broken_assets"].append({
                        "url": url,
                        "kind": kind,
                        "status": 0,
                        "error": "Mixed Content Block: HTTPS site loading insecure HTTP resource",
                        "severity": "High"
                    })
                    return

                try:
                    if kind == "script":
                        # GET script so we can also analyze its JS code
                        res = await client.get(url, timeout=6.0)
                        if res.status_code >= 400:
                            report["broken_assets"].append({
                                "url": url,
                                "kind": kind,
                                "status": res.status_code,
                                "error": f"Failed to load script (HTTP {res.status_code})",
                                "severity": "Critical"
                            })
                        else:
                            downloaded_scripts.append({
                                "url": url,
                                "code": res.text[:200000]  # limit to 200kb per script for safety
                            })
                    else:
                        res = await client.head(url, timeout=4.0)
                        if res.status_code >= 400:
                            # fallback to GET if HEAD method not allowed
                            if res.status_code == 405:
                                res = await client.get(url, timeout=4.0)
                        
                        if res.status_code >= 400:
                            report["broken_assets"].append({
                                "url": url,
                                "kind": kind,
                                "status": res.status_code,
                                "error": f"Failed to load {kind} (HTTP {res.status_code})",
                                "severity": "Medium" if kind == "image" else "High"
                            })
                except Exception as e:
                    report["broken_assets"].append({
                        "url": url,
                        "kind": kind,
                        "status": 0,
                        "error": f"Network error loading {kind}: {str(e)}",
                        "severity": "Critical" if kind == "script" else "Medium"
                    })

            tasks = []
            for s in scripts_to_fetch[:self.max_assets]:
                tasks.append(check_asset(s, "script"))
            for st in stylesheets_to_check[:10]:
                tasks.append(check_asset(st, "stylesheet"))
            for img in images_to_check[:10]:
                tasks.append(check_asset(img, "image"))

            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

            # Check Internal Links for 404s (sample up to 8 internal links)
            internal_links = []
            for link in link_tags:
                href = link.get("href", "").strip()
                if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                    continue
                full_link = urllib.parse.urljoin(normalized_url, href)
                parsed_link = urllib.parse.urlparse(full_link)
                if parsed_link.netloc == parsed_target.netloc and full_link != normalized_url:
                    if full_link not in [l["url"] for l in internal_links]:
                        internal_links.append({"url": full_link, "text": link.get_text(strip=True)[:40]})

            async def check_internal_link(link_item):
                try:
                    res = await client.head(link_item["url"], timeout=4.0)
                    if res.status_code == 405:
                        res = await client.get(link_item["url"], timeout=4.0)
                    if res.status_code >= 400:
                        report["broken_assets"].append({
                            "url": link_item["url"],
                            "kind": "link",
                            "status": res.status_code,
                            "error": f"Dead internal link '{link_item.get('text')}' returns HTTP {res.status_code}",
                            "severity": "High"
                        })
                except Exception as e:
                    report["broken_assets"].append({
                        "url": link_item["url"],
                        "kind": "link",
                        "status": 0,
                        "error": f"Failed to reach internal link '{link_item.get('text')}': {str(e)}",
                        "severity": "High"
                    })

            link_tasks = [check_internal_link(l) for l in internal_links[:8]]
            if link_tasks:
                await asyncio.gather(*link_tasks, return_exceptions=True)

            # 5. Deep Scan of JavaScript for Crash Points
            all_js_sources = []
            for i, script_text in enumerate(inline_scripts):
                all_js_sources.append({"source": f"inline_script_{i+1}", "code": script_text})
            for ds in downloaded_scripts:
                all_js_sources.append({"source": ds["url"], "code": ds["code"]})

            hazards = self._scan_js_for_crashes(all_js_sources, existing_ids, existing_classes, normalized_url)
            report["runtime_hazards"] = hazards

            # 6. Extract and verify API Endpoints
            api_endpoints = self._extract_api_endpoints(all_js_sources, base_domain)
            report["api_endpoints"] = api_endpoints

            # Check Reachability of discovered internal API endpoints
            async def test_api_endpoint(ep):
                ep_url = ep["url"]
                try:
                    res = await client.get(ep_url, timeout=4.0)
                    ep["status"] = res.status_code
                    if res.status_code in [404, 500, 502, 503]:
                        ep["error"] = f"API endpoint failed with HTTP {res.status_code}"
                        report["runtime_hazards"].append({
                            "type": "BrokenAPIEndpoint",
                            "severity": "Critical",
                            "location": ep["source"],
                            "description": f"Script calls API '{ep['raw_path']}' which returned HTTP {res.status_code} ({ep['error']}). When invoked, client-side data will fail to load or crash.",
                            "trigger": f"Triggered on API call to {ep['raw_path']}",
                            "fix_suggestion": f"Verify backend route {ep['raw_path']} is implemented and running on the target server."
                        })
                except Exception as e:
                    ep["status"] = 0
                    ep["error"] = str(e)

            api_tasks = [test_api_endpoint(ep) for ep in api_endpoints if ep.get("is_internal")][:6]
            if api_tasks:
                await asyncio.gather(*api_tasks, return_exceptions=True)

            # Check Inline Handlers for Missing Functions
            for h in inline_handlers:
                func_match = re.search(r'([a-zA-Z0-9_$]+)\s*\(', h["handler_code"])
                if func_match:
                    func_name = func_match.group(1)
                    # Check if func_name is declared in any JS code
                    found = False
                    for js in all_js_sources:
                        if re.search(rf'(function\s+{func_name}\b|window\.{func_name}\b|const\s+{func_name}\s*=|var\s+{func_name}\s*=|let\s+{func_name}\s*=)', js["code"]):
                            found = True
                            break
                    if not found and func_name not in ["alert", "console", "confirm", "prompt", "window", "location", "document"]:
                        report["runtime_hazards"].append({
                            "type": "MissingInlineEventHandler",
                            "severity": "Critical",
                            "location": f"<{h['tag']} {h['event']}=\"{h['handler_code']}\">",
                            "description": f"Inline event handler calls '{func_name}()', but '{func_name}' is not defined in any loaded scripts. Clicking this will throw 'ReferenceError: {func_name} is not defined' and site feature stops working.",
                            "trigger": f"User clicks or triggers '{h['event']}' on <{h['tag']}>",
                            "fix_suggestion": f"Define 'window.{func_name} = function() {{ ... }}' or import the script containing '{func_name}'."
                        })

            # Check for Localhost Leaks in Production
            if parsed_target.netloc not in ["localhost", "127.0.0.1"]:
                for js in all_js_sources:
                    localhost_matches = re.findall(r'https?://(?:localhost|127\.0\.0\.1)(?::\d+)?(?:/[^\s"\'`)]*)?', js["code"])
                    if localhost_matches:
                        unique_lh = list(set(localhost_matches))[:3]
                        report["runtime_hazards"].append({
                            "type": "LocalhostLeakInProduction",
                            "severity": "Critical",
                            "location": js["source"],
                            "description": f"Script on public site contains hardcoded reference to {', '.join(unique_lh)}. When users visit this site, requests to localhost will fail because their browser cannot reach your local development machine!",
                            "trigger": "Triggered when site attempts to communicate with the hardcoded localhost API",
                            "fix_suggestion": "Replace hardcoded 'http://localhost:...' with relative paths like '/api/...' or an environment variable (e.g. process.env.API_URL)."
                        })

            report["assets"]["scripts"] = scripts_to_fetch
            report["assets"]["stylesheets"] = stylesheets_to_check
            report["assets"]["images"] = images_to_check[:15]
            report["raw_issues_count"] = len(report["broken_assets"]) + len(report["runtime_hazards"])

            return report

    def _scan_js_for_crashes(
        self,
        js_sources: List[Dict[str, Any]],
        existing_ids: set,
        existing_classes: set,
        base_url: str
    ) -> List[Dict[str, Any]]:
        """
        Pinpoints specific JavaScript code patterns that cause crashes at runtime.
        """
        hazards: List[Dict[str, Any]] = []

        # 1. getElementById on missing DOM ID followed by dereference
        # e.g.: document.getElementById('login-btn').addEventListener
        id_pattern = re.compile(r"document\.getElementById\(\s*['\"]([^'\"]+)['\"]\s*\)\s*\.([a-zA-Z0-9_$]+)")
        
        # 2. querySelector on missing DOM element
        qs_pattern = re.compile(r"document\.querySelector\(\s*['\"]#([^'\"]+)['\"]\s*\)\s*\.([a-zA-Z0-9_$]+)")

        # 3. Missing Global Libraries (e.g. jQuery $, axios, React, Stripe, firebase)
        common_globals = {
            r"\$\s*\(": ("jQuery", "<script src=\"https://code.jquery.com/jquery-3.7.1.min.js\"></script>"),
            r"\baxios\.(?:get|post|put|delete|request)\b": ("Axios", "<script src=\"https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js\"></script>"),
            r"\blucide\.createIcons\b": ("Lucide Icons", "<script src=\"https://unpkg.com/lucide@latest\"></script>"),
            r"\bStripe\s*\(": ("Stripe.js", "<script src=\"https://js.stripe.com/v3/\"></script>"),
            r"\bfirebase\.(?:initializeApp|auth|firestore)\b": ("Firebase SDK", "Import Firebase modular SDK or compat bundle"),
            r"\bChart\s*\(": ("Chart.js", "<script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>")
        }

        # 4. JSON.parse localStorage without null check
        storage_pattern = re.compile(r"JSON\.parse\(\s*localStorage\.getItem\(\s*['\"]([^'\"]+)['\"]\s*\)\s*\)")

        # 5. Missing .catch on fetch calls
        fetch_missing_catch = re.compile(r"fetch\([^)]+\)\s*\.then\([^)]+\)(?!\s*\.catch)")

        for js in js_sources:
            source_name = js["source"]
            code = js["code"]

            # Check DOM ID mismatches
            for m in id_pattern.finditer(code):
                target_id = m.group(1)
                prop = m.group(2)
                if target_id not in existing_ids:
                    hazards.append({
                        "type": "NullReferenceCrash",
                        "severity": "Critical",
                        "location": source_name,
                        "code_snippet": m.group(0),
                        "description": (
                            f"Code attempts to access '.{prop}' on document.getElementById('{target_id}'), "
                            f"but element '#{target_id}' does not exist in the DOM. "
                            f"This will throw 'TypeError: Cannot read properties of null (reading \"{prop}\")' and crash the script immediately."
                        ),
                        "trigger": "Executes on initial page load or when event is fired",
                        "fix_suggestion": (
                            f"Add null check: const el = document.getElementById('{target_id}'); if (el) {{ el.{prop}... }} "
                            f"or ensure element <... id=\"{target_id}\"> exists in the HTML."
                        )
                    })

            for m in qs_pattern.finditer(code):
                target_id = m.group(1)
                prop = m.group(2)
                if target_id not in existing_ids:
                    hazards.append({
                        "type": "NullReferenceCrash",
                        "severity": "Critical",
                        "location": source_name,
                        "code_snippet": m.group(0),
                        "description": (
                            f"Code calls '.{prop}' on document.querySelector('#{target_id}'), "
                            f"but no element matching '#{target_id}' exists. "
                            f"Throws 'TypeError: Cannot read properties of null'."
                        ),
                        "trigger": "Executes on page execution",
                        "fix_suggestion": f"Check if element '#{target_id}' exists before accessing '.{prop}', or add optional chaining: document.querySelector('#{target_id}')?.{prop}"
                    })

            # Check Missing Global Libraries
            for regex_str, (lib_name, include_hint) in common_globals.items():
                if re.search(regex_str, code):
                    # verify if library was loaded
                    lib_loaded = False
                    for candidate in js_sources:
                        if lib_name.lower() in candidate["source"].lower():
                            lib_loaded = True
                            break
                        if lib_name == "jQuery" and ("jquery" in candidate["code"][:1000].lower() or "jquery" in candidate["source"].lower()):
                            lib_loaded = True
                            break
                    if not lib_loaded and not source_name.endswith(".min.js"):
                        clean_regex = regex_str.replace('\\', '')
                        hazards.append({
                            "type": "MissingDependencyCrash",
                            "severity": "Critical",
                            "location": source_name,
                            "description": (
                                f"Code uses {lib_name} globals ({clean_regex}) but {lib_name} script was not detected in HTML head/body. "
                                f"This causes 'ReferenceError: {lib_name} is not defined' and halts execution."
                            ),
                            "trigger": f"Triggered immediately when {lib_name} method is called",
                            "fix_suggestion": f"Include {lib_name} in HTML: {include_hint}"
                        })

            # Check localStorage JSON.parse crash
            for m in storage_pattern.finditer(code):
                storage_key = m.group(1)
                hazards.append({
                    "type": "UnsafeJSONParseCrash",
                    "severity": "High",
                    "location": source_name,
                    "code_snippet": m.group(0),
                    "description": (
                        f"Unsafely parsing localStorage item '{storage_key}' with JSON.parse. "
                        f"If the item is not set yet or is corrupted, this throws 'SyntaxError: \"undefined\" is not valid JSON' or 'null' errors."
                    ),
                    "trigger": "Triggered when a new user visits with empty localStorage",
                    "fix_suggestion": (
                        f"Wrap with try-catch or fallback: const raw = localStorage.getItem('{storage_key}'); "
                        f"const val = raw ? JSON.parse(raw) : null;"
                    )
                })

            # Check Unhandled Promise Rejections
            for m in fetch_missing_catch.finditer(code):
                snippet = m.group(0)[:80]
                hazards.append({
                    "type": "UnhandledPromiseRejection",
                    "severity": "Medium",
                    "location": source_name,
                    "code_snippet": snippet,
                    "description": (
                        "Fetch request has '.then()' chain without a terminal '.catch()'. "
                        "If the network request fails or the server is down, an UnhandledPromiseRejection will be thrown, causing silent UI freeze or crash."
                    ),
                    "trigger": "Triggered when network request encounters an error or timeout",
                    "fix_suggestion": "Append '.catch(err => console.error(\"Request failed:\", err))' to the promise chain."
                })

        return hazards[:20]  # Cap at 20 most relevant hazards

    def _extract_api_endpoints(self, js_sources: List[Dict[str, Any]], base_domain: str) -> List[Dict[str, Any]]:
        """
        Discovers API endpoints called within JavaScript code.
        """
        endpoints = []
        seen = set()

        api_regex = re.compile(r"""(?:fetch|axios(?:\.get|\.post|\.put|\.delete)?|\.open)\(\s*['"`]([^'"`]+)['"`]""")

        for js in js_sources:
            code = js["code"]
            for m in api_regex.finditer(code):
                raw_path = m.group(1).strip()
                if raw_path in seen or raw_path.startswith("data:"):
                    continue
                seen.add(raw_path)

                is_internal = raw_path.startswith("/") or base_domain in raw_path
                full_url = raw_path if raw_path.startswith("http") else urllib.parse.urljoin(base_domain, raw_path)

                endpoints.append({
                    "raw_path": raw_path,
                    "url": full_url,
                    "is_internal": is_internal,
                    "source": js["source"]
                })

        return endpoints[:15]
