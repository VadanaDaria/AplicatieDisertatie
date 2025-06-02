import streamlit as st
import json


@st.cache_data
def load_data():
    files = {
        "Homo_F508_1": "Homo_F508_1.json",
        "Homo_Hetero_F508": "Homo_Hetero_F508.json",
        "Non_F508": "Non_F508.json"
    }
    return {key: json.load(open(filename, encoding="utf-8")) for key, filename in files.items()}


data = load_data()


st.title("📊 Explorare Liberă")
st.write("### Selectează un studiu pentru a vizualiza datele:")
study = st.selectbox("Alege un studiu:", list(data.keys()))
study_data = data[study]

st.subheader("🔍 Grupuri de Tratament:")

arm_groups = (
    study_data.get("protocolSection", {}).get("armsInterventionsModule", {}).get("armGroups", []) +
    study_data.get("derivedSection", {}).get("armsInterventionsModule", {}).get("armGroups", [])
)

if arm_groups:
    for grup in arm_groups:
        label = grup.get("label", "Informație indisponibilă")
        description = grup.get("description", "Informație indisponibilă")
        intervention_names = grup.get("interventionNames", ["Informație indisponibilă"])
        st.write(f"**Grup:** {label}")
        st.write(f"  **Descriere:** {description}")
        st.write(f"  **Tratamente:** {', '.join(intervention_names)}")
        st.write("---")
else:
    st.warning("⚠️ Nu am găsit grupuri de tratament în JSON!")


# Rezultae
st.subheader("📊 Rezultate Clinice și Parametri de Evaluare")
outcome_measures = study_data.get("resultsSection", {}).get("outcomeMeasuresModule", {}).get("outcomeMeasures", [])

if outcome_measures:
    for measure in outcome_measures:
        title = measure.get("title", "Informație indisponibilă")
        description = measure.get("description", "Informație indisponibilă")
        param_type = measure.get("paramType", "Informație indisponibilă")
        dispersion_type = measure.get("dispersionType", "Informație indisponibilă")
        unit_of_measure = measure.get("unitOfMeasure", "Informație indisponibilă")
        
        st.write(f"**Titlu:** {title}")
        st.write(f"  **Descriere:** {description}")
        st.write(f"  **Tip Parametru:** {param_type}")
        st.write(f"  **Tip Dispersie:** {dispersion_type}")
        st.write(f"  **Unitatea de Măsură:** {unit_of_measure}")
        
        
        for category in measure.get("classes", []):
            for cat in category.get("categories", []):
                for measurement in cat.get("measurements", []):
                    group_id = measurement.get("groupId", "Informație indisponibilă")
                    value = measurement.get("value", "Informație indisponibilă")
                    spread = measurement.get("spread", "Informație indisponibilă")
                    
                    st.write(f"    - Grup: {group_id} → Valoare: {value} ± {spread}")
        st.write("---")
else:
    st.warning("⚠️ Nu am găsit măsuri de rezultat în JSON!")


#Date
with st.expander("🌐 Explorare Avansată (Debugging)"):
    st.write("📌 Tot JSON-ul:")
    st.json(study_data)

