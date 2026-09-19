"""
FastAPI Server for SiteTree Debugger.
Provides WebSockets for real-time AI tree stream, REST endpoints for audits and history,
and a built-in interactive demo site with real-world bugs for testing.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel

from .crawler import SiteCrawler
from .ai_tree import MultiAITreeEngine
from .storage import (
    load_settings,
    save_settings,
    save_audit_record,
    get_all_audits,
    get_audit_by_id
)

app = FastAPI(title="SiteTree Debugger", version="1.0.0")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

class AnalyzeRequest(BaseModel):
    url: str
    api_key: Optional[str] = None
    model: Optional[str] = "gemini-2.5-flash"

class SettingsRequest(BaseModel):
    gemini_api_key: Optional[str] = ""
    preferred_model: Optional[str] = "gemini-2.5-flash"
    deep_scan: Optional[bool] = True

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/settings")
async def get_settings():
    return load_settings()

@app.post("/api/settings")
async def update_settings(req: SettingsRequest):
    data = req.model_dump()
    save_settings(data)
    return {"status": "success", "settings": data}

@app.get("/api/history")
async def list_history():
    audits = get_all_audits()
    # return brief summary for sidebar
    summaries = []
    for a in audits:
        summaries.append({
            "id": a.get("id"),
            "timestamp": a.get("timestamp"),
            "target_url": a.get("target_url"),
            "site_crashes": a.get("summary", {}).get("site_crashes", False),
            "health_score": a.get("summary", {}).get("overall_health_score", 100),
            "crash_point": a.get("summary", {}).get("crash_point", "")
        })
    return summaries

@app.get("/api/audit/{audit_id}")
async def get_audit(audit_id: str):
    record = get_audit_by_id(audit_id)
    if not record:
        raise HTTPException(status_code=404, detail="Audit report not found")
    return record

@app.get("/api/export/{audit_id}")
async def export_audit(audit_id: str, format: str = Query("markdown", enum=["markdown", "json"])):
    record = get_audit_by_id(audit_id)
    if not record:
        raise HTTPException(status_code=404, detail="Audit report not found")
    
    if format == "json":
        return JSONResponse(record)
    
    # Generate Markdown report
    summary = record.get("summary", {})
    crawl = record.get("crawl_data", {})
    tree = record.get("tree_data", {}).get("nodes", {})
    crash_pinpointer = tree.get("synthesis_crash_pinpointer", {}).get("details", {})
    autofix = tree.get("synthesis_autofix", {}).get("details", {})

    md = f"""# SiteTree Bug & Crash Diagnostic Report
**Target URL**: `{record.get('target_url')}`  
**Analyzed At**: {record.get('timestamp')}  
**AI Diagnostic Engine**: {summary.get('ai_engine_used', 'Heuristic / Gemini')}  
**Overall Health Score**: {summary.get('overall_health_score')}/100  
**Site Crashes?**: {'🚨 YES - FATAL CRASH DETECTED' if summary.get('site_crashes') else '✅ NO FATAL CRASH'}

---

## 🚨 Critical Point of Failure
> {crash_pinpointer.get('point_of_failure', 'No fatal crashes detected.')}

### Execution Failure Timeline:
"""
    for step in crash_pinpointer.get("execution_timeline", []):
        md += f"- {step}\n"

    md += f"""
**Root Cause**: {crash_pinpointer.get('root_cause', 'N/A')}

---

## 🛠️ Auto-Fix & Remedy
### {autofix.get('patch_title', 'Recommended Fix')}
```javascript
{autofix.get('code_diff', '// No fix required')}
```

