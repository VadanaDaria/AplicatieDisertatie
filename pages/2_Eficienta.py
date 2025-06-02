import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

study_choice = st.selectbox("Alege un studiu:", list(data_all.keys()))
data = data_all[study_choice]

#Tabel outcomuri

outcome_module = data.get("protocolSection", {}).get("outcomesModule", {})
primary_outcomes = outcome_module.get("primaryOutcomes", [])
secondary_outcomes = outcome_module.get("secondaryOutcomes", [])

if not primary_outcomes and not secondary_outcomes:
    st.warning("⚠️ Nu există date de eficiență disponibile pentru acest studiu.")
    st.stop()

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
else:
    df_primary = pd.DataFrame()

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
else:
    df_secondary = pd.DataFrame()

# Valori

st.subheader("📈 Rezultate ")

try:
    outcome_measures = data["resultsSection"]["outcomeMeasuresModule"]["outcomeMeasures"]
    all_rows = []

    for outcome in outcome_measures:
        title = outcome.get("title", "N/A")
        unit = outcome.get("unitOfMeasure", "")
        timeframe = outcome.get("timeFrame", "")
        for category in outcome.get("classes", []):
            for cat in category.get("categories", []):
                for m in cat.get("measurements", []):
                    group_id = m.get("groupId", "N/A")
                    value = m.get("value", None)
                    spread = m.get("spread", None)
                    if value:
                        try:
                            all_rows.append({
                                "Indicator": title,
                                "Grup": group_id,
                                "Valoare": float(value),
                                "EroareStandard": float(spread) if spread else None,
                                "Unitate": unit,
                                "Interval de timp": timeframe
                            })
                        except ValueError:
                            continue
    df_real = pd.DataFrame(all_rows)

    if not df_real.empty:
        st.dataframe(df_real, use_container_width=True)

        st.markdown("### Selectează indicatorii pentru care dorești să vezi graficele:")
        indicators = df_real["Indicator"].unique().tolist()
        selected_indicators = st.multiselect("Indicatori:", indicators, default=indicators[:2]) 

        for indicator in selected_indicators:
            st.markdown(f"#### 📊 Grafic pentru: {indicator}")
            subset = df_real[df_real["Indicator"] == indicator]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=subset["Grup"],
                y=subset["Valoare"],
                error_y=dict(type='data', array=subset["EroareStandard"]),
                marker_color='teal'
            ))

            fig.update_layout(
                title=indicator,
                yaxis_title=subset["Unitate"].iloc[0] if subset["Unitate"].notnull().all() else "",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ Nu s-au găsit valori cantitative în outcomeMeasuresModule.")
except KeyError:
    st.info("ℹ️ Structura JSON nu conține outcomeMeasuresModule.")


#Violin Plot, Box Plot

st.subheader("🔍 Analiză Distribuție Indicatori")

if not df_primary.empty:
    fig = px.violin(df_primary, y="Indicator", box=True, points="all", title="Distribuție - Rezultate Primare")
    fig.update_layout(height=500, font=dict(size=14))
    st.plotly_chart(fig, use_container_width=True)

if not df_secondary.empty:
    fig = px.violin(df_secondary, y="Indicator", box=True, points="all", title="Distribuție - Rezultate Secundare")
    fig.update_layout(height=500, font=dict(size=14))
    st.plotly_chart(fig, use_container_width=True)

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
