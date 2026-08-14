"""
מסך חכם – Smart Screen Manager
Version 1.3.0  |  Windows 10 & 11
UI: PyQt6  |  Python 3.10+
"""

import sys, os, json, time, threading, datetime, hashlib, uuid, subprocess, ctypes
IS_WINDOWS = sys.platform == "win32"
if IS_WINDOWS:
    import winreg

VERSION     = "1.3.0"
APP_NAME    = "מסך חכם"
APP_NAME_EN = "Smart Screen"
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".masach_chacham_v1.json")

DAYS_HE = ["ראשון","שני","שלישי","רביעי","חמישי","שישי","שבת"]
DAYS_EN = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]

# ══════════════════════════════════════════════════════════════════════════════
#  SCREEN CONTROL
#  screen_off uses PostMessage (non-blocking) so it never triggers sleep.
#  We also call SetThreadExecutionState to prevent Windows sleep while running.
# ══════════════════════════════════════════════════════════════════════════════
def _prevent_sleep():
    """Tell Windows: don't sleep – only allow display off."""
    if IS_WINDOWS:
        ES_CONTINUOUS       = 0x80000000
        ES_SYSTEM_REQUIRED  = 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)

def screen_off(force: bool = False):
    """
    Turn off monitor ONLY. Never puts the system to sleep.
    force=True: use PostMessageW so Windows can't intercept and go to sleep instead.
    """
    if not IS_WINDOWS:
        return
    try:
        u32 = ctypes.windll.user32
        # SC_MONITORPOWER = 0xF170,  lParam 2 = off
        # Use PostMessageW (async) – SendMessageW can sometimes trigger sleep hooks
        u32.PostMessageW(0xFFFF, 0x0112, 0xF170, 2)
        if force:
            # Additional: directly power-off via display device
            # HWND_BROADCAST with PostMessage is safest
            u32.PostMessageW(u32.GetDesktopWindow(), 0x0112, 0xF170, 2)
    except Exception as e:
        print(f"[screen_off] {e}")

def screen_on():
    """Wake the monitor via mouse move + key press + power-on message."""
    if not IS_WINDOWS:
        return
    try:
        u32 = ctypes.windll.user32
        u32.PostMessageW(0xFFFF, 0x0112, 0xF170, -1)
        time.sleep(0.05)
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT()
        u32.GetCursorPos(ctypes.byref(pt))
        u32.SetCursorPos(pt.x + 1, pt.y + 1)
        time.sleep(0.05)
        u32.SetCursorPos(pt.x, pt.y)
        u32.keybd_event(0x10, 0, 0, 0)
        time.sleep(0.02)
        u32.keybd_event(0x10, 0, 0x0002, 0)
        u32.mouse_event(0x0001, 0, 0, 0, 0)
    except Exception as e:
        print(f"[screen_on] {e}")

