"""
SiteTree Debugger Launcher Script
Runs the FastAPI server locally or in production.
"""

import os
import sys
import uvicorn

def main():
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print("=" * 65)
    print(">> SiteTree Debugger: Multi-AI Website Bug & Crash Analyzer")
    print(f">> Running server at: http://127.0.0.1:{port}")
    print(f">> Public/LAN Host:    http://{host}:{port}")
    print("=" * 65)
    uvicorn.run("backend.server:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
