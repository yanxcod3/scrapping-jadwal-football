from flask import Flask, Response
import json
from scraper import scrape_data

app = Flask(__name__)

@app.route("/api", methods=["GET"])
def get_scraped_data():
    data = scrape_data()

    response = Response(json.dumps(data), mimetype="application/json")
    return response

if __name__ == "__main__":
    app.run(debug=True, port=5000)