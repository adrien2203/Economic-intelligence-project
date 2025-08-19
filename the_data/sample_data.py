import pandas as pd
import json
import os
from datetime import datetime, timedelta
from utils.api import get_latest_unemployment

CACHE_PATH = "unemployment_cache.json"

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
                # Assure que le résultat est bien un tuple (float, str)
                if isinstance(result, tuple) and len(result) == 2:
                    new_data[code] = result
                else:
                    new_data[code] = (None, "Données indisponibles")
            except Exception:
                new_data[code] = (None, "Données indisponibles")
        cache["data"] = new_data
        cache["last_updated"] = datetime.today().strftime("%Y-%m-%d")
        save_cache(cache)
    else:
        print("✅ Cache à jour, pas d'appel API nécessaire.")
    return cache["data"]



def get_data():
    df = pd.DataFrame({
        'Country': ['Switzerland', 'Germany', 'United States', 'China', 'Italy', 'France', 'United Kingdom', 'India', 'Japan', 'Netherlands', 'Belgium', 'Austria', 'Spain', 'Sweden', 'Poland', 'Hong Kong', 'Singapore', 'Russia', 'South Korea', 'Brazil', 'Mexico'],
        'ISO_Code': ['CHE', 'DEU', 'USA', 'CHN', 'ITA', 'FRA', 'GBR', 'IND', 'JPN', 'NLD', 'BEL', 'AUT', 'ESP', 'SWE', 'POL', 'HKG', 'SGP', 'RUS', 'KOR', 'BRA', 'MEX'],
        'Attractiveness': [90, 70, 80, 75, 60, 85, 70, 50, 40, 50, 60, 50, 40, 30, 50, 40, 30, 50, 60, 70, 80],
        'Economy': [8.5, 7.0, 8.0, 7.5, 6.0, 8.3, 8.0, 5.0, 3.0, 2.0, 5.7, 4.6, 7.0, 3.5, 6.0, 4.0, 3.5, 6.0, 6.0, 5.0, 4.5],
        'Stability': [9.0, 8.2, 5.8, 7.8, 5.5, 8.0, 6.0, 8.5, 8.0, 7.5, 6.0, 8.3, 8.0, 5.0, 3.0, 2.0, 5.7, 4.6, 7.0, 3.5, 6.0]
    })

    unemployment_data = update_cache_if_needed(df['ISO_Code'].tolist())

    # Séparation explicite des deux valeurs du tuple
    df['Unemployment'] = df['ISO_Code'].apply(lambda code: unemployment_data.get(code, (None, "Données indisponibles"))[0])
    df['UnemploymentText'] = df['ISO_Code'].apply(lambda code: unemployment_data.get(code, (None, "Données indisponibles"))[1])

    return df


# Variable globale pour les autres modules
data = get_data()