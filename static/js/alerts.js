// ======================================================
// FILE     : static/js/alerts.js
// PURPOSE  : Fetches alerts from Flask API and updates
//            dashboard badge counts + alert panel
// ======================================================

const FLASK_API   = 'http://localhost:5000';
const REFRESH_MS  = 60000; // refresh every 60 seconds

// ======================================================
// MAIN — fetch and render alerts
// ======================================================

function fetchAlerts() {
    fetch(`${FLASK_API}/api/alerts/`)
        .then(res => res.json())
        .then(data => {
            renderBadges(data);
            renderPanel(data);
        })
        .catch(err => {
            // Flask API not running — fail silently
            console.warn('REDS Alerts: Flask API not reachable.', err);
        });
}


// ======================================================
// BADGES — update count bubbles in topbar / sidebar
// ======================================================

function renderBadges(data) {
    const redCount    = data.red_count    || 0;
    const yellowCount = data.yellow_count || 0;

    // Topbar bell badge
    const bell = document.getElementById('alert-badge-count');
    if (bell) {
        const total = redCount + yellowCount;
        bell.textContent = total;
        bell.style.display = total > 0 ? 'inline-block' : 'none';
        bell.className = redCount > 0
            ? 'badge bg-danger rounded-pill'
            : 'badge bg-warning text-dark rounded-pill';
    }

    // Sidebar red badge
    const redBadge = document.getElementById('sidebar-red-count');
    if (redBadge) {
        redBadge.textContent = redCount;
        redBadge.style.display = redCount > 0 ? 'inline-block' : 'none';
    }

    // Sidebar yellow badge
    const yellowBadge = document.getElementById('sidebar-yellow-count');
    if (yellowBadge) {
        yellowBadge.textContent = yellowCount;
        yellowBadge.style.display = yellowCount > 0 ? 'inline-block' : 'none';
    }

    // Green info counts
    const availablePlots = document.getElementById('info-available-plots');
    if (availablePlots && data.green) {
        availablePlots.textContent = data.green.available_plots || 0;
    }

    const receiptsToday = document.getElementById('info-receipts-today');
    if (receiptsToday && data.green) {
        receiptsToday.textContent = data.green.receipts_today || 0;
    }
}


// ======================================================
// PANEL — render full alert detail in dropdown
// ======================================================

