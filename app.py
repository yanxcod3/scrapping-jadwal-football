from flask import Flask, Response, request
from flask_cors import CORS
import json
from scraper import scrape_data

app = Flask(__name__)
CORS(app)

@app.route("/api", methods=["GET"])
def get_scraped_data():
    limit = request.args.get('limit', type=int)
    data = scrape_data()

    if limit and limit > 0:
        data['data'] = data['data'][:limit]

    response = Response(json.dumps(data), mimetype="application/json")
    return response

if __name__ == "__main__":
    app.run(debug=True, port=5000)