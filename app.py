import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Suivi des Nuisances Chantier", layout="wide")

st.title("📊 Suivi Interactif des Nuisances de Chantier")
st.write("Saisis ou modifie les nuisances directement dans le tableau. La frise visuelle s'actualise toute seule.")

# 1. Base de données initiale (Session State pour garder les données en mémoire)
if 'nuisances_db' not in st.session_state:
    st.session_state.nuisances_db = pd.DataFrame([
        {"Date": "2026-06-15", "Début": "08:30", "Fin": "10:15", "Intensité": "🔴 Rouge (Critique)", "Étiquette": "BRUIT : CHOCS", "Description": "Marteau-piqueur dalle adjacente. Réunions impossibles."},
        {"Date": "2026-06-15", "Début": "10:15", "Fin": "12:00", "Intensité": "🟡 Jaune (Modéré)", "Étiquette": "POUSSIÈRE", "Description": "Infiltration sous la porte d'entrée."},
        {"Date": "2026-06-16", "Début": "14:00", "Fin": "16:15", "Intensité": "🟠 Orange (Fort)", "Étiquette": "VIBRATIONS", "Description": "Tremblements continus dans le sol, fatigue nerveuse."}
    ])

# 2. Interface de saisie interactive (Tableau éditable)
st.subheader("📝 Registre des nuisances")
st.info("💡 Tu peux double-cliquer sur une case pour la modifier, ou cliquer sur le '+' en bas du tableau pour ajouter une ligne.")

# Options pour les menus déroulants dans le tableau
config_colonnes = {
    "Date": st.column_config.DateColumn("Date", required=True),
    "Début": st.column_config.TextColumn("Heure Début (HH:MM)", required=True),
    "Fin": st.column_config.TextColumn("Heure Fin (HH:MM)", required=True),
    "Intensité": st.column_config.SelectboxColumn("Intensité", options=["🟢 Vert (Acceptable)", "🟡 Jaune (Modéré)", "🟠 Orange (Fort)", "🔴 Rouge (Critique)"], required=True),
    "Étiquette": st.column_config.SelectboxColumn("Étiquette", options=["BRUIT : CHOCS", "BRUIT : PERCEMENT", "BRUIT : CONTINU", "VIBRATIONS", "POUSSIÈRE", "ACCÈS ENTRAVÉ", "COUPURE SYNCHRO"], required=True),
    "Description": st.column_config.TextColumn("Description détaillée")
}

# Affichage de l'éditeur
df_edite = st.data_editor(
    st.session_state.nuisances_db, 
    column_config=config_colonnes,
    num_rows="dynamic", 
    use_container_width=True
)
st.session_state.nuisances_db = df_edite

# 3. Traitement des données pour la frise chronologique
if not df_edite.empty:
    try:
        # Conversion des heures en format datetime lisible par le graphique
        df_plot = df_edite.copy()
        df_plot['Start'] = pd.to_datetime(df_plot['Date'].astype(str) + ' ' + df_plot['Début'])
        df_plot['Finish'] = pd.to_datetime(df_plot['Date'].astype(str) + ' ' + df_plot['Fin'])
        
        # Mapping des couleurs pour Plotly
        couleurs_map = {
            "🔴 Rouge (Critique)": "#EF553B",
            "🟠 Orange (Fort)": "#EF9A3B",
            "🟡 Jaune (Modéré)": "#FECB52",
            "🟢 Vert (Acceptable)": "#636EFA"
        }

        # Génération de la frise (Gantt/Timeline chart)
        fig = px.timeline(
            df_plot, 
            x_start="Start", 
            x_end="Finish", 
            y="Date", 
            color="Intensité",
            hover_name="Étiquette",
            hover_data=["Description"],
            color_discrete_map=couleurs_map,
            title="⏳ Frise Chronologique de l'Intensité des Nuisances"
        )
        
        fig.update_yaxes(autorange="reversed") # Pour avoir les jours les plus récents en haut
        fig.update_layout(xaxis_title="Heures de la journée", yaxis_title="Date", legend_title="Gravité")
        
        # Affichage du graphique dans Streamlit
        st.subheader("📈 Rendu de la Frise Visuelle")
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error("Assure-toi de bien remplir les dates et heures au format 'AAAA-MM-JJ' et 'HH:MM'.")
else:
    st.warning("Le tableau est vide. Ajoute des lignes pour générer la frise.")
