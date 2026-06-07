# REDS — Real Estate Developer System

A complete property developer office management system built with Django 4.2.

---

## TECH STACK

- Backend  : Django 4.2
- Database : SQLite
- Frontend : Bootstrap 5 (fully offline)
- Icons    : Bootstrap Icons (fully offline)
- Python   : 3.12.10

---

## QUICK START

### 1. Activate Virtual Environment
```
cd D:\REDS
venv\Scripts\activate
```

### 2. Run Migrations
```
python manage.py migrate
```

### 3. Seed Chart of Accounts
```
python manage.py seed_accounts
```

### 4. Create Superuser
```
python manage.py createsuperuser
```

### 5. Start Development Server
```
python manage.py runserver
```

Open browser: http://127.0.0.1:8000

---

## LAN DEPLOYMENT

Double-click `lan_run.bat` or run:
```
python manage.py runserver 0.0.0.0:8000 --settings=config.settings_lan
```

Find your IP:
```
ipconfig
```

Other PCs on same WiFi open: http://YOUR-PC-IP:8000

---

## MODULES

| Module       | Features                                              |
|--------------|-------------------------------------------------------|
| Core         | Dashboard, users, business profile, bank accounts     |
| Land         | Landlords, contracts, payment schedules               |
| Development  | Towns, blocks, plots                                  |
| Customers    | Customer management                                   |
| Agents       | Agent management                                      |
| Sales        | Bookings, receipts, payment plans, cancellations      |
| Expenses     | Misc expenses, categories                             |
| Accounting   | Chart of accounts, journal entries, cash book,        |
|              | general ledger, bank ledger, trial balance            |
| Reports      | Sales, plots, customer ledger, agent commission,      |
|              | landlord, cash & bank position, P&L, tax summary      |

---

## USER ROLES

| Role      | Access                                      |
|-----------|---------------------------------------------|
| SUPERUSER | Full access including settings and users    |
| USER      | Daily operations — no settings access       |

---

## PAYMENT METHODS

- Cash (primary)
- Bank Transfer
- Cheque (with tracking: no, bank, date, status)

---

## AUTO JOURNAL ENTRIES

Journals are auto-created when:
- Receipt is saved
- Booking is confirmed
- Booking is cancelled
- Landlord payment is made
- Expense is recorded
- Agent commission is paid

---

## FOLDER STRUCTURE

```
D:\REDS\
├── manage.py
├── requirements.txt
├── README.md
├── dev_run.bat
├── lan_run.bat
├── config/
│   ├── settings.py
│   ├── settings_lan.py
│   └── urls.py
├── apps/
│   ├── core/
│   ├── land/
│   ├── development/
│   ├── customers/
│   ├── agents/
│   ├── sales/
│   ├── expenses/
│   ├── accounting/
│   └── reports/
├── templates/
├── static/
│   ├── css/
│   │   ├── bootstrap.min.css
│   │   ├── bootstrap-icons.css
│   │   └── print.css
│   └── js/
│       └── bootstrap.bundle.min.js
└── db.sqlite3
```

---

## IMPORTANT COMMANDS

```bash
# Activate venv
venv\Scripts\activate

# Migrations
python manage.py makemigrations
python manage.py migrate

# Seed accounts
python manage.py seed_accounts

# Create superuser
python manage.py createsuperuser

# Run dev server
python manage.py runserver

# Run on LAN
python manage.py runserver 0.0.0.0:8000 --settings=config.settings_lan

# Check for errors
python manage.py check
```

---

## PRINT FEATURES

- Receipt print — A5 bilingual layout
- Booking print — A4 full confirmation
- Amount in words — English + Urdu

---

*Built with Django 4.2 — REDS v1.0*
