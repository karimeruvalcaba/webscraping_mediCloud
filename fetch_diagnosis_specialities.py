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
    df["FECHA_PARSEADA"] = pd.to_datetime(df["FECHA_INGRESO"], errors="coerce", dayfirst=True)

    fecha_archivo = "2000-01-01"
    if "FECHA_INGRESO" in df.columns:
        non_empty = df["FECHA_INGRESO"].dropna()
        if not non_empty.empty:
            fecha = pd.to_datetime(non_empty.iloc[0], dayfirst=True, errors="coerce")
            if not pd.isna(fecha):
                year = fecha.year
                fecha_archivo = f"{year}-01-01"

    resultados = []

    for fuente, columna in [
        ("diagnostico", "DESCRIPCION_CIE_10"),
        ("especialidad", "SERVICIO_TRONCAL")
    ]:
        if columna not in df.columns:
            print(f"⚠️ Missing column: {columna} in {file_path}")
            continue

        grouped = df.groupby(columna).size()
        top10 = grouped.sort_values(ascending=False).head(10)
        bottom10 = grouped.sort_values(ascending=True).head(10)

        for tipo, grupo in [("top", top10), ("bottom", bottom10)]:
            for nombre, cantidad in grupo.items():
                fechas = df[df[columna] == nombre]["FECHA_PARSEADA"].dropna()

                fechas_recetadas = {}
                for fecha in fechas:
                    mes = fecha.strftime("%m")
                    fechas_recetadas[mes] = fechas_recetadas.get(mes, 0) + 1

                resultados.append({
                    "archivo": os.path.basename(file_path),
                    "tipo": tipo,
                    "institucion": institucion,
                    "fuente": fuente,
                    "nombre": nombre,
                    "cantidad": int(cantidad),
                    "fecha_archivo": fecha_archivo,
                    "fechas_recetadas": fechas_recetadas
                })

    return resultados

def fetch_all_diagnosis_and_specialities(download_dir="Webscrapping_ISSSTE"):
    if not os.path.exists(download_dir):
        raise FileNotFoundError("Webscrapping folder not found")

    all_data = []

    for file in os.listdir(download_dir):
        file_lower = file.lower()

        valid_prefixes = [
            "egresos",  # <-- Aquí puedes ajustar si los archivos tienen otro patrón
        ]

        if not any(file_lower.startswith(prefix) for prefix in valid_prefixes) or not file_lower.endswith(".csv.gz"):
            continue

        file_path = os.path.join(download_dir, file)
        meta_path = file_path + ".meta.txt"

        institucion = "Desconocida"
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                institucion = f.read().strip()

        datos = extract_from_file(file_path, institucion)

        if datos:
            all_data.extend(datos)

    return all_data

if __name__ == "__main__":
    fetch_all_diagnosis_and_specialities()
