import os
import re
import requests
from bs4 import BeautifulSoup

def run_scraper(download_dir="Webscrapping"):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    base_url = "https://datos.gob.mx"
    main_url = f"{base_url}/busca/dataset/recursos-materiales-recetas"

    print(f"🔍 Scraping main dataset page: {main_url}")
    response = requests.get(main_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Get all <a class="heading" title="Recetas Emitidas...">
    dataset_links = soup.find_all("a", class_="heading")

    datasets = []
    for link in dataset_links:
        title = link.get("title", "").strip()
        href = link.get("href", "")
        if "Recetas Emitidas" in title and href:
            full_url = href if href.startswith("http") else base_url + href
            datasets.append((title, full_url))

    print(f"📦 Found {len(datasets)} matching datasets")

    for title, url in datasets:
        print(f"\n🔁 Navigating to: {url}")
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        # Institution name
        org_link = soup.find("a", href=re.compile("/busca/organization/"))
        institucion = org_link.text.strip().upper() if org_link else "Desconocida"
        print(f"🏥 Institution: {institucion}")

        # Download link (looks like an <a> with .xls in href and 'Descargar' in text)
        download_link = soup.find("a", href=re.compile(r"\.xls"), string=re.compile("Descargar", re.I))

        if not download_link:
            print("❌ No .xls download link found.")
            continue

        file_url = download_link["href"]
        if not file_url.startswith("http"):
            file_url = base_url + file_url

        filename = title.replace(" ", "_") + ".xls"
        file_path = os.path.join(download_dir, filename)

        print(f"⬇️ Downloading: {file_url}")
        try:
            r = requests.get(file_url)
            with open(file_path, "wb") as f:
                f.write(r.content)
            print(f"✅ Saved as: {file_path}")

            # Save institution name to meta file
            meta_path = file_path + ".meta.txt"
            with open(meta_path, "w", encoding="utf-8") as f:
                f.write(institucion)
        except Exception as e:
            print(f"❌ Error downloading {file_url}: {e}")
