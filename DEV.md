# Aldus — Developer Guide

## Prerequisites

Make sure you have the following installed:
- Python 3.10+
- Node.js 18+
- npm

---

## First-Time Setup

### 1. Clone the repo
```bash
git clone <repo-url>
cd Aldus
```

### 2. Set up the Python backend
```bash
cd backend
python -m venv venv --system-site-packages
```

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

Then install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Set up the Node.js renderer
```bash
cd renderer
npm install
```

### 4. Set up the React frontend *(Phase 2 — not yet)*
```bash
cd frontend
npm install
```

---

## Running the Project

### Start the backend
```bash
cd backend

# Activate venv first (Windows)
venv\Scripts\activate

# Start the FastAPI server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

### Start the frontend
```bash
cd frontend
npm run dev
```

The UI will be available at `http://localhost:5173`.

---

## Project Structure

```
Aldus/
├── backend/          # Python FastAPI backend
│   ├── venv/         # Python virtual environment (not committed)
│   ├── main.py       # API routes
│   ├── converter.py  # Markdown → HTML pipeline
│   ├── banner.py     # Banner PNG rendering
│   ├── themes/       # Theme CSS files
│   └── requirements.txt
│
├── renderer/         # Node.js Puppeteer renderer
│   ├── node_modules/ # (not committed)
│   ├── render.js     # HTML → PDF
│   └── package.json
│
├── frontend/         # React frontend (Phase 2)
│   └── ...
│
└── test/             # Test markdown files
    └── test.md
```

---

## Testing a Conversion (Phase 1 — No UI)

Once the backend is running, you can test conversion via the API directly:

```bash
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d '{"file_path": "C:/Projects/Aldus/test/test.md"}'
```

Or just run the converter directly without the server:
```bash
cd backend
venv\Scripts\activate
python converter.py C:/Projects/Aldus/test/test.md
```

---

## Deactivating the Virtual Environment

When you're done working:
```bash
deactivate
```

---

## Installing New Python Packages

Always activate the venv first, then install and update requirements:
```bash
venv\Scripts\activate
pip install <package-name>
pip freeze > requirements.txt
```
