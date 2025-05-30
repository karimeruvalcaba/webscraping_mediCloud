import os
import re
import requests
from bs4 import BeautifulSoup
import zipfile
import gzip
import shutil

def compress_csv(file_path):
    with open(file_path, 'rb') as f_in:
        with gzip.open(file_path + '.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(file_path)

def run_scraper(download_dir="Webscrapping_ISSSTE"):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    base_url = "https://historico.datos.gob.mx"
    dataset_url = f"{base_url}/busca/dataset/datos-de-egresos-hospitalarios"

    print(f"🔍 Scraping: {dataset_url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    response = requests.get(dataset_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Get institution name from /organization/
    org_link = soup.find("a", href=re.compile("/busca/organization/"))
    institucion = org_link.text.strip().upper() if org_link else "DESCONOCIDA"
    print(f"🏥 Institution: {institucion}")

    # Find ZIP download link (with "Descargar" label)
    zip_link_tag = soup.find("a", href=True, text=re.compile("Descargar", re.I))
    if not zip_link_tag:
        print("❌ No ZIP download link found.")
        return

    zip_url = zip_link_tag["href"]
    if not zip_url.startswith("http"):
        zip_url = base_url + zip_url

    filename = "egresos_hospitalarios.zip"
    zip_path = os.path.join(download_dir, filename)

    if os.path.exists(zip_path):
        print(f"⏭️ ZIP already downloaded: {filename}")
    else:
        print(f"⬇️ Downloading ZIP: {zip_url}")
        try:
            r = requests.get(zip_url, headers=headers)
            with open(zip_path, "wb") as f:
                f.write(r.content)
            print(f"✅ ZIP saved: {zip_path}")
        except Exception as e:
            print(f"❌ Error downloading ZIP: {e}")
            return

    # Extract ZIP contents
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(download_dir)
        print(f"📂 Extracted contents to: {download_dir}")
    except Exception as e:
        print(f"❌ Error extracting ZIP: {e}")
        return

    # Compress .csv files and save metadata
    for root, _, files in os.walk(download_dir):
        for file in files:
            if file.endswith(".csv"):
                full_path = os.path.join(root, file)
                print(f"🗜️ Compressing {full_path}")
                compress_csv(full_path)
                print(f"🗃️ Compressed to: {full_path}.gz")

                meta_path = full_path + ".gz.meta.txt"
                with open(meta_path, "w", encoding="utf-8") as f:
                    f.write(institucion)
                print(f"📝 Metadata saved: {meta_path}")

# Run the scraper
if __name__ == "__main__":
    run_scraper()
