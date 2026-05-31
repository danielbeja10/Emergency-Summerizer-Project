# 🚑 Emergency Summarizer

A Flask web application that takes a patient's medical record (text or PDF) and uses **Google Gemini AI** to generate a structured, color-coded Hebrew summary for paramedics — in seconds.

> **Inspired by a real event:** when my grandfather needed urgent care, the paramedic had to ask him many critical questions before starting treatment. This tool aims to make that process faster and smarter.

---

## ✨ Features

- **AI-powered summarization** — sends the medical record to Gemini and gets back a structured Hebrew summary
- **Color-coded urgency sections:**
  - 🟥 Immediate risk factors (allergies, DNR, anticoagulants)
  - 🟧 Relevant medical history (background conditions, medications)
  - 🟩 General info (functional status, family contact)
- **PDF & text input** — paste text directly or upload a PDF
- **Summary history** — all summaries stored in a local SQLite database
- **View source** — see the original medical record used to generate each summary
- **Bulk delete** — select multiple summaries and delete them at once
- **Live demo** — one-click demo with a realistic patient record (no API key needed to preview)
- **RTL Hebrew UI** — designed for Israeli medical context

---

## 🖥️ Demo

Press **"הפעל דמו"** on the home page to see the app in action without an API key.

The demo uses a realistic (fictional) patient record with irrelevant noise — administrative details, hobbies, old injuries — to show how the AI filters and extracts only what a paramedic needs in the field.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + Flask |
| AI | Google Gemini 2.5 Flash |
| Database | SQLite (raw `sqlite3`, no ORM) |
| Frontend | Jinja2 templates + vanilla CSS/JS |
| PDF extraction | pypdf |
| UI | Hebrew RTL, dark medical theme |

---

## 🚀 How to Run

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Set up environment**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Get a free Gemini API key at: https://aistudio.google.com/

**3. Start the server**
```bash
python app.py
```

Open **http://localhost:5000**

---

## 🗂️ Project Structure

```
app.py             # Flask routes — thin controllers only
config.py          # All config from environment variables
database.py        # SQLite CRUD: init, save, get, delete
summarizer.py      # Gemini API call + Hebrew prompt template
text_extractor.py  # PDF-to-text extraction + cleaning
templates/
  base.html        # RTL Hebrew layout shell + nav
  index.html       # Submit form (text / PDF tabs) + demo banner
  history.html     # Summary history with bulk select & delete
  source.html      # View original medical record
static/
  style.css        # Dark medical theme, RTL, color-coded sections
  main.js          # Tab toggle, spinner, summary renderer, bulk select
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | *(required)* | Google AI Studio API key |
| `DATABASE_PATH` | `summaries.db` | SQLite file path |
| `UPLOAD_FOLDER` | `uploads` | Directory for uploaded PDFs |
| `MAX_FILE_MB` | `10` | Max upload size in MB |
| `FLASK_SECRET` | `dev-secret...` | Flask session secret key |

---

## 🗄️ Database Schema

```sql
CREATE TABLE summaries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT    NOT NULL,
    source_type TEXT    NOT NULL,  -- 'text' or 'pdf'
    file_path   TEXT,              -- path in uploads/, NULL for text input
    summary     TEXT    NOT NULL,
    source_text TEXT,              -- original input text
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔮 Potential Future Improvements

- **AWS deployment** — the app is cloud-ready by design (all config via env vars, runs with gunicorn)
- **Authentication** — role-based access for medical staff
- **Export to PDF** — generate a printable summary card
- **Mobile-optimized view** — for use on phones inside an ambulance
- **Audit log** — track who accessed which patient record

---

*Developed with the assistance of [Claude](https://claude.ai) (Anthropic)*
