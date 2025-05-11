from flask import Flask, jsonify, send_file
from webscrape import run_scraper
from insert_meds import insert_prescriptions
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

@app.route("/run-insert")
def run_insert():
    try:
        results = insert_prescriptions()
        return jsonify(results)
    except Exception as e:
        return jsonify({"status": "Insert failed", "error": str(e)}), 500

    
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

