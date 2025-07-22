import pandas as pd
from utils import clean_text
import spacy
from transformers import pipeline
import time

print("🔄 Cargando modelos NLP...")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

try:
    nlp = spacy.load("xx_ent_wiki_sm")
except:
    from spacy.cli import download
    download("xx_ent_wiki_sm")
    nlp = spacy.load("xx_ent_wiki_sm")

ROLE_LABELS = ["Data Scientist", "Data Analyst", "Machine Learning Engineer", "Software Engineer",
               "Business Analyst", "DevOps Engineer", "BI Analyst", "Data Engineer"]
SENIORITY_LABELS = ["Intern", "Junior", "Senior", "Lead", "Unspecified"]
INDUSTRY_LABELS = ["Finance", "Healthcare", "Retail", "Telecommunications", "IT", "Education", "Government"]
TECH_KEYWORDS = ["python", "sql", "excel", "r", "tableau", "power bi", "cloud", "aws", "azure", "linux",
                 "pytorch", "tensorflow", "spark", "hadoop", "snowflake", "looker"]

def extract_entities_spacy(text, debug=False):
    trimmed = text[:500]
    return list(set(ent.text for ent in nlp(trimmed).ents if ent.label_ != "")) if not debug else []

def detect_technologies(text):
    text_lower = text.lower()
    return [tech for tech in TECH_KEYWORDS if tech in text_lower]

def classify_field(text, labels):
    trimmed = text[:1000]
    result = classifier(trimmed, labels, multi_label=True)
    top_label = result["labels"][0]
    score = result["scores"][0]
    return top_label if score > 0.5 else "Unspecified"

def analyze_offers(input_csv, output_csv, max_offers=0, debug=False):
    df = pd.read_csv(input_csv)
    df = df.dropna(subset=["job_text"])
    if max_offers > 0:
        df = df.head(max_offers)

    print(f"🔍 Procesando {len(df)} ofertas...")

    for col in ["title", "company", "location", "job_text"]:
        df[col] = df[col].astype(str).apply(clean_text)

    roles, seniorities, industries, techs, ents = [], [], [], [], []

    for i, row in df.iterrows():
        text = row["job_text"]
        print(f"\n[{i+1}/{len(df)}] Analizando...")

        t0 = time.time()
        role = classify_field(text, ROLE_LABELS)
        seniority = classify_field(text, SENIORITY_LABELS)
        industry = classify_field(text, INDUSTRY_LABELS)
        t1 = time.time()

        print(f"⏱ Clasificación NLP completada en {t1 - t0:.2f} s")

        technologies = detect_technologies(text)
        entities = extract_entities_spacy(text, debug=debug)

        roles.append(role)
        seniorities.append(seniority)
        industries.append(industry)
        techs.append(technologies)
        ents.append(entities)

    df["role"] = roles
    df["seniority"] = seniorities
    df["industry"] = industries
    df["tech_keywords"] = techs
    df["entities"] = ents

    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"✅ Análisis completo. Guardado en: {output_csv}")

if __name__ == "__main__":
    import sys
    max_offers = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    debug = "--debug" in sys.argv
    analyze_offers("results.csv", "analyzed_offers_optimized.csv", max_offers=max_offers, debug=debug)