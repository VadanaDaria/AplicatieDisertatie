import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from lifelines import KaplanMeierFitter
from scipy import stats
from sklearn.cluster import AgglomerativeClustering
import seaborn as sns
import matplotlib.pyplot as plt
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

st.title("🌐 Comparare Globală Avansată a Studiilor de Fibroză Cistică")

st.write("### Selectează un studiu pentru a vizualiza datele:")
study_options = list(data.keys())
studies_selected = st.multiselect("Selectează studiile pentru comparare", study_options, default=study_options)

def extract_measures(study_data):
    extracted = []
    try:
        measures = study_data["resultsSection"]["baselineCharacteristicsModule"]["measures"]
        for measure in measures:
            for cls in measure["classes"]:
                for cat in cls["categories"]:
                    for measurement in cat["measurements"]:
                        extracted.append({
                            "Măsură": measure["title"],
                            "Group ID": measurement["groupId"],
                            "Valoare": float(measurement["value"]),
                            "Dispersion": measurement.get("spread", None)
                        })
    except KeyError:
        pass
    return pd.DataFrame(extracted)


# DataFrame Global
all_dataframes = [extract_measures(data[study]) for study in studies_selected]
df_measures = pd.concat(all_dataframes, keys=studies_selected)
st.dataframe(df_measures)

# Corelatie si distributie
st.markdown("### 📌 Distribuții și Corelații între grupuri")

# Violin Plot pt distributia valorilor pe grupuri
fig_violin = px.violin(df_measures, x='Group ID', y='Valoare', color=df_measures.index.get_level_values(0), box=True, points="all")
st.plotly_chart(fig_violin, use_container_width=True)

# Heatmap corelatii
st.markdown("### 🔥 Heatmap de Corelații între Studii")
pivot_df = df_measures.pivot_table(index='Group ID', columns=df_measures.index.get_level_values(0), values='Valoare')
correlation_matrix = pivot_df.corr()
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', ax=ax)
st.pyplot(fig)

#Cluter indentifica similaritati
st.markdown("### 🧬 Clusterizare pe Valorile Grupurilor")
cluster_data = df_measures.pivot_table(index='Group ID', columns='Măsură', values='Valoare').fillna(0)


cluster_model = AgglomerativeClustering(n_clusters=3)
labels = cluster_model.fit_predict(cluster_data)

cluster_data['Cluster'] = labels
st.dataframe(cluster_data)

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(cluster_data.drop(columns=['Cluster']), annot=True, cmap='viridis', ax=ax)
st.pyplot(fig)

# Statisitici

st.markdown("### 🔬 Teste Statistice între Grupuri Selectate")

group_ids = df_measures['Group ID'].unique()
group_choice = st.multiselect("Selectează grupurile pentru testare", group_ids, default=group_ids[:2])

if len(group_choice) == 2:
    data_1 = df_measures[df_measures['Group ID'] == group_choice[0]]['Valoare']
    data_2 = df_measures[df_measures['Group ID'] == group_choice[1]]['Valoare']
    stat, p_value = stats.ttest_ind(data_1, data_2, nan_policy='omit')
    
    st.write(f"📊 **Test T între {group_choice[0]} și {group_choice[1]}**")
    st.write(f"Statistică: {stat}")
    st.write(f"P-valoare: {p_value}")
else:
    st.warning("⚠️ Selectează exact două grupuri pentru comparare.")
