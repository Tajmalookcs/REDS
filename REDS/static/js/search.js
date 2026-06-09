// ======================================================
// FILE     : static\js\search.js
// PURPOSE  : Live search for plots and customers
//            Calls Flask API as user types
// ======================================================

const FLASK_SEARCH = 'http://localhost:5000';

// ======================================================
// PLOT SEARCH
// ======================================================

function initPlotSearch() {
    const input   = document.getElementById('plot-search-input');
    const results = document.getElementById('plot-search-results');
    if (!input || !results) return;

    let timer;

    input.addEventListener('input', function () {
        clearTimeout(timer);
        const q = input.value.trim();

        if (q.length < 2) {
            results.innerHTML = '';
            results.style.display = 'none';
            return;
        }

        timer = setTimeout(() => {
            fetch(`${FLASK_SEARCH}/api/search/plots/?q=${encodeURIComponent(q)}`)
                .then(res => res.json())
                .then(data => renderPlotResults(data, results))
                .catch(() => { results.style.display = 'none'; });
        }, 300);
    });

    // Hide on outside click
    document.addEventListener('click', function (e) {
        if (!input.contains(e.target) && !results.contains(e.target)) {
            results.style.display = 'none';
        }
    });
}


function renderPlotResults(data, container) {
    if (!data.plots || data.plots.length === 0) {
        container.innerHTML = `<div class="search-no-result">No plots found</div>`;
        container.style.display = 'block';
        return;
    }

    let html = '';
    data.plots.forEach(p => {
        const statusClass = {
            'AVAILABLE': 'success',
            'BOOKED':    'warning',
            'SOLD':      'danger',
            'HOLD':      'secondary',
        }[p.status] || 'secondary';

        html += `
        <a href="/development/plots/${p.id}/" class="search-result-item">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <span class="fw-bold">Plot ${p.plot_no}</span>
                    <span class="text-muted small ms-2">${p.block_name} — ${p.town_name}</span>
                </div>
                <span class="badge bg-${statusClass}">${p.status}</span>
            </div>
            <div class="text-muted small mt-1">
                ${p.size} ${p.size_unit} | ${p.plot_type} |
                Rs. ${Number(p.price).toLocaleString()}
            </div>
        </a>`;
    });

    container.innerHTML = html;
    container.style.display = 'block';
}


// ======================================================
// CUSTOMER SEARCH
// ======================================================

function initCustomerSearch() {
    const input   = document.getElementById('customer-search-input');
    const results = document.getElementById('customer-search-results');
    if (!input || !results) return;

    let timer;

    input.addEventListener('input', function () {
        clearTimeout(timer);
        const q = input.value.trim();

        if (q.length < 2) {
            results.innerHTML = '';
            results.style.display = 'none';
            return;
        }

        timer = setTimeout(() => {
            fetch(`${FLASK_SEARCH}/api/search/customers/?q=${encodeURIComponent(q)}`)
                .then(res => res.json())
                .then(data => renderCustomerResults(data, results))
                .catch(() => { results.style.display = 'none'; });
        }, 300);
    });

    document.addEventListener('click', function (e) {
        if (!input.contains(e.target) && !results.contains(e.target)) {
            results.style.display = 'none';
        }
    });
}


function renderCustomerResults(data, container) {
    if (!data.customers || data.customers.length === 0) {
        container.innerHTML = `<div class="search-no-result">No customers found</div>`;
        container.style.display = 'block';
        return;
    }

    let html = '';
    data.customers.forEach(c => {
        html += `
        <a href="/customers/${c.id}/" class="search-result-item">
            <div class="fw-bold">${c.name}</div>
            <div class="text-muted small">
                CNIC: ${c.cnic || '—'} | Phone: ${c.phone || '—'}
            </div>
        </a>`;
    });

    container.innerHTML = html;
    container.style.display = 'block';
}


// ======================================================
// STYLES — injected dynamically
// ======================================================

const searchCSS = `
    .search-wrapper { position: relative; }

    .search-results {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: #fff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        z-index: 9999;
        max-height: 320px;
        overflow-y: auto;
        display: none;
    }

    .search-result-item {
        display: block;
        padding: 10px 14px;
        text-decoration: none;
        color: #1a1a2e;
        border-bottom: 1px solid #f0f0f0;
        transition: background 0.15s;
    }

    .search-result-item:hover {
        background: #f8f9fa;
        color: #e94560;
    }

    .search-result-item:last-child {
        border-bottom: none;
    }

    .search-no-result {
        padding: 12px 14px;
        color: #6c757d;
        font-size: 0.9rem;
    }
`;

const styleTag = document.createElement('style');
styleTag.textContent = searchCSS;
document.head.appendChild(styleTag);


// ======================================================
// INIT
// ======================================================

document.addEventListener('DOMContentLoaded', function () {
    initPlotSearch();
    initCustomerSearch();
});