### Remediation Steps:
"""
    for step in autofix.get("remedy_steps", []):
        md += f"1. {step}\n"

    md += f"\n**Prevention Tip**: {autofix.get('prevention_tip', 'N/A')}\n\n---\n\n## 🌿 Multi-AI Tree Branch Findings\n"

    for node_id, node in tree.items():
        details = node.get("details", {})
        md += f"### {node.get('title')}\n"
        md += f"- **Status**: `{node.get('status')}`\n"
        if "diagnosis" in details:
            md += f"- **Diagnosis**: {details['diagnosis']}\n"
        if "issues" in details and details["issues"]:
            md += "- **Detected Issues**:\n"
            for iss in details["issues"]:
                md += f"  * {iss}\n"
        md += "\n"

    return PlainTextResponse(md, media_type="text/markdown")

# Built-in Interactive Demo Broken Site for Instant 1-Click Testing
@app.get("/api/demo-broken-site", response_class=HTMLResponse)
async def demo_broken_site():
    """
    A deliberately broken test page with real-world website crash hazards:
    1. Broken JS Bundle (404)
    2. Null reference error on missing button (#checkout-cart)
    3. Inline event handler calling an undefined function
    4. Broken image (404)
    5. Broken API endpoint call (404)
    6. Localhost leak in a public context
    """
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>E-Commerce Test Portal (Demo Broken Site)</title>
    <!-- 1. Broken External Stylesheet -->
    <link rel="stylesheet" href="/assets/non_existent_styles_404.css">
    <!-- 2. Broken External Script Bundle -->
    <script src="/assets/broken_bundle_app.js"></script>
    <style>
        body { font-family: sans-serif; padding: 2rem; background: #f8fafc; color: #1e293b; }
        .card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }
        .btn { background: #3b82f6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; margin-right: 0.5rem; }
        .btn-danger { background: #ef4444; }
        .bad-img { max-width: 100%; height: 100px; border: 1px dashed red; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Welcome to ShopMaster</h1>
        <p>This is a test deployment with intentional real-world bugs for SiteTree Debugger testing.</p>
        
        <!-- 3. Broken Image -->
        <img src="/static/non_existent_banner_image.png" alt="Promo Banner" class="bad-img">
        
        <div style="margin-top: 1rem;">
            <!-- 4. Broken Inline Handler calling undefined function -->
            <button class="btn" onclick="executeUserCheckoutProcess()">Checkout Now</button>
            <button class="btn btn-danger" onclick="triggerDeadLink()">Delete Account</button>
        </div>

        <!-- 5. Form with empty action and no submit button -->
        <form method="POST" action="" style="margin-top: 1.5rem;">
            <label>Newsletter: <input type="email" name="user_email" placeholder="you@test.com"></label>
        </form>

        <p style="margin-top: 1rem;"><a href="/non-existent-contact-us-page">Contact Support</a></p>
    </div>

    <script>
        // 6. Null Reference Trap (document.getElementById on non-existent element)
        console.log("Initializing shop script...");
        document.getElementById("missing-cart-floating-widget").addEventListener("click", function() {
            alert("Clicked cart!");
        });

        // 7. Broken API Call
        fetch("/api/non-existent-products-endpoint")
            .then(res => res.json())
            .then(data => {
                console.log("Products:", data);
            });

        // 8. Hardcoded Localhost Leak
        fetch("http://localhost:9999/api/dev-secret-keys");
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html)

# Real-Time WebSocket for Streaming Tree Analysis
@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    await websocket.accept()
    settings = load_settings()

    try:
        data = await websocket.receive_json()
        target_url = data.get("url")
        api_key = data.get("api_key") or settings.get("gemini_api_key")
        model = data.get("model") or settings.get("preferred_model", "gemini-2.5-flash")

        if not target_url:
            await websocket.send_json({"type": "error", "message": "URL is required."})
            await websocket.close()
            return

        # 1. Start Crawl Notification
        await websocket.send_json({
            "type": "crawl_started",
            "message": f"Crawling and inspecting website at {target_url}..."
        })

        crawler = SiteCrawler()
        crawl_data = await crawler.inspect_url(target_url)

        await websocket.send_json({
            "type": "crawl_completed",
            "crawl_summary": {
                "status_code": crawl_data["status_code"],
                "latency_ms": crawl_data["latency_ms"],
                "page_title": crawl_data["page_title"],
                "scripts_found": len(crawl_data["assets"]["scripts"]),
                "broken_assets": len(crawl_data["broken_assets"]),
                "runtime_hazards": len(crawl_data["runtime_hazards"])
            }
        })

        # 2. Multi-AI Tree Execution with streaming updates
        tree_engine = MultiAITreeEngine(api_key=api_key, preferred_model=model)

        async def on_node_update(node_payload: Dict[str, Any]):
            await websocket.send_json({
                "type": "node_update",
                "node": node_payload
            })

        tree_data = await tree_engine.run_tree_analysis(crawl_data, on_node_update=on_node_update)

        # 3. Save Record
        record = {
            "target_url": crawl_data["target_url"],
            "summary": tree_data["summary"],
            "crawl_data": {
                "status_code": crawl_data["status_code"],
                "latency_ms": crawl_data["latency_ms"],
                "page_title": crawl_data["page_title"],
                "broken_assets": crawl_data["broken_assets"],
                "runtime_hazards": crawl_data["runtime_hazards"],
                "api_endpoints": crawl_data["api_endpoints"],
                "forms": crawl_data["assets"]["forms"]
            },
            "tree_data": tree_data
        }
        audit_id = save_audit_record(record)
        record["id"] = audit_id

        # 4. Final Notification
        await websocket.send_json({
            "type": "audit_completed",
            "audit_id": audit_id,
            "summary": tree_data["summary"],
            "full_data": record
        })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Analysis failed: {str(e)}"
            })
        except Exception:
            pass
