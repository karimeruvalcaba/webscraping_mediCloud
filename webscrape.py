import os
import re
import requests
from bs4 import BeautifulSoup

def run_scraper(download_dir="Webscrapping"):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    base_url = "https://historico.datos.gob.mx"
    dataset_url = f"{base_url}/busca/dataset/recursos-materiales-recetas"

    print(f"🔍 Scraping: {dataset_url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    response = requests.get(dataset_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    xls_links = soup.find_all("a", string=re.compile("Descargar", re.I), href=re.compile(r"\.xls$", re.I))

    if not xls_links:
        print("❌ No .xls links found.")
        return

    print(f"📦 Found {len(xls_links)} .xls files to download")

    org_link = soup.find("a", href=re.compile("/busca/organization/"))
    institucion = org_link.text.strip().upper() if org_link else "DESCONOCIDA"
    print(f"🏥 Institution: {institucion}")

    for i, link in enumerate(xls_links):
        file_url = link.get("href")
        if not file_url.startswith("http"):
            file_url = base_url + file_url

        title = link.get("data-name") or link.text.strip() or f"archivo_{i}"
        filename = title.replace(" ", "_").replace("/", "_") + ".xls"
        file_path = os.path.join(download_dir, filename)

        print(f"⬇️ Downloading {file_url}")
        try:
            r = requests.get(file_url, headers=headers)
            with open(file_path, "wb") as f:
                f.write(r.content)
            print(f"✅ Saved: {file_path}")

            meta_path = file_path + ".meta.txt"
            with open(meta_path, "w", encoding="utf-8") as f:
                f.write(institucion)
            print(f"📝 Metadata saved: {meta_path}")

        except Exception as e:
            print(f"❌ Error downloading {file_url}: {e}")

