import os
import pandas as pd
import unicodedata

def normalize_column(col):
    raw = str(col)
    normalized = unicodedata.normalize("NFKD", raw)
    clean = "".join(c for c in normalized if not unicodedata.combining(c))
    return clean.upper().strip().replace("  ", " ")

def extract_from_file(file_path, institucion):
    try:
        df = pd.read_excel(file_path, engine="xlrd", header=3)
    except Exception as e:
        print(f"❌ Failed to read {file_path}: {e}")
        return []

    print(f"🔍 Raw columns from {file_path}: {df.columns.tolist()}")

    df = df.loc[:, ~df.columns.astype(str).str.startswith("UNNAMED", na=False)]
    df = df.loc[:, ~df.columns.duplicated()]
    df.columns = [normalize_column(col) for col in df.columns]

    print(f"🧠 Normalized columns from {file_path}: {df.columns.tolist()}")

    df.rename(columns={"CANTIDAD  PRESCRITA": "CANTIDAD PRESCRITA"}, inplace=True)

    # ✅ Extract year from FECHA DE EMISION column
    fecha_archivo = "2000-01-01"
    if "FECHA DE EMISION" in df.columns:
        non_empty = df["FECHA DE EMISION"].dropna()
        if not non_empty.empty:
            fecha = pd.to_datetime(non_empty.iloc[0], errors="coerce")
            if not pd.isna(fecha):
                year = fecha.year
                fecha_archivo = f"{year}-01-01"

    # ✅ Validate required columns exist
    if "DESCRIPCION DEL MEDICAMENTO" not in df.columns or "CANTIDAD PRESCRITA" not in df.columns:
        print(f"⚠️ Missing columns in {file_path}")
        return []

    grouped = df.groupby("DESCRIPCION DEL MEDICAMENTO")["CANTIDAD PRESCRITA"].sum()

    top10 = grouped.sort_values(ascending=False).head(10)
    bottom10 = grouped.sort_values(ascending=True).head(10)

    result = []

    for tipo, grupo in [("top", top10), ("bottom", bottom10)]:
        for medicamento, cantidad in grupo.items():
            result.append({
                "archivo": os.path.basename(file_path),
                "tipo": tipo,
                "institucion": institucion,
                "medicamento": medicamento,
                "cantidad": int(cantidad),
                "fecha_archivo": fecha_archivo
            })

    return result

def fetch_all_prescriptions(download_dir="Webscrapping"):
    if not os.path.exists(download_dir):
        raise FileNotFoundError("Webscrapping folder not found")

    all_data = []

    for file in os.listdir(download_dir):
        if not file.endswith(".xls"):
            continue

        file_path = os.path.join(download_dir, file)
        meta_path = file_path + ".meta.txt"

        institucion = "Desconocida"
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                institucion = f.read().strip()

        meds = extract_from_file(file_path, institucion)

        # ✅ Defensive: in case extract returns None
        if meds:
            all_data.extend(meds)

    return all_data
