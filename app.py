from flask import Flask, jsonify, send_file
from webscrape import run_scraper
from fetch_meds import fetch_all_prescriptions  # 🧠 pulls logic from fetch_meds.py
import os

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

@app.route("/medicinas-externas")
def get_medicinas_externas():
    try:
        data = fetch_all_prescriptions()
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "Fetch failed", "error": str(e)}), 500

@app.route("/list-files")
def list_files():
    folder = "Webscrapping"
    files = os.listdir(folder) if os.path.exists(folder) else []
    return {"files": files}

@app.route("/download/<filename>")
def download_file(filename):
    filepath = os.path.join("Webscrapping", filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return {"error": "File not found"}, 404

if __name__ == "__main__":
    app.run(debug=True)
