import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Analiză CFQ-R și Test Sudorii", layout="wide")

@st.cache_data
def load_data():
    files = {
        "Homo_F508_1": "Homo_F508_1.json",
        "Homo_Hetero_F508": "Homo_Hetero_F508.json",
        "Non_F508": "Non_F508.json"
    }
    data = {}
    for key, filename in files.items():
        with open(filename, encoding="utf-8") as f:
            data[key] = json.load(f)
    return data

def extract_outcome_measurements(study_data, keywords):
    outcomes = study_data.get("resultsSection", {}).get("outcomeMeasuresModule", {}).get("outcomeMeasures", [])
    records = []
    for outcome in outcomes:
        if any(kw.lower() in outcome.get("title", "").lower() for kw in keywords):
            title = outcome.get("title", "N/A")
            measure_type = outcome.get("type", "N/A")
            classes = outcome.get("classes", [])
            for cls in classes:
                for cat in cls.get("categories", []):
                    for m in cat.get("measurements", []):
                        records.append({
                            "Measure": title,
                            "Group": m.get("groupId", "N/A"),
                            "Value": float(m.get("value", 0)),
                            "Lower": float(m.get("lowerLimit", 0)),
                            "Upper": float(m.get("upperLimit", 0))
                        })
    return pd.DataFrame(records)

data = load_data()
st.title("📊 Analiza Studiilor Clinice - CFQ-R și Testul Sudorii")
study = st.selectbox("Selectează studiul:", ["Toate Studiile"] + list(data.keys()))
measure_type = st.radio("Selectează măsura de analizat:", ("CFQ-R (Respiratory Domain Score)", "Testul Sudorii"))

keywords = ["cfq-r"] if "CFQ-R" in measure_type else ["sweat chloride"]

if study == "Toate Studiile":
    dfs = []
    for name, content in data.items():
        df = extract_outcome_measurements(content, keywords)
        if not df.empty:
            df["Study"] = name
            dfs.append(df)
    df_filtered = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
else:
    df_filtered = extract_outcome_measurements(data[study], keywords)
    if not df_filtered.empty:
        df_filtered["Study"] = study

if df_filtered.empty:
    st.warning("Nu există date numerice disponibile pentru selecția curentă.")
else:
    st.subheader(f"Datele pentru {'toate studiile' if study == 'Toate Studiile' else study} - {measure_type}")
    st.dataframe(df_filtered)

    # Bar Chart
    st.subheader("📊 Valori medii per grup (și studiu)")
    fig_bar = px.bar(df_filtered, x="Group", y="Value", color="Group",
                     barmode="group", facet_col="Study" if study == "Toate Studiile" else None,
                     title="Valori medii pe grupuri")
    st.plotly_chart(fig_bar, use_container_width=True)

    # CI
    st.subheader("📏 Valori medii și Interval de Încredere (95%)")
    fig_error = go.Figure()
    for grp in df_filtered["Group"].unique():
        sub = df_filtered[df_filtered["Group"] == grp]
        fig_error.add_trace(go.Bar(
            name=grp,
            x=sub["Measure"] + ", " + sub["Study"] if "Study" in sub else sub["Measure"],
            y=sub["Value"],
            error_y=dict(
                type='data',
                array=sub["Upper"] - sub["Value"],
                arrayminus=sub["Value"] - sub["Lower"]
            )
        ))
    fig_error.update_layout(barmode='group')
    st.plotly_chart(fig_error, use_container_width=True)

   
# Violin Plot
st.subheader("🎻 Distribuția valorilor (Violin Plot)")

fig_violin = px.violin(
    df_filtered,
    x="Group",
    y="Value",
    color="Group",
    box=True,  
    points="all",  
    title="Distribuția valorilor și estimarea densității "
)
st.plotly_chart(fig_violin, use_container_width=True)
