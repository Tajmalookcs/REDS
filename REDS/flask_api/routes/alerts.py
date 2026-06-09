# ======================================================
# FILE     : flask_api/routes/alerts.py
# PURPOSE  : Returns alert/notification data as JSON
#            Called by dashboard JavaScript
# ======================================================

from flask import Blueprint, jsonify
from datetime import date, timedelta
import sqlite3
import os

alerts_bp = Blueprint('alerts', __name__)

# ── Path to Django's SQLite database ──────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH    = os.path.join(BASE_DIR, 'db.sqlite3')


def get_db():
    """Open a read-only connection to the shared SQLite DB."""
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    return conn


# ======================================================
# MAIN ALERTS ENDPOINT
# GET /api/alerts/
# Returns counts and detail lists for dashboard
# ======================================================

@alerts_bp.route('/api/alerts/')
def get_alerts():
    today      = date.today().isoformat()
    soon       = (date.today() + timedelta(days=7)).isoformat()
    soon_30    = (date.today() + timedelta(days=30)).isoformat()

    conn = get_db()
    cur  = conn.cursor()

    # ── RED: Overdue customer installments ────────────
    cur.execute("""
        SELECT
            pp.id,
            pp.installment_no,
            pp.due_date,
            pp.amount,
            c.name  AS customer_name,
            pl.plot_no,
            bl.name AS block_name,
            t.name  AS town_name
        FROM sales_paymentplan pp
        JOIN sales_booking b   ON b.id = pp.booking_id
        JOIN customers_customer c ON c.id = b.customer_id
        JOIN development_plot pl  ON pl.id = b.plot_id
        JOIN development_block bl ON bl.id = pl.block_id
        JOIN development_town  t  ON t.id  = bl.town_id
        WHERE pp.status IN ('PENDING','PARTIAL')
          AND pp.due_date < ?
          AND b.status = 'ACTIVE'
          AND b.is_deleted = 0
        ORDER BY pp.due_date ASC
        LIMIT 20
    """, (today,))
    overdue_installments = [dict(r) for r in cur.fetchall()]

    # ── RED: Bounced cheques ───────────────────────────
    cur.execute("""
        SELECT
            r.id,
            r.receipt_no,
            r.cheque_no,
            r.cheque_bank,
            r.amount,
            c.name AS customer_name
        FROM sales_receipt r
        JOIN sales_booking b      ON b.id = r.booking_id
        JOIN customers_customer c ON c.id = b.customer_id
        WHERE r.cheque_status = 'BOUNCED'
          AND r.is_deleted = 0
        ORDER BY r.created_at DESC
        LIMIT 20
    """)
    bounced_cheques = [dict(r) for r in cur.fetchall()]

    # ── RED: Pending refunds (cancelled bookings) ──────
    cur.execute("""
        SELECT
            cn.id,
            cn.refund_amount,
            cn.cancellation_date,
            c.name AS customer_name,
            pl.plot_no,
            bl.name AS block_name
        FROM sales_cancellation cn
        JOIN sales_booking b      ON b.id = cn.booking_id
        JOIN customers_customer c ON c.id = b.customer_id
        JOIN development_plot pl  ON pl.id = b.plot_id
        JOIN development_block bl ON bl.id = pl.block_id
        WHERE cn.refund_amount > 0
        ORDER BY cn.cancellation_date DESC
        LIMIT 20
    """)
    pending_refunds = [dict(r) for r in cur.fetchall()]

    # ── YELLOW: Installments due within 7 days ─────────
    cur.execute("""
        SELECT
            pp.id,
            pp.installment_no,
            pp.due_date,
            pp.amount,
            c.name  AS customer_name,
            pl.plot_no,
            bl.name AS block_name
        FROM sales_paymentplan pp
        JOIN sales_booking b      ON b.id = pp.booking_id
        JOIN customers_customer c ON c.id = b.customer_id
        JOIN development_plot pl  ON pl.id = b.plot_id
        JOIN development_block bl ON bl.id = pl.block_id
        WHERE pp.status IN ('PENDING','PARTIAL')
          AND pp.due_date >= ?
          AND pp.due_date <= ?
          AND b.status = 'ACTIVE'
          AND b.is_deleted = 0
        ORDER BY pp.due_date ASC
        LIMIT 20
    """, (today, soon))
    due_soon = [dict(r) for r in cur.fetchall()]

    # ── YELLOW: Landlord payments due within 30 days ───
    cur.execute("""
        SELECT
            cps.id,
            cps.installment_no,
            cps.due_date,
            cps.amount,
            ll.name AS landlord_name,
            lc.title AS contract_title
        FROM land_contractpaymentschedule cps
        JOIN land_landcontract lc ON lc.id = cps.contract_id
        JOIN land_landlord     ll ON ll.id = lc.landlord_id
        WHERE cps.status IN ('PENDING','PARTIAL')
          AND cps.due_date >= ?
          AND cps.due_date <= ?
        ORDER BY cps.due_date ASC
        LIMIT 20
    """, (today, soon_30))
    landlord_due = [dict(r) for r in cur.fetchall()]

    # ── YELLOW: Cheques pending clearance > 7 days ─────
    cur.execute("""
        SELECT
            r.id,
            r.receipt_no,
            r.cheque_no,
            r.cheque_bank,
            r.cheque_date,
            r.amount,
            c.name AS customer_name
        FROM sales_receipt r
        JOIN sales_booking b      ON b.id = r.booking_id
        JOIN customers_customer c ON c.id = b.customer_id
        WHERE r.payment_mode = 'CHEQUE'
          AND (r.cheque_status = 'PENDING' OR r.cheque_status = '')
          AND r.cheque_date <= ?
          AND r.is_deleted = 0
        ORDER BY r.cheque_date ASC
        LIMIT 20
    """, ((date.today() - timedelta(days=7)).isoformat(),))
    pending_cheques = [dict(r) for r in cur.fetchall()]

    # ── GREEN: Plots available after cancellation ──────
    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM development_plot
        WHERE status = 'AVAILABLE'
          AND is_deleted = 0
    """)
    available_plots = cur.fetchone()['cnt']

    # ── GREEN: Receipts entered today ──────────────────
    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM sales_receipt
        WHERE DATE(created_at) = ?
          AND is_deleted = 0
    """, (today,))
    receipts_today = cur.fetchone()['cnt']

    conn.close()

    # ── Build summary counts ───────────────────────────
    red_count    = len(overdue_installments) + len(bounced_cheques) + len(pending_refunds)
    yellow_count = len(due_soon) + len(landlord_due) + len(pending_cheques)

    return jsonify({
        'red_count':    red_count,
        'yellow_count': yellow_count,

        'red': {
            'overdue_installments': overdue_installments,
            'bounced_cheques':      bounced_cheques,
            'pending_refunds':      pending_refunds,
        },

        'yellow': {
            'due_soon':       due_soon,
            'landlord_due':   landlord_due,
            'pending_cheques': pending_cheques,
        },

        'green': {
            'available_plots': available_plots,
            'receipts_today':  receipts_today,
        },
    })