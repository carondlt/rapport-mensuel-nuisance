import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Configuration de la page
st.set_page_config(page_title="Frise Chronologique des Nuisances", layout="wide")

st.title("⏳ Frise Chronologique Historique des Nuisances")
st.write("Saisis tes données dans le tableau. Elles s'aligneront automatiquement sur une seule grande ligne du temps continue.")

# 1. Base de données initiale
if 'nuisances_db' not in st.session_state:
    st.session_state.nuisances_db = pd.DataFrame([
        {
            "Date": datetime.date(2026, 6, 15), 
            "Début": "08:30", 
            "Fin": "10:15", 
            "Intensité": "🔴 Rouge (Critique)", 
            "Étiquette": "BRUIT : CHOCS", 
            "Description": "Marteau-piqueur dalle adjacente."
        },
        {
            "Date": datetime.date(2026, 6, 15), 
            "Début": "10:15", 
            "Fin": "12:00", 
            "Intensité": "🟡 Jaune (Modéré)", 
            "Étiquette": "POUSSIÈRE", 
            "Description": "Infiltration sous la porte d'entrée."
        },
        {
            "Date": datetime.date(2026, 6, 15), 
            "Début": "14:00", 
            "Fin": "17:00", 
            "Intensité": "🟠 Orange (Fort)", 
            "Étiquette": "ACCÈS ENTRAVÉ", 
            "Description": "Ascenseur bloqué par les livraisons."
        },
        {
            "Date": datetime.date(2026, 6, 16), 
            "Début": "08:00", 
            "Fin": "11:30", 
            "Intensité": "🔴 Rouge (Critique)", 
            "Étiquette": "VIBRATIONS", 
            "Description": "Tremblements continus dans le sol."
        }
    ])

# 2. Interface de saisie
st.subheader("📝 Registre des nuisances")
config_colonnes = {
    "Date": st.column_config.DateColumn("Date", required=True),
    "Début": st.column_config.TextColumn("Heure Début (HH:MM)", required=True),
    "Fin": st.column_config.TextColumn("Heure Fin (HH:MM)", required=True),
    "Intensité": st.column_config.SelectboxColumn("Intensité", options=["🟢 Vert (Acceptable)", "🟡 Jaune (Modéré)", "🟠 Orange (Fort)", "🔴 Rouge (Critique)"], required=True),
    "Étiquette": st.column_config.SelectboxColumn("Étiquette", options=["BRUIT : CHOCS", "BRUIT : PERCEMENT", "BRUIT : CONTINU", "VIBRATIONS", "POUSSIÈRE", "ACCÈS ENTRAVÉ", "COUPURE SYNCHRO"], required=True),
    "Description": st.column_config.TextColumn("Description détaillée")
}

df_edite = st.data_editor(
    st.session_state.nuisances_db, 
    column_config=config_colonnes,
    num_rows="dynamic", 
    use_container_width=True
)
st.session_state.nuisances_db = df_edite

# 3. Génération de la Frise Historique
if not df_edite.empty:
    try:
        df_plot = df_edite.copy()
        df_plot['Start'] = pd.to_datetime(df_plot['Date'].astype(str) + ' ' + df_plot['Début'])
        df_plot['Finish'] = pd.to_datetime(df_plot['Date'].astype(str) + ' ' + df_plot['Fin'])
        
        # Astuce : on crée une colonne fixe pour forcer l'alignement sur une seule ligne
        df_plot['Ligne Unique'] = "Chronologie des Nuisances"
        
        couleurs_map = {
            "🔴 Rouge (Critique)": "#EF553B",
            "🟠 Orange (Fort)": "#EF9A3B",
            "🟡 Jaune (Modéré)": "#FECB52",
            "🟢 Vert (Acceptable)": "#636EFA"
        }

        # Création du graphique de type frise linéaire
        fig = px.timeline(
            df_plot, 
            x_start="Start", 
            x_end="Finish", 
            y="Ligne Unique", 
            color="Intensité",
            text="Étiquette",  # Affiche l'étiquette directement dans le bloc coloré
            hover_name="Étiquette",
            hover_data={"Date": True, "Début": True, "Fin": True, "Description": True, "Ligne Unique": False},
            color_discrete_map=couleurs_map,
            title="🎯 Ligne du Temps Continue"
        )
        
        # Style pour que ça ressemble à une vraie frise d'histoire
        fig.update_layout(
            xaxis_title="Déroulement du Temps (Jours et Heures)",
            yaxis_title="",
            showlegend=True,
            legend_title="Gravité",
            height=300  # Moins haut pour accentuer l'effet "bandeau/frise"
        )
        
        # Masquer les labels de l'axe Y pour épurer le visuel
        fig.update_yaxes(showticklabels=False, ticktext=[])
        
        # Ajustement du texte à l'intérieur des blocs
        fig.update_traces(textposition="inside", insidetextanchor="middle")
        
        st.subheader("📈 Rendu de la Frise")
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error("Vérifie le format de tes dates (AAAA-MM-JJ) et heures (HH:MM).")
else:
    st.warning("Ajoute des lignes pour voir apparaître la frise.")
