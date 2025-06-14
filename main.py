import streamlit as st
import json

#Incarcare date
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

json_files = {
    "Homo_F508_1": "Homo_F508_1.json",  
    "Homo_Hetero_F508": "Homo_Hetero_F508.json",  
    "Non_F508": "Non_F508.json"  
}

data_studies = {key: load_json(path) for key, path in json_files.items()}


#  Streamlit
st.title("🧬Analiza Eficienței Tratamentelor Medicale pentru Fibroză Chistică")

st.write("### Selectează un studiu pentru a vizualiza datele:")
study_choice = st.selectbox("Alege un studiu:", list(data_studies.keys()))

study_data = data_studies[study_choice]

st.write(f"### Detalii pentru studiul: {study_choice}")

#Titlu, stadiu, descriere studiu
description_module = study_data.get('protocolSection', {}).get('descriptionModule', {})
status_module = study_data.get('protocolSection', {}).get('statusModule', {})
sponsor_module = study_data.get('protocolSection', {}).get('sponsorCollaboratorsModule', {}).get('leadSponsor', {})

st.write(f"Titlu: {description_module.get('briefSummary', 'Textul nu este disponibil')}")
st.write(f"Status: {status_module.get('overallStatus', 'Status necunoscut')}")
st.write(f"Sponsor: {sponsor_module.get('name', 'Sponsor necunoscut')}")
st.write(f"Descriere: {description_module.get('briefSummary', 'Descrierea nu este disponibilă')}")

# Rezultate studii
st.write("### Rezultate:")
outcome_module = study_data.get('protocolSection', {}).get('outcomesModule', {})

# PrimaryOutcomes si secondaryOutcomes
if 'primaryOutcomes' in outcome_module and outcome_module['primaryOutcomes']:
    st.write("#### Primary Outcomes:")
    for outcome in outcome_module['primaryOutcomes']:
        # Descriere
        description = outcome.get('description', 'Descriere nu este disponibilă')
        st.write(f"- **{outcome['measure']}**: {description}")
        st.write(f"  - **Time Frame**: {outcome['timeFrame']}")
        st.write("---")

if 'secondaryOutcomes' in outcome_module and outcome_module['secondaryOutcomes']:
    st.write("#### Secondary Outcomes:")
    for outcome in outcome_module['secondaryOutcomes']:
        # Descriere
        description = outcome.get('description', 'Descriere nu este disponibilă')
        st.write(f"- **{outcome['measure']}**: {description}")
        st.write(f"  - **Time Frame**: {outcome['timeFrame']}")
        st.write("---")

if not outcome_module.get('primaryOutcomes') and not outcome_module.get('secondaryOutcomes'):
    st.write("Nu sunt disponibile outcome-uri pentru acest studiu.")

