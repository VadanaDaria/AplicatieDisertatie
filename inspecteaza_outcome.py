import streamlit as st
import json

# Functie pentru a încărca fișiere JSON
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Încărcați fișierele JSON (asigură-te că folosești calea corectă)
json_files = {
    "Homo_F508_1": "C:/Users/vadan/Desktop/Disertatie/Aplicatie/Homo_F508_1.json",
    "Homo_Hetero_F508": "C:/Users/vadan/Desktop/Disertatie/Aplicatie/Homo_Hetero_F508.json",
    "Non_F508": "C:/Users/vadan/Desktop/Disertatie/Aplicatie/Non_F508.json"
}

data_studies = {key: load_json(path) for key, path in json_files.items()}

# Aplicația Streamlit
st.title("🧬Analiza Eficienței Tratamentelor Medicale pentru Fibroză Chistică")

st.write("### Selectează un studiu pentru a vizualiza datele:")
study_choice = st.selectbox("Alege un studiu:", list(data_studies.keys()))

study_data = data_studies[study_choice]

st.write(f"### Detalii pentru studiul: {study_choice}")

# Afișează datele de titlu, status, sponsor și descriere
description_module = study_data.get('protocolSection', {}).get('descriptionModule', {})
status_module = study_data.get('protocolSection', {}).get('statusModule', {})
sponsor_module = study_data.get('protocolSection', {}).get('sponsorCollaboratorsModule', {}).get('leadSponsor', {})

# Folosește datele sau mesaje de eroare personalizate
st.write(f"Titlu: {description_module.get('briefSummary', 'Textul nu este disponibil')}")
st.write(f"Status: {status_module.get('overallStatus', 'Status necunoscut')}")
st.write(f"Sponsor: {sponsor_module.get('name', 'Sponsor necunoscut')}")
st.write(f"Descriere: {description_module.get('briefSummary', 'Descrierea nu este disponibilă')}")


# Afișarea outcome-urilor măsurate
st.write("### Outcome-uri măsurate:")

outcome_module = study_data.get('protocolSection', {}).get('outcomesModule', {})

# Verifică dacă există primaryOutcomes și secondaryOutcomes și afișează-le
if 'primaryOutcomes' in outcome_module and outcome_module['primaryOutcomes']:
    st.write("#### Primary Outcomes:")
    for outcome in outcome_module['primaryOutcomes']:
        # Verifică dacă există descriere
        description = outcome.get('description', 'Descriere nu este disponibilă')
        st.write(f"- **{outcome['measure']}**: {description}")
        st.write(f"  - **Time Frame**: {outcome['timeFrame']}")
        st.write("---")

if 'secondaryOutcomes' in outcome_module and outcome_module['secondaryOutcomes']:
    st.write("#### Secondary Outcomes:")
    for outcome in outcome_module['secondaryOutcomes']:
        # Verifică dacă există descriere
        description = outcome.get('description', 'Descriere nu este disponibilă')
        st.write(f"- **{outcome['measure']}**: {description}")
        st.write(f"  - **Time Frame**: {outcome['timeFrame']}")
        st.write("---")

# Dacă nu sunt outcome-uri disponibile
if not outcome_module.get('primaryOutcomes') and not outcome_module.get('secondaryOutcomes'):
    st.write("Nu sunt disponibile outcome-uri pentru acest studiu.")

#Butoane+ pagini
    st.write("## 📂 Navigare Detaliată")

col1, col2, col3 = st.columns(3)

with col1:
    st.page_link("pages/1_Demografie.py", label="🔍 Demografie participanți", icon="👥")

with col2:
    st.page_link("pages/2_Eficienta.py", label="📈 Eficiența tratamentului", icon="💊")

with col3:
    st.page_link("pages/3_Siguranta.py", label="🛡️ Siguranță și TEAE/SAE", icon="⚠️")