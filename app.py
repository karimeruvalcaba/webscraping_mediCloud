from flask import Flask, jsonify, send_file
from webscrape import run_scraper as run_meds_scraper
from webscrapeINRPRF import run_scraper as run_studies_scraper
from webscrapeISSSTE import run_scraper as run_egresos_scraper

from fetch_meds import fetch_all_prescriptions as fetch_meds_data
from fetch_studies import fetch_all_studies as fetch_studies_data
from fetch_diagnosis_specialities import fetch_all_diagnosis_and_specialities as fetch_diagnosis_and_specialities

import os
import json
import os
import traceback
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
        all_data, _, _ = fetch_meds_data()

        # Return only the required fields, no 'id'
        enriched = []
        for row in all_data:
            enriched.append({
                "archivo": row["archivo"],
                "tipo": row["tipo"],
                "institucion": row["institucion"],
                "medicamento": row["medicamento"],
                "cantidad": row["cantidad"],
                "fechaArchivo": row["fecha_archivo"]
            })

        return jsonify(enriched)

    except Exception as e:
        return jsonify({
            "status": "Fetch meds failed",
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

@app.route("/estudios-externos")
def get_estudios_externos():
    try:
        all_data = fetch_studies_data()  # must point to your updated fetch_all_prescriptions()

        filtered = []
        for row in all_data:
            filtered.append({
                "archivo": row["archivo"],
                "cantidad": row["cantidad"],
                "fecha_archivo": row["fecha_archivo"],
                "institucion": row["institucion"],
                "nombre_estudio": row["nombre_estudio"],
                "tipo": row["tipo"]
            })

        return jsonify(filtered)

    except Exception as e:
        return jsonify({
            "status": "Fetch estudios failed",
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

@app.route("/diagnosis-specialities-externos")
def get_egresos_externos():
    try:
        data = fetch_diagnosis_and_specialities()

        filtered = []
        for row in data:
            filtered.append({
                "archivo": row["archivo"],
                "cantidad": row["cantidad"],
                "fecha_archivo": row["fecha_archivo"],
                "fuente": row["fuente"],
                "institucion": row["institucion"],
                "nombre": row["nombre"],
                "tipo": row["tipo"]
            })

        return jsonify(filtered)

    except Exception as e:
        return jsonify({
            "status": "Fetch egresos failed",
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500


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

# ------------------ PREDICCIONES ------------------

@app.route("/meds-por-mes")
def meds_por_mes():
    try:
        all_data, fechas_map, cantidades_por_mes = fetch_meds_data()  # update to return the new data
        enriched = []
        for row in all_data:
            med = row["medicamento"].strip().upper()
            enriched.append({
                "medicina": med,
                "fechaArchivo": row.get("fecha_archivo", "2000-01-01"),
                "fechas_recetadas": cantidades_por_mes.get(med, {})
            })
        return jsonify(enriched)
    except Exception as e:
        return jsonify({
            "status": "Fetch meds por mes failed",
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

@app.route("/studies-por-mes")
def estudios_por_mes():
    try:
        all_data = fetch_studies_data()  # already returns list with fechas_recetadas per estudio

        enriched = []
        for row in all_data:
            enriched.append({
                "estudio": row["nombre_estudio"].strip().upper(),
                "fechaArchivo": row.get("fecha_archivo", "2000-01-01"),
                "fechas_recetadas": row.get("fechas_recetadas", {})
            })

        return jsonify(enriched)

    except Exception as e:
        return jsonify({
            "status": "Fetch estudios por mes failed",
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

@app.route("/diagnosis-specialities-por-mes")
def diagnosticos_por_mes():
    try:
        all_data = fetch_diagnosis_and_specialities()  # from your import

        enriched = []
        for row in all_data:
            if row["fuente"] == "diagnostico":
                enriched.append({
                    "nombre": row["nombre"],
                    "fechaArchivo": row["fecha_archivo"],
                    "fechas_recetadas": row.get("fechas_recetadas", {})
                })

        return jsonify(enriched)

    except Exception as e:
        return jsonify({
            "status": "Fetch diagnosticos por mes failed",
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
