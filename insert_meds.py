import os
import pandas as pd
from sqlalchemy import create_engine, text

# 🧠 Load MySQL connection from environment variables pls work
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST")
port = os.getenv("MYSQL_PORT", "3306")
database = os.getenv("MYSQL_DB")

engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")

# 🧱 Ensure table exists (includes fecha_archivo)
create_table_sql = """
CREATE TABLE IF NOT EXISTS Medicinas_externas_lab (
  id INT AUTO_INCREMENT PRIMARY KEY,
  archivo VARCHAR(255),
  tipo ENUM('top', 'bottom'),
  institucion VARCHAR(100),
  medicamento VARCHAR(255),
  cantidad INT,
  fecha_archivo DATE,
  UNIQUE (archivo, tipo, medicamento)
)
"""

with engine.connect() as conn:
    conn.execute(text(create_table_sql))
    print("✅ Table Medicinas_externas_lab created (or already exists).")

# 🧠 Main insert logic
def insert_prescriptions(download_dir="Webscrapping"):
    if not os.path.exists(download_dir):
        raise FileNotFoundError("Webscrapping folder not found.")

    summary = {}

    for file in os.listdir(download_dir):
        if not file.endswith(".xls"):
            continue

        file_path = os.path.join(download_dir, file)
        meta_path = file_path + ".meta.txt"
        institucion = "Desconocida"
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                institucion = f.read().strip()

        try:
            df = pd.read_excel(file_path, engine="xlrd", header=3)
        except Exception as e:
            summary[file] = {"error": f"Excel read error: {e}", "institution": institucion}
            continue

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

        # 🟡 Extract date from inside the file
        fecha_archivo = None
        for col in df.columns:
            if "FECHA" in col:
                fecha_archivo = pd.to_datetime(df[col].dropna().iloc[0], errors='coerce').date()
                break
        if not fecha_archivo:
            fecha_archivo = pd.to_datetime("2000-01-01").date()  # fallback

        if "DESCRIPCIÓN DEL MEDICAMENTO" not in df.columns or "CANTIDAD PRESCRITA" not in df.columns:
            summary[file] = {
                "error": "Missing required columns",
                "institution": institucion,
                "fecha_archivo": str(fecha_archivo)
            }
            continue

        grouped = df.groupby("DESCRIPCIÓN DEL MEDICAMENTO")["CANTIDAD PRESCRITA"].sum()

        with engine.connect() as conn:
            top_exists = conn.execute(
                text("SELECT COUNT(*) FROM Medicinas_externas_lab WHERE archivo = :archivo AND tipo = 'top'"),
                {"archivo": file}
            ).scalar() > 0
            bottom_exists = conn.execute(
                text("SELECT COUNT(*) FROM Medicinas_externas_lab WHERE archivo = :archivo AND tipo = 'bottom'"),
                {"archivo": file}
            ).scalar() > 0

        result = {"institution": institucion, "fecha_archivo": str(fecha_archivo)}

        if not top_exists:
            top10 = grouped.sort_values(ascending=False).head(10)
            top_df = pd.DataFrame({
                "archivo": file,
                "tipo": "top",
                "institucion": institucion,
                "medicamento": top10.index,
                "cantidad": top10.values,
                "fecha_archivo": fecha_archivo
            })
            top_df.to_sql("Medicinas_externas_lab", engine, if_exists="append", index=False)
            result["top"] = "✅ Inserted"
        else:
            result["top"] = "⏭️ Already exists"

        if not bottom_exists:
            bottom10 = grouped.sort_values(ascending=True).head(10)
            bottom_df = pd.DataFrame({
                "archivo": file,
                "tipo": "bottom",
                "institucion": institucion,
                "medicamento": bottom10.index,
                "cantidad": bottom10.values,
                "fecha_archivo": fecha_archivo
            })
            bottom_df.to_sql("Medicinas_externas_lab", engine, if_exists="append", index=False)
            result["bottom"] = "✅ Inserted"
        else:
            result["bottom"] = "⏭️ Already exists"

        summary[file] = result

    return summary
