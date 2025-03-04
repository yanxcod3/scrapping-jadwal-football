from flask import Flask, Response, request, render_template_string
from flask_cors import CORS
import json
from scraper import scrape_data

app = Flask(__name__)
CORS(app)

# Counter untuk melacak penggunaan API
api_counter = 0

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
        .counter {
            font-size: 24px;
            color: #007bff;
            margin: 20px 0;
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
        <div class="counter">
            Total API Calls: {{ api_counter }}
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

@app.route("/")
def home():
    return render_template_string(MAIN_PAGE_HTML, api_counter=api_counter)

@app.route("/api", methods=["GET"])
def get_scraped_data():
    global api_counter
    api_counter += 1
    
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

if __name__ == "__main__":
    app.run(debug=True, port=5000)