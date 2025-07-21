import pandas as pd
import time
import random
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Configuración del navegador
def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    service = Service(executable_path="D:/jobs/chromedriver.exe")  # Ajusta si cambias ubicación
    return webdriver.Chrome(service=service, options=options)

# Función para extraer los datos de la oferta
def extract_job_text(driver, url):
    try:
        driver.get(url)
        time.sleep(random.uniform(2.0, 3.5))

        def safe_extract(by, selector):
            try:
                return driver.find_element(by, selector).text.strip()
            except:
                return ""

        description = safe_extract(By.CSS_SELECTOR, 'div[data-cy="vacancy-description"]')

        publication_date = safe_extract(By.CSS_SELECTOR, "li[data-cy='info-publication'] span.white-space_nowrap")
        workload = safe_extract(By.CSS_SELECTOR, "li[data-cy='info-workload'] span.white-space_nowrap")
        contract_type_detail = safe_extract(By.CSS_SELECTOR, "li[data-cy='info-contract'] span.white-space_nowrap")
        language = safe_extract(By.CSS_SELECTOR, "li[data-cy='info-language'] span:not([class])")
        place_of_work = safe_extract(By.CSS_SELECTOR, "li[data-cy='info-workplace'] span:not([class])")

        return {
            "description": description,
            "publication_date": publication_date,
            "workload": workload,
            "contract_type_detail": contract_type_detail,
            "language": language,
            "place_of_work": place_of_work
        }

    except Exception as e:
        print(f"❌ Error al extraer contenido de {url}:{e}")
        return None

# Función principal
def scrape_job_details(input_csv, output_csv, debug=False):
    df = pd.read_csv(input_csv)
    df = df.dropna(subset=["link"])
    df["link"] = df["link"].str.strip()
    df["link"] = df["link"].str.replace("https://www.jobs.chhttps://www.jobs.ch", "https://www.jobs.ch")

    if debug:
        df = df.head(1)

    driver = setup_driver()
    results = []

    start_time = time.time()
    total = len(df)
    errores = 0

    try:
        for i, row in df.iterrows():
            url = row["link"]
            print(f"\n[{i+1}/{total}] Procesando URL:\n{url}")

            iter_start = time.time()
            data = extract_job_text(driver, url)
            iter_time = time.time() - iter_start

            if data:
                job_text = data.get("description", "")
                pub_date = data.get("publication_date", "")
                workload = data.get("workload", "")
                contract_type_detail = data.get("contract_type_detail", "")
                language = data.get("language", "")
                place_of_work = data.get("place_of_work", "")
                print(f"✅ Datos extraídos correctamente en {iter_time:.2f} seg")
            else:
                job_text = pub_date = workload = contract_type_detail = language = place_of_work = ""
                errores += 1
                print(f"❌ Error al extraer texto (Errores acumulados: {errores})")

            elapsed = time.time() - start_time
            avg_time = elapsed / (i + 1)
            remaining = avg_time * (total - i - 1)
            eta = datetime.timedelta(seconds=int(remaining))
            print(f"⏱ Tiempo estimado restante: {eta}")

            results.append({
                "title": row["title"],
                "company": row["company"],
                "location": row["location"],
                "contract_type": row.get("contract_type", ""),
                "level": row.get("level", ""),
                "url": url,
                "publication_date": pub_date,
                "workload": workload,
                "contract_type_detail": contract_type_detail,
                "language": language,
                "place_of_work": place_of_work,
                "job_text": job_text
            })

    finally:
        driver.quit()

    output_df = pd.DataFrame(results)
    output_df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"\n✅ Proceso finalizado: {len(output_df)} filas guardadas en '{output_csv}'")
    print(f"⚠️ Total de errores: {errores}")

# Ejecutar directamente
if __name__ == "__main__":
    scrape_job_details("jobs_relevant_only.csv", "results.csv", debug=False)