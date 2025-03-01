from flask import Flask, Response, request
from flask_cors import CORS
import json
from scraper import scrape_data

app = Flask(__name__)
CORS(app)

@app.route("/api", methods=["GET"])
def get_scraped_data():
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