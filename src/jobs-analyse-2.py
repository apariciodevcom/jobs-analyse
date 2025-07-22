import pandas as pd
from utils import clean_text

# Parámetros configurables
LEVEL_KEYWORDS = ["praktikum", "intern", "junior", "senior"]
EXCLUDE_TITLES = ["ceo", "chief executive", "geschäftsführer", "director", "teamleitung", "leiter/in", "head of"]
EXCLUDE_KEYWORDS = ["reinigung", "verkauf", "stapler", "pflege"]
INCLUDE_TECH_KEYWORDS = ["python", "sql", "sap", "excel", "r", "tableau", "power bi", "cloud", "aws", "azure", "linux"]

def classify_job_titles(df):
    df = df.copy()
    df["title_lower"] = df["title"].str.lower()

    # Flags
    df["is_excluded"] = df["title_lower"].apply(lambda x: any(kw in x for kw in EXCLUDE_TITLES + EXCLUDE_KEYWORDS))
    df["has_tech_keyword"] = df["title_lower"].apply(lambda x: any(kw in x for kw in INCLUDE_TECH_KEYWORDS))
    df["level"] = df["title_lower"].apply(lambda x: next((lvl for lvl in LEVEL_KEYWORDS if lvl in x), "unspecified"))

    # Clasificación tipo de contrato
    def classify_contract(loc):
        if isinstance(loc, str):
            loc_lower = loc.lower()
            if "intern" in loc_lower or "praktikum" in loc_lower:
                return "internship"
            elif "unlimited" in loc_lower or "unbefristet" in loc_lower:
                return "permanent"
            elif "temporary" in loc_lower or "befristet" in loc_lower:
                return "temporary"
            elif "year" in loc_lower or "chf" in loc_lower:
                return "with_salary_info"
        return "unspecified"

    df["contract_type"] = df["location"].apply(classify_contract)

    # Filtro final recomendado como flag
    df["is_relevant"] = (~df["is_excluded"]) & (df["level"] != "unspecified") & (df["has_tech_keyword"])

    return df

# Leer y limpiar
df = pd.read_csv("jobs_scraped.csv")
for col in ["title", "company", "location", "link"]:
    df[col] = df[col].astype(str).apply(clean_text)

# Clasificar y exportar con todas las filas conservadas
classified_df = classify_job_titles(df)
classified_df.to_csv("output_2.csv", index=False, encoding="utf-8")
print("✅ Guardado: output_2.csv con todas las ofertas y campos de filtro.")
