import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import config
import database
import summarizer
import text_extractor

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET
app.config["MAX_CONTENT_LENGTH"] = config.MAX_FILE_MB * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
database.init_db()


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/summarize", methods=["POST"])
def do_summarize():
    source_name = request.form.get("source_name", "").strip()
    input_type  = request.form.get("input_type", "text")

    if not source_name:
        flash("יש להזין שם מטופל.", "error")
        return redirect(url_for("index"))

    try:
        if input_type == "pdf":
            file = request.files.get("pdf_file")
            if not file or not allowed_file(file.filename):
                flash("יש להעלות קובץ PDF תקין.", "error")
                return redirect(url_for("index"))

            filename    = secure_filename(file.filename)
            file_path   = os.path.join(config.UPLOAD_FOLDER, filename)
            file.save(file_path)
            patient_text = text_extractor.extract_from_pdf(file_path)
            source_type  = "pdf"
        else:
            patient_text = request.form.get("patient_text", "").strip()
            file_path    = None
            source_type  = "text"

        if not patient_text:
            flash("לא נמצא טקסט לסיכום.", "error")
            return redirect(url_for("index"))

        summary = summarizer.summarize(patient_text)
        database.save_summary(source_name, source_type, file_path, summary,
                              source_text=patient_text)

    except Exception as e:
        flash(f"שגיאה בעת יצירת הסיכום: {str(e)}", "error")
        return render_template("index.html",
                               prefill_name=source_name,
                               prefill_text=request.form.get("patient_text", ""),
                               prefill_tab=input_type)

    flash("הסיכום נוצר בהצלחה!", "success")
    return redirect(url_for("history"))


@app.route("/history")
def history():
    summaries = database.get_all_summaries()
    return render_template("history.html", summaries=summaries)


@app.route("/summary/<int:summary_id>")
def view_summary(summary_id):
    record = database.get_summary_by_id(summary_id)
    if not record:
        flash("הסיכום לא נמצא.", "error")
        return redirect(url_for("history"))
    return render_template("history.html", summaries=[record], single_view=True)


@app.route("/summary/<int:summary_id>/delete", methods=["POST"])
def delete_summary(summary_id):
    database.delete_summary(summary_id)
    flash("הסיכום נמחק.", "success")
    return redirect(url_for("history"))


@app.route("/summaries/delete-bulk", methods=["POST"])
def delete_summaries_bulk():
    raw_ids = request.form.getlist("ids")
    ids = [int(i) for i in raw_ids if i.isdigit()]
    count = database.delete_summaries_bulk(ids)
    flash(f"{count} סיכומים נמחקו.", "success")
    return redirect(url_for("history"))


@app.route("/summary/<int:summary_id>/source")
def view_source(summary_id):
    record = database.get_summary_by_id(summary_id)
    if not record:
        flash("הסיכום לא נמצא.", "error")
        return redirect(url_for("history"))

    if record["source_type"] == "pdf" and record.get("file_path"):
        path = record["file_path"]
        if os.path.exists(path):
            return send_file(path, mimetype="application/pdf")
        flash("קובץ ה-PDF לא נמצא בשרת.", "error")
        return redirect(url_for("history"))

    source_text = record.get("source_text")
    if not source_text:
        flash("הטקסט המקורי לא נשמר עבור סיכום זה.", "error")
        return redirect(url_for("history"))

    return render_template("source.html", record=record, source_text=source_text)


DEMO_SUMMARY = """🟥 גורמי סיכון מיידיים
- אלרגיות/רגישויות:
  • פניצילין (תגובה אנפילקטית מתועדת)
  • סולפנאמידים
- הנחיות/מגבלות:
  • הנחיית DNR חתומה ובתוקף
  • אין לתת NSAIDs (אי-ספיקת כליות כרונית)
  • נוטל וורפרין — סיכון דימום מוגבר, לבדוק INR לפני פרוצדורה

🟧 היסטוריה רפואית רלוונטית
- מחלות רקע:
  • סוכרת סוג 2 (10 שנים)
  • מחלת לב איסכמית — סטנט ב-2019
  • יתר לחץ דם
  • פרפור פרוזדורים כרוני
  • אי-ספיקת כליות כרונית שלב 3
- תרופות קבועות:
  • וורפרין 5 מ"ג
  • מטפורמין 1000 מ"ג פעמיים ביום
  • אמלודיפין 10 מ"ג
  • פורוסמיד 40 מ"ג
  • אטורבסטטין 40 מ"ג
  • אספירין 100 מ"ג

🟩 מידע כללי
- מחלות רקע:
  • ירידה תפקודית מתקדמת — תלוי בסיוע חלקי לפעילות יומיומית
- הנחיות/מגבלות:
  • יפוי כוח: רחל לוי (בת) — 050-1234567"""

