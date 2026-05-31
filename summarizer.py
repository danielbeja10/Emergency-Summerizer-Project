from google import genai
from config import GEMINI_API_KEY

PROMPT_TEMPLATE = """
אתה עוזר רפואי. קרא את הרשומה הרפואית הבאה וצור סיכום רפואי מובנה בעברית לפרמדיק.

פרמט את הפלט לפי הסעיפים הבאים, כל אחד מתחיל בסמל הצבע שלו:

🟥 גורמי סיכון מיידיים
🟧 היסטוריה רפואית רלוונטית
🟩 מידע כללי

בכל מקטע השתמש בתת-קטגוריות הבאות רק אם יש מידע רלוונטי:
- אלרגיות/רגישויות:
- מחלות רקע:
- תרופות קבועות:
- הנחיות/מגבלות:

פורמט חובה — כל פריט בשורה נפרדת עם • מתחת לכותרת:
- תרופות קבועות:
  • אספירין 100מ"ג
  • מטפורמין 500מ"ג

כללים חשובים:
- אל תכתוב תת-קטגוריה אם אין לה מידע ברשומה
- אל תכתוב כותרת מקטע כלל אם אין בו אף פריט
- אסור לרשום מספר פריטים על אותה שורה
- אל תמציא עובדות — רק מה שמופיע ברשומה
- תכליתי וקצר

רשומה רפואית:
{patient_text}
"""


def build_prompt(patient_text: str) -> str:
    return PROMPT_TEMPLATE.format(patient_text=patient_text)


def summarize(patient_text: str) -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=build_prompt(patient_text),
    )
    return response.text
