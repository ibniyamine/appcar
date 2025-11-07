import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit_authenticator as stauth
import yaml

#from streamlit_dynamic_filters import DynamicFilters"

st.set_page_config(layout="wide", page_icon=":bar_chart:")

from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)


authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
   
)



try:
    authenticator.login()
except LoginError as e:
    st.error(e)

# Authenticating user

if st.session_state.get('authentication_status') and not st.session_state.get('already_logged_in'):
    st.session_state['already_logged_in'] = True
    st.rerun()

# Réinitialiser le flag après déconnexion
if st.session_state.get('authentication_status') is False or st.session_state.get('authentication_status') is None:
    st.session_state['already_logged_in'] = False

# Affichage conditionnel
if st.session_state.get('authentication_status'):
    with st.sidebar:
        authenticator.logout()
        st.write(f'Bienvenue *{st.session_state["name"]}*')
    st.title("📊 Tableau de bord de visualisation des vehicules")
    df = pd.read_csv("vehicules_nettoyes_finale.csv")
    
    # filtrer par date
    ## conversion de la colonne date
    df['veh_date_circulation'] = pd.to_datetime(df['veh_date_circulation'], errors='coerce')

    # Définir la date limite
    # date_limite = pd.Timestamp('2025-08-31')

    # Remplacer les dates supérieures à la limite
    # df.loc[df['veh_date_circulation'] > date_limite, 'veh_date_circulation'] = date_limite

    # Définir les bornes possibles
    min_date = df['veh_date_circulation'].min().date()
    max_date = df['veh_date_circulation'].max().date()
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input(
            "Date de début",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )

    with col2:
        date_fin = st.date_input(
            "Date de fin",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

    # Vérification des dates
    if date_debut > date_fin:
        st.warning("La date de début ne peut pas être postérieure à la date de fin.")

        # Filtrage
    date_debut = pd.to_datetime(date_debut)
    date_fin = pd.to_datetime(date_fin)
        
    df = df[(df['veh_date_circulation'] >= date_debut) & (df['veh_date_circulation'] <= date_fin)]


    matricule_input = st.sidebar.text_input("Entre la matricule")
    if matricule_input:

        df = df[df['veh_immatriculation']==matricule_input.upper()]


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



    veh_immatriculation_dispo = df[df['anomalie'] == 'oui']['veh_immatriculation'].unique().tolist()
    veh_immatriculation = st.sidebar.multiselect("Matricules anomalies", veh_immatriculation_dispo)
    if veh_immatriculation:
        df = df[df['veh_immatriculation'].isin(veh_immatriculation)]

    statuts_disponibles = df['anomalie'].unique().tolist()

    # Multiselect dans la sidebar
    statut_selection = st.multiselect(
        "Filtrer par statut d'anomalie oui/non:",
        options=statuts_disponibles
    )

    # Filtrage du DataFrame
    if statut_selection:
        df = df[df['anomalie'].isin(statut_selection)]


    enregistrement = df['veh_nombre_de_place'].count()
    nb_vehicule = df['veh_immatriculation'].nunique()
    nb_vehicule_anomalie = df[df['anomalie'] == 'oui']['veh_immatriculation'].nunique()
    nb_vehicule_clean = nb_vehicule - nb_vehicule_anomalie


    


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
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_card("Nombre d'enregistrement", f"{enregistrement:,.0f}", "👥")

    with col2:
        kpi_card("Nombre des vehicules", nb_vehicule, "🚙")

    with col3:
        kpi_card("vehicules anomalies", nb_vehicule_anomalie, "🧾")

    with col4:
        kpi_card("vehicules cleans", nb_vehicule_clean, "🧾")



    st.write("")

    st.dataframe(df)

    # Nombre de voiture par mois/année
    st.subheader("Nombre de voiture par mois/année")

    # Créer deux colonnes : pour l'affichage et pour le tri
    df['Mois_Annee_affichage'] = df['veh_date_circulation'].dt.strftime('%b %Y')  # ex: Jan 2024
    df['Mois_Annee_tri'] = df['veh_date_circulation'].dt.to_period('M').astype(str)

    # Grouper par mois-année tri
    ventes_par_mois = df.groupby('Mois_Annee_tri').size().reset_index(name='Total_ventes')

    # Ajouter la version affichable pour les labels
    ventes_par_mois['Mois_Annee_affichage'] = pd.to_datetime(ventes_par_mois['Mois_Annee_tri']).dt.strftime('%b %Y')

    # Trier par date réelle
    ventes_par_mois['Mois_Annee_date'] = pd.to_datetime(ventes_par_mois['Mois_Annee_tri'])
    ventes_par_mois = ventes_par_mois.sort_values('Mois_Annee_date')

    # Tracer la courbe
    fig7 = px.line(
        ventes_par_mois,
        x='Mois_Annee_affichage',
        y='Total_ventes',
        markers=True,
        title="Nombre total de ventes par mois"
    )
    fig7.update_xaxes(tickangle=45)
    st.plotly_chart(fig7)


    # nombre de voitures par marque
    st.subheader("top 15 des marques")
    top_clients = df['veh_marque'].value_counts().sort_values(ascending=False).head(15)

    # Création du barplot
    fig3 = px.bar(
        x=top_clients.values,
        y=top_clients.index,
        orientation='h',
        text=top_clients.values,
        labels={'x': 'Nombre', 'y': 'marque'},
        color=top_clients.values,
        color_continuous_scale='Tealgrn'
        )
    fig3.update_layout(yaxis=dict(autorange="reversed"))
    fig3.update_traces(textposition='outside')
    st.plotly_chart(fig3, width='stretch')
elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')


