from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time

def setup_driver():
    options = Options()
    options.add_argument("--headless")  # elimina ventana gráfica
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    service = Service(executable_path="D:/jobs/chromedriver.exe")
    return webdriver.Chrome(service=service, options=options)

def get_jobs_basic(driver, max_pages=100):
    base_url = "https://www.jobs.ch/en/vacancies/?page={page}&region=18&term="
    results = []

    for page in range(1, max_pages + 1):
        url = base_url.format(page=page)
        print(f"\nCargando página {page} → {url}")
        driver.get(url)
        time.sleep(2.5)

        offers = driver.find_elements(By.CSS_SELECTOR, "a[data-cy='job-link']")
        print(f"→ {len(offers)} ofertas detectadas")

        for offer in offers:
            try:
                title = offer.get_attribute("title").strip()
                href = offer.get_attribute("href").strip()
                link = href if href.startswith("http") else "https://www.jobs.ch" + href
            except:
                title = link = ""

            try:
                ps = offer.find_elements(By.CSS_SELECTOR, "p.textStyle_p2")
                location = company = ""

                for p in ps:
                    if p.find_elements(By.TAG_NAME, "strong"):
                        company = p.text.strip()
                    else:
                        location = p.text.strip()
            except:
                location = company = ""

            results.append({
                "title": title,
                "company": company,
                "location": location,
                "link": link
            })

        print(f"→ Acumuladas: {len(results)} ofertas")

    return results

if __name__ == "__main__":
    driver = setup_driver()
    try:
        jobs = get_jobs_basic(driver, max_pages=100)
        df = pd.DataFrame(jobs)
        df.to_csv("jobs_scraped_.csv", index=False, encoding="utf-8")
        print(f"\n✅ Guardado: {len(df)} ofertas en 'jobs_scraped.csv'")
    finally:
        driver.quit()
