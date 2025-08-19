import pandas as pd
import json
import os
import requests
from datetime import datetime, timedelta

CACHE_PATH = "unemployment_cache.json"

# 🔍 Fonction pour récupérer les données de chômage depuis l'API World Bank
def get_latest_unemployment(country_code):
    iso_map = {
        "CHE": "CH", "DEU": "DE", "USA": "US", "CHN": "CN", "ITA": "IT", "FRA": "FR",
        "GBR": "GB", "IND": "IN", "JPN": "JP", "NLD": "NL", "BEL": "BE", "AUT": "AT",
        "ESP": "ES", "SWE": "SE", "POL": "PL", "HKG": "HK", "SGP": "SG", "RUS": "RU",
        "KOR": "KR", "BRA": "BR", "MEX": "MX"
    }

    if country_code not in iso_map:
        return (None, "Code ISO non reconnu")

    indicator = "SL.UEM.TOTL.ZS"
    url = f"https://api.worldbank.org/v2/country/{iso_map[country_code]}/indicator/{indicator}?format=json&per_page=1"

    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        if data and len(data) > 1 and data[1]:
            latest = data[1][0]
            value = latest['value']
            date = latest['date']
            if value is not None:
                return (value, f"{value:.1f}% ({date})")
            else:
                return (None, "Pas de données disponibles")
        else:
            return (None, "Réponse vide")
    except Exception as e:
        print(f"❌ Erreur API pour {country_code} : {e}")
        return (None, "Erreur API")

# 📦 Gestion du cache local
def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    return {"last_updated": None, "data": {}}

def save_cache(cache):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f)

def should_update(last_updated):
    if not last_updated:
        return True
    last_date = datetime.strptime(last_updated, "%Y-%m-%d")
    return datetime.today() - last_date > timedelta(days=7)

def update_cache_if_needed(iso_codes):
    cache = load_cache()
    if should_update(cache["last_updated"]):
        print("🔄 Mise à jour des données de chômage...")
        new_data = {}
        for code in iso_codes:
            try:
                result = get_latest_unemployment(code)
                print(f"📡 {code} → {result}")
                new_data[code] = result
            except Exception:
                new_data[code] = (None, "Données indisponibles")
        cache["data"] = new_data
        cache["last_updated"] = datetime.today().strftime("%Y-%m-%d")
        save_cache(cache)
    else:
        print("✅ Cache à jour, pas d'appel API nécessaire.")
    return cache["data"]

# 📊 Construction du DataFrame enrichi
def get_data():
    df = pd.DataFrame({
        'Country': ['Switzerland', 'Germany', 'United States', 'China', 'Italy', 'France', 'United Kingdom', 'India', 'Japan', 'Netherlands', 'Belgium', 'Austria', 'Spain', 'Sweden', 'Poland', 'Hong Kong', 'Singapore', 'Russia', 'South Korea', 'Brazil', 'Mexico'],
        'ISO_Code': ['CHE', 'DEU', 'USA', 'CHN', 'ITA', 'FRA', 'GBR', 'IND', 'JPN', 'NLD', 'BEL', 'AUT', 'ESP', 'SWE', 'POL', 'HKG', 'SGP', 'RUS', 'KOR', 'BRA', 'MEX'],
        'Attractiveness': [90, 70, 80, 75, 60, 85, 70, 50, 40, 50, 60, 50, 40, 30, 50, 40, 30, 50, 60, 70, 80],
        'Economy': [8.5, 7.0, 8.0, 7.5, 6.0, 8.3, 8.0, 5.0, 3.0, 2.0, 5.7, 4.6, 7.0, 3.5, 6.0, 4.0, 3.5, 6.0, 6.0, 5.0, 4.5],
        'Stability': [9.0, 8.2, 5.8, 7.8, 5.5, 8.0, 6.0, 8.5, 8.0, 7.5, 6.0, 8.3, 8.0, 5.0, 3.0, 2.0, 5.7, 4.6, 7.0, 3.5, 6.0]
    })

    unemployment_data = update_cache_if_needed(df['ISO_Code'].tolist())
    df[['Unemployment', 'UnemploymentText']] = df['ISO_Code'].apply(lambda code: unemployment_data.get(code, (None, "Données indisponibles"))).apply(pd.Series)
    return df

# 📂 Variable globale accessible par les autres modules
data = get_data()