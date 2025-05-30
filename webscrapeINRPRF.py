import os
import re
import requests
from bs4 import BeautifulSoup
import gzip
import shutil

def compress_csv(file_path):
    with open(file_path, 'rb') as f_in:
        with gzip.open(file_path + '.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(file_path)  # remove the original uncompressed file

def run_scraper(download_dir="Webscrapping"):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    base_url = "https://historico.datos.gob.mx"
    dataset_url = f"{base_url}/busca/dataset/estudios-otorgados-de-analisis-clinicos"

    print(f"🔍 Scraping: {dataset_url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    response = requests.get(dataset_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find .csv links
    download_links = soup.find_all("a", href=re.compile(r"\.csv$", re.I))

    if not download_links:
        print("❌ No .csv links found.")
        return

    print(f"📦 Found {len(download_links)} .csv file(s) to download")

    # Try to get institution name
    org_link = soup.find("a", href=re.compile("/busca/organization/"))
    institucion = org_link.text.strip().upper() if org_link else "DESCONOCIDA"
    print(f"🏥 Institution: {institucion}")

    for i, link in enumerate(download_links):
        file_url = link.get("href")
        if not file_url.startswith("http"):
            file_url = base_url + file_url

        title = link.get("data-name") or link.text.strip() or f"archivo_{i}"
        filename = title.replace(" ", "_").replace("/", "_") + ".csv"
        file_path = os.path.join(download_dir, filename)

        # ✅ Skip already downloaded (compressed) file
        if os.path.exists(file_path + ".gz"):
            print(f"⏭️ Already downloaded and compressed: {filename}.gz")
            continue

        print(f"⬇️ Downloading {file_url}")
        try:
            r = requests.get(file_url, headers=headers)
            with open(file_path, "wb") as f:
                f.write(r.content)
            print(f"✅ Saved: {file_path}")

            # 🗜️ Compress the file
            compress_csv(file_path)
            print(f"🗃️ Compressed to: {file_path}.gz")

            # Save metadata
            meta_path = file_path + ".gz.meta.txt"
            with open(meta_path, "w", encoding="utf-8") as f:
                f.write(institucion)
            print(f"📝 Metadata saved: {meta_path}")

        except Exception as e:
            print(f"❌ Error downloading {file_url}: {e}")

# Run the scraper
if __name__ == "__main__":
    run_scraper()
