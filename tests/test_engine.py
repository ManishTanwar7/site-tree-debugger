"""
Automated unit tests for SiteTree Debugger Crawler and AI Tree Engine.
"""

import asyncio
from backend.crawler import SiteCrawler
from backend.ai_tree import MultiAITreeEngine

async def run_test():
    print("Testing SiteCrawler with sample mock HTML...")
    crawler = SiteCrawler()

    # Test JS scan logic directly with synthetic HTML & JS
    existing_ids = {"app-root", "submit-btn"}
    existing_classes = {"btn", "primary"}
    
    # Intentionally broken JS: document.getElementById('non_existent_btn').addEventListener...
    test_js = [
        {
            "source": "broken_inline_script",
            "code": """
                console.log("Starting app");
                document.getElementById('non_existent_checkout_btn').addEventListener('click', function() {
                    alert('pay');
                });
                fetch('/api/missing-cart-endpoint').then(res => res.json());
            """
        }
    ]

    hazards = crawler._scan_js_for_crashes(test_js, existing_ids, existing_classes, "https://example.com")
    print(f"Hazards detected: {len(hazards)}")
    assert len(hazards) >= 1, "Should have detected at least 1 runtime hazard"
    assert any(h["type"] == "NullReferenceCrash" for h in hazards), "Should detect NullReferenceCrash"
    print("  [SUCCESS] Detected NullReferenceCrash on #non_existent_checkout_btn!")

    # Test AI Tree Engine with synthetic crawl data
    print("Testing Multi-AI Tree Engine...")
    tree_engine = MultiAITreeEngine()

    mock_crawl_data = {
        "target_url": "https://test-buggy-store.com",
        "domain": "test-buggy-store.com",
        "scheme": "https",
        "status_code": 200,
        "latency_ms": 180,
        "headers": {"content-type": "text/html"},
        "page_title": "Test Buggy Store",
        "html_size": 2048,
        "dom_stats": {"total_elements": 24, "total_ids": 2, "total_classes": 3, "has_viewport": True},
        "assets": {"scripts": [{"url": "https://test.com/app.js"}], "stylesheets": [], "forms": []},
        "broken_assets": [{"url": "https://test.com/app.js", "kind": "script", "status": 404, "error": "HTTP 404"}],
        "runtime_hazards": hazards,
        "api_endpoints": [{"raw_path": "/api/missing-cart-endpoint", "url": "https://test.com/api/missing-cart-endpoint", "is_internal": True, "status": 404}]
    }

    tree_results = await tree_engine.run_tree_analysis(mock_crawl_data)
    
    assert "root_orchestrator" in tree_results["nodes"], "Root orchestrator must be present"
    assert "w11_script_bundle_404" in tree_results["nodes"], "Worker 11 (script bundle) must be present"
    assert "w21_null_deref" in tree_results["nodes"], "Worker 21 (null deref) must be present"
    assert "synthesis_crash_pinpointer" in tree_results["nodes"], "Crash pinpointer must be present"
    assert "synthesis_autofix" in tree_results["nodes"], "Autofix synthesizer must be present"

    summary = tree_results["summary"]
    print(f"  Summary: site_crashes={summary['site_crashes']}")
    print(f"  Failure Point: {summary['crash_point']}")
    print(f"  Total AI Workers Evaluated: {summary['total_ai_workers']}")
    assert summary["site_crashes"] is True, "Site should be flagged as crashing"
    assert summary["total_ai_workers"] == 50, "Should evaluate exactly 50 AI worker parameters"
    print("  [SUCCESS] 50 AI Worker Parameters successfully analyzed website and pinpointed crash!")
    print("ALL 50-AI TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_test())
