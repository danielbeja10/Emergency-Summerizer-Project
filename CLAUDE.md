# Emergency Summarizer — CLAUDE.md

## Project Overview
A Flask web application that takes a patient's medical record (text or PDF) and uses Google Gemini to generate a structured Hebrew summary for paramedics. The summary is color-coded by urgency (🟥🟧🟩) and stored in a local SQLite database.

## Stack
- **Backend:** Python + Flask
- **AI:** Google Gemini 1.5 Flash (`google-generativeai`)
- **Database:** SQLite via raw `sqlite3` (no ORM)
- **Frontend:** Jinja2 templates + vanilla CSS/JS, Hebrew RTL

## Project Structure
```
app.py             # Flask routes — thin controllers only
config.py          # All config from env vars (AWS-ready)
database.py        # SQLite CRUD: init_db, save_summary, get_all_summaries, get_summary_by_id
summarizer.py      # Gemini API call + Hebrew prompt template
text_extractor.py  # PDF-to-text (PyMuPDF) + text cleaning
templates/
  base.html        # RTL Hebrew layout shell + nav
  index.html       # Submit form (text / PDF tabs)
  history.html     # Summary history + inline view
static/
  style.css        # Dark medical theme, RTL, colored sections
  main.js          # Tab toggle, spinner, summary color renderer
uploads/           # Uploaded PDFs (gitignored)
```

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Start the server
python app.py
# Open http://localhost:5000
```

## Environment Variables (.env)
| Variable        | Default        | Description                    |
|----------------|---------------|--------------------------------|
| GEMINI_API_KEY  | (required)     | Google AI Studio API key       |
| DATABASE_PATH   | summaries.db   | SQLite file path               |
| UPLOAD_FOLDER   | uploads        | Directory for uploaded PDFs    |
| MAX_FILE_MB     | 10             | Max upload size in MB          |
| FLASK_SECRET    | dev-secret...  | Flask session secret key       |

Get a free Gemini API key at: https://aistudio.google.com/

## Database Schema
```sql
CREATE TABLE summaries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT    NOT NULL,
    source_type TEXT    NOT NULL,  -- 'text' or 'pdf'
    file_path   TEXT,              -- path in uploads/, NULL for text input
    summary     TEXT    NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## AWS Deployment (Phase 2)
The app is AWS-ready by design — all config via env vars, runs with gunicorn:
```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 app:app
```
See the plan file for full EC2 deployment steps.

## Key Design Decisions
- No ORM — raw `sqlite3` is simpler to explain in interviews
- No React/npm — plain HTML/CSS/JS served by Flask, zero build step
- RTL Hebrew UI — authentic to the Israeli medical use case
- All secrets in env vars — portable between local and AWS
