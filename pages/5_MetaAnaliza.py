import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from scipy import stats
import json


def load_data():
    files = {
        "Homo_F508_1": "Homo_F508_1.json",
        "Homo_Hetero_F508": "Homo_Hetero_F508.json",
        "Non_F508": "Non_F508.json"
    }
    
    data = {}
    for key, file_name in files.items():
        with open(file_name, "r", encoding='utf-8') as f:
            data[key] = json.load(f)
    
    return data

meta_data = load_data()


st.title("📊 Meta-Analiza Studiilor în Fibroză Cistică")


st.write("### Selectează un studiu pentru a vizualiza datele:")
studiu_selectat = st.selectbox("Selectează studiul pentru analiză", list(meta_data.keys()))

studiul_data = meta_data[studiu_selectat]
titlu_studiu = studiul_data['protocolSection']['identificationModule']['briefTitle']
st.subheader(f"Studiu: {titlu_studiu}")

#Grupuri
grupe = studiul_data["resultsSection"]["participantFlowModule"]["groups"]
milestones = studiul_data["resultsSection"]["participantFlowModule"]["periods"][0]["milestones"]

#Numar participant pe grupuri
participanti_grupuri = {}
for milestone in milestones:
    if milestone["type"] == "STARTED":
        for achievement in milestone["achievements"]:
            grup_id = achievement["groupId"]
            num_subjects = int(achievement["numSubjects"])
            participanti_grupuri[grup_id] = num_subjects

st.write("### Grupuri și număr de participanți:")
for grup in grupe:
    grup_id = grup["id"]
    st.write(f"- {grup['title']}: {participanti_grupuri.get(grup_id, 0)} participanți")


# ForestPlot
date_grupuri = {
    grup["title"]: [0.15, 0.05, 0.25] if grup["id"] in participanti_grupuri else [0, 0, 0]
    for grup in grupe
}

# Medie, CI inferior si superior per grup
mean_diff = [np.mean(date) for date in date_grupuri.values()]
lower_ci = [min(date) for date in date_grupuri.values()]
upper_ci = [max(date) for date in date_grupuri.values()]

# ForestPlot
fig = go.Figure()

for index, row in enumerate(zip(date_grupuri.keys(), mean_diff, lower_ci, upper_ci)):
    grup, mean, lower, upper = row

   
    fig.add_trace(go.Scatter(
        x=[mean],
        y=[grup],
        mode='markers',
        marker=dict(color='blue', size=10),
        name=f'{grup} - Diferență Medie'
    ))

    
    fig.add_trace(go.Scatter(
        x=[lower, upper],
        y=[grup, grup],
        mode='lines',
        line=dict(color='blue', width=2),
        name=f'{grup} - Interval Confidență 95%'
    ))

fig.update_layout(
    title="📉 Forest Plot pentru Compararea Grupurilor",
    xaxis_title="Diferența Medie",
    yaxis_title="Grupuri",
    height=400,
    showlegend=True,
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

# Tabel Statictici
st.markdown("### 🧮 Tabel de statistici pentru fiecare grup selectat")
df_stats = pd.DataFrame({
    "Grup": list(date_grupuri.keys()),
    "Diferența Medie": mean_diff,
    "CI Inferior": lower_ci,
    "CI Superior": upper_ci
})
st.dataframe(df_stats)

# Salvare Date
st.markdown("### 📤 Salvează datele și graficele")
if st.button("Descarcă tabelul de statistici ca CSV"):
    csv = df_stats.to_csv(index=False)
    st.download_button("Descarcă CSV", csv, "tabel_statistici.csv", "text/csv")

if st.button("Descarcă Forest Plot ca imagine"):
    fig.write_image("forest_plot.png")
    st.download_button("Descarcă Forest Plot", "forest_plot.png", "image/png")

    st.markdown("## 🔎 Subgroup Analysis")
    subgroup = st.selectbox("Selectează subgrupul pentru analiză:", ["Sex", "Vârstă"])
  

st.markdown("## 📊 Teste Statistice între Grupuri (Chi² și Indici de Diversitate)")

#extragem din baselineCharacteristicmodule

def extract_baseline_values(data, field_keyword, numeric=False):
    extracted = []
    for study_id, study_data in data.items():
        try:
            measures = study_data["resultsSection"]["baselineCharacteristicsModule"]["measures"]
            for measure in measures:
                if field_keyword.lower() in measure["title"].lower():
                    for cls in measure["classes"]:
                        for cat in cls["categories"]:
                            for m in cat["measurements"]:
                                value = m.get("value")
                                if value is None:
                                    continue
                                try:
                                    extracted.append({
                                        "Studiu": study_id,
                                        "Grup": m["groupId"],
                                        "Categorie": cat["title"],
                                        "Valoare": float(value) if numeric else value
                                    })
                                except ValueError:
                                    if not numeric:
                                        extracted.append({
                                            "Studiu": study_id,
                                            "Grup": m["groupId"],
                                            "Categorie": cat["title"],
                                            "Valoare": value
                                        })
        except KeyError:
            continue
    return pd.DataFrame(extracted)

# indice de diverisitate
def shannon_index(counts):
    proportions = counts / counts.sum()
    proportions = proportions[proportions > 0]  
    return -np.sum(proportions * np.log(proportions))

def gini_index(counts):
    proportions = counts / counts.sum()
    return 1 - np.sum(proportions ** 2)

#Lista variabile anaizate
categorical_vars = ["Sex", "Age", "Ethnicity", "Race"]

for var in categorical_vars:
    st.subheader(f"🧪 Test Chi-pătrat și Indici Diversitate: {var}")
    df_cat = extract_baseline_values(meta_data, field_keyword=var, numeric=False)

    if df_cat.empty:
        st.warning(f"⚠️ Nu au fost găsite date pentru variabila `{var}`.")
        continue

# tabel cotingenta
    chi_table = pd.crosstab(df_cat["Categorie"], df_cat["Grup"])
    st.write(f"📋 Tabel de contingență ({var} vs Grup):")
    st.dataframe(chi_table)

   
    # Chi-patraat
    try:
        chi2, p, dof, expected = stats.chi2_contingency(chi_table)
        st.write(f"**Chi²:** {chi2:.2f} | **p-valoare:** {p:.4f}")
        if p < 0.05:
            st.success("✅ Distribuția diferă semnificativ între grupuri.")
        else:
            st.info("ℹ️ Nu s-au identificat diferențe semnificative între grupuri.")
    except Exception as e:
        st.error(f"⚠️ Eroare la testul Chi-pătrat: {e}")

#calcul si afisare indice div
   
    st.write("📊 Indici de diversitate pentru fiecare grup:")
    diversity_indices = []
    for grp in chi_table.columns:
        counts = chi_table[grp]
        shannon = shannon_index(counts)
        gini = gini_index(counts)
        diversity_indices.append({"Grup": grp, "Shannon": shannon, "Gini": gini})
    df_diversity = pd.DataFrame(diversity_indices)
    st.dataframe(df_diversity)