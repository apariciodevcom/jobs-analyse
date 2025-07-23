import os
import re
import pandas as pd
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import regexp_tokenize
from nltk import ngrams
from langdetect import detect
import nltk

nltk.download("punkt")
nltk.download("stopwords")

# Ruta de entrada
input_file = r"D:\jobs-analyse\data\analyzed_offers_optimized_a.csv"
output_dir = r"D:\jobs-analyse\data"
os.makedirs(output_dir, exist_ok=True)

# Cargar datos
df = pd.read_csv(input_file)
df = df.dropna(subset=["titel", "beschreibung"])

# Detectar idioma
def detect_language(text):
    try:
        return detect(text)
    except:
        return "unknown"

df["lang_besch"] = df["beschreibung"].apply(detect_language)
df["lang_titel"] = df["titel"].apply(detect_language)

# Stopwords por idioma
stopwords_dict = {
    "de": set(stopwords.words("german")),
    "en": set(stopwords.words("english"))
}

def clean_and_tokenize(text, lang_code):
    text = re.sub(r"[^\w\s]", " ", str(text).lower())
    tokens = regexp_tokenize(text, r"\w+")
    stopwords_set = stopwords_dict.get(lang_code[:2], set())
    tokens_clean = [t for t in tokens if t not in stopwords_set and len(t) > 2]
    return tokens_clean

def extract_ngrams(tokens_list, n):
    return list(ngrams(tokens_list, n))

def process_column(df, column, lang_column):
    freq_tokens = Counter()
    freq_bigrams = Counter()
    freq_trigrams = Counter()

    print(f"\n🧪 Analizando columna: {column}\n")
    for idx, row in df.iterrows():
        lang = row[lang_column]
        text = row[column]
        tokens = clean_and_tokenize(text, lang)

        if idx < 10:
            print(f"[{idx}] Lang: {lang}, Tokens: {tokens}")
            print(f"→ {len(tokens)} tokens válidos.")

        if tokens:
            freq_tokens.update(tokens)
            freq_bigrams.update(extract_ngrams(tokens, 2))
            freq_trigrams.update(extract_ngrams(tokens, 3))

    def to_dataframe(counter_obj):
        df = pd.DataFrame(counter_obj.items(), columns=["ngram", "frecuencia"])
        df["ngram"] = df["ngram"].apply(lambda x: " ".join(x) if isinstance(x, tuple) else x)
        return df.sort_values(by="frecuencia", ascending=False)

    return to_dataframe(freq_tokens), to_dataframe(freq_bigrams), to_dataframe(freq_trigrams)

# Analizar 'titel'
tokens_titel, bigrams_titel, trigrams_titel = process_column(df, "titel", "lang_titel")
tokens_titel.to_csv(os.path.join(output_dir, "freq_titel_tokens.csv"), index=False)
bigrams_titel.to_csv(os.path.join(output_dir, "freq_titel_bigrams.csv"), index=False)
trigrams_titel.to_csv(os.path.join(output_dir, "freq_titel_trigrams.csv"), index=False)

# Analizar 'beschreibung'
tokens_besch, bigrams_besch, trigrams_besch = process_column(df, "beschreibung", "lang_besch")
tokens_besch.to_csv(os.path.join(output_dir, "freq_beschreibung_tokens.csv"), index=False)
bigrams_besch.to_csv(os.path.join(output_dir, "freq_beschreibung_bigrams.csv"), index=False)
trigrams_besch.to_csv(os.path.join(output_dir, "freq_beschreibung_trigrams.csv"), index=False)

print("\n✅ Análisis completado con logs. Revisa la consola para ver los tokens por fila.")
