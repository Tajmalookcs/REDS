# ======================================================
# FILE     : flask_api/routes/reports.py
# PURPOSE  : Returns report data as JSON
#            Called by dashboard JS for charts and KPIs
# ======================================================

from flask import Blueprint, jsonify, request
from datetime import date, timedelta
import sqlite3
import os

reports_bp = Blueprint('reports', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH  = os.path.join(BASE_DIR, 'db.sqlite3')


def get_db():
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    return conn


# ======================================================
# 1. SALES SUMMARY
# GET /api/reports/sales/
# ======================================================

@reports_bp.route('/api/reports/sales/')
def sales_summary():
    date_from = request.args.get('date_from', '')
    date_to   = request.args.get('date_to', '')

    conn = get_db()
    cur  = conn.cursor()

    # Build filter
    where  = "WHERE b.is_deleted = 0"
    params = []
    if date_from:
        where  += " AND b.booking_date >= ?"
        params.append(date_from)
    if date_to:
        where  += " AND b.booking_date <= ?"
        params.append(date_to)

    # Total bookings by status
    cur.execute(f"""
        SELECT
            COUNT(*)                                    AS total,
            SUM(CASE WHEN status='ACTIVE'    THEN 1 ELSE 0 END) AS active,
            SUM(CASE WHEN status='COMPLETED' THEN 1 ELSE 0 END) AS completed,
            SUM(CASE WHEN status='CANCELLED' THEN 1 ELSE 0 END) AS cancelled,
            COALESCE(SUM(net_price), 0)                AS total_value
        FROM sales_booking b
        {where}
    """, params)
    row = cur.fetchone()

    # Total receipts received
    cur.execute(f"""
        SELECT COALESCE(SUM(r.amount), 0) AS total_received
        FROM sales_receipt r
        JOIN sales_booking b ON b.id = r.booking_id
        {where}
        AND r.is_deleted = 0
    """, params)
    received = cur.fetchone()['total_received']

    # Monthly sales trend (last 6 months)
    cur.execute("""
        SELECT
            strftime('%Y-%m', booking_date) AS month,
            COUNT(*)                        AS count,
            COALESCE(SUM(net_price), 0)     AS value
        FROM sales_booking
        WHERE is_deleted = 0
          AND booking_date >= date('now', '-6 months')
        GROUP BY month
        ORDER BY month ASC
    """)
    monthly = [dict(r) for r in cur.fetchall()]

    conn.close()

    return jsonify({
        'total_bookings':  row['total'],
        'active':          row['active'],
        'completed':       row['completed'],
        'cancelled':       row['cancelled'],
        'total_value':     float(row['total_value']),
        'total_received':  float(received),
        'balance_due':     float(row['total_value']) - float(received),
        'monthly_trend':   monthly,
    })


# ======================================================
# 2. PLOT STATISTICS
# GET /api/reports/plots/
# ======================================================

@reports_bp.route('/api/reports/plots/')
def plot_stats():
    conn = get_db()
    cur  = conn.cursor()

    cur.execute("""
        SELECT
            COUNT(*)                                           AS total,
            SUM(CASE WHEN status='AVAILABLE' THEN 1 ELSE 0 END) AS available,
            SUM(CASE WHEN status='BOOKED'    THEN 1 ELSE 0 END) AS booked,
            SUM(CASE WHEN status='SOLD'      THEN 1 ELSE 0 END) AS sold,
            SUM(CASE WHEN status='HOLD'      THEN 1 ELSE 0 END) AS on_hold
        FROM development_plot
        WHERE is_deleted = 0
    """)
    row = cur.fetchone()

    # Per-town breakdown
    cur.execute("""
        SELECT
            t.name                                             AS town,
            COUNT(p.id)                                        AS total,
            SUM(CASE WHEN p.status='AVAILABLE' THEN 1 ELSE 0 END) AS available,
            SUM(CASE WHEN p.status='BOOKED'    THEN 1 ELSE 0 END) AS booked,
            SUM(CASE WHEN p.status='SOLD'      THEN 1 ELSE 0 END) AS sold
        FROM development_plot p
        JOIN development_block bl ON bl.id = p.block_id
        JOIN development_town  t  ON t.id  = bl.town_id
        WHERE p.is_deleted = 0
        GROUP BY t.id
        ORDER BY t.name
    """)
    by_town = [dict(r) for r in cur.fetchall()]

    conn.close()

    return jsonify({
        'total':     row['total'],
        'available': row['available'],
        'booked':    row['booked'],
        'sold':      row['sold'],
        'on_hold':   row['on_hold'],
        'by_town':   by_town,
    })


# ======================================================
# 3. CASH AND BANK POSITION
# GET /api/reports/cash/
# ======================================================

@reports_bp.route('/api/reports/cash/')
def cash_position():
    conn = get_db()
    cur  = conn.cursor()

    # Total cash received from customers
    cur.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM sales_receipt
        WHERE payment_mode = 'CASH'
          AND is_deleted = 0
    """)
    cash_in = cur.fetchone()['total']

    # Total cash paid to landlords
    cur.execute("""
        SELECT COALESCE(SUM(paid_amount), 0) AS total
        FROM land_contractpaymentschedule
        WHERE payment_mode = 'CASH'
          AND status = 'PAID'
    """)
    landlord_cash_out = cur.fetchone()['total']

    # Total cash expenses
    cur.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM expenses_expense
        WHERE payment_mode IN ('CASH', 'PETTY_CASH')
    """)
    expense_cash_out = cur.fetchone()['total']

    # Cheques in hand (received but not cleared)
    cur.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM sales_receipt
        WHERE payment_mode = 'CHEQUE'
          AND (cheque_status = 'PENDING' OR cheque_status = '')
          AND is_deleted = 0
    """)
    cheques_in_hand = cur.fetchone()['total']

    # Today's receipts
    cur.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM sales_receipt
        WHERE DATE(created_at) = DATE('now')
          AND is_deleted = 0
    """)
    today_receipts = cur.fetchone()['total']

    conn.close()

    net_cash = float(cash_in) - float(landlord_cash_out) - float(expense_cash_out)

    return jsonify({
        'cash_in':            float(cash_in),
        'landlord_cash_out':  float(landlord_cash_out),
        'expense_cash_out':   float(expense_cash_out),
        'net_cash_position':  net_cash,
        'cheques_in_hand':    float(cheques_in_hand),
        'today_receipts':     float(today_receipts),
    })


