# מסך חכם — Smart Screen Manager

![banner](docs/banner.svg)

**גרסה 1.3.0** | Windows 10/11 | Python 3.8+ | PyQt6

ניהול זמן מסך למחשב: כיבוי מסך, התראות והשהיות לפי משימות — עם שליטה מלאה על התנהגות הכיבוי, כולל כיבוי בכפייה, ניסיונות חוזרים ותזמון במדויק.

---

## 📥 הורדה והתקנה

| קובץ | קישור |
|---|---|
| `Masach-Chacham.exe` | [הורדה ישירה](https://github.com/chezy734-ship-it/masach-chacham/raw/main/dist/Masach-Chacham.exe) |

> חלצו והריצו. לבנייה מקוד — התקינו תלויות והריצו:

```bash
pip install PyQt6 pillow pystray
python masach_chacham.py
```

לבניית EXE: לחצו פעמיים על `build_exe.bat`.

---

## ✨ מה בגרסה 1.3

| # | שינוי |
|---|---|
| 1 | גרסה 1.3.0 בכל מקום |
| 2 | **סרגל צידי** — ימני בעברית, שמאלי באנגלית |
| 3 | **הגדרות מודעה + כיבוי מחדש** — בתוך כל משימה בנפרד |
| 4 | **כיבוי בכפייה** (`force_off`) — גובר על פעילות משתמש |
| 5 | **ניסיון חוזר** לכיבוי אם המשתמש היה פעיל |
| 6 | כל ההגדרות קיימות גם בלשונית טיימר |
| 7 | **`screen_off` משתמש ב-`PostMessageW`** — לא מכניס למצב שינה |
| 8 | זמן הודעה ו-`reoff` בפורמט דקות:שניות (MM:SS) |

---

## ⚙️ שדות הגדרה לכל משימה

| שדה | תפקיד |
|---|---|
| `notif` | הצגת הודעה לפני כיבוי (MM:SS לפני) |
| `force_off` | כיבוי בכפייה (גובר על פעילות המשתמש) |
| `reoff` | כיבוי מחדש לאחר פעילות (MM:SS) |
| `retry_off` | ניסיון חוזר אחרי N שניות (מוסתר כש-`force_off` מסומן) |

---

## 🔨 בנייה ל-EXE

לחצו פעמיים על `build_exe.bat`, או ידנית:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "Masach-Chacham" masach_chacham.py
```

הקובץ ייווצר ב-`dist\Masach-Chacham.exe`.
