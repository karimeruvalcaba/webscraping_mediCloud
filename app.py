from flask import Flask, jsonify, send_file
from webscrape import run_scraper as run_meds_scraper
from webscrapeINRPRF import run_scraper as run_studies_scraper
from webscrapeISSSTE import run_scraper as run_egresos_scraper

from fetch_meds import fetch_all_prescriptions as fetch_meds_data
from fetch_studies import fetch_all_prescriptions as fetch_studies_data
from fetch_diagnosis_specialities import fetch_all_diagnosis_and_specialities as fetch_diagnosis_and_specialities

import os

app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Prescription scraping API is up."

# ------------------ SCRAPE ROUTES ------------------

@app.route("/run-scrape-meds")
def scrape_meds():
    try:
        run_meds_scraper()
        return jsonify({"status": "Scraping meds done ✅"})
    except Exception as e:
        import traceback
        return jsonify({
            "status": "Scraping meds failed ❌",
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

@app.route("/run-scrape-studies")
def scrape_studies():
    try:
        run_studies_scraper()
        return jsonify({"status": "Scraping studies done ✅"})
    except Exception as e:
        import traceback
        return jsonify({
            "status": "Scraping studies failed ❌",
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

@app.route("/run-scrape-diagnosis-specialities")
def scrape_egresos():
    try:
        run_egresos_scraper()
        return jsonify({"status": "Scraping egresos done ✅"})
    except Exception as e:
        import traceback
        return jsonify({
            "status": "Scraping egresos failed ❌",
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

# ------------------ FETCH ROUTES ------------------

@app.route("/medicinas-externas")
def get_medicinas_externas():
    try:
        data = fetch_meds_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "Fetch meds failed", "error": str(e)}), 500

@app.route("/estudios-externos")
def get_estudios_externos():
    try:
        data = fetch_studies_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "Fetch studies failed", "error": str(e)}), 500

@app.route("/diagnosis-specialities-externos")
def get_egresos_externos():
    try:
        data = fetch_diagnosis_and_specialities()
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "Fetch egresos failed", "error": str(e)}), 500

# ------------------ FILE MANAGEMENT ------------------

@app.route("/list-files")
def list_files():
    folder = "Webscrapping"
    files = os.listdir(folder) if os.path.exists(folder) else []
    return {"files": files}

@app.route("/list-egresos-files")
def list_egresos_files():
    folder = "Webscrapping_Egresos"
    files = os.listdir(folder) if os.path.exists(folder) else []
    return {"files": files}

@app.route("/download/<filename>")
def download_file(filename):
    filepath = os.path.join("Webscrapping", filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return {"error": "File not found"}, 404

@app.route("/download-egresos/<filename>")
def download_egresos_file(filename):
    filepath = os.path.join("Webscrapping_Egresos", filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return {"error": "File not found"}, 404

if __name__ == "__main__":
    app.run(debug=True)
