


from flask import Flask
from flask_cors import CORS

from routes.alerts  import alerts_bp
from routes.reports import reports_bp
from routes.dashboard import dashboard_bp   # add this
from routes.search    import search_bp

# ── Create Flask app ───────────────────────────────────
app = Flask(__name__)

# ── Enable CORS so Django pages can call this API ──────
# Allows requests from Django running on port 8000
CORS(app, resources={r"/api/*": {"origins": "*"}})


# ── Register blueprints ────────────────────────────────

app.register_blueprint(dashboard_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(search_bp)
# ── Health check endpoint ──────────────────────────────
@app.route('/api/ping/')
def ping():
    return {'status': 'ok', 'message': 'REDS Flask API is running'}


# ── Run server ─────────────────────────────────────────
if __name__ == '__main__':
    app.run(
        host  = '0.0.0.0',   # accessible on LAN too
        port  = 5000,
        debug = True
    )