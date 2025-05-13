import os
import pandas as pd

def extract_from_file(file_path, institucion):
    try:
        df = pd.read_excel(file_path, engine="xlrd", header=3)
    except Exception:
        return []

    df = df.loc[:, ~df.columns.astype(str).str.startswith("UNNAMED", na=False)]
    df = df.loc[:, ~df.columns.duplicated()]
    df.columns = [
        str(col).upper().strip()
        .replace("Ò", "Ó")
        .replace("À", "Á")
        .replace("È", "É")
        .replace("Ì", "Í")
        .replace("Ù", "Ú")
        .replace("  ", " ")
        for col in df.columns
    ]
    df.rename(columns={"CANTIDAD  PRESCRITA": "CANTIDAD PRESCRITA"}, inplace=True)

    # Get fecha from column
    fecha_archivo = None
    for col in df.columns:
        if "FECHA" in col:
            fecha_archivo = pd.to_datetime(df[col].dropna().iloc[0], errors='coerce').date()
            break
    if not fecha_archivo:
        fecha_archivo = pd.to_datetime("2000-01-01").date()

    if "DESCRIPCIÓN DEL MEDICAMENTO" not in df.columns or "CANTIDAD PRESCRITA" not in df.columns:
        return []

    grouped = df.groupby("DESCRIPCIÓN DEL MEDICAMENTO")["CANTIDAD PRESCRITA"].sum()

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
                "fecha_archivo": str(fecha_archivo)
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
        all_data.extend(meds)

    return all_data
