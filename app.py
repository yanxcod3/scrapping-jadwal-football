from flask import Flask, Response
from flask_cors import CORS
import json
from scraper import scrape_data

app = Flask(__name__)
CORS(app)

@app.route("/api", methods=["GET"])
def get_scraped_data():
    data = scrape_data()

    response = Response(json.dumps(data), mimetype="application/json")
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)