// ======================================================
// FILE     : static/js/dashboard.js
// PURPOSE  : Fetches KPI data from Flask API and renders
//            charts + live numbers on the dashboard
// ======================================================

const FLASK_BASE = 'http://localhost:5000';

// ======================================================
// UTILITY — format PKR numbers
// ======================================================

function formatPKR(amount) {
    if (amount >= 10000000) {
        return 'Rs. ' + (amount / 10000000).toFixed(2) + ' Cr';
    } else if (amount >= 100000) {
        return 'Rs. ' + (amount / 100000).toFixed(2) + ' Lac';
    } else {
        return 'Rs. ' + Number(amount).toLocaleString();
    }
}


// ======================================================
// 1. PLOT STATUS DONUT CHART
// ======================================================

function loadPlotChart() {
    fetch(`${FLASK_BASE}/api/reports/plots/`)
        .then(res => res.json())
        .then(data => {

            // Update KPI number cards
            setEl('kpi-total-plots',     data.total     || 0);
            setEl('kpi-available-plots', data.available || 0);
            setEl('kpi-booked-plots',    data.booked    || 0);
            setEl('kpi-sold-plots',      data.sold      || 0);

            // Draw donut chart
            const canvas = document.getElementById('plotStatusChart');
            if (!canvas) return;

            // Destroy existing chart if re-rendering
            if (window._plotChart) window._plotChart.destroy();

            window._plotChart = new Chart(canvas, {
                type: 'doughnut',
                data: {
                    labels: ['Available', 'Booked', 'Sold', 'On Hold'],
                    datasets: [{
                        data: [
                            data.available || 0,
                            data.booked    || 0,
                            data.sold      || 0,
                            data.on_hold   || 0,
                        ],
                        backgroundColor: [
                            '#28a745',  // green  — available
                            '#ffc107',  // yellow — booked
                            '#dc3545',  // red    — sold
                            '#6c757d',  // grey   — hold
                        ],
                        borderWidth: 2,
                        borderColor: '#fff',
                    }]
                },
                options: {
                    responsive: true,
                    cutout: '65%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { padding: 15, font: { size: 12 } }
                        },
                        tooltip: {
                            callbacks: {
                                label: ctx => ` ${ctx.label}: ${ctx.parsed} plots`
                            }
                        }
                    }
                }
            });
        })
        .catch(err => console.warn('Plot chart: Flask API not reachable.', err));
}


// ======================================================
// 2. MONTHLY SALES BAR CHART
// ======================================================

function loadSalesChart() {
    fetch(`${FLASK_BASE}/api/reports/sales/`)
        .then(res => res.json())
        .then(data => {

            // Update sales KPI cards
            setEl('kpi-total-bookings',  data.total_bookings  || 0);
            setEl('kpi-active-bookings', data.active          || 0);
            setEl('kpi-total-value',     formatPKR(data.total_value     || 0));
            setEl('kpi-total-received',  formatPKR(data.total_received  || 0));
            setEl('kpi-balance-due',     formatPKR(data.balance_due     || 0));

            // Draw monthly bar chart
            const canvas = document.getElementById('monthlySalesChart');
            if (!canvas) return;

            if (window._salesChart) window._salesChart.destroy();

            const trend  = data.monthly_trend || [];
            const labels = trend.map(r => r.month);
            const values = trend.map(r => r.value);
            const counts = trend.map(r => r.count);

            window._salesChart = new Chart(canvas, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Sales Value (Rs.)',
                            data: values,
                            backgroundColor: '#e9456088',
                            borderColor: '#e94560',
                            borderWidth: 1,
                            yAxisID: 'y',
                        },
                        {
                            label: 'Bookings Count',
                            data: counts,
                            type: 'line',
                            borderColor: '#1a1a2e',
                            backgroundColor: '#1a1a2e22',
                            borderWidth: 2,
                            pointRadius: 4,
                            tension: 0.3,
                            yAxisID: 'y1',
                        }
                    ]
                },
                options: {
                    responsive: true,
                    interaction: { mode: 'index', intersect: false },
                    plugins: {
                        legend: { position: 'top' },
                        tooltip: {
                            callbacks: {
                                label: ctx => {
                                    if (ctx.datasetIndex === 0) {
                                        return ` Value: ${formatPKR(ctx.parsed.y)}`;
                                    }
                                    return ` Bookings: ${ctx.parsed.y}`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            position: 'left',
                            ticks: {
                                callback: val => formatPKR(val)
                            }
                        },
                        y1: {
                            type: 'linear',
                            position: 'right',
                            grid: { drawOnChartArea: false },
                            ticks: { stepSize: 1 }
                        }
                    }
                }
            });
        })
        .catch(err => console.warn('Sales chart: Flask API not reachable.', err));
}


// ======================================================
// 3. CASH POSITION KPI CARDS
// ======================================================

function loadCashPosition() {
    fetch(`${FLASK_BASE}/api/reports/cash/`)
        .then(res => res.json())
        .then(data => {
            setEl('kpi-cash-in',           formatPKR(data.cash_in            || 0));
            setEl('kpi-cash-out',          formatPKR((data.landlord_cash_out || 0) + (data.expense_cash_out || 0)));
            setEl('kpi-net-cash',          formatPKR(data.net_cash_position  || 0));
            setEl('kpi-cheques-in-hand',   formatPKR(data.cheques_in_hand    || 0));
            setEl('kpi-today-receipts',    formatPKR(data.today_receipts     || 0));
        })
        .catch(err => console.warn('Cash position: Flask API not reachable.', err));
}


// ======================================================
// UTILITY — safely set element text
// ======================================================

function setEl(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}


// ======================================================
// INIT — load everything on page load
// ======================================================

document.addEventListener('DOMContentLoaded', function () {
    loadPlotChart();
    loadSalesChart();
    loadCashPosition();

    // Auto-refresh every 5 minutes
    setInterval(() => {
        loadPlotChart();
        loadSalesChart();
        loadCashPosition();
    }, 300000);
});