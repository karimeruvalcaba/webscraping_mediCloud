# 💊 Prescription Scraping API

This project is a Flask API that automates the download of `.xls` files from the Mexican Government's open data portal. It extracts prescription data issued by public institutions, cleans the data, and exposes the most and least prescribed medications through JSON-based endpoints.

---

## 🚀 What Does This API Do?

1. **Automatically downloads `.xls` files** from an official dataset (e.g. INNN).
2. **Stores metadata** like the issuing institution in `.meta.txt` files.
3. **Processes downloaded files** using Pandas: cleans headers and aggregates data.
4. **Exposes cleaned and aggregated information** through a RESTful API.

---

## 🔗 Available Endpoints

| Method | Route                     | Description                                                |
|--------|---------------------------|------------------------------------------------------------|
| GET    | `/`                       | Basic health check                                          |
| GET    | `/run-scrape`             | Scrapes and downloads `.xls` files from the dataset        |
| GET    | `/medicinas-externas`     | Returns the top/bottom 10 most prescribed medications      |
| GET    | `/list-files`             | Lists all downloaded files in the local directory          |
| GET    | `/download/<filename>`    | Downloads a specific `.xls` or `.meta.txt` file            |

---

## 🗂 Folder Structure

```
📁 Webscrapping/
│   ├── Recetas_Emitidas_Abril-Diciembre_2023.xls
│   ├── Recetas_Emitidas_Abril-Diciembre_2023.xls.meta.txt
│   ├── Recetas_Emitidas_2024.xls.meta.txt
│   ├── Recetas_Emitidas_2024.xls
│   └── ...
├── app.py             # Flask app with endpoints
├── webscrape.py       # Scrapes files and metadata using BeautifulSoup
├── insert_meds.py     # Cleans + loads data into MySQL
├── requirements.txt   # All dependencies
└── .render.yaml       # Deployment config
```

## 🚀 Endpoints


---

## 📥 Endpoint: `/run-scrape`

- Scrapes data from: [datos.gob.mx](https://historico.datos.gob.mx/busca/dataset/recursos-materiales-recetas)
- Downloads `.xls` files only (not `.csv`)
- Saves them in the `Webscrapping/` folder
- Generates a `.meta.txt` file for each `.xls`, containing the institution name

---

## 📊 Endpoint: `/medicinas-externas`

- Processes all `.xls` files in the `Webscrapping/` directory
- Cleans poorly formatted or duplicated columns
- Normalizes column headers (e.g., fixes `"CANTIDAD  PRESCRITA"`)
- Groups by medication and returns:
  - **Top 10 most prescribed**
  - **Bottom 10 least prescribed**

Sample JSON response:

```json
[
  {
    "archivo": "Recetas_Emitidas_2024.xls",
    "tipo": "top",
    "institucion": "INSTITUTO NACIONAL DE NEUROLOGÍA Y NEUROCIRUGÍA",
    "medicamento": "PARACETAMOL",
    "cantidad": 13782,
    "fecha_archivo": "2024-01-01"
  },
  ...
]
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

# Run endpoints
```
#Run flask locally
flask run
```
