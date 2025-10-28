import streamlit as st
import pandas as pd
import plotly as pl
from streamlit_dynamic_filters import DynamicFilters

st.title("Visualisation des données des vehicules 🚙")
df = pd.read_csv("vehicules_nettoyes.csv")



# Filtrage par marque
veh_marque_dispo = df['veh_marque'].unique().tolist()
veh_marque = st.sidebar.multiselect("marques", veh_marque_dispo)

if veh_marque:
    df = df[df['veh_marque'].isin(veh_marque)]


#Filtrage par model
model_dispo = df['veh_modele'].unique().tolist()
model = st.sidebar.multiselect("modeles", model_dispo)
if model:
    df = df[df['veh_modele'].isin(model)]


#Filtrage par matricule



veh_immatriculation_dispo = df[df['suspect'] == 'oui']['veh_immatriculation'].unique().tolist()
veh_immatriculation = st.sidebar.multiselect("Matricules suspects", veh_immatriculation_dispo)
if veh_immatriculation:
    df = df[df['veh_immatriculation'].isin(veh_immatriculation)]


enregistrement = df['veh_nombre_de_place'].count()
nb_vehicule = df['veh_immatriculation'].nunique()
nb_vehicule_suspect = df[df['suspect'] == 'oui']['veh_immatriculation'].nunique()

# Fonction pour créer une carte
def kpi_card(title, value, emoji):
    st.markdown(f"""
        <div style='
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        '>
            <div style='font-size:16px; color:#555;'>{emoji} {title}</div>
            <div style='font-size:32px; font-weight:bold; color:#1f77b4;'>{value}</div>
        </div>
    """, unsafe_allow_html=True)

# Affichage en colonnes
col1, col2, col3 = st.columns(3)

with col1:
    kpi_card("Nombre d'enregistrement", f"{enregistrement:,.0f}", "👥")

with col2:
    kpi_card("Nombre des vehicules", nb_vehicule, "🚙")

with col3:
    kpi_card("vehicules suspects", nb_vehicule_suspect, "🧾")



st.write("")

st.dataframe(df.head(10))