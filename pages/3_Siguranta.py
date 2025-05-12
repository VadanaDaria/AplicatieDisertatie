import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns


@st.cache_data
def load_data():
    files = {
        "Homo_F508_1": "Homo_F508_1.json",
        "Homo_Hetero_F508": "Homo_Hetero_F508.json",
        "Non_F508": "Non_F508.json"
    }
    return {key: json.load(open(filename, encoding="utf-8")) for key, filename in files.items()}

data = load_data()

st.title("🛡️ Siguranța și Evenimente Adverse")
st.write("### Selectează un studiu pentru a vizualiza datele:")
study = st.selectbox("Alege studiul:", list(data.keys()))


study_data = data[study]
results_section = study_data.get("resultsSection", {})
adverse_events_module = results_section.get("adverseEventsModule", {})


if not adverse_events_module:
    st.warning("⚠️ Nu există date de siguranță disponibile pentru acest studiu.")
    st.stop()

# Efecte adverese descriere
st.subheader("📋 Descrierea Efectelor Adverse (Adverse Events - AE)")

ae_descriptions = []
for group in adverse_events_module.get("eventGroups", []):
    ae_title = group.get("title", "N/A")
    ae_description = group.get("description", "N/A")

    # Numar efecte adverse serioase, altele
    ae_serious_effects = group.get("seriousNumAffected", 0)
    ae_other_effects = group.get("otherNumAffected", 0)

    ae_descriptions.append({
        "Grup": ae_title,
        "Descriere ": ae_description,
        "Efecte Serioase (Număr Afectați)": ae_serious_effects,
        "Alte Efecte (Număr Afectați)": ae_other_effects,
    })

# Descriere efecte
if ae_descriptions:
    df_descriptions = pd.DataFrame(ae_descriptions)
    st.dataframe(df_descriptions, use_container_width=True)

#Distributie severitate
st.subheader("📊 Distribuția Severității Efectelor Adverse")
severities = [
    ev["Efecte Serioase (Număr Afectați)"] + ev["Alte Efecte (Număr Afectați)"] 
    for ev in ae_descriptions
]

if severities:
    fig = go.Figure(data=[go.Bar(
        x=["Serioase", "Altele"],
        y=[sum(ev["Efecte Serioase (Număr Afectați)"] for ev in ae_descriptions), 
           sum(ev["Alte Efecte (Număr Afectați)"] for ev in ae_descriptions)],
        marker_color='orange'
    )])
    fig.update_layout(
        title="Distribuția Severității Efectelor Adverse",
        xaxis_title="Tip Eveniment",
        yaxis_title="Număr de Efecte Adverse",
        height=400,
        font=dict(size=14),
    )
    st.plotly_chart(fig, use_container_width=True)

# Boxplot efecte pe grupuri
st.subheader("📦 Distribuția Efectelor Adverse pe Grupuri")
plt.figure(figsize=(8, 5))
sns.boxplot(data=pd.DataFrame(ae_descriptions)[["Efecte Serioase (Număr Afectați)", "Alte Efecte (Număr Afectați)"]])
plt.title('Distribuția Efectelor Adverse pe Grupuri')
st.pyplot(plt)

#Pie Chart
st.subheader("🥧 Proporția Efectelor Adverse")
fig = go.Figure(data=[go.Pie(labels=["Serioase", "Altele"], 
                             values=[sum(ev["Efecte Serioase (Număr Afectați)"] for ev in ae_descriptions), 
                                     sum(ev["Alte Efecte (Număr Afectați)"] for ev in ae_descriptions)])])
fig.update_layout(title="Proporția Efectelor Adverse")
st.plotly_chart(fig, use_container_width=True)


#Tabel Detalii 
def parse_adverse_events(event_type):
    events = adverse_events_module.get(event_type, [])
    parsed_data = []
    for event in events:
        term = event.get("term", "N/A")
        organ_system = event.get("organSystem", "N/A")
        assessment_type = event.get("assessmentType", "N/A")
        
        for stat in event.get("stats", []):
            group_id = stat.get("groupId", "N/A")
            num_affected = stat.get("numAffected", 0)
            num_at_risk = stat.get("numAtRisk", 0)
            
            group_title = next((g["title"] for g in adverse_events_module.get("eventGroups", []) if g["id"] == group_id), "N/A")
            
            parsed_data.append({
                "Tip Eveniment": "Serios" if event_type == "seriousEvents" else "Altele",
                "Grup": group_title,
                "Termen": term,
                "Sistem Afectat": organ_system,
                "Număr Afectați": num_affected,
                "Număr la Risc": num_at_risk
            })
    return parsed_data

serious_events = parse_adverse_events("seriousEvents")
other_events = parse_adverse_events("otherEvents")

# Buton detalii
with st.expander("🔎 Vezi Evenimente Adverse Detaliate"):
    if serious_events:
        st.markdown("### 🛑 Evenimente Adverse Serioase")
        st.dataframe(pd.DataFrame(serious_events), use_container_width=True)

    if other_events:
        st.markdown("### ⚠️ Alte Evenimente Adverse")
        st.dataframe(pd.DataFrame(other_events), use_container_width=True)
