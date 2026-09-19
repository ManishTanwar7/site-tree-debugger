# 🌿 SiteTree Debugger
> **Hierarchical Multi-AI Model Tree Website Bug & Crash Point Analyzer**

SiteTree Debugger is a local and cloud-ready web application that analyzes any website URL without requiring files or code uploads. It automatically crawls the target site, inspects DOM elements, script dependencies, network connectivity, and API endpoints, and orchestrates a **tree of specialized AI diagnostic models** to pinpoint the exact failure point where a website stops working.

---

## 🚀 Key Features

- 🔗 **Zero File Uploads**: Just paste any web address (e.g., `https://my-site.vercel.app` or `http://localhost:3000`).
- 🌲 **Hierarchical Multi-AI Model Tree**:
  - **Level 0 (Root)**: Orchestrator / Site Decomposer.
  - **Level 1 (Domain Branches)**:
    - *Network & Security Guardian*: HTTP response codes, redirects, SSL, CORS, and security headers.
    - *Asset & Dependency Hunter*: Detects missing/broken script files, stylesheets, images, and fonts.
    - *DOM & Interaction Auditor*: Detects missing IDs/classes, broken forms, and dead internal links.
    - *Script Runtime Crash Specialist*: Pinpoints JavaScript null dereferences (`TypeError: Cannot read properties of null`), unhandled promises, and missing global libraries (jQuery, Axios, Firebase, etc.).
    - *API & Backend Tracer*: Detects broken `fetch`/`axios` routes and flags accidental `localhost` leaks in production deployments.
  - **Level 2 (Diagnostic Synthesis)**:
    - *Crash Point Pinpointer*: Constructs a step-by-step chronological execution timeline showing exactly when and why the site crashes.
    - *Auto-Fix Synthesizer*: Produces copy-pasteable code diffs and remedial action plans.
- ⚡ **Dual-Engine Flexibility**:
  - **Autonomous Heuristic Mode**: Works 100% offline out-of-the-box with zero API keys required.
  - **Gemini Cloud Model Mode**: Optional upgrade to Gemini 2.5 Flash / Pro for neural code analysis and customized code diffs.
- 📊 **Real-Time Interactive UI**:
  - WebSocket streaming with live node-by-node updates.
  - Visual Decision Tree diagram with animated status rings.
  - Built-in **1-Click Demo Broken Site** for immediate testing.
  - History drawer & Markdown/JSON export.

---

## 🛠️ Local Installation & Run

### Prerequisites
- Python 3.10+
- Git

### 1. Clone or Open Project
```bash
cd site-tree-debugger
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Locally
```bash
python run.py
```
Or with uvicorn directly:
```bash
uvicorn backend.server:app --reload --port 8000
```

Open your browser at: **`http://127.0.0.1:8000`**

Click the **"Try Demo Broken Site"** button in the header to immediately see the multi-AI tree detect real-world website crashes and render the step-by-step point of failure!

---

## ☁️ Deploying on Render

This project is fully configured for continuous deployment on **Render**:

### Method 1: Automatic Blueprint (`render.yaml`)
1. Push this repository to your GitHub account (see instructions below).
2. Log in to [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** -> **Blueprint**.
4. Select your `site-tree-debugger` repository.
5. Render will automatically read `render.yaml` and configure the web service.
6. Click **Apply**!

### Method 2: Manual Web Service on Render
1. Log in to Render and click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure the following settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.server:app --host 0.0.0.0 --port $PORT`
4. In **Environment Variables**, optionally add:
   - `GEMINI_API_KEY`: *(Optional)* Your Google Gemini API Key.
   - `PYTHON_VERSION`: `3.11.9`
5. Click **Create Web Service**.

---

## 🐙 Deploying to GitHub

To push this project to your GitHub repository:

```bash
# 1. Initialize git repository (if not already initialized)
git init

# 2. Add all files
git add .

# 3. Commit changes
git commit -m "Initial commit: SiteTree Debugger with Multi-AI tree engine and Render config"

# 4. Create repository on GitHub (e.g. named 'site-tree-debugger')
# Then add remote and push:
git branch -M main
git remote add origin https://github.com/ManishTanwar7/site-tree-debugger.git
git push -u origin main
```

---

## 🧪 Testing the Engine

Run the built-in automated test suite:
```bash
python -m tests.test_engine
```

---

## 📄 License
MIT License &copy; 2026 Manish Tanwar
