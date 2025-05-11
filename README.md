# 🧠 MediCloud Web Scraper

This project automates the download, extraction, and analysis of medical prescription datasets from [datos.gob.mx](https://datos.gob.mx/), specifically from the "Recursos Materiales Recetas" dataset.

It’s deployed on [Render](https://render.com) and designed to:
- 🔽 Scrape new `.xls` prescription files as they are published
- 🏥 Capture institution metadata (like "INNN")
- 💊 Insert Top 10 and Bottom 10 most prescribed medications into a MySQL database
- 🧾 Avoid duplicate inserts by checking existing records
- 🧩 Expose `/run-scrape` and `/run-insert` endpoints for admin use

---

## 🗂 Folder Structure
📁 Webscrapping/
├── Recetas_Emitidas_2024.xls
├── Recetas_Emitidas_2024.xls.meta.txt
├── ...
📄 app.py # Flask app with endpoints
📄 webscrape.py # Scrapes files and metadata using BeautifulSoup
📄 insert_meds.py # Cleans + loads data into MySQL
📄 requirements.txt # All dependencies
📄 .render.yaml # Deployment config

---

## 🚀 Endpoints

### `/run-scrape`
- Downloads all `.xls` files from datasets titled "Recetas Emitidas"
- Saves them in `Webscrapping/`
- Stores institution name in `.meta.txt`

### `/run-insert`
- Reads `.xls` files from `Webscrapping/`
- Cleans + normalizes columns
- Inserts top/bottom 10 prescribed medications into a MySQL table
- Skips records that already exist

Returns JSON like:
```json
{
  "Recetas_Emitidas_2024.xls": {
    "institution": "INNN",
    "top": "✅ Inserted",
    "bottom": "⏭️ Already exists"
  }
}

---

## ⚙️ MySQL Setup

Table used:

```sql
CREATE TABLE estadisticas_externas_lab (
  id INT AUTO_INCREMENT PRIMARY KEY,
  archivo VARCHAR(255),
  tipo ENUM('top', 'bottom'),
  medicamento VARCHAR(255),
  cantidad INT,
  UNIQUE (archivo, tipo, medicamento)
);
```

## 🔐 Environment Variables

Set these in your local shell or in the Render Environment tab:

```bash
MYSQL_USER=root
MYSQL_PASSWORD=diogo1
MYSQL_HOST=localhost    # or your ngrok host
MYSQL_PORT=3306         # or your ngrok port
MYSQL_DB=dummy_base
```

## ☁️ Deployment on Render

1. Push your code to GitHub
2. Create a new **Web Service** on [Render](https://render.com)
3. Link your GitHub repository
4. Set the build command:

   ```bash
   pip install -r requirements.txt
```
5. Set the start command:
   ```bash
   gunicorn app:app
```
6. Define all necessary environment variables in the Environment tab
7. (Optional) Add a `.render.yaml` if needed for config as code

