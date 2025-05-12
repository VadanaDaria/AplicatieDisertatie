import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


@st.cache_data
def load_data():
    files = {
        "Homo_F508_1": "Homo_F508_1.json",
        "Homo_Hetero_F508": "Homo_Hetero_F508.json",
        "Non_F508": "Non_F508.json"
    }
    return {key: json.load(open(filename, encoding="utf-8")) for key, filename in files.items()}


data = load_data()

st.title("📊 Analiza Outcome-urilor în Studiile Clinice")
st.write("### Selectează un studiu pentru a vizualiza datele:")
study = st.selectbox("Alege studiul sau compară toate studiile:", ["Toate Studiile"] + list(data.keys()))

# Statistici
st.subheader("📊 Statistici pentru Outcome-uri")
st.markdown('''Outcome-urile sunt măsurători specifice utilizate pentru a evalua eficacitatea și siguranța tratamentului în cadrul unui studiu clinic. 
Acestea pot include parametri fiziologici, biochimici, calitatea vieții sau măsurători clinice obiective.''')


# Extragere oucomes
def get_outcomes_module(study_data):
    return study_data.get("protocolSection", {}).get("outcomesModule", {})

if study == "Toate Studiile":
    primary_outcomes_list = []
    secondary_outcomes_list = []

   
    for key, study_data in data.items():
        outcomes_module = get_outcomes_module(study_data)
        primary = outcomes_module.get("primaryOutcomes", [])
        secondary = outcomes_module.get("secondaryOutcomes", [])

        for outcome in primary:
            primary_outcomes_list.append({
                "Studiu": key,
                "Măsură": outcome.get("measure", "N/A"),
                "Interval de timp": outcome.get("timeFrame", "N/A")
            })

        for outcome in secondary:
            secondary_outcomes_list.append({
                "Studiu": key,
                "Măsură": outcome.get("measure", "N/A"),
                "Interval de timp": outcome.get("timeFrame", "N/A")
            })

    
    # DataFrame-uri
    primary_df = pd.DataFrame(primary_outcomes_list)
    secondary_df = pd.DataFrame(secondary_outcomes_list)

    st.markdown("### 📌 Outcome-uri Primare")
    st.dataframe(primary_df, use_container_width=True)
    st.markdown("### 📌 Outcome-uri Secundare")
    st.dataframe(secondary_df, use_container_width=True)

    
    # Distributie pe Studii
    st.markdown("### 🔎 Distribuția Outcome-urilor pe Studii")
    
    # Histograme
    fig_primary = px.histogram(primary_df, x="Studiu", color="Studiu", title="Distribuția Outcome-urilor Primare")
    st.plotly_chart(fig_primary, use_container_width=True)

    fig_secondary = px.histogram(secondary_df, x="Studiu", color="Studiu", title="Distribuția Outcome-urilor Secundare")
    st.plotly_chart(fig_secondary, use_container_width=True)

   
    #Box Plot distributie
    st.subheader("📦 Box Plot pentru Distribuția Outcome-urilor")
    fig_box = go.Figure()
    fig_box.add_trace(go.Box(
        y=primary_df["Măsură"],
        name="Outcome Primar",
        boxmean="sd"
    ))
    fig_box.update_layout(
        title="Distribuția Outcome-urilor Primare (Box Plot)",
        yaxis_title="Măsură",
        height=600,
        width=900
    )
    st.plotly_chart(fig_box, use_container_width=True)

 
    #Grafic Densitate
    st.subheader("🌫️ Grafic de Densitate pentru Outcome-uri Primare")
    fig_density = px.density_contour(primary_df, x="Măsură", title="Distribuția Densității Outcome-urilor Primare")
    fig_density.update_layout(
        height=600,
        width=900
    )
    st.plotly_chart(fig_density, use_container_width=True)

    # Grafic evolutie temporala
    st.subheader("📈 Evoluția Temporală a Outcome-urilor")
    if "Interval de timp" in primary_df.columns:
        fig_time = px.line(primary_df, x="Interval de timp", y="Măsură", title="Evoluția Outcome-urilor Primare în Timp")
        fig_time.update_layout(
            height=600,
            width=900
        )
        st.plotly_chart(fig_time, use_container_width=True)

else:
    
    #Un singur studiu
    study_data = data[study]
    outcomes_module = get_outcomes_module(study_data)

    primary_outcomes = outcomes_module.get("primaryOutcomes", [])
    secondary_outcomes = outcomes_module.get("secondaryOutcomes", [])

   
    #DataFrame pt afisare
    primary_df = pd.DataFrame([{
        "Măsură": outcome.get("measure", "N/A"),
        "Descriere": outcome.get("description", "N/A"),
        "Interval de timp": outcome.get("timeFrame", "N/A")
    } for outcome in primary_outcomes])

    secondary_df = pd.DataFrame([{
        "Măsură": outcome.get("measure", "N/A"),
        "Descriere": outcome.get("description", "N/A"),
        "Interval de timp": outcome.get("timeFrame", "N/A")
    } for outcome in secondary_outcomes])

    st.markdown("### 📌 Outcome-uri Primare")
    st.dataframe(primary_df, use_container_width=True)

    st.markdown("### 📌 Outcome-uri Secundare")
    st.dataframe(secondary_df, use_container_width=True)

   
    st.subheader("📈 Analiză Vizuală a Outcome-urilor")
    categories = ["Outcome-uri Primare", "Outcome-uri Secundare"]
    num_outcomes = [len(primary_outcomes), len(secondary_outcomes)]

    fig = go.Figure(data=[go.Bar(x=categories, y=num_outcomes, marker_color=['#4CAF50', '#FF9800'])])
    fig.update_layout(
        title="Numărul de Outcome-uri per Categorie",
        xaxis_title="Categorie",
        yaxis_title="Număr de Outcome-uri",
        height=400,
        font=dict(size=14)
    )
    st.plotly_chart(fig, use_container_width=True)
