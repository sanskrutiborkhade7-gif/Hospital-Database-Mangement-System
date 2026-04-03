# hospital_mgmt_ui.py (Light Theme)
import json
import os
import mysql.connector
import tkinter as tk
from tkinter import messagebox, simpledialog
import ttkbootstrap as tb
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.widgets import DateEntry
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ------------- CONFIG -------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Sanskruti@07",
    "database": "hospital_db"
}
OFFICIAL_FILE = "official_account.json"

# ------------- Globals -------------
root = None
current_user = None
current_page = "dashboard"
sidebar_btns = {}

# ------------- Light Theme Colors -------------
COLORS = {
    "bg_main": "#f8fafc",
    "bg_sidebar": "#ffffff",
    "bg_card": "#ffffff",
    "bg_input": "#f1f5f9",
    "text_primary": "#0f172a",
    "text_secondary": "#475569",
    "text_muted": "#94a3b8",
    "accent_blue": "#2563eb",
    "accent_cyan": "#0891b2",
    "accent_green": "#059669",
    "accent_orange": "#d97706",
    "accent_red": "#dc2626",
    "accent_purple": "#7c3aed",
    "accent_pink": "#db2777",
    "border": "#e2e8f0",
    "hover": "#f1f5f9",
    "patient_color": "#0891b2",
    "doctor_color": "#059669",
    "visit_color": "#d97706",
    "record_color": "#7c3aed",
}

# ------------- DB Helpers -------------
def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error connecting: {err}")
        return None