# ======================================================
# 4. LANDLORD PAYMENTS
# GET /api/reports/landlord/
# ======================================================

@reports_bp.route('/api/reports/landlord/')
def landlord_payments():
    conn = get_db()
    cur  = conn.cursor()

    cur.execute("""
        SELECT
            ll.name                                AS landlord_name,
            lc.title                               AS contract_title,
            lc.total_amount,
            COALESCE(SUM(
                CASE WHEN cps.status='PAID'
                THEN cps.paid_amount ELSE 0 END
            ), 0)                                  AS total_paid,
            lc.total_amount - COALESCE(SUM(
                CASE WHEN cps.status='PAID'
                THEN cps.paid_amount ELSE 0 END
            ), 0)                                  AS balance,
            COUNT(
                CASE WHEN cps.status='PENDING'
                THEN 1 END
            )                                      AS pending_count
        FROM land_landcontract lc
        JOIN land_landlord ll ON ll.id = lc.landlord_id
        LEFT JOIN land_contractpaymentschedule cps ON cps.contract_id = lc.id
        WHERE lc.status = 'ACTIVE'
        GROUP BY lc.id
        ORDER BY ll.name
    """)
    contracts = [dict(r) for r in cur.fetchall()]

    conn.close()

    return jsonify({
        'contracts': contracts,
        'total':     len(contracts),
    })