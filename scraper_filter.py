import pandas as pd

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

    # Filtro final recomendado
    df["is_relevant"] = (~df["is_excluded"]) & (df["level"] != "unspecified") & (df["has_tech_keyword"])

    # Seleccionar columnas relevantes
    columns = ["title", "company", "location", "contract_type", "level", "has_tech_keyword", "is_excluded", "is_relevant", "link"]
    return df[columns]

df = pd.read_csv("jobs_scraped.csv")
filtered_df = classify_job_titles(df)
filtered_df.to_csv("jobs_filtered.csv", index=False)

relevant_df = filtered_df[filtered_df["is_relevant"]]
relevant_df.head()
relevant_df.to_csv("jobs_relevant_only.csv", index=False)