def init_db():
    conn = get_connection()
    if conn is None:
        return
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(50) NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INT,
            gender VARCHAR(10),
            diagnosis VARCHAR(255),
            admission_date DATE,
            status VARCHAR(50)
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            specialisation VARCHAR(50),
            department VARCHAR(100)
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT,
            visit_date DATE,
            complaint TEXT,
            assigned_doctor_id INT,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE SET NULL,
            FOREIGN KEY (assigned_doctor_id) REFERENCES doctors(id) ON DELETE SET NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS medical_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            visit_id INT,
            record_type VARCHAR(100),
            notes TEXT,
            FOREIGN KEY (visit_id) REFERENCES visits(id) ON DELETE CASCADE
        )
    ''')
    try:
        cur.execute("""
            SELECT COUNT(1)
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE table_schema=DATABASE() AND table_name='patients' AND index_name='idx_patient_name'
        """)
        if cur.fetchone()[0] == 0:
            cur.execute('CREATE INDEX idx_patient_name ON patients(name)')
    except Exception:
        pass
    conn.commit()
    cur.close()
    conn.close()

# ------------- Utility Functions -------------
def clear_content():
    for w in content_frame.winfo_children():
        w.destroy()

def styled_label(parent, text, size=11, weight="normal", color=None, **kwargs):
    c = color or COLORS["text_primary"]
    return tb.Label(parent, text=text, font=("Segoe UI", size, weight), foreground=c, **kwargs)

def styled_button(parent, text, style="primary", command=None, width=None, **kwargs):
    return tb.Button(parent, text=text, bootstyle=style, command=command, width=width, **kwargs)

def light_card(parent, padding=20, **kwargs):
    frame = tk.Frame(parent, bg=COLORS["bg_card"], highlightbackground=COLORS["border"],
                     highlightthickness=1, bd=0, **kwargs)
    inner = tk.Frame(frame, bg=COLORS["bg_card"])
    inner.pack(fill="both", expand=True, padx=padding, pady=padding)
    return frame, inner

def glass_card(parent, color_accent, padding=20, **kwargs):
    frame = tk.Frame(parent, bg=COLORS["bg_card"], bd=0, **kwargs)
    bar = tk.Frame(frame, bg=color_accent, height=4)
    bar.pack(fill="x", side="top")
    bar.pack_propagate(False)
    inner = tk.Frame(frame, bg=COLORS["bg_card"])
    inner.pack(fill="both", expand=True, padx=padding, pady=padding)
    return frame, inner

def styled_entry(parent, placeholder="", show_char=None, **kwargs):
    if show_char:
        ent = tb.Entry(parent, show=show_char, **kwargs)
    else:
        ent = tb.Entry(parent, **kwargs)
    return ent

def hover_effect(widget, normal_bg, hover_bg):
    def on_enter(e):
        widget.config(bg=hover_bg)
    def on_leave(e):
        widget.config(bg=normal_bg)
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

# ------------- Fetch FK Options -------------
def fetch_fk_options(fk_table, display_columns, id_column="id"):
    options = []
    try:
        conn = get_connection()
        if conn is None:
            return options
        cur = conn.cursor()
        cols = ", ".join([id_column] + display_columns)
        cur.execute(f"SELECT {cols} FROM {fk_table} ORDER BY {id_column} DESC LIMIT 100")
        rows = cur.fetchall()
        for row in rows:
            rid = row[0]
            display_parts = [str(r) if r else "N/A" for r in row[1:]]
            display = f"ID:{rid} | " + " | ".join(display_parts)
            options.append((display, rid))
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error fetching FK options: {e}")
    return options

# ------------- Auth -------------
def signup_user(uname, pwd):
    if not uname or not pwd:
        messagebox.showwarning("Input Error", "Enter username and password")
        return False
    conn = get_connection()
    if conn is None:
        return False
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (%s,%s)", (uname, pwd))
        conn.commit()
        messagebox.showinfo("Success", "User registered! You can login now.")
        return True
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def change_password(username):
    new = simpledialog.askstring("Change Password", "Enter new password:", show="*")
    if not new:
        return
    conn = get_connection()
    if conn is None:
        return
    cur = conn.cursor()
    try:
        cur.execute("UPDATE users SET password=%s WHERE username=%s", (new, username))
        conn.commit()
        messagebox.showinfo("Success", "Password changed.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        cur.close()
        conn.close()

# ------------- Field Definitions -------------
def get_fields_for_table(table_name):
    if table_name == "patients":
        return [
            ("Name", "text"),
            ("Age", "number"),
            ("Gender", "dropdown:Male,Female,Other"),
            ("Diagnosis", "text"),
            ("Admission Date", "date"),
            ("Status", "dropdown:Admitted,Discharged,Under Treatment,Deceased")
        ]
    if table_name == "doctors":
        return [
            ("Name", "text"),
            ("Specialisation", "dropdown:Cardiology,Neurology,Orthopedics,Pediatrics,General,Dermatology,Radiology,Other"),
            ("Department", "text")
        ]
    if table_name == "visits":
        return [
            ("Patient ID", "fk:patients:name,age,gender"),
            ("Visit Date", "date"),
            ("Complaint", "text"),
            ("Assigned Doctor ID", "fk:doctors:name,specialisation,department")
        ]
    if table_name == "medical_records":
        return [
            ("Visit ID", "fk:visits:patient_id,visit_date,complaint"),
            ("Record Type", "dropdown:Prescription,Lab Report,Imaging,Surgical Notes,Discharge Summary,Other"),
            ("Notes", "text")
        ]
    return []

def get_field_names(table_name):
    return [f[0] for f in get_fields_for_table(table_name)]

# ------------- Build Dynamic Form Fields -------------
def build_form_field(container, field_label, field_type):
    fk_map = {}
    icons = {"date": "📅", "number": "🔢"}
    icon = icons.get(field_type, "")
    if field_type.startswith("dropdown"):
        icon = "▼"
    elif field_type.startswith("fk"):
        icon = "🔗"

    lbl = tk.Label(container, text=f"  {icon}  {field_label}",
                   font=("Segoe UI", 10, "bold"), bg=COLORS["bg_card"],
                   fg=COLORS["text_secondary"], anchor="w")
    lbl.pack(fill="x", pady=(10, 4))

    widget = None
    if field_type == "date":
        widget = DateEntry(container, dateformat="%Y-%m-%d", width=20)
        widget.pack(fill="x", pady=(0, 2), ipady=4)
    elif field_type.startswith("dropdown"):
        options = field_type.split(":")[1].split(",")
        widget = tb.Combobox(container, values=options, state="readonly", width=30)
        widget.pack(fill="x", pady=(0, 2), ipady=4)
    elif field_type.startswith("fk"):
        parts = field_type.split(":")
        fk_table = parts[1]
        fk_display_cols = parts[2].split(",")
        fk_options = fetch_fk_options(fk_table, fk_display_cols)
        if fk_options:
            display_list = [opt[0] for opt in fk_options]
            fk_map = {opt[0]: opt[1] for opt in fk_options}
            widget = tb.Combobox(container, values=display_list, state="readonly", width=45)
            widget.pack(fill="x", pady=(0, 2), ipady=4)
        else:
            widget = tb.Entry(container)
            widget.insert(0, "No records found - enter ID manually")
            widget.pack(fill="x", pady=(0, 2))
    elif field_type == "number":
        def validate_num(P):
            return P.isdigit() or P == ""
        vcmd = container.register(validate_num)
        widget = tb.Entry(container, validate="key", validatecommand=(vcmd, '%P'))
        widget.pack(fill="x", pady=(0, 2))
    else:
        widget = tb.Entry(container)
        widget.pack(fill="x", pady=(0, 2))

    return lbl, widget, fk_map

def get_widget_value(widget, field_type, fk_map):
    try:
        if field_type == "date":
            if hasattr(widget, 'get_date'):
                return widget.get_date()
            elif hasattr(widget, 'entry') and hasattr(widget.entry, 'get'):
                return widget.entry.get().strip()
            elif hasattr(widget, 'get'):
                return widget.get().strip()
            return ""
        elif field_type.startswith("fk"):
            if hasattr(widget, 'get'):
                selected = widget.get()
                if selected in fk_map:
                    return str(fk_map[selected])
                return selected
            return ""
        elif field_type.startswith("dropdown"):
            if hasattr(widget, 'get'):
                return widget.get()
            return ""
        else:
            if hasattr(widget, 'get'):
                return widget.get().strip()
            return ""
    except Exception:
        return ""

# ------------- Count Queries -------------
def get_counts():
    counts = {"patients": 0, "doctors": 0, "visits": 0, "medical_records": 0}
    try:
        conn = get_connection()
        if conn is None:
            return counts
        cur = conn.cursor()
        for k in list(counts.keys()):
            try:
                cur.execute(f"SELECT COUNT(1) FROM {k}")
                r = cur.fetchone()
                counts[k] = r[0] if r and r[0] is not None else 0
            except Exception:
                counts[k] = 0
        cur.close()
        conn.close()
    except Exception:
        pass
    return counts

def get_recent_patients(limit=5):
    rows = []
    try:
        conn = get_connection()
        if conn is None:
            return rows
        cur = conn.cursor()
        cur.execute(f"SELECT id, name, age, gender, diagnosis, status FROM patients ORDER BY id DESC LIMIT {limit}")
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        pass
    return rows

def get_recent_visits(limit=5):
    rows = []
    try:
        conn = get_connection()
        if conn is None:
            return rows
        cur = conn.cursor()
        cur.execute("""
            SELECT v.id, p.name, d.name, v.visit_date, v.complaint 
            FROM visits v 
            LEFT JOIN patients p ON v.patient_id = p.id 
            LEFT JOIN doctors d ON v.assigned_doctor_id = d.id 
            ORDER BY v.id DESC LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        pass
    return rows

# =====================================================================
#                         LOGIN SCREEN
# =====================================================================
def show_login_screen():
    for w in root.winfo_children():
        w.destroy()

    bg = tk.Frame(root, bg=COLORS["bg_main"])
    bg.pack(fill="both", expand=True)

    left = tk.Frame(bg, bg=COLORS["bg_sidebar"], width=600)
    left.pack(side="left", fill="both")
    left.pack_propagate(False)

    left_inner = tk.Frame(left, bg=COLORS["bg_sidebar"])
    left_inner.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(left_inner, text="🏥", font=("Segoe UI", 72), bg=COLORS["bg_sidebar"],
             fg=COLORS["accent_cyan"]).pack()
    tk.Label(left_inner, text="HOSPITAL", font=("Segoe UI", 36, "bold"), bg=COLORS["bg_sidebar"],
             fg=COLORS["text_primary"]).pack(pady=(10, 0))
    tk.Label(left_inner, text="MANAGEMENT SYSTEM", font=("Segoe UI", 14), bg=COLORS["bg_sidebar"],
             fg=COLORS["text_muted"]).pack()
    tk.Label(left_inner, text="━━━━━━━━━━━━━━━━━━━━", font=("Segoe UI", 12), bg=COLORS["bg_sidebar"],
             fg=COLORS["accent_cyan"]).pack(pady=20)
    tk.Label(left_inner, text="Manage patients, doctors, visits\nand medical records efficiently",
             font=("Segoe UI", 11), bg=COLORS["bg_sidebar"],
             fg=COLORS["text_secondary"], justify="center").pack()

    right = tk.Frame(bg, bg=COLORS["bg_main"])
    right.pack(side="left", fill="both", expand=True)

    form = tk.Frame(right, bg=COLORS["bg_main"])
    form.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(form, text="Welcome Back", font=("Segoe UI", 28, "bold"),
             bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack(anchor="w")
    tk.Label(form, text="Sign in to continue to your dashboard",
             font=("Segoe UI", 11), bg=COLORS["bg_main"],
             fg=COLORS["text_muted"]).pack(anchor="w", pady=(4, 30))

    tk.Label(form, text="  👤  Username", font=("Segoe UI", 10, "bold"),
             bg=COLORS["bg_main"], fg=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 4))
    username_entry = tb.Entry(form, width=40)
    username_entry.pack(fill="x", pady=(0, 16), ipady=6)

    tk.Label(form, text="  🔑  Password", font=("Segoe UI", 10, "bold"),
             bg=COLORS["bg_main"], fg=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 4))
    password_entry = tb.Entry(form, show="•", width=40)
    password_entry.pack(fill="x", pady=(0, 24), ipady=6)

    def do_login():
        uname = username_entry.get().strip()
        pwd = password_entry.get().strip()
        if not uname or not pwd:
            messagebox.showwarning("Input Error", "Enter username and password")
            return
        conn = get_connection()
        if conn is None:
            return
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (uname, pwd))
        if cur.fetchone():
            cur.close()
            conn.close()
            global current_user
            current_user = uname
            build_main_ui()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
            cur.close()
            conn.close()

    def do_signup():
        signup_user(username_entry.get().strip(), password_entry.get().strip())

    login_btn = tk.Button(form, text="🔓  Sign In", font=("Segoe UI", 12, "bold"),
                          bg=COLORS["accent_blue"], fg="white", bd=0, cursor="hand2",
                          activebackground="#1d4ed8", activeforeground="white",
                          command=do_login, padx=20, pady=10)
    login_btn.pack(fill="x", pady=(0, 12))
    hover_effect(login_btn, COLORS["accent_blue"], "#1d4ed8")

    sign_row = tk.Frame(form, bg=COLORS["bg_main"])
    sign_row.pack()
    tk.Label(sign_row, text="Don't have an account?", font=("Segoe UI", 10),
             bg=COLORS["bg_main"], fg=COLORS["text_muted"]).pack(side="left")
    signup_btn = tk.Button(sign_row, text=" Sign Up", font=("Segoe UI", 10, "bold"),
                           bg=COLORS["bg_main"], fg=COLORS["accent_cyan"], bd=0, cursor="hand2",
                           activebackground=COLORS["bg_main"], activeforeground=COLORS["accent_cyan"],
                           command=do_signup)
    signup_btn.pack(side="left")

# =====================================================================
#                      MAIN UI (SIDEBAR + CONTENT)
# =====================================================================
content_frame = None

def build_main_ui():
    for w in root.winfo_children():
        w.destroy()

    topbar = tk.Frame(root, bg=COLORS["bg_sidebar"], height=56)
    topbar.pack(side="top", fill="x")
    topbar.pack_propagate(False)

    logo_frame = tk.Frame(topbar, bg=COLORS["bg_sidebar"])
    logo_frame.pack(side="left", padx=20)
    tk.Label(logo_frame, text="🏥", font=("Segoe UI", 20), bg=COLORS["bg_sidebar"],
             fg=COLORS["accent_cyan"]).pack(side="left")
    tk.Label(logo_frame, text=" HOSPITAL DBMS", font=("Segoe UI", 14, "bold"),
             bg=COLORS["bg_sidebar"], fg=COLORS["text_primary"]).pack(side="left", padx=(8, 0))

    user_frame = tk.Frame(topbar, bg=COLORS["bg_sidebar"])
    user_frame.pack(side="right", padx=20)
    tk.Label(user_frame, text=f"👤 {current_user}", font=("Segoe UI", 11),
             bg=COLORS["bg_sidebar"], fg=COLORS["text_secondary"]).pack(side="left", padx=(0, 12))
    
    def do_logout():
        global current_user
        current_user = None
        show_login_screen()

    logout_btn = tk.Button(user_frame, text="⏻ Logout", font=("Segoe UI", 10, "bold"),
                           bg=COLORS["accent_red"], fg="white", bd=0, cursor="hand2",
                           activebackground="#b91c1c", padx=14, pady=4, command=do_logout)
    logout_btn.pack(side="left")
    hover_effect(logout_btn, COLORS["accent_red"], "#b91c1c")

    main_area = tk.Frame(root, bg=COLORS["bg_main"])
    main_area.pack(fill="both", expand=True)

    sidebar = tk.Frame(main_area, bg=COLORS["bg_sidebar"], width=240)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="  NAVIGATION", font=("Segoe UI", 9, "bold"),
             bg=COLORS["bg_sidebar"], fg=COLORS["text_muted"]).pack(anchor="w", padx=20, pady=(20, 10))

    nav_items = [
        ("📊  Dashboard", "dashboard"),
        ("🧑  Patients", "patients"),
        ("👨‍  Doctors", "doctors"),
        ("🏥  Visits", "visits"),
        ("📋  Medical Records", "medical_records"),
    ]

    global sidebar_btns
    sidebar_btns = {}

    for label, page in nav_items:
        btn = tk.Label(sidebar, text=label, font=("Segoe UI", 11),
                       bg=COLORS["bg_sidebar"], fg=COLORS["text_secondary"],
                       anchor="w", padx=20, pady=10, cursor="hand2")
        btn.pack(fill="x", pady=1)
        sidebar_btns[page] = btn

        def make_handler(p):
            def handler(e):
                global current_page
                current_page = p
                update_sidebar()
                navigate_to(p)
            return handler
        btn.bind("<Button-1>", make_handler(page))
        hover_effect(btn, COLORS["bg_sidebar"], COLORS["hover"])

    tk.Label(sidebar, text="━━━━━━━━━━━━━━━━━━━", font=("Segoe UI", 8),
             bg=COLORS["bg_sidebar"], fg=COLORS["border"]).pack(side="bottom", pady=10)
    tk.Label(sidebar, text=f"v2.0  |  {current_user}", font=("Segoe UI", 8),
             bg=COLORS["bg_sidebar"], fg=COLORS["text_muted"]).pack(side="bottom", pady=4)

    global content_frame
    content_frame = tk.Frame(main_area, bg=COLORS["bg_main"])
    content_frame.pack(side="left", fill="both", expand=True)

    update_sidebar()
    navigate_to("dashboard")

def update_sidebar():
    for page, btn in sidebar_btns.items():
        if page == current_page:
            btn.config(bg=COLORS["accent_blue"], fg="white", font=("Segoe UI", 11, "bold"))
            hover_effect(btn, COLORS["accent_blue"], "#1d4ed8")
        else:
            btn.config(bg=COLORS["bg_sidebar"], fg=COLORS["text_secondary"], font=("Segoe UI", 11))
            hover_effect(btn, COLORS["bg_sidebar"], COLORS["hover"])

def navigate_to(page):
    clear_content()
    if page == "dashboard":
        page_dashboard()
    elif page == "patients":
        page_table("patients")
    elif page == "doctors":
        page_table("doctors")
    elif page == "visits":
        page_table("visits")
    elif page == "medical_records":
        page_table("medical_records")

# =====================================================================
#                         DASHBOARD PAGE
# =====================================================================
def page_dashboard():
    canvas = tk.Canvas(content_frame, bg=COLORS["bg_main"], highlightthickness=0)
    scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable = tk.Frame(canvas, bg=COLORS["bg_main"])
    canvas.create_window((0, 0), window=scrollable, anchor="nw", tags="inner")

    def on_configure(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig("inner", width=e.width)
    scrollable.bind("<Configure>", on_configure)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig("inner", width=e.width))

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    pad = tk.Frame(scrollable, bg=COLORS["bg_main"])
    pad.pack(fill="both", expand=True, padx=30, pady=25)

    header = tk.Frame(pad, bg=COLORS["bg_main"])
    header.pack(fill="x", pady=(0, 20))
    tk.Label(header, text="📊  Dashboard", font=("Segoe UI", 24, "bold"),
             bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack(side="left")
    tk.Label(header, text=f"  Welcome, {current_user}", font=("Segoe UI", 13),
             bg=COLORS["bg_main"], fg=COLORS["text_muted"]).pack(side="left", padx=(10, 0), pady=(8, 0))

    stats_row = tk.Frame(pad, bg=COLORS["bg_main"])
    stats_row.pack(fill="x", pady=(0, 20))

    counts = get_counts()
    stats = [
        ("🧑", "Total Patients", counts.get("patients", 0), COLORS["patient_color"], "patients"),
        ("👨‍", "Total Doctors", counts.get("doctors", 0), COLORS["doctor_color"], "doctors"),
        ("🏥", "Total Visits", counts.get("visits", 0), COLORS["visit_color"], "visits"),
        ("📋", "Medical Records", counts.get("medical_records", 0), COLORS["record_color"], "medical_records"),
    ]

    for i, (icon, title, count, color, page) in enumerate(stats):
        card, inner_c = glass_card(stats_row, color, padding=16)
        card.grid(row=0, column=i, padx=6, pady=4, sticky="nsew")

        top = tk.Frame(inner_c, bg=COLORS["bg_card"])
        top.pack(fill="x")
        tk.Label(top, text=icon, font=("Segoe UI", 28), bg=COLORS["bg_card"],
                 fg=color).pack(side="left")
        tk.Label(top, text=f"  {title}", font=("Segoe UI", 10, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(side="left", padx=(6, 0), anchor="s")

        tk.Label(inner_c, text=str(count), font=("Segoe UI", 32, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(anchor="w", pady=(8, 0))

        def make_nav(p):
            def handler(e):
                global current_page
                current_page = p
                update_sidebar()
                navigate_to(p)
            return handler

        nav = tk.Label(inner_c, text="View All →", font=("Segoe UI", 9, "underline"),
                       bg=COLORS["bg_card"], fg=color, cursor="hand2")
        nav.pack(anchor="e", pady=(8, 0))
        nav.bind("<Button-1>", make_nav(page))

    stats_row.columnconfigure(0, weight=1)
    stats_row.columnconfigure(1, weight=1)
    stats_row.columnconfigure(2, weight=1)
    stats_row.columnconfigure(3, weight=1)

    actions_frame, actions_inner = light_card(pad, padding=16)
    actions_frame.pack(fill="x", pady=(0, 20))

    tk.Label(actions_inner, text="⚡  Quick Actions", font=("Segoe UI", 14, "bold"),
             bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(anchor="w", pady=(0, 12))

    btn_row = tk.Frame(actions_inner, bg=COLORS["bg_card"])
    btn_row.pack(fill="x")

    action_btns = [
        ("➕ Add Patient", COLORS["patient_color"], lambda: open_add("patients")),
        ("➕ Add Doctor", COLORS["doctor_color"], lambda: open_add("doctors")),
        ("➕ New Visit", COLORS["visit_color"], lambda: open_add("visits")),
        ("➕ Add Record", COLORS["record_color"], lambda: open_add("medical_records")),
    ]

    for text, color, cmd in action_btns:
        btn = tk.Button(btn_row, text=text, font=("Segoe UI", 10, "bold"),
                        bg=color, fg="white", bd=0, cursor="hand2",
                        padx=16, pady=8, command=cmd)
        btn.pack(side="left", padx=(0, 10))
        hover_effect(btn, color, COLORS["hover"])

    recent_row = tk.Frame(pad, bg=COLORS["bg_main"])
    recent_row.pack(fill="both", expand=True)
    recent_row.columnconfigure(0, weight=1)
    recent_row.columnconfigure(1, weight=1)

    rp_card, rp_inner = light_card(recent_row, padding=16)
    rp_card.grid(row=0, column=0, padx=(0, 10), pady=4, sticky="nsew")

    tk.Label(rp_inner, text="🧑  Recent Patients", font=("Segoe UI", 13, "bold"),
             bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(anchor="w", pady=(0, 10))

    recent_patients = get_recent_patients(5)
    if recent_patients:
        for p in recent_patients:
            row = tk.Frame(rp_inner, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"  #{p[0]}  {p[1]}", font=("Segoe UI", 10, "bold"),
                     bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(side="left")
            status_colors = {"Admitted": COLORS["accent_green"], "Discharged": COLORS["accent_blue"],
                             "Under Treatment": COLORS["accent_orange"], "Deceased": COLORS["accent_red"]}
            sc = status_colors.get(str(p[5]) if p[5] else "", COLORS["text_muted"])
            tk.Label(row, text=f"  {p[5] if p[5] else 'N/A'}  ", font=("Segoe UI", 9, "bold"),
                     bg=sc, fg="white").pack(side="right", padx=4)
    else:
        tk.Label(rp_inner, text="No patients yet", font=("Segoe UI", 10),
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(anchor="w")

    rv_card, rv_inner = light_card(recent_row, padding=16)
    rv_card.grid(row=0, column=1, padx=(10, 0), pady=4, sticky="nsew")

    tk.Label(rv_inner, text="🏥  Recent Visits", font=("Segoe UI", 13, "bold"),
             bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(anchor="w", pady=(0, 10))

    recent_visits = get_recent_visits(5)
    if recent_visits:
        for v in recent_visits:
            row = tk.Frame(rv_inner, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=2)
            patient = v[1] if v[1] else "Unknown"
            doctor = v[2] if v[2] else "Unassigned"
            tk.Label(row, text=f"  #{v[0]}  {patient} → Dr. {doctor}", font=("Segoe UI", 10, "bold"),
                     bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(side="left")
            date_str = str(v[3]) if v[3] else "N/A"
            tk.Label(row, text=f"  {date_str}  ", font=("Segoe UI", 9),
                     bg=COLORS["text_muted"], fg="white").pack(side="right", padx=4)
    else:
        tk.Label(rv_inner, text="No visits yet", font=("Segoe UI", 10),
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(anchor="w")

# =====================================================================
#                     TABLE PAGE
# =====================================================================
def page_table(table_name):
    pad = tk.Frame(content_frame, bg=COLORS["bg_main"])
    pad.pack(fill="both", expand=True, padx=30, pady=25)

    icons = {"patients": "🧑", "doctors": "👨‍⚕", "visits": "🏥", "medical_records": "📋"}
    colors = {"patients": COLORS["patient_color"], "doctors": COLORS["doctor_color"],
              "visits": COLORS["visit_color"], "medical_records": COLORS["record_color"]}
    titles = {"patients": "Patients", "doctors": "Doctors", "visits": "Visits", "medical_records": "Medical Records"}

    ic = icons.get(table_name, "📋")
    ac = colors.get(table_name, COLORS["accent_blue"])
    title = titles.get(table_name, table_name)

    header = tk.Frame(pad, bg=COLORS["bg_main"])
    header.pack(fill="x", pady=(0, 16))
    tk.Label(header, text=f"{ic}  {title}", font=("Segoe UI", 24, "bold"),
             bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack(side="left")

    btn_actions = tk.Frame(header, bg=COLORS["bg_main"])
    btn_actions.pack(side="right")

    fields = get_fields_for_table(table_name)

    def make_btn(text, color, command):
        b = tk.Button(btn_actions, text=text, font=("Segoe UI", 10, "bold"),
                      bg=color, fg="white", bd=0, cursor="hand2",
                      padx=14, pady=6, command=command)
        b.pack(side="left", padx=(8, 0))
        hover_effect(b, color, COLORS["hover"])
        return b

    make_btn("➕ Add New", COLORS["accent_green"], lambda: open_add(table_name))
    make_btn("✏ Update", COLORS["accent_orange"], lambda: open_update(table_name))
    make_btn("🗑 Delete", COLORS["accent_red"], lambda: open_delete(table_name))

    table_card, table_inner = light_card(pad, padding=12)
    table_card.pack(fill="both", expand=True)

    field_names = [f[0] for f in fields]
    coldata = [{"text": "ID", "stretch": False}] + [{"text": f} for f in field_names]
    rows = []
    try:
        conn = get_connection()
        if conn is not None:
            cur = conn.cursor()
            cols = ", ".join([f.lower().replace(" ", "_") for f in field_names])
            cur.execute(f"SELECT id, {cols} FROM {table_name}")
            rows = cur.fetchall()
            cur.close()
            conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))

    count_bar = tk.Frame(table_inner, bg=COLORS["bg_card"])
    count_bar.pack(fill="x", pady=(0, 8))
    tk.Label(count_bar, text=f"  📊  Total: {len(rows)} records", font=("Segoe UI", 10),
             bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(side="left")

    table = Tableview(table_inner, coldata=coldata, rowdata=rows, paginated=True, pagesize=15, searchable=True)
    table.pack(fill="both", expand=True)

# =====================================================================
#                     CRUD: ADD RECORD
# =====================================================================
def open_add(table_name):
    fields = get_fields_for_table(table_name)
    icons = {"patients": "🧑", "doctors": "👨‍⚕", "visits": "🏥", "medical_records": "📋"}
    colors = {"patients": COLORS["patient_color"], "doctors": COLORS["doctor_color"],
              "visits": COLORS["visit_color"], "medical_records": COLORS["record_color"]}
    titles = {"patients": "Patient", "doctors": "Doctor", "visits": "Visit", "medical_records": "Record"}

    ic = icons.get(table_name, "➕")
    ac = colors.get(table_name, COLORS["accent_blue"])
    title = titles.get(table_name, table_name)

    win = tb.Toplevel(root)
    win.title(f"Add {title}")
    win.geometry("580x720")
    win.configure(bg=COLORS["bg_main"])

    hdr = tk.Frame(win, bg=COLORS["bg_sidebar"], height=60)
    hdr.pack(fill="x")
    hdr.pack_propagate(False)
    tk.Label(hdr, text=f"  {ic}  Add New {title}", font=("Segoe UI", 16, "bold"),
             bg=COLORS["bg_sidebar"], fg=COLORS["text_primary"]).pack(side="left", padx=20)

    body = tk.Frame(win, bg=COLORS["bg_card"])
    body.pack(fill="both", expand=True, padx=24, pady=16)

    canvas = tk.Canvas(body, bg=COLORS["bg_card"], highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    form_frame = tk.Frame(canvas, bg=COLORS["bg_card"])
    canvas.create_window((0, 0), window=form_frame, anchor="nw")

    def on_conf(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig("all", width=e.width)
    form_frame.bind("<Configure>", on_conf)

    widgets = []
    fk_maps = []

    for label, ftype in fields:
        _, w, fmap = build_form_field(form_frame, label, ftype)
        widgets.append(w)
        fk_maps.append(fmap)

    btn_bar = tk.Frame(win, bg=COLORS["bg_main"])
    btn_bar.pack(fill="x", padx=24, pady=(0, 16))

    def save():
        vals = []
        for i, (label, ftype) in enumerate(fields):
            val = get_widget_value(widgets[i], ftype, fk_maps[i])
            if not val:
                messagebox.showwarning("Input Error", f"Please fill: {label}")
                return
            if ftype == "date":
                if isinstance(val, str):
                    try:
                        val = datetime.strptime(val, "%Y-%m-%d").date()
                    except Exception:
                        messagebox.showerror("Input Error", f"Invalid date for {label}")
                        return
            if ftype == "number":
                try:
                    val = int(val)
                except Exception:
                    messagebox.showerror("Input Error", f"Invalid number for {label}")
                    return
            vals.append(val)

        col_names = [label.lower().replace(" ", "_") for label, _ in fields]
        cols = ", ".join(col_names)
        placeholders = ", ".join(["%s"] * len(fields))
        query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
        try:
            conn = get_connection()
            if conn is None:
                return
            cur = conn.cursor()
            cur.execute(query, vals)
            conn.commit()
            messagebox.showinfo("Success", f"✅ {title} added successfully!")
            win.destroy()
            navigate_to(current_page)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            try:
                cur.close()
                conn.close()
            except Exception:
                pass

    def refresh_fk():
        win.destroy()
        open_add(table_name)

    tk.Button(btn_bar, text="🔄 Refresh Lists", font=("Segoe UI", 10, "bold"),
              bg=COLORS["accent_purple"], fg="white", bd=0, cursor="hand2",
              padx=16, pady=8, command=refresh_fk).pack(side="left")
    tk.Button(btn_bar, text="✖ Cancel", font=("Segoe UI", 10, "bold"),
              bg=COLORS["text_muted"], fg="white", bd=0, cursor="hand2",
              padx=16, pady=8, command=win.destroy).pack(side="right")
    tk.Button(btn_bar, text="💾 Save Record", font=("Segoe UI", 10, "bold"),
              bg=COLORS["accent_green"], fg="white", bd=0, cursor="hand2",
              padx=16, pady=8, command=save).pack(side="right", padx=(0, 10))

# =====================================================================
#                     CRUD: UPDATE RECORD
# =====================================================================
def open_update(table_name):
    fields = get_fields_for_table(table_name)
    field_names = [f[0] for f in fields]
    icons = {"patients": "🧑", "doctors": "👨‍", "visits": "🏥", "medical_records": "📋"}
    titles = {"patients": "Patient", "doctors": "Doctor", "visits": "Visit", "medical_records": "Record"}

    ic = icons.get(table_name, "✏")
    title = titles.get(table_name, table_name)

    win = tb.Toplevel(root)
    win.title(f"Update {title}")
    win.geometry("580x800")
    win.configure(bg=COLORS["bg_main"])

    hdr = tk.Frame(win, bg=COLORS["bg_sidebar"], height=60)
    hdr.pack(fill="x")
    hdr.pack_propagate(False)
    tk.Label(hdr, text=f"  ✏  Update {title}", font=("Segoe UI", 16, "bold"),
             bg=COLORS["bg_sidebar"], fg=COLORS["text_primary"]).pack(side="left", padx=20)

    id_frame = tk.Frame(win, bg=COLORS["bg_card"])
    id_frame.pack(fill="x", padx=24, pady=(16, 8))
    tk.Label(id_frame, text="  🔍  Enter Record ID:", font=("Segoe UI", 11, "bold"),
             bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(side="left", padx=(10, 10))
    id_entry = tb.Entry(id_frame, width=10)
    id_entry.pack(side="left", ipady=4)

    load_status = tk.Label(id_frame, text="", font=("Segoe UI", 10),
                           bg=COLORS["bg_card"], fg=COLORS["accent_green"])
    load_status.pack(side="left", padx=10)

    body = tk.Frame(win, bg=COLORS["bg_card"])
    body.pack(fill="both", expand=True, padx=24, pady=(8, 8))

    canvas = tk.Canvas(body, bg=COLORS["bg_card"], highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    form_frame = tk.Frame(canvas, bg=COLORS["bg_card"])
    canvas.create_window((0, 0), window=form_frame, anchor="nw")

    def on_conf(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
    form_frame.bind("<Configure>", on_conf)

    widgets = []
    fk_maps = []

    for label, ftype in fields:
        _, w, fmap = build_form_field(form_frame, label, ftype)
        widgets.append(w)
        fk_maps.append(fmap)

    def load_data():
        cid = id_entry.get().strip()
        if not cid.isdigit():
            messagebox.showerror("Input Error", "Enter valid ID")
            return
        try:
            conn = get_connection()
            if conn is None:
                return
            cur = conn.cursor()
            cols = ", ".join([f.lower().replace(" ", "_") for f in field_names])
            cur.execute(f"SELECT {cols} FROM {table_name} WHERE id=%s", (cid,))
            row = cur.fetchone()
            if not row:
                messagebox.showerror("Not Found", "No record found")
                load_status.config(text="❌ Not Found", fg=COLORS["accent_red"])
                return

            for i, (label, ftype) in enumerate(fields):
                val = row[i]
                if val is None:
                    val = ""
                if ftype == "date":
                    if isinstance(val, datetime) or hasattr(val, 'strftime'):
                        try:
                            widgets[i].entry.delete(0, tk.END)
                            widgets[i].entry.insert(0, val.strftime("%Y-%m-%d"))
                        except Exception:
                            pass
                elif ftype.startswith("dropdown"):
                    widgets[i].set(str(val))
                elif ftype.startswith("fk"):
                    try:
                        options = widgets[i]['values']
                        for opt in options:
                            if f"ID:{val}" in str(opt):
                                widgets[i].set(opt)
                                break
                    except Exception:
                        pass
                else:
                    widgets[i].delete(0, tk.END)
                    widgets[i].insert(0, str(val))

            load_status.config(text="✅ Data Loaded", fg=COLORS["accent_green"])
        except Exception as e:
            messagebox.showerror("Error", str(e))
            load_status.config(text="❌ Error", fg=COLORS["accent_red"])
        finally:
            try:
                cur.close()
                conn.close()
            except Exception:
                pass

    def save_update():
        cid = id_entry.get().strip()
        if not cid.isdigit():
            messagebox.showerror("Input Error", "Enter valid ID")
            return
        vals = []
        for i, (label, ftype) in enumerate(fields):
            val = get_widget_value(widgets[i], ftype, fk_maps[i])
            if not val:
                messagebox.showwarning("Input Error", f"Please fill: {label}")
                return
            if ftype == "date":
                if isinstance(val, str):
                    try:
                        val = datetime.strptime(val, "%Y-%m-%d").date()
                    except Exception:
                        messagebox.showerror("Input Error", f"Invalid date for {label}")
                        return
            if ftype == "number":
                try:
                    val = int(val)
                except Exception:
                    messagebox.showerror("Input Error", f"Invalid number for {label}")
                    return
            vals.append(val)

        placeholders = ", ".join([f"{f.lower().replace(' ','_')}=%s" for f in field_names])
        query = f"UPDATE {table_name} SET {placeholders} WHERE id=%s"
        try:
            conn = get_connection()
            if conn is None:
                return
            cur = conn.cursor()
            cur.execute(query, (*vals, cid))
            conn.commit()
            messagebox.showinfo("Updated", "✅ Record updated successfully!")
            win.destroy()
            navigate_to(current_page)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            try:
                cur.close()
                conn.close()
            except Exception:
                pass

    btn_bar = tk.Frame(win, bg=COLORS["bg_main"])
    btn_bar.pack(fill="x", padx=24, pady=(0, 16))

    tk.Button(id_frame, text="🔍 Load", font=("Segoe UI", 10, "bold"),
              bg=COLORS["accent_blue"], fg="white", bd=0, cursor="hand2",
              padx=12, pady=4, command=load_data).pack(side="left", padx=(6, 0))

    tk.Button(btn_bar, text="✖ Cancel", font=("Segoe UI", 10, "bold"),
              bg=COLORS["text_muted"], fg="white", bd=0, cursor="hand2",
              padx=16, pady=8, command=win.destroy).pack(side="right")
    tk.Button(btn_bar, text="💾 Save Update", font=("Segoe UI", 10, "bold"),
              bg=COLORS["accent_green"], fg="white", bd=0, cursor="hand2",
              padx=16, pady=8, command=save_update).pack(side="right", padx=(0, 10))

# =====================================================================
#                     CRUD: DELETE RECORD
# =====================================================================
def open_delete(table_name):
    titles = {"patients": "Patient", "doctors": "Doctor", "visits": "Visit", "medical_records": "Record"}
    icons = {"patients": "🧑", "doctors": "👨‍", "visits": "🏥", "medical_records": "📋"}
    title = titles.get(table_name, table_name)
    ic = icons.get(table_name, "🗑")

    win = tb.Toplevel(root)
    win.title(f"Delete {title}")
    win.geometry("420x280")
    win.configure(bg=COLORS["bg_main"])

    hdr = tk.Frame(win, bg=COLORS["accent_red"], height=50)
    hdr.pack(fill="x")
    hdr.pack_propagate(False)
    tk.Label(hdr, text=f"  🗑  Delete {title}", font=("Segoe UI", 15, "bold"),
             bg=COLORS["accent_red"], fg="white").pack(side="left", padx=20)

    body = tk.Frame(win, bg=COLORS["bg_card"])
    body.pack(fill="both", expand=True, padx=24, pady=16)

    tk.Label(body, text="⚠️  Warning: This action cannot be undone", font=("Segoe UI", 10),
             bg=COLORS["bg_card"], fg=COLORS["accent_orange"]).pack(anchor="w", pady=(0, 12))
    tk.Label(body, text="Enter Record ID to Delete:", font=("Segoe UI", 11, "bold"),
             bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(anchor="w")
    id_entry = tb.Entry(body, width=15)
    id_entry.pack(fill="x", pady=(6, 16), ipady=4)

    def do_delete():
        cid = id_entry.get().strip()
        if not cid.isdigit():
            messagebox.showerror("Input Error", "Enter valid ID")
            return
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {title} ID {cid}?")
        if not confirm:
            return
        try:
            conn = get_connection()
            if conn is None:
                return
            cur = conn.cursor()
            cur.execute(f"DELETE FROM {table_name} WHERE id=%s", (cid,))
            conn.commit()
            if cur.rowcount > 0:
                messagebox.showinfo("Deleted", f"✅ Record ID {cid} deleted.")
            else:
                messagebox.showwarning("Not Found", f"No record found with ID {cid}")
            win.destroy()
            navigate_to(current_page)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            try:
                cur.close()
                conn.close()
            except Exception:
                pass

    btn_bar = tk.Frame(body, bg=COLORS["bg_card"])
    btn_bar.pack(fill="x")
    tk.Button(btn_bar, text="🗑 Delete Permanently", font=("Segoe UI", 10, "bold"),
              bg=COLORS["accent_red"], fg="white", bd=0, cursor="hand2",
              padx=16, pady=8, command=do_delete).pack(side="right")
    tk.Button(btn_bar, text="✖ Cancel", font=("Segoe UI", 10, "bold"),
              bg=COLORS["text_muted"], fg="white", bd=0, cursor="hand2",
              padx=16, pady=8, command=win.destroy).pack(side="right", padx=(0, 10))

# =====================================================================
#                         START APP
# =====================================================================
def main():
    global root
    root = tb.Window(themename="litera")  # Light theme
    root.title("🏥 Hospital Management System")
    root.geometry("1920x1080")
    root.minsize(1400, 800)
    root.state("zoomed")

    init_db()
    show_login_screen()
    root.mainloop()

if __name__ == "__main__":
    main()