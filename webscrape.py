import os
import time
import urllib.request
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Download directory
download_dir = "C:\\Users\\abdel\\Downloads\\Webscrapping"

# 🧼 Firefox setup
options = Options()
options.set_preference("network.proxy.type", 0)
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.dir", download_dir)
options.set_preference("browser.helperApps.neverAsk.saveToDisk",
    "application/vnd.ms-excel,application/octet-stream,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
options.set_preference("pdfjs.disabled", True)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("dom.security.allow_insecure_downloads", True)

# 🚀 Launch browser
driver = webdriver.Firefox(options=options)
driver.get("https://datos.gob.mx/busca/dataset/recursos-materiales-recetas")

try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "heading"))
    )

    headings = driver.find_elements(By.CLASS_NAME, "heading")
    datasets = []
    for h in headings:
        title = h.get_attribute("title")
        href = h.get_attribute("href")
        if title and href and "Recetas Emitidas" in title:
            full_url = href if href.startswith("http") else "http://datos.gob.mx" + href
            datasets.append((title, full_url))

    print(f"🔎 Found {len(datasets)} dataset(s) matching 'Recetas Emitidas'")

    for title, url in datasets:
        print(f"\n🔁 Navigating to: {url}")
        driver.get(url)

        try:
            # Get institution name
            WebDriverWait(driver, 10).until(
                  EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
            )

            org_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/busca/organization/')]")
            if org_links:
                institucion = org_links[0].text.strip().upper()
                print(f"🏥 Institution: {institucion}")
            else:
                institucion = "Desconocida"
                print("⚠️ Institution not found — fallback used.")

            # Find download link
            download_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Descargar') and contains(@href, '.xls')]"))
            )
            href = download_button.get_attribute("href")
            base_name = title.replace(" ", "_") + ".xls"
            renamed_path = os.path.join(download_dir, base_name)

            #Save institution to match .meta.txt
            meta_path = os.path.join(download_dir, base_name + ".meta.txt")

            print(f"⬇️ Downloading from: {href}")
            urllib.request.urlretrieve(href, renamed_path)
            print(f"✅ Saved as: {renamed_path}")

            # Save institution to meta file
            meta_path = os.path.join(download_dir, base_name + ".meta.txt")
            with open(meta_path, "w", encoding="utf-8") as f:
                f.write(institucion)

        except Exception as inner_e:
            print(f"❌ Failed to download for: {title} → {inner_e}")

except Exception as e:
    print(f"❌ Global error: {e}")

finally:
    driver.quit()
    print("🧹 Browser closed.")
