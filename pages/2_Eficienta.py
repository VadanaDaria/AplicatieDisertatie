import streamlit as st
import json
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

@st.cache_data
def load_data():
    with open("Homo_F508_1.json", encoding='utf-8') as f:
        data1 = json.load(f)
    with open("Homo_Hetero_F508.json", encoding='utf-8') as f:
        data2 = json.load(f)
    with open("Non_F508.json", encoding='utf-8') as f:
        data3 = json.load(f)
    return {"Homo_F508_1": data1, "Homo_Hetero_F508": data2, "Non_F508": data3}

data_all = load_data()

st.title("📊 Analiza Eficienței Tratamentului")

st.write("### Selectează un studiu pentru a vizualiza datele:")
study_choice = st.selectbox("Alege un studiu:", list(data_all.keys()))
data = data_all[study_choice]


outcome_module = data.get("protocolSection", {}).get("outcomesModule", {})
primary_outcomes = outcome_module.get("primaryOutcomes", [])
secondary_outcomes = outcome_module.get("secondaryOutcomes", [])

if not primary_outcomes and not secondary_outcomes:
    st.warning("⚠️ Nu există date de eficiență disponibile pentru acest studiu.")
    st.stop()

#Rezultate
st.subheader("🎯 Rezultate Primare")
primary_data = []
for outcome in primary_outcomes:
    measure = outcome.get("measure", "N/A")
    description = outcome.get("description", "N/A")
    timeframe = outcome.get("timeFrame", "N/A")
    
    if measure != "N/A":
        primary_data.append({
            "Indicator": measure,
            "Descriere": description,
            "Interval de timp": timeframe
        })

if primary_data:
    df_primary = pd.DataFrame(primary_data)
    st.dataframe(df_primary, use_container_width=True)


st.subheader("📌 Rezultate Secundare")
secondary_data = []
for outcome in secondary_outcomes:
    measure = outcome.get("measure", "N/A")
    description = outcome.get("description", "N/A")
    timeframe = outcome.get("timeFrame", "N/A")
    
    if measure != "N/A":
        secondary_data.append({
            "Indicator": measure,
            "Descriere": description,
            "Interval de timp": timeframe
        })

if secondary_data:
    df_secondary = pd.DataFrame(secondary_data)
    st.dataframe(df_secondary, use_container_width=True)

#Grafice
st.subheader("🔍 Analiză Distribuție Eficiență")

#Violin Plot distributie
if not df_primary.empty:
    fig = px.violin(df_primary, y="Indicator", box=True, points="all", title="Distribuție - Rezultate Primare")
    fig.update_layout(height=500, font=dict(size=14))
    st.plotly_chart(fig, use_container_width=True)

if not df_secondary.empty:
    fig = px.violin(df_secondary, y="Indicator", box=True, points="all", title="Distribuție - Rezultate Secundare")
    fig.update_layout(height=500, font=dict(size=14))
    st.plotly_chart(fig, use_container_width=True)


st.info("✅ Graficele de distribuție sunt reprezentate prin Violin Plot pentru a observa variațiile și densitatea rezultatelor măsurate în cadrul studiului ales.")

#Corelatie Box Plot
st.subheader("📦 Box Plot: Corelație între Rezultate Primare și Secundare")

df_primary_valid = df_primary[df_primary["Indicator"] != "N/A"]
df_secondary_valid = df_secondary[df_secondary["Indicator"] != "N/A"]

combined_df = pd.concat([
    pd.DataFrame({"Tip": "Primar", "Indicator": df_primary_valid["Indicator"]}),
    pd.DataFrame({"Tip": "Secundar", "Indicator": df_secondary_valid["Indicator"]})
])

fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(x="Tip", y="Indicator", data=combined_df, ax=ax)
plt.title("Distribuția Valorilor pentru Rezultate Primare și Secundare")
plt.grid(True, linestyle='--', alpha=0.7)

st.pyplot(fig)





