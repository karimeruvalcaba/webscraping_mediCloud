import gzip
import pandas as pd
import os
import unicodedata

def normalize_column(col):
    raw = str(col)
    normalized = unicodedata.normalize("NFKD", raw)
    clean = "".join(c for c in normalized if not unicodedata.combining(c))
    return clean.upper().strip().replace("  ", " ")

def extract_from_file(file_path, institucion):
    try:
        if file_path.endswith(".csv.gz"):
            with gzip.open(file_path, "rt", encoding="latin1") as f:
                df = pd.read_csv(f)
        else:
            print(f"⏭️ Unsupported file type: {file_path}")
            return []
    except Exception as e:
        print(f"❌ Failed to read {file_path}: {e}")
        return []

    df = df.loc[:, ~df.columns.astype(str).str.startswith("UNNAMED", na=False)]
    df = df.loc[:, ~df.columns.duplicated()]
    df.columns = [normalize_column(col) for col in df.columns]

    fecha_archivo = "2000-01-01"
    if "FECHA DE LA CITA" in df.columns:
        non_empty = df["FECHA DE LA CITA"].dropna()
        if not non_empty.empty:
            fecha = pd.to_datetime(non_empty.iloc[0], errors="coerce")
            if not pd.isna(fecha):
                year = fecha.year
                fecha_archivo = f"{year}-01-01"

    if "ESTUDIO" not in df.columns or "SERVICIO" not in df.columns or "FECHA DE LA CITA" not in df.columns:
        print(f"⚠️ Missing columns in {file_path}")
        return []

    # ✅ Parse all fechas
    df["FECHA_DE_CITA_PARSEADA"] = pd.to_datetime(df["FECHA DE LA CITA"], errors="coerce", dayfirst=True)

    # ✅ Agrupar por estudio
    top_bottom_result = []

    grouped = df.groupby("ESTUDIO")["SERVICIO"].count()
    top10 = grouped.sort_values(ascending=False).head(10)
    bottom10 = grouped.sort_values(ascending=True).head(10)

    for tipo, grupo in [("top", top10), ("bottom", bottom10)]:
        for estudio, cantidad in grupo.items():
            fechas_mes = df[df["ESTUDIO"] == estudio]["FECHA_DE_CITA_PARSEADA"].dropna()
            fechas_recetadas = {}

            for fecha in fechas_mes:
                mes = fecha.strftime("%m")
                fechas_recetadas[mes] = fechas_recetadas.get(mes, 0) + 1

            top_bottom_result.append({
                "archivo": os.path.basename(file_path),
                "tipo": tipo,
                "institucion": institucion,
                "nombre_estudio": estudio,
                "cantidad": int(cantidad),
                "fecha_archivo": fecha_archivo,
                "fechas_recetadas": fechas_recetadas
            })

    return top_bottom_result

def fetch_all_studies(download_dir="Webscrapping"):
    if not os.path.exists(download_dir):
        raise FileNotFoundError("Webscrapping folder not found")

    all_data = []

    for file in os.listdir(download_dir):
        file_lower = file.lower()

        valid_prefixes = [
            "estudios_otorgadas_de_laboratorio_de_análisis_clínicos_del_",
            "estudios_otorgados_de_laboratorio_de_análisis_clínicos_del_"
        ]

        if not any(file_lower.startswith(prefix) for prefix in valid_prefixes) or not file_lower.endswith(".csv.gz"):
            if not file.endswith(".xls"):
                print(f"⏭️ Skipping unrelated file: {file}")
            continue

        file_path = os.path.join(download_dir, file)
        meta_path = file_path + ".meta.txt"

        institucion = "Desconocida"
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                institucion = f.read().strip()

        estudios = extract_from_file(file_path, institucion)

        if estudios:
            all_data.extend(estudios)

    return all_data