def open_display_settings():
    if IS_WINDOWS:
        try:    subprocess.Popen("start ms-settings:display", shell=True)
        except: subprocess.Popen("control desk.cpl", shell=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TRANSLATIONS
# ══════════════════════════════════════════════════════════════════════════════
T = {
"he": {
    "app_name":"מסך חכם",
    "nav_tasks":"משימות","nav_timer":"טיימר","nav_settings":"הגדרות","nav_about":"אודות",
    "add_task":"הוסף משימה","edit":"ערוך","delete":"מחק","enable":"הפעל","disable":"השבת",
    "no_tasks":"אין משימות מוגדרות עדיין.\nלחץ על ״הוסף משימה״ כדי להתחיל.",
    "task_type":"סוג משימה","weekly":"שבועי","by_date":"לפי תאריך","timer_kind":"טיימר",
    "action":"פעולה","act_off":"כיבוי מסך","act_on":"הדלקת מסך","act_both":"כיבוי + הדלקה",
    "days":"ימים","time_off":"שעת כיבוי","time_on":"שעת הדלקה",
    "date_lbl":"תאריך","save":"שמור","cancel":"ביטול",
    "dur":"משך הטיימר","timer_act":"פעולת הטיימר",
    "hours":"שעות","minutes":"דקות","seconds":"שניות",
    "start":"▶  הפעל","stop":"⏹  עצור","countdown":"ספירה לאחור",
    "disp_btn":"הגדרות תצוגה Windows","disp_icon":"🖥",
    "lang_lbl":"שפה","startup_chk":"הפעל עם Windows",
    "pw_lbl":"הגנת סיסמה","set_pw":"הגדר סיסמה","rem_pw":"הסר סיסמה",
    "pw_set":"סיסמה מוגדרת ✓","pw_none":"ללא סיסמה",
    "enter_pw":"הכנס סיסמה","wrong_pw":"סיסמה שגויה!",
    "confirm_del":"למחוק משימה זו?","task_name":"שם משימה (אופציונלי)",
    "screen_on_lbl":"מסך דלוק","screen_off_lbl":"מסך כבוי",
    "man_off":"כבה מסך","man_on":"הדלק מסך",
    "open":"פתח","quit":"סגור לחלוטין","tray_tip":"מסך חכם פועל ברקע",
    "all_days":"כל הימים",
    "timer_done_off":"המסך כובה ✓","timer_done_on":"המסך הודלק ✓",
    "ver":"גרסה","days_list":DAYS_HE,
    "notif_msg":"המסך יכבה בעוד {n}",
    "appearance":"מראה","dark_mode":"מצב כהה","light_mode":"מצב בהיר",
    "general":"כללי","security":"אבטחה","display":"תצוגה",
    "about_title":"אודות מסך חכם",
    "dlg_title_add":"הוסף משימה","dlg_title_edit":"ערוך משימה",
    "task_name_ph":"לדוגמה: כיבוי לילה",
    # Per-task notification
    "notif_grp":"הודעה לפני כיבוי",
    "notif_chk":"הצג הודעה לפני כיבוי",
    "notif_before":"הצג לפני כיבוי (דד:שש)",
    # Per-task reoff
    "reoff_grp":"כיבוי מחדש לאחר פעילות",
    "reoff_chk":"כבה מחדש לאחר פעילות",
    "reoff_delay":"זמן עד כיבוי מחדש (דד:שש)",
    # Force off
    "force_grp":"כיבוי בכפיה",
    "force_chk":"כיבוי בכפיה (גובר על פעילות משתמש)",
    # Retry off
    "retry_grp":"ניסיון חוזר לכיבוי",
    "retry_chk":"נסה שוב לכבות לאחר כישלון",
    "retry_secs":"שניות עד ניסיון חוזר",
},
"en": {
    "app_name":"Smart Screen",
    "nav_tasks":"Tasks","nav_timer":"Timer","nav_settings":"Settings","nav_about":"About",
    "add_task":"Add Task","edit":"Edit","delete":"Delete","enable":"Enable","disable":"Disable",
    "no_tasks":"No tasks defined yet.\nClick 'Add Task' to get started.",
    "task_type":"Task Type","weekly":"Weekly","by_date":"By Date","timer_kind":"Timer",
    "action":"Action","act_off":"Turn Off Screen","act_on":"Turn On Screen","act_both":"Off + On",
    "days":"Days","time_off":"Off Time","time_on":"On Time",
    "date_lbl":"Date","save":"Save","cancel":"Cancel",
    "dur":"Timer Duration","timer_act":"Timer Action",
    "hours":"Hours","minutes":"Minutes","seconds":"Seconds",
    "start":"▶  Start","stop":"⏹  Stop","countdown":"Countdown",
    "disp_btn":"Windows Display Settings","disp_icon":"🖥",
    "lang_lbl":"Language","startup_chk":"Run with Windows",
    "pw_lbl":"Password Protection","set_pw":"Set Password","rem_pw":"Remove Password",
    "pw_set":"Password set ✓","pw_none":"No password set",
    "enter_pw":"Enter password","wrong_pw":"Wrong password!",
    "confirm_del":"Delete this task?","task_name":"Task name (optional)",
    "screen_on_lbl":"Screen ON","screen_off_lbl":"Screen OFF",
    "man_off":"Turn Off Screen","man_on":"Turn On Screen",
    "open":"Open","quit":"Quit","tray_tip":"Smart Screen running in background",
    "all_days":"All days",
    "timer_done_off":"Screen turned off ✓","timer_done_on":"Screen turned on ✓",
    "ver":"Version","days_list":DAYS_EN,
    "notif_msg":"Screen will turn off in {n}",
    "appearance":"Appearance","dark_mode":"Dark Mode","light_mode":"Light Mode",
    "general":"General","security":"Security","display":"Display",
    "about_title":"About Smart Screen",
    "dlg_title_add":"Add Task","dlg_title_edit":"Edit Task",
    "task_name_ph":"e.g. Night shutdown",
    "notif_grp":"Notification Before Off",
    "notif_chk":"Show notification before screen off",
    "notif_before":"Show before off (MM:SS)",
    "reoff_grp":"Re-Off After Activity",
    "reoff_chk":"Re-off screen after user activity",
    "reoff_delay":"Delay until re-off (MM:SS)",
    "force_grp":"Force Off",
    "force_chk":"Force off (overrides user activity)",
    "retry_grp":"Retry Off on Failure",
    "retry_chk":"Retry screen off if user was active",
    "retry_secs":"Seconds until retry",
},
}

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════════════════
class Config:
    DEFAULTS = dict(language="he", dark=True, startup=True, pw_hash=None, tasks=[])
    def __init__(self):
        self.d = dict(self.DEFAULTS)
        try:
            if os.path.exists(CONFIG_FILE):
                self.d.update(json.load(open(CONFIG_FILE, encoding="utf-8")))
        except: pass
    def save(self):
        try: json.dump(self.d, open(CONFIG_FILE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
        except: pass
    def get(self, k, default=None): return self.d.get(k, default)
    def set(self, k, v): self.d[k]=v; self.save()
    def apply_startup(self, enabled):
        if not IS_WINDOWS: return
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            if enabled:
                winreg.SetValueEx(key, APP_NAME_EN, 0, winreg.REG_SZ,
                    f'"{sys.executable}" "{os.path.abspath(__file__)}"')
            else:
                try: winreg.DeleteValue(key, APP_NAME_EN)
                except: pass
            winreg.CloseKey(key)
        except: pass
    def hash_pw(self, pw): return hashlib.sha256(pw.encode()).hexdigest()
    def verify_pw(self, pw):
        h = self.get("pw_hash")
        return True if not h else self.hash_pw(pw) == h

# ══════════════════════════════════════════════════════════════════════════════
#  TASK MODEL  – per-task notification + reoff + force + retry
# ══════════════════════════════════════════════════════════════════════════════
class Task:
    WEEKLY="weekly"; DATE="date"; TIMER="timer"
    OFF="off"; ON="on"; BOTH="both"
    def __init__(self, d=None):
        d = d or {}
        self.id       = d.get("id", str(uuid.uuid4())[:8])
        self.enabled  = d.get("enabled", True)
        self.kind     = d.get("kind", self.WEEKLY)
        self.action   = d.get("action", self.OFF)
        self.name     = d.get("name", "")
        self.days     = d.get("days", [])
        self.off_h    = d.get("off_h",22); self.off_m=d.get("off_m",0);  self.off_s=d.get("off_s",0)
        self.on_h     = d.get("on_h",7);  self.on_m=d.get("on_m",0);    self.on_s=d.get("on_s",0)
        self.date_str = d.get("date_str", str(datetime.date.today()))
        self.date_h   = d.get("date_h",22); self.date_m=d.get("date_m",0); self.date_s=d.get("date_s",0)
        self.t_hours  = d.get("t_hours",0); self.t_mins=d.get("t_mins",30); self.t_secs=d.get("t_secs",0)
        self.t_action = d.get("t_action", self.OFF)
        self.t_start  = d.get("t_start", "")   # ISO של תחילת הספירה (טיימר)
        # ── Per-task options ──
        self.notif         = d.get("notif", False)          # show notification?
        self.notif_m       = d.get("notif_m", 1)            # minutes before
        self.notif_s       = d.get("notif_s", 0)            # seconds before
        self.reoff         = d.get("reoff", False)          # re-off after activity?
        self.reoff_m       = d.get("reoff_m", 0)            # re-off delay minutes
        self.reoff_s       = d.get("reoff_s", 30)           # re-off delay seconds
        self.force_off     = d.get("force_off", False)      # force off (overrides activity)
        self.retry_off     = d.get("retry_off", False)      # retry if user was active
        self.retry_secs    = d.get("retry_secs", 15)        # retry after N seconds
    def to_dict(self): return self.__dict__
    def label(self, lang):
        t   = T[lang]
        act = {self.OFF:t["act_off"], self.ON:t["act_on"], self.BOTH:t["act_both"]}[self.action]
        sfx = f"  [{self.name}]" if self.name else ""
        opts = []
        if self.force_off:   opts.append("⚡" if lang=="he" else "⚡force")
        if self.notif:       opts.append("🔔")
        if self.reoff:       opts.append("🔄")
        if self.retry_off and not self.force_off: opts.append("↩️")
        tag = ("  " + " ".join(opts)) if opts else ""
        if self.kind == self.TIMER:
            a = t["act_off"] if self.t_action==self.OFF else t["act_on"]
            parts=[f"{self.t_hours}h" if self.t_hours else "",
                   f"{self.t_mins}m" if self.t_mins else "",
                   f"{self.t_secs}s" if self.t_secs else ""]
            return f"⏱  {' '.join(p for p in parts if p) or '0s'}  →  {a}{sfx}{tag}"
        if self.kind == self.DATE:
            return f"📅  {self.date_str}  {self.date_h:02d}:{self.date_m:02d}:{self.date_s:02d}  →  {act}{sfx}{tag}"
        dn = ", ".join(t["days_list"][d] for d in self.days) if self.days else t["all_days"]
        s = f"🗓  {dn}  {self.off_h:02d}:{self.off_m:02d}:{self.off_s:02d}  →  {act}"
        if self.action==self.BOTH:
            s += f"  /  {self.on_h:02d}:{self.on_m:02d}:{self.on_s:02d}"
        return s + sfx + tag

# ══════════════════════════════════════════════════════════════════════════════
#  SCHEDULER
# ══════════════════════════════════════════════════════════════════════════════
class Scheduler:
    def __init__(self, cfg, cb):
        self.cfg=cfg; self.cb=cb; self._run=False; self._fired=set()
    def start(self):
        _prevent_sleep()
        self._run=True
        threading.Thread(target=self._loop, daemon=True).start()
    def stop(self): self._run=False
    def _loop(self):
        last_day=None
        while self._run:
            now=datetime.datetime.now(); today=now.date()
            if today!=last_day: self._fired.clear(); last_day=today
            for d in self.cfg.get("tasks",[]):
                task=Task(d)
                if task.enabled: self._check(task, now)
            time.sleep(5)
    @staticmethod
    def _py2sun(wd): return (wd+1)%7

    def _fire(self, key, action, task: Task):
        if key in self._fired: return
        self._fired.add(key)
        def do():
            # Notification before off
            if action in (Task.OFF, Task.BOTH) and task.notif:
                delay = task.notif_m*60 + task.notif_s
                if delay > 0:
                    dur_str = f"{task.notif_m:02d}:{task.notif_s:02d}"
                    self.cb("notify", task, dur_str)
                    time.sleep(delay)
            act = action if action != Task.BOTH else Task.OFF
            self._do_off_or_on(act, task)
            # If BOTH: also schedule the ON
            if action == Task.BOTH:
                pass  # on-time is handled separately in _check
        threading.Thread(target=do, daemon=True).start()

    def _do_off_or_on(self, action, task: Task):
        if action == Task.ON:
            screen_on()
            self.cb("on", task, None)
            return
        # action == OFF
        self._do_screen_off(task)

    def _do_screen_off(self, task: Task):
        """Execute screen-off with force/retry/reoff logic."""
        screen_off(force=task.force_off)
        self.cb("off", task, None)
        # re-off after activity
        if task.reoff:
            delay = task.reoff_m*60 + task.reoff_s
            def reoff_later():
                time.sleep(max(delay, 3))
                screen_off(force=task.force_off)
            threading.Thread(target=reoff_later, daemon=True).start()
        # retry on failure (only if not force)
        if task.retry_off and not task.force_off:
            def retry_later():
                time.sleep(max(task.retry_secs, 3))
                screen_off(force=False)
            threading.Thread(target=retry_later, daemon=True).start()

    def _check(self, task: Task, now: datetime.datetime):
        if not task.enabled:
            return
        sun=self._py2sun(now.weekday())
        ss=now.second//5*5
        if task.kind==Task.WEEKLY:
            if (not task.days) or (sun in task.days):
                if task.action in(Task.OFF,Task.BOTH):
                    if now.hour==task.off_h and now.minute==task.off_m and ss==task.off_s//5*5:
                        self._fire(f"{task.id}_off_{now.date()}_{task.off_h}:{task.off_m}",Task.OFF,task)
                if task.action in(Task.ON,Task.BOTH):
                    if now.hour==task.on_h and now.minute==task.on_m and ss==task.on_s//5*5:
                        self._fire(f"{task.id}_on_{now.date()}_{task.on_h}:{task.on_m}",Task.ON,task)
        elif task.kind==Task.DATE:
            try:
                d=datetime.date.fromisoformat(task.date_str)
                if d==now.date() and now.hour==task.date_h and now.minute==task.date_m and ss==task.date_s//5*5:
                    self._fire(f"{task.id}_date_{task.date_str}",task.action,task)
            except: pass
        elif task.kind==Task.TIMER:
            try:
                # תחילת ספירה: נשמרה בשמירת המשימה; למשימות ישנות בלי t_start —
                # הספירה מתחילה מהפעם הראשונה שהסכדול רואה אותן.
                if not task.t_start:
                    task.t_start=now.isoformat()
                    for d in self.cfg.get("tasks",[]):
                        if d.get("id")==task.id:
                            d["t_start"]=task.t_start; self.cfg.save(); break
                start=datetime.datetime.fromisoformat(task.t_start)
                target=start+datetime.timedelta(
                    hours=task.t_hours, minutes=task.t_mins, seconds=task.t_secs)
                if now>=target:
                    self._fire(f"{task.id}_timer_{now.date()}",task.t_action,task)
                    # טיימר הוא חד-פעמי — מסמנים כהושלם כדי שלא יופעל שוב מחר
                    for d in self.cfg.get("tasks",[]):
                        if d.get("id")==task.id:
                            d["enabled"]=False; self.cfg.save(); break
            except Exception:
                pass

# ══════════════════════════════════════════════════════════════════════════════
#  PyQt6
# ══════════════════════════════════════════════════════════════════════════════
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QFrame, QScrollArea,
    QCheckBox, QSpinBox, QComboBox, QLineEdit, QDialog,
    QButtonGroup, QRadioButton, QDateEdit, QSizePolicy,
    QSystemTrayIcon, QMenu, QMessageBox, QInputDialog, QGroupBox,
    QGridLayout
)
from PyQt6.QtCore  import Qt, QTimer, pyqtSignal, QDate, QSize, QObject
from PyQt6.QtGui   import (QFont, QIcon, QPixmap, QPainter, QColor,
                             QBrush, QAction, QFontDatabase)

# ── Icon ──────────────────────────────────────────────────────────────────────
ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#1565C0"/>
  <rect x="8" y="10" width="48" height="32" rx="4" fill="#E3F2FD" stroke="#42A5F5" stroke-width="2"/>
  <rect x="12" y="14" width="40" height="24" rx="2" fill="#0D47A1"/>
  <circle cx="32" cy="26" r="7" fill="#42A5F5" opacity="0.9"/>
  <circle cx="32" cy="26" r="4" fill="#E3F2FD"/>
  <rect x="24" y="42" width="16" height="4" rx="2" fill="#42A5F5"/>
  <rect x="20" y="46" width="24" height="3" rx="1.5" fill="#1E88E5"/>
  <line x1="29" y1="26" x2="32" y2="21" stroke="#0D47A1" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="32" y1="26" x2="36" y2="24" stroke="#0D47A1" stroke-width="1.5" stroke-linecap="round"/>
</svg>"""

def get_icon():
    try:
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtCore import QByteArray
        rnd = QSvgRenderer(QByteArray(ICON_SVG.encode()))
        px = QPixmap(64,64); px.fill(Qt.GlobalColor.transparent)
        p = QPainter(px); rnd.render(p); p.end()
        return QIcon(px)
    except:
        px = QPixmap(64,64); px.fill(Qt.GlobalColor.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor("#1565C0"))); p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0,0,64,64,12,12)
        p.setBrush(QBrush(QColor("#0D47A1"))); p.drawRoundedRect(12,14,40,24,2,2)
        p.setBrush(QBrush(QColor("#42A5F5"))); p.drawEllipse(25,19,14,14)
        p.setBrush(QBrush(QColor("#E3F2FD"))); p.drawEllipse(28,22,8,8)
        p.drawRoundedRect(24,42,16,4,2,2)
        p.end()
        return QIcon(px)

# ── Palettes ──────────────────────────────────────────────────────────────────
PALETTE_DARK = {
    "window":"#0D1B2A","sidebar":"#070F1A","sidebar_hover":"#0F2035","sidebar_sel":"#1565C0",
    "card":"#162032","card_border":"#1E2D3E","surface":"#1E2D3E","input_bg":"#243447",
    "primary":"#42A5F5","accent":"#00E5FF","success":"#66BB6A","danger":"#EF5350","warning":"#FFA726",
    "text":"#E8F0FE","text2":"#90A4AE","text3":"#546E7A","border":"#1E2D3E",
    "tag_weekly":"#2E7D32","tag_date":"#1565C0","tag_timer":"#6A1B9A",
    "pill_on":"#2E7D32","pill_off":"#C62828","sep":"#1E2D3E",
}
PALETTE_LIGHT = {
    "window":"#F0F4F8","sidebar":"#1A3A5C","sidebar_hover":"#1E4676","sidebar_sel":"#1565C0",
    "card":"#FFFFFF","card_border":"#E0E7EF","surface":"#FFFFFF","input_bg":"#E8EEF7",
    "primary":"#1565C0","accent":"#0097A7","success":"#2E7D32","danger":"#C62828","warning":"#E65100",
    "text":"#1A202C","text2":"#4A5568","text3":"#90A4AE","border":"#CBD5E0",
    "tag_weekly":"#2E7D32","tag_date":"#1565C0","tag_timer":"#6A1B9A",
    "pill_on":"#2E7D32","pill_off":"#C62828","sep":"#CBD5E0",
}
def P(k): return _APP.palette_[k]

def qss_btn(bg, fg="#FFF", hover=None, radius=8, pad="6px 18px"):
    hv = hover or bg
    return (f"QPushButton{{background:{bg};color:{fg};border:none;"
            f"border-radius:{radius}px;padding:{pad};font-weight:600;}}"
            f"QPushButton:hover{{background:{hv};}}"
            f"QPushButton:disabled{{background:#555;color:#888;}}")

# ── Helpers: MM:SS spinbox pair ───────────────────────────────────────────────
def mmss_widget(m_val=0, s_val=30, parent=None):
    """Return (QWidget, m_spin, s_spin) showing  MM : SS."""
    w = QWidget(parent)
    lay = QHBoxLayout(w); lay.setContentsMargins(0,0,0,0); lay.setSpacing(3)
    m_sp = QSpinBox(); m_sp.setRange(0,99); m_sp.setValue(m_val); m_sp.setFixedWidth(52)
    s_sp = QSpinBox(); s_sp.setRange(0,59); s_sp.setValue(s_val); s_sp.setFixedWidth(52)
    sep  = QLabel(":"); sep.setFixedWidth(10); sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lay.addWidget(m_sp); lay.addWidget(sep); lay.addWidget(s_sp)
    lay.addStretch()
    return w, m_sp, s_sp

# ── Option group used in both TaskDialog and TimerPage ───────────────────────
class OffOptionsWidget(QWidget):
    """
    Reusable block:  Notification | Force-off | Reoff | Retry
    Only shown when action includes screen-off.
    """
    def __init__(self, task: Task = None, parent=None):
        super().__init__(parent)
        d = task or Task()
        self._build(d)

    def _build(self, d: Task):
        P_ = _APP.palette_; t = T[_APP.lang]
        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(6)

        def grp(title):
            g = QGroupBox(title); g.setCheckable(False)
            g.setStyleSheet(f"""
                QGroupBox{{color:{P_['text2']};font-weight:600;font-size:11px;
                    border:1px solid {P_['card_border']};border-radius:8px;
                    margin-top:6px;padding:8px;background:{P_['card']};}}
                QGroupBox::title{{subcontrol-origin:margin;left:10px;padding:0 4px;}}
            """)
            l = QVBoxLayout(g)
            return g, l

        def chk(text, checked):
            c = QCheckBox(text); c.setChecked(checked)
            c.setStyleSheet(f"color:{P_['text']};font-size:12px;")
            return c

        def mmss_row(label_text, m, s):
            row = QHBoxLayout()
            row.setDirection(QHBoxLayout.Direction.RightToLeft if _APP.lang=="he"
                             else QHBoxLayout.Direction.LeftToRight)
            lbl = QLabel(label_text); lbl.setStyleSheet(f"color:{P_['text2']};font-size:11px;")
            w, ms, ss = mmss_widget(m, s)
            w.setStyleSheet(f"""
                QSpinBox{{background:{P_['input_bg']};color:{P_['text']};
                    border:1px solid {P_['border']};border-radius:5px;
                    padding:2px 4px;font-size:12px;}}
            """)
            row.addWidget(lbl, 1); row.addWidget(w)
            return row, ms, ss

        # ── Notification group ──
        g1, l1 = grp(t["notif_grp"])
        self.c_notif = chk(t["notif_chk"], d.notif); l1.addWidget(self.c_notif)
        r1, self.notif_m, self.notif_s = mmss_row(t["notif_before"], d.notif_m, d.notif_s)
        self.notif_time_w = QWidget(); nl = QVBoxLayout(self.notif_time_w)
        nl.setContentsMargins(0,0,0,0); nl.addLayout(r1)
        l1.addWidget(self.notif_time_w)
        self.c_notif.toggled.connect(self.notif_time_w.setVisible)
        self.notif_time_w.setVisible(d.notif)
        root.addWidget(g1)

        # ── Force off group ──
        g2, l2 = grp(t["force_grp"])
        self.c_force = chk(t["force_chk"], d.force_off); l2.addWidget(self.c_force)
        root.addWidget(g2)

        # ── Reoff group ──
        g3, l3 = grp(t["reoff_grp"])
        self.c_reoff = chk(t["reoff_chk"], d.reoff); l3.addWidget(self.c_reoff)
        r3, self.reoff_m, self.reoff_s = mmss_row(t["reoff_delay"], d.reoff_m, d.reoff_s)
        self.reoff_time_w = QWidget(); rl = QVBoxLayout(self.reoff_time_w)
        rl.setContentsMargins(0,0,0,0); rl.addLayout(r3)
        l3.addWidget(self.reoff_time_w)
        self.c_reoff.toggled.connect(self.reoff_time_w.setVisible)
        self.reoff_time_w.setVisible(d.reoff)
        root.addWidget(g3)

        # ── Retry group (hidden when force_off) ──
        g4, l4 = grp(t["retry_grp"])
        self.c_retry = chk(t["retry_chk"], d.retry_off); l4.addWidget(self.c_retry)
        retry_row = QHBoxLayout()
        retry_row.setDirection(QHBoxLayout.Direction.RightToLeft if _APP.lang=="he"
                               else QHBoxLayout.Direction.LeftToRight)
        retry_lbl = QLabel(t["retry_secs"]+":"); retry_lbl.setStyleSheet(f"color:{P_['text2']};font-size:11px;")
        self.retry_sp = QSpinBox(); self.retry_sp.setRange(3,300); self.retry_sp.setValue(d.retry_secs)
        self.retry_sp.setFixedWidth(64)
        self.retry_sp.setStyleSheet(f"""QSpinBox{{background:{P_['input_bg']};color:{P_['text']};
            border:1px solid {P_['border']};border-radius:5px;padding:2px 4px;font-size:12px;}}""")
        retry_row.addWidget(retry_lbl,1); retry_row.addWidget(self.retry_sp)
        self.retry_time_w = QWidget(); rtl = QVBoxLayout(self.retry_time_w)
        rtl.setContentsMargins(0,0,0,0); rtl.addLayout(retry_row)
        l4.addWidget(self.retry_time_w)
        self.c_retry.toggled.connect(self.retry_time_w.setVisible)
        self.retry_time_w.setVisible(d.retry_off)
        self.g4 = g4; root.addWidget(g4)

        # force_off hides retry group
        self.c_force.toggled.connect(lambda v: self.g4.setVisible(not v))
        self.g4.setVisible(not d.force_off)

    def apply_to(self, task: Task):
        task.notif      = self.c_notif.isChecked()
        task.notif_m    = self.notif_m.value()
        task.notif_s    = self.notif_s.value()
        task.force_off  = self.c_force.isChecked()
        task.reoff      = self.c_reoff.isChecked()
        task.reoff_m    = self.reoff_m.value()
        task.reoff_s    = self.reoff_s.value()
        task.retry_off  = self.c_retry.isChecked() and not task.force_off
        task.retry_secs = self.retry_sp.value()

# ── Nav button ────────────────────────────────────────────────────────────────
class NavButton(QPushButton):
    def __init__(self, icon_text, label, parent=None):
        super().__init__(parent)
        self.icon_text = icon_text; self.label_text = label; self.selected = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(52); self._refresh()
    def set_selected(self, v): self.selected=v; self._refresh()
    def set_label(self, label): self.label_text=label; self._refresh()
    def _refresh(self):
        P_ = _APP.palette_ if _APP else PALETTE_DARK
        bg = P_["sidebar_sel"] if self.selected else "transparent"
        fg = "#FFF" if self.selected else P_["text2"]
        fw = "700" if self.selected else "400"
        self.setStyleSheet(f"""
            QPushButton{{background:{bg};color:{fg};border:none;border-radius:10px;
                padding:0 14px;text-align:right;font-size:14px;font-weight:{fw};}}
            QPushButton:hover{{background:{P_["sidebar_hover"]};color:#FFF;}}
        """)
        self.setText(f"{self.icon_text}   {self.label_text}")

# ── Task card ─────────────────────────────────────────────────────────────────
class TaskCard(QFrame):
    sig_edit   = pyqtSignal(object)
    sig_delete = pyqtSignal(object)
    sig_toggle = pyqtSignal(object)
    def __init__(self, task: Task, lang: str, parent=None):
        super().__init__(parent); self.task=task; self.lang=lang; self._build()
    def _build(self):
        P_=_APP.palette_; t=T[self.lang]; task=self.task
        self.setObjectName("TC")
        self.setStyleSheet(f"#TC{{background:{P_['card']};border:1px solid {P_['card_border']};border-radius:12px;}}")
        stripe_c = {Task.WEEKLY:P_["tag_weekly"],Task.DATE:P_["tag_date"],
                    Task.TIMER:P_["tag_timer"]}.get(task.kind,P_["primary"])
        if not task.enabled: stripe_c=P_["text3"]
        outer=QHBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)
        # RTL: stripe RIGHT, buttons LEFT, text in middle
        stripe=QFrame(); stripe.setFixedWidth(5)
        stripe.setStyleSheet(f"background:{stripe_c};border-radius:0 12px 12px 0;")
        btn_w=QWidget(); btn_w.setStyleSheet(f"background:{P_['card']};")
        bl=QVBoxLayout(btn_w); bl.setContentsMargins(8,8,8,8); bl.setSpacing(4)
        bl.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        for txt,bg,sig in [(t["edit"],P_["primary"],self.sig_edit),(t["delete"],P_["danger"],self.sig_delete)]:
            b=QPushButton(txt); b.setFixedWidth(64)
            b.setStyleSheet(qss_btn(bg,radius=6,pad="3px 4px"))
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _,s=sig: s.emit(self.task)); bl.addWidget(b)
        en_b=QPushButton(t["disable"] if task.enabled else t["enable"])
        en_b.setFixedWidth(64)
        en_b.setStyleSheet(qss_btn(P_["warning"] if task.enabled else P_["success"],radius=6,pad="3px 4px"))
        en_b.setCursor(Qt.CursorShape.PointingHandCursor)
        en_b.clicked.connect(lambda: self.sig_toggle.emit(self.task)); bl.addWidget(en_b)
        body=QWidget(); body.setStyleSheet(f"background:{P_['card']};")
        body_l=QVBoxLayout(body); body_l.setContentsMargins(14,14,14,14)
        lbl=QLabel(task.label(self.lang)); lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        lbl.setStyleSheet(f"color:{P_['text'] if task.enabled else P_['text3']};font-size:13px;font-weight:600;background:transparent;")
        body_l.addWidget(lbl)
        outer.addWidget(btn_w); outer.addWidget(body,1); outer.addWidget(stripe)

# ── Task Dialog ───────────────────────────────────────────────────────────────
class TaskDialog(QDialog):
    def __init__(self, cfg: Config, task=None, parent=None):
        super().__init__(parent)
        self.cfg=cfg; self.task=task or Task()
        self.lang=cfg.get("language","he"); self.t=T[self.lang]; self.is_new=task is None
        self.setWindowTitle(self.t["dlg_title_add"] if self.is_new else self.t["dlg_title_edit"])
        self.setModal(True); self.setMinimumWidth(500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if self.lang=="he"
                                else Qt.LayoutDirection.LeftToRight)
        self._apply_style(); self._build()

    def _apply_style(self):
        P_=_APP.palette_
        self.setStyleSheet(f"""
            QDialog{{background:{P_['window']};}}
            QLabel{{color:{P_['text']};background:transparent;}}
            QGroupBox{{color:{P_['text2']};font-weight:600;border:1px solid {P_['border']};
                border-radius:8px;margin-top:8px;padding-top:8px;}}
            QGroupBox::title{{subcontrol-origin:margin;left:10px;}}
            QSpinBox,QDateEdit,QLineEdit{{background:{P_['input_bg']};color:{P_['text']};
                border:1px solid {P_['border']};border-radius:6px;padding:4px 8px;font-size:13px;}}
            QRadioButton,QCheckBox{{color:{P_['text']};spacing:6px;font-size:13px;}}
        """)

    def _spin(self, lo, hi, val, w=64):
        s=QSpinBox(); s.setRange(lo,hi); s.setValue(val); s.setFixedWidth(w)
        s.setAlignment(Qt.AlignmentFlag.AlignCenter); return s

    def _time3_row(self, lbl_text, h, m, s_):
        row=QHBoxLayout()
        row.setDirection(QHBoxLayout.Direction.RightToLeft if self.lang=="he"
                         else QHBoxLayout.Direction.LeftToRight)
        lbl=QLabel(lbl_text); lbl.setFixedWidth(100); row.addWidget(lbl)
        sh=self._spin(0,23,h); sm=self._spin(0,59,m); ss=self._spin(0,59,s_)
        for w_,c in [(sh,":"),(sm,":"),(ss,None)]:
            row.addWidget(w_)
            if c: row.addWidget(QLabel(c))
        row.addStretch(); return row, sh, sm, ss

    def _build(self):
        P_=_APP.palette_; t=self.t; task=self.task
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"background:{P_['window']};")
        inner=QWidget(); inner.setStyleSheet(f"background:{P_['window']};")
        main=QVBoxLayout(inner); main.setSpacing(10); main.setContentsMargins(16,16,16,16)

        # Name
        nr=QHBoxLayout()
        nr.setDirection(QHBoxLayout.Direction.RightToLeft if self.lang=="he" else QHBoxLayout.Direction.LeftToRight)
        nr.addWidget(QLabel(t["task_name"]+":"))
        self.e_name=QLineEdit(task.name); self.e_name.setPlaceholderText(t["task_name_ph"])
        nr.addWidget(self.e_name,1); main.addLayout(nr)

        # Kind
        kind_g=QGroupBox(t["task_type"]); kl=QHBoxLayout(kind_g)
        kl.setDirection(QHBoxLayout.Direction.RightToLeft if self.lang=="he" else QHBoxLayout.Direction.LeftToRight)
        self.r_weekly=QRadioButton(t["weekly"]); self.r_date=QRadioButton(t["by_date"])
        self.r_timer=QRadioButton(t["timer_kind"])
        bg_k=QButtonGroup(self)
        for r,v in [(self.r_weekly,Task.WEEKLY),(self.r_date,Task.DATE),(self.r_timer,Task.TIMER)]:
            bg_k.addButton(r); kl.addWidget(r)
            if task.kind==v: r.setChecked(True)
        main.addWidget(kind_g)

        # Action
        act_g=QGroupBox(t["action"]); al=QHBoxLayout(act_g)
        al.setDirection(QHBoxLayout.Direction.RightToLeft if self.lang=="he" else QHBoxLayout.Direction.LeftToRight)
        self.r_off=QRadioButton(t["act_off"]); self.r_on=QRadioButton(t["act_on"])
        self.r_both=QRadioButton(t["act_both"])
        bg_a=QButtonGroup(self)
        for r,v in [(self.r_off,Task.OFF),(self.r_on,Task.ON),(self.r_both,Task.BOTH)]:
            bg_a.addButton(r); al.addWidget(r)
            if task.action==v: r.setChecked(True)
        main.addWidget(act_g)

        sep=QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{P_['sep']};"); main.addWidget(sep)

        # Dynamic stack
        self.stack=QStackedWidget()

        # --- Weekly ---
        wp=QWidget(); wl=QVBoxLayout(wp); wl.setSpacing(8)
        wl.addWidget(QLabel(t["days"]+":"))
        dr=QHBoxLayout()
        dr.setDirection(QHBoxLayout.Direction.RightToLeft if self.lang=="he" else QHBoxLayout.Direction.LeftToRight)
        self.day_chks=[]
        for i,d in enumerate(t["days_list"]):
            cb=QCheckBox(d); cb.setChecked(i in task.days)
            self.day_chks.append(cb); dr.addWidget(cb)
        wl.addLayout(dr)
        r_off,self.w_oh,self.w_om,self.w_os=self._time3_row(t["time_off"]+":",task.off_h,task.off_m,task.off_s)
        wl.addLayout(r_off)
        self.on_grp=QGroupBox(t["time_on"]); ol=QVBoxLayout(self.on_grp)
        r_on,self.w_nh,self.w_nm,self.w_ns=self._time3_row("",task.on_h,task.on_m,task.on_s)
        ol.addLayout(r_on)
        wl.addWidget(self.on_grp)
        self.stack.addWidget(wp)

        # --- Date ---
        dp=QWidget(); dl=QVBoxLayout(dp); dl.setSpacing(8)
        date_r=QHBoxLayout()
        date_r.setDirection(QHBoxLayout.Direction.RightToLeft if self.lang=="he" else QHBoxLayout.Direction.LeftToRight)
        date_r.addWidget(QLabel(t["date_lbl"]+":"))
        self.date_edit=QDateEdit(); self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        try:
            parts=task.date_str.split("-")
            self.date_edit.setDate(QDate(int(parts[0]),int(parts[1]),int(parts[2])))
        except: self.date_edit.setDate(QDate.currentDate())
        date_r.addWidget(self.date_edit); date_r.addStretch(); dl.addLayout(date_r)
        r_dt,self.d_h,self.d_m,self.d_s=self._time3_row(t["time_off"]+":",task.date_h,task.date_m,task.date_s)
        dl.addLayout(r_dt); dl.addStretch()
        self.stack.addWidget(dp)

        # --- Timer ---
        tp=QWidget(); tl=QVBoxLayout(tp); tl.setSpacing(8)
        dur_g=QGroupBox(t["dur"]); dl2=QHBoxLayout(dur_g)
        dl2.setDirection(QHBoxLayout.Direction.RightToLeft if self.lang=="he" else QHBoxLayout.Direction.LeftToRight)
        self.t_h=self._spin(0,23,task.t_hours,72); self.t_m=self._spin(0,59,task.t_mins,72)
        self.t_s=self._spin(0,59,task.t_secs,72)
        for sp,lbl in [(self.t_h,t["hours"]),(self.t_m,t["minutes"]),(self.t_s,t["seconds"])]:
            col=QVBoxLayout(); cl=QLabel(lbl); cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            col.addWidget(cl); col.addWidget(sp); dl2.addLayout(col)
        tl.addWidget(dur_g)
        tact_g=QGroupBox(t["timer_act"]); tal=QHBoxLayout(tact_g)
        tal.setDirection(QHBoxLayout.Direction.RightToLeft if self.lang=="he" else QHBoxLayout.Direction.LeftToRight)
        self.rt_off=QRadioButton(t["act_off"]); self.rt_on=QRadioButton(t["act_on"])
        bg_ta=QButtonGroup(self)
        for r,v in [(self.rt_off,Task.OFF),(self.rt_on,Task.ON)]:
            bg_ta.addButton(r); tal.addWidget(r)
            if task.t_action==v: r.setChecked(True)
        if not(self.rt_off.isChecked() or self.rt_on.isChecked()): self.rt_off.setChecked(True)
        tl.addWidget(tact_g); tl.addStretch()
        self.stack.addWidget(tp)

        main.addWidget(self.stack)

        # ── Off options (notification / force / reoff / retry) ──
        self.off_opts=OffOptionsWidget(task)
        self.off_opts_grp=QGroupBox()
        self.off_opts_grp.setStyleSheet(f"""
            QGroupBox{{background:{P_['surface']};border:1px solid {P_['border']};
                border-radius:10px;margin-top:4px;padding:8px;}}
        """)
        og=QVBoxLayout(self.off_opts_grp); og.addWidget(self.off_opts)
        main.addWidget(self.off_opts_grp)

        # Buttons
        br=QHBoxLayout()
        br.setDirection(QHBoxLayout.Direction.RightToLeft if self.lang=="he" else QHBoxLayout.Direction.LeftToRight)
        sv=QPushButton(t["save"]); sv.setStyleSheet(qss_btn(P_["primary"],pad="8px 28px"))
        sv.setCursor(Qt.CursorShape.PointingHandCursor); sv.clicked.connect(self._save)
        cl=QPushButton(t["cancel"]); cl.setStyleSheet(qss_btn(P_["surface"],P_["text2"],pad="8px 28px"))
        cl.setCursor(Qt.CursorShape.PointingHandCursor); cl.clicked.connect(self.reject)
        br.addWidget(sv); br.addWidget(cl); br.addStretch()
        main.addLayout(br)

        scroll.setWidget(inner)
        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.addWidget(scroll)

        # Wire signals
        for r in [self.r_weekly,self.r_date,self.r_timer]: r.toggled.connect(self._refresh_stack)
        self.r_both.toggled.connect(self._refresh_on_grp)
        for r in [self.r_off,self.r_on,self.r_both]: r.toggled.connect(self._refresh_off_opts)
        self._refresh_stack(); self._refresh_off_opts()

    def _refresh_stack(self):
        if self.r_weekly.isChecked(): self.stack.setCurrentIndex(0); self._refresh_on_grp()
        elif self.r_date.isChecked():
            self.stack.setCurrentIndex(1)
            # משימת תאריך אינה תומכת ב'כיבוי+הדלקה' (אין שדה שעת הדלקה) —
            # אם נבחר BOTH בעבר, הורד ל-OFF בלבד כדי למנוע חוסר עקביות.
            self.r_both.setVisible(False)
            if self.r_both.isChecked():
                self.r_off.setChecked(True)
        else:
            self.stack.setCurrentIndex(2)
            self.r_both.setVisible(True)

    def _refresh_on_grp(self):
        self.on_grp.setVisible(self.r_weekly.isChecked() and self.r_both.isChecked())

    def _refresh_off_opts(self):
        action_has_off = self.r_off.isChecked() or self.r_both.isChecked() or \
                         (self.r_timer.isChecked() and self.rt_off.isChecked())
        self.off_opts_grp.setVisible(action_has_off)

    def _save(self):
        t=self.task
        t.name=self.e_name.text().strip()
        if self.r_weekly.isChecked():  t.kind=Task.WEEKLY
        elif self.r_date.isChecked():  t.kind=Task.DATE
        else:                          t.kind=Task.TIMER
        if self.r_off.isChecked():    t.action=Task.OFF
        elif self.r_on.isChecked():   t.action=Task.ON
        else:                         t.action=Task.BOTH
        if t.kind==Task.WEEKLY:
            t.days=[i for i,c in enumerate(self.day_chks) if c.isChecked()]
            t.off_h=self.w_oh.value(); t.off_m=self.w_om.value(); t.off_s=self.w_os.value()
            t.on_h=self.w_nh.value();  t.on_m=self.w_nm.value();  t.on_s=self.w_ns.value()
        elif t.kind==Task.DATE:
            d=self.date_edit.date()
            t.date_str=f"{d.year():04d}-{d.month():02d}-{d.day():02d}"
            t.date_h=self.d_h.value(); t.date_m=self.d_m.value(); t.date_s=self.d_s.value()
        else:
            t.t_hours=self.t_h.value(); t.t_mins=self.t_m.value(); t.t_secs=self.t_s.value()
            t.t_action=Task.OFF if self.rt_off.isChecked() else Task.ON
            # טיימר: הספירה מתחילה מרגע השמירה/העריכה
            t.t_start=datetime.datetime.now().isoformat()
        self.off_opts.apply_to(t)
        self.accept()

# ══════════════════════════════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════════════════════════════
class TasksPage(QWidget):
    def __init__(self, cfg: Config, parent=None):
        super().__init__(parent); self.cfg=cfg; self._build()

    def _build(self):
        P_=_APP.palette_; t=T[_APP.lang]
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        dir_=Qt.LayoutDirection.RightToLeft if _APP.lang=="he" else Qt.LayoutDirection.LeftToRight

        # Toolbar
        tb=QWidget(); tb.setFixedHeight(60)
        tb.setStyleSheet(f"background:{P_['surface']};border-bottom:1px solid {P_['sep']};")
        tbl=QHBoxLayout(tb); tbl.setContentsMargins(16,0,16,0)
        tbl.setDirection(QHBoxLayout.Direction.RightToLeft if _APP.lang=="he" else QHBoxLayout.Direction.LeftToRight)
        add_btn=QPushButton("  ＋  "+t["add_task"]); add_btn.setStyleSheet(qss_btn(P_["primary"],pad="8px 18px"))
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor); add_btn.clicked.connect(self._add_task)
        man_off=QPushButton("⚫  "+t["man_off"]); man_off.setStyleSheet(qss_btn(P_["surface"],P_["text"],hover=P_["card_border"],pad="8px 14px"))
        man_off.setCursor(Qt.CursorShape.PointingHandCursor); man_off.clicked.connect(lambda: (screen_off(), _APP.main_win.set_screen_off(True)))
        man_on=QPushButton("⚪  "+t["man_on"]); man_on.setStyleSheet(qss_btn(P_["success"],pad="8px 14px"))
        man_on.setCursor(Qt.CursorShape.PointingHandCursor); man_on.clicked.connect(lambda: (screen_on(), _APP.main_win.set_screen_off(False)))
        disp=QPushButton(t["disp_icon"]+"  "+t["disp_btn"]); disp.setStyleSheet(qss_btn(P_["accent"],pad="8px 14px"))
        disp.setCursor(Qt.CursorShape.PointingHandCursor); disp.clicked.connect(open_display_settings)
        tbl.addWidget(add_btn); tbl.addStretch()
        tbl.addWidget(man_on); tbl.addWidget(man_off); tbl.addWidget(disp)
        root.addWidget(tb)

        # Scroll list
        self.scroll=QScrollArea(); self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet(f"background:{P_['window']};")
        self.inner=QWidget(); self.inner.setStyleSheet(f"background:{P_['window']};")
        self.list_l=QVBoxLayout(self.inner); self.list_l.setContentsMargins(16,12,16,12)
        self.list_l.setSpacing(8); self.list_l.addStretch()
        self.scroll.setWidget(self.inner)
        root.addWidget(self.scroll,1)
        self.refresh()

    def refresh(self):
        while self.list_l.count()>1:
            item=self.list_l.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        tasks=[Task(d) for d in self.cfg.get("tasks",[])]
        P_=_APP.palette_; t=T[_APP.lang]
        if not tasks:
            lbl=QLabel(t["no_tasks"]); lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color:{P_['text3']};font-size:14px;font-style:italic;")
            lbl.setWordWrap(True); self.list_l.insertWidget(0,lbl); return
        for task in tasks:
            card=TaskCard(task,_APP.lang)
            card.sig_edit.connect(self._edit_task); card.sig_delete.connect(self._del_task)
            card.sig_toggle.connect(self._toggle_task)
            self.list_l.insertWidget(self.list_l.count()-1,card)

    def _add_task(self):
        dlg=TaskDialog(self.cfg,parent=self)
        if dlg.exec()==QDialog.DialogCode.Accepted:
            tasks=self.cfg.get("tasks",[]); tasks.append(dlg.task.to_dict())
            self.cfg.set("tasks",tasks); self.refresh()

    def _edit_task(self,task):
        dlg=TaskDialog(self.cfg,task=task,parent=self)
        if dlg.exec()==QDialog.DialogCode.Accepted:
            tasks=self.cfg.get("tasks",[])
            for i,d in enumerate(tasks):
                if d.get("id")==task.id: tasks[i]=dlg.task.to_dict(); break
            self.cfg.set("tasks",tasks); self.refresh()

    def _del_task(self,task):
        t=T[_APP.lang]
        if QMessageBox.question(self,t["delete"],t["confirm_del"])==QMessageBox.StandardButton.Yes:
            self.cfg.set("tasks",[d for d in self.cfg.get("tasks",[]) if d.get("id")!=task.id])
            self.refresh()

    def _toggle_task(self,task):
        task.enabled=not task.enabled
        tasks=self.cfg.get("tasks",[])
        for i,d in enumerate(tasks):
            if d.get("id")==task.id: tasks[i]=task.to_dict(); break
        self.cfg.set("tasks",tasks); self.refresh()


class TimerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._active=False; self._end=0; self._action=Task.OFF
        self._build()
        self._qtimer=QTimer(self); self._qtimer.setInterval(500)
        self._qtimer.timeout.connect(self._tick)

    def _build(self):
        P_=_APP.palette_; t=T[_APP.lang]
        root=QVBoxLayout(self); root.setAlignment(Qt.AlignmentFlag.AlignTop)
        root.setSpacing(12); root.setContentsMargins(30,20,30,20)

        # Countdown
        self.cd_lbl=QLabel("00 : 00 : 00")
        self.cd_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cd_lbl.setStyleSheet(f"color:{P_['accent']};font-size:52px;font-weight:700;letter-spacing:4px;")
        root.addWidget(self.cd_lbl)
        sub=QLabel(t["countdown"]); sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color:{P_['text3']};font-size:11px;"); root.addWidget(sub)

        # H M S
        inp=QWidget(); il=QHBoxLayout(inp); il.setSpacing(6); inp.setMaximumWidth(360)
        self.i_h=QSpinBox(); self.i_h.setRange(0,23); self.i_h.setValue(0)
        self.i_m=QSpinBox(); self.i_m.setRange(0,59); self.i_m.setValue(30)
        self.i_s=QSpinBox(); self.i_s.setRange(0,59); self.i_s.setValue(0)
        sp_ss=f"QSpinBox{{background:{P_['surface']};color:{P_['text']};border:1px solid {P_['border']};border-radius:8px;font-size:20px;font-weight:700;padding:6px;min-width:64px;}} QSpinBox::up-button,QSpinBox::down-button{{width:18px;}}"
        sep_ss=f"color:{P_['text2']};font-size:24px;font-weight:700;background:transparent;"
        for sp in [self.i_h,self.i_m,self.i_s]:
            sp.setStyleSheet(sp_ss); sp.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sp.valueChanged.connect(self._update_display)
        for lbl_txt,is_spin,widget in [
            (t["hours"],False,None),(None,True,self.i_h),
            (":",False,None),(None,True,self.i_m),
            (":",False,None),(None,True,self.i_s),
            (t["seconds"],False,None)]:
            if is_spin: il.addWidget(widget,1)
            else:
                l=QLabel(lbl_txt); l.setAlignment(Qt.AlignmentFlag.AlignCenter)
                l.setStyleSheet(sep_ss if lbl_txt==":" else f"color:{P_['text2']};font-size:10px;background:transparent;")
                il.addWidget(l)
        root.addWidget(inp,alignment=Qt.AlignmentFlag.AlignCenter)

        # Action
        act_w=QWidget(); act_l=QHBoxLayout(act_w)
        act_l.setDirection(QHBoxLayout.Direction.RightToLeft if _APP.lang=="he" else QHBoxLayout.Direction.LeftToRight)
        act_lbl=QLabel(t["timer_act"]+":"); act_lbl.setStyleSheet(f"color:{P_['text2']};font-size:12px;")
        self.r_off=QRadioButton(t["act_off"]); self.r_off.setChecked(True)
        self.r_on=QRadioButton(t["act_on"])
        bg=QButtonGroup(self); bg.addButton(self.r_off); bg.addButton(self.r_on)
        for r in [self.r_off,self.r_on]: r.setStyleSheet(f"color:{P_['text']};font-size:12px;")
        act_l.addWidget(act_lbl); act_l.addWidget(self.r_off); act_l.addWidget(self.r_on); act_l.addStretch()
        root.addWidget(act_w,alignment=Qt.AlignmentFlag.AlignCenter)

        # ── Off options (same widget as TaskDialog) ──
        dummy=Task(); dummy.notif=False; dummy.force_off=False; dummy.reoff=False; dummy.retry_off=False
        dummy.notif_m=0; dummy.notif_s=30; dummy.reoff_m=0; dummy.reoff_s=30; dummy.retry_secs=15
        self.off_opts=OffOptionsWidget(dummy)
        off_frame=QFrame(); off_frame.setStyleSheet(f"background:{P_['surface']};border:1px solid {P_['card_border']};border-radius:10px;")
        off_fl=QVBoxLayout(off_frame); off_fl.addWidget(self.off_opts)
        self.off_opts_frame=off_frame
        self.r_off.toggled.connect(lambda v: self.off_opts_frame.setVisible(v))
        root.addWidget(off_frame)

        # Buttons
        bf=QWidget(); bl=QHBoxLayout(bf); bl.setSpacing(12)
        self.start_btn=QPushButton(t["start"]); self.start_btn.setFixedSize(150,44)
        self.start_btn.setStyleSheet(qss_btn(P_["success"],pad="10px 0"))
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor); self.start_btn.clicked.connect(self._start)
        self.stop_btn=QPushButton(t["stop"]); self.stop_btn.setFixedSize(150,44)
        self.stop_btn.setStyleSheet(qss_btn(P_["danger"],pad="10px 0"))
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor); self.stop_btn.setEnabled(False); self.stop_btn.clicked.connect(self._stop)
        bl.addWidget(self.start_btn); bl.addWidget(self.stop_btn)
        root.addWidget(bf,alignment=Qt.AlignmentFlag.AlignCenter)
        self.status_lbl=QLabel(""); self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet(f"color:{P_['success']};font-size:12px;font-weight:600;")
        root.addWidget(self.status_lbl); root.addStretch()
        self._update_display()

    def _update_display(self):
        h=self.i_h.value(); m=self.i_m.value(); s=self.i_s.value()
        self.cd_lbl.setText(f"{h:02d} : {m:02d} : {s:02d}")

    def _start(self):
        total=self.i_h.value()*3600+self.i_m.value()*60+self.i_s.value()
        if total<=0: return
        self._active=True; self._end=time.time()+total
        self._action=Task.OFF if self.r_off.isChecked() else Task.ON
        self.start_btn.setEnabled(False); self.stop_btn.setEnabled(True)
        self.status_lbl.setText("⏳"); self._qtimer.start()

    def _stop(self):
        self._active=False; self._qtimer.stop()
        self.cd_lbl.setText("00 : 00 : 00")
        self.start_btn.setEnabled(True); self.stop_btn.setEnabled(False)
        self.status_lbl.setText("")

    def _tick(self):
        rem=self._end-time.time()
        if rem<=0:
            self._stop()
            # Build a temporary Task from off_opts
            tmp=Task()
            self.off_opts.apply_to(tmp)
            if self._action==Task.OFF:
                tmp.t_action=Task.OFF
                def do_off():
                    if tmp.notif:
                        delay=tmp.notif_m*60+tmp.notif_s
                        if delay>0:
                            dur_str=f"{tmp.notif_m:02d}:{tmp.notif_s:02d}"
                            if hasattr(_APP,'tray'):
                                _APP.tray.showMessage(APP_NAME, T[_APP.lang]["notif_msg"].format(n=dur_str),
                                                      QSystemTrayIcon.MessageIcon.Information, 8000)
                            time.sleep(delay)
                    screen_off(force=tmp.force_off)
                    _APP.main_win.set_screen_off(True)
                    if tmp.reoff:
                        d2=tmp.reoff_m*60+tmp.reoff_s
                        time.sleep(max(d2,3)); screen_off(force=tmp.force_off)
                    if tmp.retry_off and not tmp.force_off:
                        time.sleep(max(tmp.retry_secs,3)); screen_off(False)
                threading.Thread(target=do_off,daemon=True).start()
                self.status_lbl.setText(T[_APP.lang]["timer_done_off"])
            else:
                screen_on(); _APP.main_win.set_screen_off(False)
                self.status_lbl.setText(T[_APP.lang]["timer_done_on"])
            return
        r=int(rem); hh,r2=divmod(r,3600); mm,ss=divmod(r2,60)
        self.cd_lbl.setText(f"{hh:02d} : {mm:02d} : {ss:02d}")


class SettingsPage(QWidget):
    def __init__(self, cfg: Config, parent=None):
        super().__init__(parent); self.cfg=cfg; self._build()

    def _build(self):
        P_=_APP.palette_; t=T[_APP.lang]
        scroll=QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame); scroll.setStyleSheet(f"background:{P_['window']};")
        rw=QWidget(); rw.setStyleSheet(f"background:{P_['window']};")
        root=QVBoxLayout(rw); root.setContentsMargins(32,24,32,32); root.setSpacing(16)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)
        dir_=Qt.LayoutDirection.RightToLeft if _APP.lang=="he" else Qt.LayoutDirection.LeftToRight

        def sec(title):
            l=QLabel(title); l.setLayoutDirection(dir_)
            l.setStyleSheet(f"color:{P_['primary']};font-size:13px;font-weight:700;")
            root.addWidget(l)
            s=QFrame(); s.setFrameShape(QFrame.Shape.HLine); s.setStyleSheet(f"color:{P_['sep']};")
            root.addWidget(s)

        def row(lbl,w):
            f=QWidget(); f.setLayoutDirection(dir_); fl=QHBoxLayout(f); fl.setContentsMargins(0,0,0,0)
            l=QLabel(lbl); l.setStyleSheet(f"color:{P_['text']};font-size:13px;")
            fl.addWidget(l,1); fl.addWidget(w); root.addWidget(f)

        # Appearance
        sec("🎨  " + t["appearance"])
        tw=QWidget(); tw.setLayoutDirection(dir_); tl=QHBoxLayout(tw); tl.setContentsMargins(0,0,0,0)
        self.r_dark=QRadioButton(t["dark_mode"]); self.r_light=QRadioButton(t["light_mode"])
        bgt=QButtonGroup(self); bgt.addButton(self.r_dark); bgt.addButton(self.r_light)
        (self.r_dark if self.cfg.get("dark",True) else self.r_light).setChecked(True)
        for r in [self.r_dark,self.r_light]:
            r.setStyleSheet(f"color:{P_['text']};font-size:13px;"); tl.addWidget(r)
        tl.addStretch(); self.r_dark.toggled.connect(self._apply_theme)
        root.addWidget(tw)

        # Language
        sec("🌐  " + t["lang_lbl"])
        self.lang_combo=QComboBox()
        self.lang_combo.addItems(["עברית (RTL)","English (LTR)"])
        self.lang_combo.setCurrentIndex(0 if _APP.lang=="he" else 1)
        self.lang_combo.setFixedWidth(160)
        self.lang_combo.setStyleSheet(f"""
            QComboBox{{background:{P_['input_bg']};color:{P_['text']};border:1px solid {P_['border']};
                border-radius:6px;padding:4px 8px;font-size:13px;}}
            QComboBox::drop-down{{border:none;}}
            QComboBox QAbstractItemView{{background:{P_['surface']};color:{P_['text']};}}
        """)
        self.lang_combo.currentIndexChanged.connect(self._apply_lang)
        row(t["lang_lbl"]+":", self.lang_combo)

        # General
        sec("⚡  " + t["general"])
        self.startup_chk=QCheckBox(t["startup_chk"])
        self.startup_chk.setChecked(self.cfg.get("startup",True))
        self.startup_chk.setStyleSheet(f"color:{P_['text']};font-size:13px;")
        self.startup_chk.stateChanged.connect(lambda: (self.cfg.set("startup",self.startup_chk.isChecked()),self.cfg.apply_startup(self.startup_chk.isChecked())))
        root.addWidget(self.startup_chk)

        # Display
        sec("🖥  " + t["display"])
        db=QPushButton(t["disp_icon"]+"  "+t["disp_btn"])
        db.setStyleSheet(qss_btn(P_["accent"],pad="8px 20px")); db.setFixedWidth(220)
        db.setCursor(Qt.CursorShape.PointingHandCursor); db.clicked.connect(open_display_settings)
        root.addWidget(db)

        # Security
        sec("🔒  " + t["security"])
        has_pw=bool(self.cfg.get("pw_hash"))
        self.pw_status=QLabel(t["pw_set"] if has_pw else t["pw_none"])
        self.pw_status.setStyleSheet(f"color:{P_['success'] if has_pw else P_['text3']};font-size:12px;font-style:italic;")
        pww=QWidget(); pww.setLayoutDirection(dir_); pwl=QHBoxLayout(pww); pwl.setContentsMargins(0,0,0,0)
        sp=QPushButton(t["set_pw"]); sp.setStyleSheet(qss_btn(P_["primary"],pad="6px 16px"))
        sp.setCursor(Qt.CursorShape.PointingHandCursor); sp.clicked.connect(self._set_pw)
        rp=QPushButton(t["rem_pw"]); rp.setStyleSheet(qss_btn(P_["danger"],pad="6px 16px"))
        rp.setCursor(Qt.CursorShape.PointingHandCursor); rp.clicked.connect(self._rem_pw); rp.setVisible(has_pw)
        pwl.addWidget(self.pw_status); pwl.addSpacing(12); pwl.addWidget(sp); pwl.addWidget(rp); pwl.addStretch()
        root.addWidget(pww); root.addStretch()
        scroll.setWidget(rw)
        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.addWidget(scroll)

    def _apply_theme(self):
        _APP.apply_palette(self.r_dark.isChecked())

    def _apply_lang(self,idx):
        _APP.apply_language("he" if idx==0 else "en")

    def _set_pw(self):
        t=T[_APP.lang]
        pw,ok=QInputDialog.getText(self,t["set_pw"],t["enter_pw"]+":",QLineEdit.EchoMode.Password)
        if ok and pw:
            self.cfg.set("pw_hash",self.cfg.hash_pw(pw))
            self.pw_status.setText(t["pw_set"]); self.pw_status.setStyleSheet(f"color:{_APP.palette_['success']};font-size:12px;font-style:italic;")

    def _rem_pw(self):
        t=T[_APP.lang]
        pw,ok=QInputDialog.getText(self,t["enter_pw"],t["enter_pw"]+":",QLineEdit.EchoMode.Password)
        if ok and self.cfg.verify_pw(pw):
            self.cfg.set("pw_hash",None)
            self.pw_status.setText(t["pw_none"]); self.pw_status.setStyleSheet(f"color:{_APP.palette_['text3']};font-size:12px;font-style:italic;")
        elif ok:
            QMessageBox.warning(self,t["wrong_pw"],t["wrong_pw"])


class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._build()
    def _build(self):
        P_=_APP.palette_; t=T[_APP.lang]
        scroll=QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame); scroll.setStyleSheet(f"background:{P_['window']};")
        rw=QWidget(); rw.setStyleSheet(f"background:{P_['window']};")
        root=QVBoxLayout(rw); root.setContentsMargins(40,28,40,36); root.setSpacing(12)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)
        logo=QLabel("💡"); logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("font-size:52px;background:transparent;"); root.addWidget(logo)
        name=QLabel(APP_NAME if _APP.lang=="he" else APP_NAME_EN)
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name.setStyleSheet(f"color:{P_['primary']};font-size:24px;font-weight:700;background:transparent;"); root.addWidget(name)
        ver=QLabel(f"{t['ver']} {VERSION}"); ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet(f"color:{P_['text3']};font-size:11px;background:transparent;"); root.addWidget(ver)
        sep=QFrame(); sep.setFrameShape(QFrame.Shape.HLine); sep.setStyleSheet(f"color:{P_['sep']};"); root.addWidget(sep)

        def card(title, items):
            g=QGroupBox(title)
            g.setStyleSheet(f"""QGroupBox{{color:{P_['primary']};font-weight:700;font-size:12px;
                border:1px solid {P_['card_border']};border-radius:10px;
                margin-top:8px;padding:10px;background:{P_['card']};}}
                QGroupBox::title{{subcontrol-origin:margin;left:12px;padding:0 6px;}}""")
            gl=QVBoxLayout(g)
            for item in items:
                l=QLabel(item); l.setWordWrap(True)
                l.setStyleSheet(f"color:{P_['text']};font-size:11px;background:transparent;")
                l.setAlignment(Qt.AlignmentFlag.AlignRight if _APP.lang=="he" else Qt.AlignmentFlag.AlignLeft)
                gl.addWidget(l)
            root.addWidget(g)

        if _APP.lang=="he":
            card("✨ תכונות",[
                "✓  כיבוי/הדלקת מסך בלבד – ללא שינה או כיבוי מחשב",
                "✓  תזמון שבועי, תאריך מדויק, טיימר ספירה לאחור",
                "✓  הגדרות הודעה, כיבוי בכפיה, ניסיון חוזר – לכל משימה בנפרד",
                "✓  פועל ברקע בשורת המשימות | סרגל ניווט צידי",
                "✓  עברית RTL + אנגלית LTR – החלפה מיידית",
                "✓  מצב לילה/יום – החלפה מיידית | הגנת סיסמה",])
        else:
            card("✨ Features",[
                "✓  Screen off/on only – no sleep or shutdown",
                "✓  Weekly, date & time scheduling + countdown timer",
                "✓  Per-task: notification, force-off, re-off, retry",
                "✓  Runs in system tray | Side navigation bar",
                "✓  Hebrew RTL + English LTR – instant switch",
                "✓  Dark/Light mode – instant switch | Password protection",])

        card("📚 Libraries & Credits",[
            "PyQt6  ©  Riverbank Computing Ltd.  (GPL v3 / Commercial)",
            "    https://www.riverbankcomputing.com/software/pyqt/",
            "Qt framework  ©  The Qt Company Ltd.  (LGPL v3)",
            "    https://www.qt.io/",
            "Pillow (PIL Fork)  ©  Jeffrey A. Clark & contributors  (HPND)",
            "    https://python-pillow.org/",
            "pystray  ©  Moses Palmér  (LGPL v3)",
            "    https://github.com/moses-palmer/pystray",
            "Python  ©  Python Software Foundation  (PSF License)",
            "    https://www.python.org/",
            "Windows API (ctypes)  ©  Microsoft Corporation",
            "    screen_off via PostMessageW · screen_on via SetCursorPos + keybd_event",])

        card("⚖️ License",[
            "© 2025  מסך חכם – Smart Screen  |  All rights reserved.",
            "This software is provided for personal use.",
            "Third-party libraries retain their respective licenses.",])

        root.addStretch(); scroll.setWidget(rw)
        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.addWidget(scroll)

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg=cfg; self._scr_off=False
        self.setWindowTitle(T[_APP.lang]["app_name"])
        self.resize(880,640); self.setMinimumSize(720,500)
        self.setWindowIcon(get_icon())
        self._build()

    def _build(self):
        P_=_APP.palette_; t=T[_APP.lang]
        central=QWidget(); self.setCentralWidget(central)
        outer=QHBoxLayout(central); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)

        # ── Sidebar ──
        self.sidebar=QWidget(); self.sidebar.setFixedWidth(190)
        self.sidebar.setStyleSheet(f"background:{P_['sidebar']};")
        sbl=QVBoxLayout(self.sidebar); sbl.setContentsMargins(10,16,10,16); sbl.setSpacing(4)
        sbl.setAlignment(Qt.AlignmentFlag.AlignTop)

        aln=QLabel(APP_NAME if _APP.lang=="he" else APP_NAME_EN)
        aln.setAlignment(Qt.AlignmentFlag.AlignCenter)
        aln.setStyleSheet("color:#FFF;font-size:16px;font-weight:700;background:transparent;")
        vln=QLabel(f"v{VERSION}"); vln.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vln.setStyleSheet(f"color:{P_['text3']};font-size:11px;background:transparent;")
        sbl.addWidget(aln); sbl.addWidget(vln); sbl.addSpacing(10)

        sp=QFrame(); sp.setFrameShape(QFrame.Shape.HLine); sp.setStyleSheet(f"color:{P_['border']};"); sbl.addWidget(sp)
        sbl.addSpacing(6)

        self.pill=QLabel("🟢 "+t["screen_on_lbl"]); self.pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pill.setFixedHeight(28)
        self.pill.setStyleSheet(f"background:{P_['pill_on']};color:white;border-radius:14px;font-size:11px;font-weight:600;")
        sbl.addWidget(self.pill); sbl.addSpacing(10)

        self.nav_btns=[]
        for icon,label,idx in [("📋",t["nav_tasks"],0),("⏱",t["nav_timer"],1),("⚙️",t["nav_settings"],2),("ℹ️",t["nav_about"],3)]:
            btn=NavButton(icon,label)
            btn.clicked.connect(lambda _,i=idx: self._switch(i))
            sbl.addWidget(btn); self.nav_btns.append(btn)

        sbl.addStretch()
        self.theme_btn=QPushButton(("☀️  "+t["light_mode"]) if self.cfg.get("dark") else ("🌙  "+t["dark_mode"]))
        self.theme_btn.setStyleSheet(f"QPushButton{{background:transparent;color:{P_['text2']};border:1px solid {P_['border']};border-radius:8px;padding:6px;font-size:12px;}} QPushButton:hover{{color:#FFF;background:{P_['sidebar_hover']};}}")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.clicked.connect(lambda: _APP.apply_palette(not self.cfg.get("dark",True)))
        sbl.addWidget(self.theme_btn)

        # ── Content stack ──
        self.stack=QStackedWidget(); self.stack.setStyleSheet(f"background:{P_['window']};")
        self.page_tasks=TasksPage(self.cfg)
        self.page_timer=TimerPage()
        self.page_settings=SettingsPage(self.cfg)
        self.page_about=AboutPage()
        for p in [self.page_tasks,self.page_timer,self.page_settings,self.page_about]:
            self.stack.addWidget(p)

        # ── Layout direction: Hebrew → sidebar RIGHT; English → sidebar LEFT ──
        if _APP.lang == "he":
            outer.addWidget(self.stack, 1)
            outer.addWidget(self.sidebar)
        else:
            outer.addWidget(self.sidebar)
            outer.addWidget(self.stack, 1)

        self._switch(0)

    def _switch(self, idx):
        self.stack.setCurrentIndex(idx)
        for i,btn in enumerate(self.nav_btns): btn.set_selected(i==idx)

    def set_screen_off(self, off: bool):
        self._scr_off=off; P_=_APP.palette_; t=T[_APP.lang]
        if off:
            self.pill.setText("🔴 "+t["screen_off_lbl"])
            self.pill.setStyleSheet(f"background:{P_['pill_off']};color:white;border-radius:14px;font-size:11px;font-weight:600;")
        else:
            self.pill.setText("🟢 "+t["screen_on_lbl"])
            self.pill.setStyleSheet(f"background:{P_['pill_on']};color:white;border-radius:14px;font-size:11px;font-weight:600;")

    def rebuild(self):
        central=QWidget(); self.setCentralWidget(central)
        self.setWindowTitle(T[_APP.lang]["app_name"])
        self._build()

    def closeEvent(self, ev):
        ev.ignore(); self.hide()

# ══════════════════════════════════════════════════════════════════════════════
#  APP CONTROLLER
# ══════════════════════════════════════════════════════════════════════════════
class SmartScreenApp(QObject):
    # סיגנלים לניתוב קריאות מחוטי רקע אל חוט ה-GUI (בטוח, אוטומטי)
    sig_screen_off = pyqtSignal(bool)
    sig_notify     = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        global _APP; _APP=self
        self.cfg=Config()
        self.lang=self.cfg.get("language","he")
        self.palette_=PALETTE_DARK if self.cfg.get("dark",True) else PALETTE_LIGHT
        self.qapp=QApplication(sys.argv)
        self.qapp.setApplicationName(APP_NAME_EN)
        self.qapp.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft if self.lang=="he" else Qt.LayoutDirection.LeftToRight)
        self.qapp.setFont(QFont("Segoe UI",10))
        self.main_win=MainWindow(self.cfg)
        self._setup_tray()
        self.sig_screen_off.connect(lambda v: self.main_win.set_screen_off(v))
        self.sig_notify.connect(self._show_notify)
        self.sched=Scheduler(self.cfg, self._on_sched)
        self.sched.start()
        self.cfg.apply_startup(self.cfg.get("startup",True))

    def _show_notify(self, msg):
        if self.tray:
            self.tray.showMessage(T[self.lang]["app_name"], msg,
                                  QSystemTrayIcon.MessageIcon.Information, 8000)

    def apply_palette(self, dark: bool):
        self.cfg.set("dark",dark)
        self.palette_=PALETTE_DARK if dark else PALETTE_LIGHT
        self.main_win.rebuild()

    def apply_language(self, lang: str):
        self.lang=lang; self.cfg.set("language",lang)
        self.qapp.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft if lang=="he" else Qt.LayoutDirection.LeftToRight)
        self.main_win.rebuild()

    def _setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable(): self.tray=None; return
        self.tray=QSystemTrayIcon(get_icon(),self.qapp)
        self.tray.setToolTip(T[self.lang]["tray_tip"])
        menu=QMenu(); t=T[self.lang]
        title_act=QAction(t["app_name"],self.qapp); title_act.setEnabled(False)
        open_act=QAction(t["open"],self.qapp); open_act.triggered.connect(self._show)
        quit_act=QAction(t["quit"],self.qapp); quit_act.triggered.connect(self._quit)
        menu.addAction(title_act); menu.addSeparator(); menu.addAction(open_act)
        menu.addSeparator(); menu.addAction(quit_act)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda r: self._show() if r==QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray.show()

    def _show(self):
        self.main_win.show(); self.main_win.raise_(); self.main_win.activateWindow()

    def _quit(self):
        self.sched.stop(); self.qapp.quit()

    def _on_sched(self, event, task, data):
        # קריאה מחוט רקע → פליטת סיגנל → Qt מנתב לחוט ה-GUI (queued).
        if event=="off":
            self.sig_screen_off.emit(True)
        elif event=="on":
            self.sig_screen_off.emit(False)
        elif event=="notify" and self.tray:
            msg=T[self.lang]["notif_msg"].format(n=data)
            self.sig_notify.emit(msg)

    def run(self):
        self.main_win.show()
        sys.exit(self.qapp.exec())

# ══════════════════════════════════════════════════════════════════════════════
_APP: "SmartScreenApp" = None

if __name__=="__main__":
    SmartScreenApp().run()
