import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Configuration de la page
st.set_page_config(page_title="Frise Chronologique des Nuisances", layout="wide")

st.title("⏳ Frise Chronologique Auto-Générée (Calme vs Crises)")
st.write("Note uniquement les événements perturbateurs. Les périodes de calme (Vert) se calculent et s'affichent automatiquement entre tes signalements.")

# 1. Base de données initiale (uniquement les points critiques)
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
            "Début": "14:00", 
            "Fin": "15:30", 
            "Intensité": "🟠 Orange (Fort)", 
            "Étiquette": "ACCÈS ENTRAVÉ", 
            "Description": "Ascenseur bloqué par les livraisons."
        },
        {
            "Date": datetime.date(2026, 6, 16), 
            "Début": "09:00", 
            "Fin": "11:30", 
            "Intensité": "🔴 Rouge (Critique)", 
            "Étiquette": "VIBRATIONS", 
            "Description": "Tremblements continus dans le sol."
        }
    ])

# 2. Interface de saisie (Tu ne saisis que les crises ici)
st.subheader("📝 Registre des événements critiques")
config_colonnes = {
    "Date": st.column_config.DateColumn("Date", required=True),
    "Début": st.column_config.TextColumn("Heure Début (HH:MM)", required=True),
    "Fin": st.column_config.TextColumn("Heure Fin (HH:MM)", required=True),
    "Intensité": st.column_config.SelectboxColumn("Intensité", options=["🔴 Rouge (Critique)", "🟠 Orange (Fort)", "🟡 Jaune (Modéré)"], required=True),
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

# 3. Algorithme de génération des plages de calme (Vert)
if not df_edite.empty:
    try:
        df_events = df_edite.copy()
        df_events['Start'] = pd.to_datetime(df_events['Date'].astype(str) + ' ' + df_events['Début'])
        df_events['Finish'] = pd.to_datetime(df_events['Date'].astype(str) + ' ' + df_events['Fin'])
        
        # Tri indispensable pour calculer les intervalles
        df_events = df_events.sort_values('Start').reset_index(drop=True)
        
        chronologie_complete = []
        
        for i in range(len(df_events)):
            # S'il y a un espace de temps libre entre la fin de l'événement précédent et le début du suivant
            if i > 0 and df_events.loc[i, 'Start'] > df_events.loc[i-1, 'Finish']:
                chronologie_complete.append({
                    "Date": df_events.loc[i-1, 'Date'],
                    "Start": df_events.loc[i-1, 'Finish'],
                    "Finish": df_events.loc[i, 'Start'],
                    "Intensité": "🟢 Vert (Calme / Normal)",
                    "Étiquette": "RÀS",
                    "Description": "Aucune nuisance – Jouissance normale du logement."
                })
            
            # Ajouter l'événement critique saisi par l'utilisateur
            chronologie_complete.append({
                "Date": df_events.loc[i, 'Date'],
                "Start": df_events.loc[i, 'Start'],
                "Finish": df_events.loc[i, 'Finish'],
                "Intensité": df_events.loc[i, 'Intensité'],
                "Étiquette": df_events.loc[i, 'Étiquette'],
                "Description": df_events.loc[i, 'Description']
            })
            
        df_plot = pd.DataFrame(chronologie_complete)
        df_plot['Ligne Unique'] = "Frise Historique"
        
        # Palette de couleurs bien tranchée
        couleurs_map = {
            "🔴 Rouge (Critique)": "#EF553B",
            "🟠 Orange (Fort)": "#EF9A3B",
            "🟡 Jaune (Modéré)": "#FECB52",
            "🟢 Vert (Calme / Normal)": "#00CC96"  # Un beau vert d'autorisation / calme
        }

        # Création de la frise linéaire
        fig = px.timeline(
            df_plot, 
            x_start="Start", 
            x_end="Finish", 
            y="Ligne Unique", 
            color="Intensité",
            text="Étiquette",
            hover_name="Étiquette",
            hover_data={"Date": True, "Intensité": False, "Ligne Unique": False, "Description": True},
            color_discrete_map=couleurs_map,
            title="🎯 Impact Réel des Travaux sur le Temps de Vie"
        )
        
        fig.update_layout(
            xaxis_title="Chronologie continue",
            yaxis_title="",
            showlegend=True,
            legend_title="État du Logement",
            height=280
        )
        
        fig.update_yaxes(showticklabels=False)
        fig.update_traces(textposition="inside", insidetextanchor="middle")
        
        st.subheader("📈 Rendu Visuel de la Ligne du Temps")
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error("Vérifie bien que toutes les cases Date, Début (HH:MM) et Fin (HH:MM) soient remplies.")
else:
    st.warning("Ajoute au moins une nuisance pour voir la frise.")
