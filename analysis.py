import pandas as pd

# Cargar el archivo original
df = pd.read_csv("jobs_zurich.csv")

# Eliminar duplicados
df_clean = df.drop_duplicates(subset=["title", "company", "location"])

# Contar número de ofertas por empresa
freq = df_clean["company"].value_counts().reset_index()
freq.columns = ["company", "n_ofertas"]

# Guardar resultados
df_clean.to_csv("jobs_st_gallen_basic_dedup.csv", index=False, encoding="utf-8")
freq.to_csv("frecuencia_empresas.csv", index=False, encoding="utf-8")

# Mostrar top 10
print(freq.head(20))
