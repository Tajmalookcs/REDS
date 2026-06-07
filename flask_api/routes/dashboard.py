# ======================================================
# FILE     : flask_api/routes/dashboard.py
# PURPOSE  : Combined KPIs + alerts for dashboard
#            Single endpoint so dashboard loads fast
# ======================================================

from flask import Blueprint, jsonify
from datetime import date, timedelta
import sqlite3
import os

dashboard_bp = Blueprint('dashboard', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH  = os.path.join(BASE_DIR, 'db.sqlite3')


def get_db():
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    return conn


# ======================================================
# MAIN DASHBOARD ENDPOINT
# GET /api/dashboard/
# Returns KPIs + alert counts in one call
# ======================================================

@dashboard_bp.route('/api/dashboard/')
def dashboard():
    today   = date.today().isoformat()
    soon_7  = (date.today() + timedelta(days=7)).isoformat()
    soon_30 = (date.today() + timedelta(days=30)).isoformat()

    conn = get_db()
    cur  = conn.cursor()

    # ── PLOT KPIs ──────────────────────────────────────
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
    plots = dict(cur.fetchone())

    # ── SALES KPIs ─────────────────────────────────────
    cur.execute("""
        SELECT
            COUNT(*)                                               AS total_bookings,
            SUM(CASE WHEN status='ACTIVE'    THEN 1 ELSE 0 END)   AS active,
            SUM(CASE WHEN status='COMPLETED' THEN 1 ELSE 0 END)   AS completed,
            SUM(CASE WHEN status='CANCELLED' THEN 1 ELSE 0 END)   AS cancelled,
            COALESCE(SUM(net_price), 0)                           AS total_value
        FROM sales_booking
        WHERE is_deleted = 0
    """)
    sales = dict(cur.fetchone())

    # Total received
    cur.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total_received
        FROM sales_receipt
        WHERE is_deleted = 0
    """)
    total_received = cur.fetchone()['total_received']

    # Today's receipts
    cur.execute("""
        SELECT COALESCE(SUM(amount), 0) AS today_total,
               COUNT(*)                 AS today_count
        FROM sales_receipt
        WHERE DATE(created_at) = ?
          AND is_deleted = 0
    """, (today,))
    today_row = dict(cur.fetchone())

    # ── ALERT COUNTS ───────────────────────────────────

    # Overdue installments
    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM sales_paymentplan pp
        JOIN sales_booking b ON b.id = pp.booking_id
        WHERE pp.status IN ('PENDING','PARTIAL')
          AND pp.due_date < ?
          AND b.status = 'ACTIVE'
          AND b.is_deleted = 0
    """, (today,))
    overdue_count = cur.fetchone()['cnt']

    # Bounced cheques
    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM sales_receipt
        WHERE cheque_status = 'BOUNCED'
          AND is_deleted = 0
    """)
    bounced_count = cur.fetchone()['cnt']

    # Pending refunds
    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM sales_cancellation
        WHERE refund_amount > 0
    """)
    refund_count = cur.fetchone()['cnt']

    # Due within 7 days
    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM sales_paymentplan pp
        JOIN sales_booking b ON b.id = pp.booking_id
        WHERE pp.status IN ('PENDING','PARTIAL')
          AND pp.due_date >= ?
          AND pp.due_date <= ?
          AND b.status = 'ACTIVE'
          AND b.is_deleted = 0
    """, (today, soon_7))
    due_soon_count = cur.fetchone()['cnt']

    # Landlord payments due within 30 days
    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM land_contractpaymentschedule
        WHERE status IN ('PENDING','PARTIAL')
          AND due_date >= ?
          AND due_date <= ?
    """, (today, soon_30))
    landlord_due_count = cur.fetchone()['cnt']

    # Pending cheques > 7 days
    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM sales_receipt
        WHERE payment_mode = 'CHEQUE'
          AND (cheque_status = 'PENDING' OR cheque_status = '')
          AND cheque_date <= ?
          AND is_deleted = 0
    """, ((date.today() - timedelta(days=7)).isoformat(),))
    pending_cheques_count = cur.fetchone()['cnt']

    conn.close()

    red_count    = overdue_count + bounced_count + refund_count
    yellow_count = due_soon_count + landlord_due_count + pending_cheques_count

    total_value    = float(sales['total_value'])
    total_received = float(total_received)

    return jsonify({
        'plots': {
            'total':     plots['total'],
            'available': plots['available'],
            'booked':    plots['booked'],
            'sold':      plots['sold'],
            'on_hold':   plots['on_hold'],
        },
        'sales': {
            'total_bookings': sales['total_bookings'],
            'active':         sales['active'],
            'completed':      sales['completed'],
            'cancelled':      sales['cancelled'],
            'total_value':    total_value,
            'total_received': total_received,
            'balance_due':    total_value - total_received,
        },
        'today': {
            'receipts_amount': float(today_row['today_total']),
            'receipts_count':  today_row['today_count'],
        },
        'alerts': {
            'red_count':    red_count,
            'yellow_count': yellow_count,
            'overdue_installments': overdue_count,
            'bounced_cheques':      bounced_count,
            'pending_refunds':      refund_count,
            'due_soon':             due_soon_count,
            'landlord_due':         landlord_due_count,
            'pending_cheques':      pending_cheques_count,
        },
    })