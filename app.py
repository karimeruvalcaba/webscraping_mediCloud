from flask import Flask, jsonify
from webscrape import run_scraper
from insert_meds import insert_prescriptions

app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Prescription scraping API is up."

@app.route("/run-scrape")
def scrape():
    try:
        run_scraper()
        return jsonify({"status": "Scraping done ✅"})
    except Exception as e:
        import traceback
        return jsonify({
            "status": "Scraping failed ❌",
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

@app.route("/run-insert")
def insert():
    try:
        insert_prescriptions()
        return jsonify({"status": "Insert done ✅"})
    except Exception as e:
        return jsonify({"status": "Insert failed", "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
