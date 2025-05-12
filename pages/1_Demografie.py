import streamlit as st
import json
import matplotlib.pyplot as plt


def load_json(file):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)

json_files = {
    "Homo_F508_1": "Homo_F508_1.json",
    "Homo_Hetero_F508": "Homo_Hetero_F508.json",
    "Non_F508": "Non_F508.json"
}

st.title("📊 Profilul Demografic al Participanților")

st.write("### Selectează un studiu pentru a vizualiza datele:")
study = st.selectbox("Alege un studiu:", list(json_files.keys()))
data = load_json(json_files[study])

#  Datele din eligibilityModule
eligibility = data.get("protocolSection", {}).get("eligibilityModule", {})

# Gen, varsta
sex = eligibility.get("sex", "Informație nedisponibilă")
st.subheader("🧬 Genurile Acceptate")
st.write(f"**Gen:** {sex}")

min_age = eligibility.get("minimumAge", "Nespecificat")
max_age = eligibility.get("maximumAge", "Nespecificat")
st.subheader("🎂 Grupa de Vârstă Acceptată")
st.write(f"**Vârsta minimă:** {min_age}")
st.write(f"**Vârsta maximă:** {max_age}")

# Criterii de eligibilitate
st.subheader("📄 Criterii de eligibilitate")
eligibility = data.get("protocolSection", {}).get("eligibilityModule", {})

# Gen, varsta
sex = eligibility.get("sex", "Informație nedisponibilă")
st.write(f"**Genuri acceptate:** {sex}")
min_age = eligibility.get("minimumAge", "Nespecificat")
max_age = eligibility.get("maximumAge", "Nespecificat")
st.write(f"**Grupa de vârstă admisă:** {min_age} - {max_age}")

# Criterii includere/excludere
criterii = eligibility.get("eligibilityCriteria", "Nu există criterii disponibile.")

with st.expander("📋 Vezi criteriile de includere și excludere"):
    st.markdown(criterii.replace("\n", "  \n"))  

# Grafic varsta
st.subheader("📊 Reprezentare Vizuală Vârstă")
if min_age != "Nespecificat" or max_age != "Nespecificat":
    age_labels = ['Minimă', 'Maximă']
    try:
        min_val = int(min_age.split()[0])
    except:
        min_val = 0
    try:
        max_val = int(max_age.split()[0])
    except:
        max_val = min_val + 20  

    fig2, ax2 = plt.subplots()
    ax2.bar(age_labels, [min_val, max_val], color='lightgreen')
    ax2.set_ylabel("Vârstă (ani)")
    st.pyplot(fig2)
else:
    st.info("Nu sunt suficiente date pentru a genera graficul de vârstă.")

# Locatii, spitale unde s-au facut studiilee
st.subheader("🌍 Locațiile centrelor de studiu")

locations = data.get("protocolSection", {}).get("contactsLocationsModule", {}).get("locations", [])

if locations:
    import pandas as pd

    # Coordonate
    coords = []
    for loc in locations:
        geo = loc.get("geoPoint", {})
        if "lat" in geo and "lon" in geo:
            coords.append({
               
                "Oraș": loc.get("city", "N/A"),
                "Țară": loc.get("country", "N/A"),
                "Centru": loc.get("facility", "N/A"),
                 "lat": geo["lat"],
                "lon": geo["lon"]
            })

    df_coords = pd.DataFrame(coords)


    st.map(df_coords[["lat", "lon"]])

    # Tabel cu locatii
    st.write("📌 Detalii locații:")
    st.dataframe(df_coords)
else:
    st.warning("Nu există informații despre locațiile studiului.")