DEMO_RECORD = """תיק מטופל — קופת חולים מכבי
מספר תיק: 4821-לד | תאריך פתיחת תיק: 14/03/1989
רופא משפחה: ד"ר אבי שפירא | מרפאה: סניף רחובות מרכז

שם: יוסף לוי | גיל: 68 | ת"ז: 043XXXXXX
כתובת: רחוב הרצל 42, רחובות | טלפון: 08-944XXXX
מצב משפחתי: נשוי (חנה לוי) | ילדים: 3 (רחל, דוד, מיכל)
עיסוק: גמלאי — לשעבר מנהל מחסן בחברת שיכון ובינוי
תחביבים: שחמט, גינון, צפייה בכדורגל (אוהד מכבי ת"א)

--- רקע כללי ---
עלה לישראל מרומניה ב-1971. דובר עברית, רומנית ויידיש. השכלה: תיכונית.
ביקור אחרון במרפאה: 03/04/2026 — בדיקת שגרה, תלונות על עייפות קלה.
חיסונים: שפעת (אוקטובר 2025), פנאומוקוק (2023), קורונה × 4.
בדיקת דם אחרונה (פברואר 2026): סוכר 138, HbA1c 7.4%, קראטינין 1.8, INR 2.3 — תקין לטווח מטרה.

--- מחלות רקע ---
סוכרת סוג 2 (אובחן 2014, טיפול תרופתי בלבד).
מחלת לב איסכמית — אוטם שריר הלב 2018, הותקן סטנט בעורק יורד קדמי (LAD) ב-2019.
יתר לחץ דם (מאובחן מ-2010, מאוזן תחת טיפול).
פרפור פרוזדורים כרוני — מנוטר אחת לשלושה חודשים.
אי-ספיקת כליות כרונית שלב 3 (GFR 42).
בקע מפשעתי ימני — ניתוח תיקון ב-2015, ללא תלונות מאז.
היסטוריה של כאבי גב תחתון (בלט דיסק L4-L5, 2009) — מטופל פיזיותרפיה, כיום ללא מגבלה משמעותית.

--- אלרגיות ורגישויות ---
פניצילין — תגובה אנפילקטית מתועדת (1998): בצקת, לחץ דם נמוך, אשפוז.
סולפנאמידים — פריחה ועלייה באנזימי כבד.
אגוזי עץ — אי נוחות קלה בבטן (לא אנפילקסיס, לא מתועד רשמית).

--- תרופות קבועות ---
וורפרין 5מ"ג פעם ביום (בוקר) — לפרפור פרוזדורים.
מטפורמין 1000מ"ג פעמיים ביום (בוקר וערב) — לסוכרת.
אמלודיפין 10מ"ג פעם ביום — ליתר לחץ דם.
פורוסמיד 40מ"ג פעם ביום (בוקר) — לאגירת נוזלים.
אטורבסטטין 40מ"ג פעם ביום (לילה) — לשומני דם.
אספירין 100מ"ג פעם ביום — לאחר אוטם.
ויטמין D 1000 יחב"ל פעם ביום — לפי המלצת רופא.
אומפרזול 20מ"ג — לפי הצורך לצרבות (לא קבוע).

--- הנחיות רפואיות ---
הנחיית DNR (אל תחיה) חתומה ב-12/01/2025 ומאוחסנת בתיק + העתק אצל הבת רחל.
אין לתת NSAIDs (איבופרופן, נפרוקסן וכד') — אי-ספיקת כליות כרונית.
לבדוק INR לפני כל פרוצדורה פולשנית — נוטל וורפרין, סיכון דימום.
הגבלת נוזלים: עד 1.5 ליטר ביום (בשל אס"כ).

--- מצב תפקודי וסוציאלי ---
ירידה תפקודית מתקדמת בחצי שנה האחרונה — עלייה במדרגות קשה, עייפות מהירה.
תלוי בסיוע חלקי בפעילות יומיומית (קניות, ניקיון). אינו תלוי באכילה ורחצה.
מתגורר עם אשתו. בת רחל מגיעה 3 פעמים בשבוע.
אין עישון (הפסיק 1995). שתיית אלכוהול: מדי פעם, כוס יין בשבת.
ביקר בפורטוגל, אוגוסט 2025 — ללא אירועים רפואיים.

--- יפוי כוח ---
בת: רחל לוי — 050-1234567 (מיופת כוח לכל החלטה רפואית)
אשה: חנה לוי — 054-987XXXX"""


@app.route("/demo", methods=["POST"])
def run_demo():
    database.clean_demo_duplicates()
    if database.demo_exists():
        database.update_demo_entry(DEMO_SUMMARY, DEMO_RECORD)
        flash("סיכום הדמו כבר קיים בהיסטוריה.", "info")
    else:
        database.save_summary("יוסף לוי (דמו)", "text", None, DEMO_SUMMARY,
                              source_text=DEMO_RECORD)
        flash("סיכום דמו נוצר — זה מה שהמוצר מייצר מהרשומה הרפואית למטה.", "success")
    return redirect(url_for("history"))


if __name__ == "__main__":
    app.run(debug=True)
