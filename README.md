# 💊 Prescription Scraping API

Este proyecto es una API en Flask que automatiza la descarga de archivos `.xls` desde el portal de Datos Abiertos del Gobierno de México. Extrae información de recetas médicas emitidas, las limpia y expone los datos más relevantes mediante endpoints JSON.

---

## 🚀 ¿Qué hace esta API?

1. **Descarga automática de archivos `.xls`** con datos de recetas emitidas.
2. **Guarda metadatos** como la institución emisora en archivos `.meta.txt`.
3. **Procesa los archivos** para obtener el top 10 y bottom 10 de medicamentos más recetados.
4. **Expone la información limpia** vía endpoints REST.

---

## 🔗 Endpoints disponibles

| Método | Ruta                      | Descripción                                               |
|--------|---------------------------|-----------------------------------------------------------|
| GET    | `/`                       | Verifica que la API esté corriendo                        |
| GET    | `/run-scrape`             | Ejecuta el scraper y descarga los archivos `.xls`         |
| GET    | `/medicinas-externas`     | Devuelve los medicamentos más/menos recetados             |
| GET    | `/list-files`             | Lista los archivos descargados en el directorio local     |
| GET    | `/download/<filename>`    | Permite descargar un archivo específico                   |

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
flask run
# or
streamlit run connection2.py  # for local visualizations
```
