from flask import Flask, Response, request, render_template_string
from flask_cors import CORS
import json
from scraper import scrape_data
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# File untuk menyimpan statistik
STATS_FILE = '/tmp/api_stats.json'  # Menggunakan /tmp untuk Vercel

def load_stats():
    """Memuat statistik dari file JSON"""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                data = json.load(f)
                return data.get('total_calls', 0), data.get('daily_counter', {})
        except json.JSONDecodeError:
            return 0, {}
    return 0, {}

def save_stats():
    """Menyimpan statistik ke file JSON"""
    data = {
        'total_calls': api_counter,
        'daily_counter': daily_counter
    }
    with open(STATS_FILE, 'w') as f:
        json.dump(data, f)

# Counter untuk melacak penggunaan API
api_counter, daily_counter = load_stats()

# Template HTML untuk halaman utama
MAIN_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>API Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .container {
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
        }
        .stats-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-box {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .stat-value {
            font-size: 24px;
            color: #007bff;
            margin: 10px 0;
        }
        .stat-label {
            color: #666;
            font-size: 14px;
        }
        .endpoint {
            background-color: #fff;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
            border-left: 4px solid #007bff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>API Dashboard</h1>
        <div class="stats-container">
            <div class="stat-box">
                <div class="stat-value">{{ total_calls }}</div>
                <div class="stat-label">Total API Calls</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{{ today_calls }}</div>
                <div class="stat-label">Today's API Calls</div>
            </div>
        </div>
        <div class="endpoint">
            <h3>Available Endpoints:</h3>
            <p><strong>GET /api</strong> - Get scraped data football</p>
            <p>Query parameters:</p>
            <ul>
                <li>limit: Optional. Format: number or start,end</li>
                <li>Example: /api?limit=5 or /api?limit=1,10</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

def update_daily_counter():
    today = datetime.now().strftime('%Y-%m-%d')
    if today not in daily_counter:
        daily_counter[today] = 0
    daily_counter[today] += 1
    save_stats()  # Simpan setiap kali ada update
    return daily_counter[today]

@app.route("/")
def home():
    today = datetime.now().strftime('%Y-%m-%d')
    today_calls = daily_counter.get(today, 0)
    
    # Sort daily stats by date in descending order
    sorted_daily_stats = dict(sorted(daily_counter.items(), reverse=True))
    
    return render_template_string(
        MAIN_PAGE_HTML,
        total_calls=api_counter,
        today_calls=today_calls,
        daily_stats=sorted_daily_stats
    )

@app.route("/api", methods=["GET"])
def get_scraped_data():
    global api_counter
    api_counter += 1
    update_daily_counter()
    
    limit_param = request.args.get('limit', default=None)
    data = scrape_data()

    if limit_param:
        try:
            # Split parameter limit berdasarkan koma
            limits = [int(x) for x in limit_param.split(',')]
            
            if len(limits) == 2:
                # Jika format x,y, gunakan keduanya sebagai range
                start = max(limits[0] - 1, 0)  # Konversi ke 0-based index
                end = limits[1]
                data['data'] = data['data'][start:end]
            elif len(limits) == 1:
                # Jika hanya satu angka, ambil dari awal sampai angka tersebut
                end = limits[0]
                data['data'] = data['data'][:end]
        except (ValueError, IndexError):
            # Jika format tidak valid, kembalikan semua data
            pass

    response = Response(json.dumps(data), mimetype="application/json")
    return response

# Untuk development lokal
if __name__ == "__main__":
    app.run(debug=True, port=5000)