function renderPanel(data) {
    const panel = document.getElementById('alert-panel-body');
    if (!panel) return;

    let html = '';

    // ── RED: Overdue installments ──────────────────────
    if (data.red && data.red.overdue_installments.length > 0) {
        html += `<div class="alert-section">
            <div class="alert-section-title text-danger">
                <i class="bi bi-exclamation-circle-fill"></i>
                Overdue Installments (${data.red.overdue_installments.length})
            </div>`;
        data.red.overdue_installments.forEach(item => {
            html += `<div class="alert-item border-start border-danger border-3 ps-2 mb-2">
                <div class="fw-semibold">${item.customer_name}</div>
                <div class="text-muted small">
                    Plot ${item.plot_no} — ${item.block_name} |
                    Installment #${item.installment_no} |
                    Due: ${item.due_date}
                </div>
                <div class="text-danger small fw-bold">
                    Rs. ${Number(item.amount).toLocaleString()}
                </div>
            </div>`;
        });
        html += `</div>`;
    }

    // ── RED: Bounced cheques ───────────────────────────
    if (data.red && data.red.bounced_cheques.length > 0) {
        html += `<div class="alert-section mt-2">
            <div class="alert-section-title text-danger">
                <i class="bi bi-x-circle-fill"></i>
                Bounced Cheques (${data.red.bounced_cheques.length})
            </div>`;
        data.red.bounced_cheques.forEach(item => {
            html += `<div class="alert-item border-start border-danger border-3 ps-2 mb-2">
                <div class="fw-semibold">${item.customer_name}</div>
                <div class="text-muted small">
                    Cheque #${item.cheque_no} — ${item.cheque_bank} |
                    Receipt: ${item.receipt_no}
                </div>
                <div class="text-danger small fw-bold">
                    Rs. ${Number(item.amount).toLocaleString()}
                </div>
            </div>`;
        });
        html += `</div>`;
    }

    // ── RED: Pending refunds ───────────────────────────
    if (data.red && data.red.pending_refunds.length > 0) {
        html += `<div class="alert-section mt-2">
            <div class="alert-section-title text-danger">
                <i class="bi bi-arrow-counterclockwise"></i>
                Pending Refunds (${data.red.pending_refunds.length})
            </div>`;
        data.red.pending_refunds.forEach(item => {
            html += `<div class="alert-item border-start border-danger border-3 ps-2 mb-2">
                <div class="fw-semibold">${item.customer_name}</div>
                <div class="text-muted small">
                    Plot ${item.plot_no} — ${item.block_name} |
                    Cancelled: ${item.cancellation_date}
                </div>
                <div class="text-danger small fw-bold">
                    Refund: Rs. ${Number(item.refund_amount).toLocaleString()}
                </div>
            </div>`;
        });
        html += `</div>`;
    }

    // ── YELLOW: Due within 7 days ──────────────────────
    if (data.yellow && data.yellow.due_soon.length > 0) {
        html += `<div class="alert-section mt-2">
            <div class="alert-section-title text-warning">
                <i class="bi bi-clock-fill"></i>
                Due Within 7 Days (${data.yellow.due_soon.length})
            </div>`;
        data.yellow.due_soon.forEach(item => {
            html += `<div class="alert-item border-start border-warning border-3 ps-2 mb-2">
                <div class="fw-semibold">${item.customer_name}</div>
                <div class="text-muted small">
                    Plot ${item.plot_no} — ${item.block_name} |
                    Installment #${item.installment_no} |
                    Due: ${item.due_date}
                </div>
                <div class="text-warning small fw-bold">
                    Rs. ${Number(item.amount).toLocaleString()}
                </div>
            </div>`;
        });
        html += `</div>`;
    }

    // ── YELLOW: Landlord payments due ─────────────────
    if (data.yellow && data.yellow.landlord_due.length > 0) {
        html += `<div class="alert-section mt-2">
            <div class="alert-section-title text-warning">
                <i class="bi bi-building"></i>
                Landlord Payments Due (${data.yellow.landlord_due.length})
            </div>`;
        data.yellow.landlord_due.forEach(item => {
            html += `<div class="alert-item border-start border-warning border-3 ps-2 mb-2">
                <div class="fw-semibold">${item.landlord_name}</div>
                <div class="text-muted small">
                    ${item.contract_title} |
                    Installment #${item.installment_no} |
                    Due: ${item.due_date}
                </div>
                <div class="text-warning small fw-bold">
                    Rs. ${Number(item.amount).toLocaleString()}
                </div>
            </div>`;
        });
        html += `</div>`;
    }

    // ── YELLOW: Pending cheques ────────────────────────
    if (data.yellow && data.yellow.pending_cheques.length > 0) {
        html += `<div class="alert-section mt-2">
            <div class="alert-section-title text-warning">
                <i class="bi bi-journal-check"></i>
                Cheques Pending Clearance (${data.yellow.pending_cheques.length})
            </div>`;
        data.yellow.pending_cheques.forEach(item => {
            html += `<div class="alert-item border-start border-warning border-3 ps-2 mb-2">
                <div class="fw-semibold">${item.customer_name}</div>
                <div class="text-muted small">
                    Cheque #${item.cheque_no} — ${item.cheque_bank} |
                    Date: ${item.cheque_date}
                </div>
                <div class="text-warning small fw-bold">
                    Rs. ${Number(item.amount).toLocaleString()}
                </div>
            </div>`;
        });
        html += `</div>`;
    }

    // ── Empty state ────────────────────────────────────
    if (html === '') {
        html = `<div class="text-center text-muted py-4">
            <i class="bi bi-check-circle-fill text-success fs-3"></i>
            <div class="mt-2">No alerts. All clear!</div>
        </div>`;
    }

    panel.innerHTML = html;
}


// ======================================================
// INIT — run on page load then repeat every 60s
// ======================================================

document.addEventListener('DOMContentLoaded', function () {
    fetchAlerts();
    setInterval(fetchAlerts, REFRESH_MS);
});