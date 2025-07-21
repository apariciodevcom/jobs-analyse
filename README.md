# Jobs Analyse St. Gallen

Automatisierte Analyse von Stellenangeboten in der Ostschweiz (Region St. Gallen).

Dieses Projekt umfasst:

- **Scraping von Stellenangeboten** von jobs.ch mit Selenium
- **Semantische Klassifikation** nach Rolle, Seniorität, Branche und Technologien
- **Erkennung von Unternehmensart** (Startup, privat, öffentlich, Beratung)
- **Extraktion von Schlüsselwörtern**, Technologien, Funktionen und Anforderungen
- **Erstellung einer strukturierten CSV-Datei** zur Entscheidungsunterstützung
- **Wöchentliche Ausführung möglich**, mit detailliertem Logging

## Struktur

- `scraper_jobs_info.py`: Extrahiert die vollständigen Stellenanzeigen von jobs.ch
- `fase3_analysis.py`: Analysiert den Text jeder Anzeige mithilfe von NLP
- `results.csv`: Rohdaten der gesammelten Anzeigen
- `analyzed_offers.csv`: Finales, angereichertes Ergebnis

## Voraussetzungen

```bash
pip install -r requirements.txt
```

Benötigte Hauptpakete:
- `pandas`
- `sentence-transformers`
- `scikit-learn` (optional für spätere Klassifikation)
- `selenium`

## Lizenz

Dieses Projekt verwendet die MIT-Lizenz.