import os
import pandas as pd
import unicodedata
import json
from collections import defaultdict

def normalize_column(col):
    raw = str(col)
    normalized = unicodedata.normalize("NFKD", raw)
    clean = "".join(c for c in normalized if not unicodedata.combining(c))
    return clean.upper().strip().replace("  ", " ")

def extract_from_file(file_path, institucion, fechas_dict, cantidades_por_mes):
    try:
        df = pd.read_excel(file_path, engine="xlrd", header=3)
    except Exception as e:
        print(f"❌ Failed to read {file_path}: {e}")
        return []

    df = df.loc[:, ~df.columns.astype(str).str.startswith("UNNAMED", na=False)]
    df = df.loc[:, ~df.columns.duplicated()]
    df.columns = [normalize_column(col) for col in df.columns]
    df.rename(columns={"CANTIDAD  PRESCRITA": "CANTIDAD PRESCRITA"}, inplace=True)

    fecha_archivo_dict = defaultdict(list)

    if "FECHA DE EMISION" in df.columns:
        for _, row in df.iterrows():
            med = str(row["DESCRIPCION DEL MEDICAMENTO"]).strip().upper()
            fecha = row["FECHA DE EMISION"]
            cantidad = row.get("CANTIDAD PRESCRITA", 0)

            if pd.notnull(fecha) and pd.notnull(cantidad):
                try:
                    parsed = pd.to_datetime(str(fecha), errors="coerce", dayfirst=True)
                    if pd.isna(parsed):
                        print(f"⚠️ Invalid date for {med}: {fecha}")
                        continue

                    fecha_str = str(parsed.date())
                    fechas_dict[med].add(fecha_str)
                    fecha_archivo_dict[med].append(fecha_str)

                    # Add month count here
                    month_str = parsed.strftime("%m")  # e.g., "01"
                    cantidades_por_mes[med][month_str] += int(cantidad)
                except Exception as e:
                    print(f"❌ Unexpected error for {med} on fecha '{fecha}': {e}")
                    continue

    if "DESCRIPCION DEL MEDICAMENTO" not in df.columns or "CANTIDAD PRESCRITA" not in df.columns:
        print(f"⚠️ Missing columns in {file_path}")
        return []

    grouped = df.groupby("DESCRIPCION DEL MEDICAMENTO")["CANTIDAD PRESCRITA"].sum()
    top10 = grouped.sort_values(ascending=False).head(10)
    bottom10 = grouped.sort_values(ascending=True).head(10)

    result = []
    for tipo, grupo in [("top", top10), ("bottom", bottom10)]:
        for medicamento, cantidad in grupo.items():
            fechas_para_med = fecha_archivo_dict.get(medicamento.strip().upper(), [])
            fecha_archivo = fechas_para_med[0] if fechas_para_med else "2000-01-01"
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
    fechas_recetadas_dict = defaultdict(set)
    cantidades_por_mes = defaultdict(lambda: defaultdict(int))

    for file in os.listdir(download_dir):
        if not file.endswith(".xls"):
            continue

        file_path = os.path.join(download_dir, file)
        meta_path = file_path + ".meta.txt"

        institucion = "Desconocida"
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                institucion = f.read().strip()

        meds = extract_from_file(file_path, institucion, fechas_recetadas_dict, cantidades_por_mes)

        if meds:
            all_data.extend(meds)

    """
    fechas_final = {
        med: sorted(list(fechas)) for med, fechas in fechas_recetadas_dict.items()
    }

    with open("fechas_recetadas.json", "w", encoding="utf-8") as f:
        json.dump(fechas_final, f, indent=2, ensure_ascii=False)

    """
    return all_data, cantidades_por_mes
