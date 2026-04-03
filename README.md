# 🏥 Hospital Management System

A modern, fully-featured **Hospital Management System** built with Python,
Tkinter, ttkbootstrap, and MySQL. Features a clean **light-themed UI**
with a professional sidebar layout optimized for **1920×1080** displays.

---

## 📸 Features

- 🔐 **Login & Signup** system with user authentication
- 📊 **Dashboard** with live stats, quick actions, and recent activity
- 🧑 **Patient Management** — Add, View, Update, Delete patients
- 👨‍⚕ **Doctor Management** — Manage doctor profiles and specialisations
- 🏥 **Visit Tracking** — Record and manage patient visits
- 📋 **Medical Records** — Link lab reports, prescriptions to visits
- 📅 **Date Picker** — Built-in calendar date selector
- 🔗 **Foreign Key Dropdowns** — Select existing patients/doctors from dropdown
- 🔍 **Searchable Tables** — Paginated, searchable data tables
- ⚡ **Quick Actions** — One-click add from the dashboard
- 🌟 **Light Theme** — Clean, professional clinical UI

---

## 🗂️ Project Structure
Hospital_Management-DBMS/
├── hospital_mgmt_ui.py # Main application (single file)
├── requirements.txt # Python dependencies
└── README.md # Project documentation

text


---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.x | Core language |
| Tkinter | GUI framework |
| ttkbootstrap | Modern themed widgets |
| MySQL | Database backend |
| mysql-connector-python | MySQL Python driver |
| Pillow | Image support for ttkbootstrap |

---

## ⚙️ Prerequisites

Before running the app, ensure you have:

- ✅ Python 3.10+ installed (recommended: 3.13)
- ✅ MySQL Server 8.0+ running locally
- ✅ pip package manager

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/Hospital_Management-DBMS.git
cd Hospital_Management-DBMS
2. Create a Virtual Environment (Optional but Recommended)
Bash

# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
3. Install Dependencies
Bash

pip install -r requirements.txt
4. Configure MySQL Database
Open hospital_mgmt_ui.py and update the DB_CONFIG section:

Python

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",  # ← Change this
    "database": "hospital_db"
}
The app will automatically create all required tables on first run.

5. Run the Application
Bash

python hospital_mgmt_ui.py
🗄️ Database Schema
The system automatically creates the following tables in hospital_db:

SQL

users
├── id          INT AUTO_INCREMENT PRIMARY KEY
├── username    VARCHAR(50) UNIQUE NOT NULL
└── password    VARCHAR(50) NOT NULL

patients
├── id              INT AUTO_INCREMENT PRIMARY KEY
├── name            VARCHAR(100) NOT NULL
├── age             INT
├── gender          VARCHAR(10)
├── diagnosis       VARCHAR(255)
├── admission_date  DATE
└── status          VARCHAR(50)

doctors
├── id              INT AUTO_INCREMENT PRIMARY KEY
├── name            VARCHAR(100) NOT NULL
├── specialisation  VARCHAR(50)
└── department      VARCHAR(100)

visits
├── id                  INT AUTO_INCREMENT PRIMARY KEY
├── patient_id          INT (FK → patients.id)
├── visit_date          DATE
├── complaint           TEXT
└── assigned_doctor_id  INT (FK → doctors.id)

medical_records
├── id           INT AUTO_INCREMENT PRIMARY KEY
├── visit_id     INT (FK → visits.id)
├── record_type  VARCHAR(100)
└── notes        TEXT


📋 Usage Guide
First Time Setup
Run the app: python hospital_mgmt_ui.py
Click Sign Up to create your admin account
Log in with your credentials
Adding Records
Go to Dashboard → Click any Quick Action button
OR navigate to a section via the sidebar → Click ➕ Add New
Fill in the form fields
For Visit / Medical Record forms, use the FK dropdown to select existing patients/doctors
Click 💾 Save Record
Updating Records
Navigate to the section (e.g., Patients)
Note the ID of the record you want to update (visible in the table)
Click ✏ Update → Enter the ID → Click 🔍 Load
Modify the fields → Click 💾 Save Update
Deleting Records
Navigate to the section
Click 🗑 Delete → Enter the record ID
Confirm the deletion
