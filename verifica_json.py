import streamlit as st
import json

# Funcție pentru încărcarea fișierelor JSON
@st.cache_data
def load_data():
    files = {
        "Homo_F508_1": "Homo_F508_1.json",
        "Homo_Hetero_F508": "Homo_Hetero_F508.json",
        "Non_F508": "Non_F508.json"
    }
    return {key: json.load(open(filename, encoding="utf-8")) for key, filename in files.items()}

# Încarcă toate datele
data = load_data()


# Funcție pentru extragerea datelor relevante
def extrage_date_studiu():
    # Extragem grupurile de tratament
    grupuri = data.get("armsInterventionsModule", {}).get("armGroups", [])
    
    print("Grupuri de tratament:")
    for grup in grupuri:
        label = grup.get("label")
        description = grup.get("description")
        num_subjects = grup.get("subjects", {}).get("numSubjects", "N/A")
        
        print(f"Grup: {label}")
        print(f"  Descriere: {description}")
        print(f"  Număr participanți: {num_subjects}")
        print('---')
    
    # Extragem măsurile de rezultat (exemplu: ppFEV1)
    outcome_measures = data.get("outcomeMeasuresModule", {}).get("outcomeMeasures", [])
    
    print("Măsuri de rezultat:")
    for measure in outcome_measures:
        if measure["title"] == "Percent Predicted Forced Expiratory Volume in 1 Second (ppFEV1)":
            description = measure.get("description")
            param_type = measure.get("paramType")
            dispersion_type = measure.get("dispersionType")
            unit_of_measure = measure.get("unitOfMeasure")
            
            # Extragem măsurile de la grupuri
            for category in measure.get("classes", []):
                for cat in category.get("categories", []):
                    for measurement in cat.get("measurements", []):
                        group_id = measurement.get("groupId")
                        value = measurement.get("value")
                        spread = measurement.get("spread")
                        
                        print(f"Grup: {group_id}")
                        print(f"  {description}: {value} {unit_of_measure}")
                        print(f"  Dispersion: {spread}")
            print('---')

# Apelăm funcția pentru a extrage datele
extrage_date_studiu()