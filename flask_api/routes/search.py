# ======================================================
# FILE     : flask_api/routes/search.py
# PURPOSE  : Live search for plots and customers
#            Called by search.js as user types
# ======================================================

from flask import Blueprint, jsonify, request
import sqlite3
import os

search_bp = Blueprint('search', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH  = os.path.join(BASE_DIR, 'db.sqlite3')


def get_db():
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    return conn


# ======================================================
# PLOT SEARCH
# GET /api/search/plots/?q=<query>
# Searches plot_no, block name, town name, plot type
# ======================================================

@search_bp.route('/api/search/plots/')
def search_plots():
    q = request.args.get('q', '').strip()

    if len(q) < 2:
        return jsonify({'plots': [], 'count': 0})

    conn = get_db()
    cur  = conn.cursor()

    cur.execute("""
        SELECT
            p.id,
            p.plot_no,
            p.size,
            p.size_unit,
            p.plot_type,
            p.status,
            p.price,
            bl.name  AS block_name,
            t.name   AS town_name
        FROM development_plot p
        JOIN development_block bl ON bl.id = p.block_id
        JOIN development_town  t  ON t.id  = bl.town_id
        WHERE p.is_deleted = 0
          AND (
              p.plot_no   LIKE ?
           OR bl.name     LIKE ?
           OR t.name      LIKE ?
           OR p.plot_type LIKE ?
          )
        ORDER BY
            CASE p.status
                WHEN 'AVAILABLE' THEN 1
                WHEN 'BOOKED'    THEN 2
                WHEN 'HOLD'      THEN 3
                WHEN 'SOLD'      THEN 4
                ELSE 5
            END,
            p.plot_no ASC
        LIMIT 15
    """, (f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%'))

    plots = [dict(r) for r in cur.fetchall()]
    conn.close()

    return jsonify({'plots': plots, 'count': len(plots)})


# ======================================================
# CUSTOMER SEARCH
# GET /api/search/customers/?q=<query>
# Searches name, CNIC, phone
# ======================================================

@search_bp.route('/api/search/customers/')
def search_customers():
    q = request.args.get('q', '').strip()

    if len(q) < 2:
        return jsonify({'customers': [], 'count': 0})

    conn = get_db()
    cur  = conn.cursor()

    cur.execute("""
        SELECT
            c.id,
            c.name,
            c.cnic,
            c.phone,
            c.city,
            COUNT(b.id) AS booking_count
        FROM customers_customer c
        LEFT JOIN sales_booking b
               ON b.customer_id = c.id
              AND b.is_deleted = 0
        WHERE c.is_deleted = 0
          AND (
              c.name  LIKE ?
           OR c.cnic  LIKE ?
           OR c.phone LIKE ?
          )
        GROUP BY c.id
        ORDER BY c.name ASC
        LIMIT 15
    """, (f'%{q}%', f'%{q}%', f'%{q}%'))

    customers = [dict(r) for r in cur.fetchall()]
    conn.close()

    return jsonify({'customers': customers, 'count': len(customers)})