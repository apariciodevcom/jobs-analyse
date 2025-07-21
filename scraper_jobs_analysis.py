import pandas as pd
import re
from sentence_transformers import SentenceTransformer, util
from collections import Counter
import datetime
import logging

# Configuración de logging
logging.basicConfig(
    filename='logs_fase3.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Inicializar modelo SBERT para embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Lista base de tecnologías
TECH_KEYWORDS = ['python', 'sql', 'tableau', 'aws', 'azure', 'powerbi']

# Categorías por similitud (prototipos)
ROLE_PROTOTYPES = {
    "Data Scientist": "Builds models, analyzes data patterns, uses ML algorithms.",
    "Data Analyst": "Creates dashboards, queries databases, prepares reports.",
    "Machine Learning Engineer": "Productionizes ML models, optimizes pipelines.",
    "Data Engineer": "Builds data pipelines, manages ETL, ensures data quality.",
    "Business Analyst": "Interprets business needs, provides analytical insights.",
    "Software Engineer": "Writes and tests code, builds applications."
}

SENIORITY_KEYWORDS = {
    "Junior": ["junior", "entry level", "beginn", "praktikum"],
    "Mid": ["mitte", "mid level", "professional"],
    "Senior": ["senior", "lead", "principal", "expert"],
}

INDUSTRY_HINTS = {
    "Finance": ["bank", "insurance", "finanz", "financial"],
    "Healthcare": ["health", "hospital", "clinic", "medizin"],
    "Retail": ["retail", "verkauf", "e-commerce"],
    "Technology": ["software", "cloud", "ai", "data"],
    "Public": ["university", "government", "verwaltung"],
    "Industry": ["manufacturing", "produktion", "supply chain"],
}

def clean_text(text):
    return re.sub(r"\s+", " ", text.lower()).strip()

def classify_role(text):
    job_embedding = model.encode(text, convert_to_tensor=True)
    sims = {role: util.cos_sim(job_embedding, model.encode(desc, convert_to_tensor=True)).item()
            for role, desc in ROLE_PROTOTYPES.items()}
    return max(sims, key=sims.get)

def detect_seniority(text):
    text = text.lower()
    for level, keywords in SENIORITY_KEYWORDS.items():
        if any(k in text for k in keywords):
            return level
    return "Unspecified"

def infer_industry(text):
    text = text.lower()
    for industry, hints in INDUSTRY_HINTS.items():
        if any(h in text for h in hints):
            return industry
    return "Other"

def extract_technologies(text):
    text = text.lower()
    found = [tech for tech in TECH_KEYWORDS if tech in text]
    return found

def guess_company_type(company_name, text):
    if pd.isna(company_name): return "Unknown"
    text = text.lower()
    if any(k in text for k in ["start-up", "startup", "scale-up"]): return "Startup"
    if any(k in text for k in ["gmbh", "ag", "inc", "corp"]): return "Private"
    if any(k in text for k in ["university", "eth", "epfl", "city of", "kanton"]): return "Public"
    if any(k in text for k in ["consult", "beratung"]): return "Consulting"
    return "Private"

def process_offers(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df["job_text_clean"] = df["job_text"].fillna("").apply(clean_text)

    df["classified_role"] = df["job_text_clean"].apply(classify_role)
    df["seniority"] = df["job_text_clean"].apply(detect_seniority)
    df["industry"] = df["job_text_clean"].apply(infer_industry)
    df["technologies"] = df["job_text_clean"].apply(extract_technologies)
    df["company_type"] = df.apply(lambda row: guess_company_type(row.get("company", ""), row["job_text_clean"]), axis=1)

    # Histograma global de tecnologías
    all_techs = [tech for sublist in df["technologies"] for tech in sublist]
    tech_hist = Counter(all_techs)
    logging.info(f"Tecnologías más frecuentes: {tech_hist.most_common(10)}")

    df.drop(columns=["job_text_clean"], inplace=True)
    df.to_csv(output_csv, index=False, encoding="utf-8")
    logging.info(f"Archivo generado: {output_csv} ({len(df)} filas)")

if __name__ == "__main__":
    process_offers("results.csv", "analyzed_offers.csv")