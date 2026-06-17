import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Configuration de la page
st.set_page_config(page_title="Frise Chronologique des Nuisances", layout="wide")

st.title("⏳ Frise Chronologique Historique des Nuisances")
st.write("Note uniquement les événements perturbateurs. Les périodes de calme (Vert) se calculent et s'affichent automatiquement.")

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

# 2. Interface de saisie
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

# 3. Algorithme et Design Épuré de la Frise
if not df_edite.empty:
    try:
        df_events = df_edite.copy()
        df_events['Start'] = pd.to_datetime(df_events['Date'].astype(str) + ' ' + df_events['Début'])
        df_events['Finish'] = pd.to_datetime(df_events['Date'].astype(str) + ' ' + df_events['Fin'])
        
        df_events = df_events.sort_values('Start').reset_index(drop=True)
        chronologie_complete = []
        
        for i in range(len(df_events)):
            if i > 0 and df_events.loc[i, 'Start'] > df_events.loc[i-1, 'Finish']:
                chronologie_complete.append({
                    "Date": df_events.loc[i-1, 'Date'],
                    "Start": df_events.loc[i-1, 'Finish'],
                    "Finish": df_events.loc[i, 'Start'],
                    "Intensité": "🟢 Vert (Calme / Normal)",
                    "Étiquette": "RÀS",
                    "Description": "Aucune nuisance constatée."
                })
            
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
        
        couleurs_map = {
            "🔴 Rouge (Critique)": "#EF553B",
            "🟠 Orange (Fort)": "#FF9933",
            "🟡 Jaune (Modéré)": "#FCD116",
            "🟢 Vert (Calme / Normal)": "#2ECC71"
        }

        fig = px.timeline(
            df_plot, 
            x_start="Start", 
            x_end="Finish", 
            y="Ligne Unique", 
            color="Intensité",
            text="Étiquette",
            hover_name="Étiquette",
            hover_data={"Date": True, "Intensité": False, "Ligne Unique": False, "Description": True},
            color_discrete_map=couleurs_map
        )
        
        # Calcul des bornes de temps pour ajouter une marge propre à droite pour la flèche
        temps_min = df_plot['Start'].min()
        temps_max = df_plot['Finish'].max()
        delta_total = temps_max - temps_min
        temps_marge_droite = temps_max + (delta_total * 0.03) # +3% de marge de ligne

        # Personnalisation esthétique "Frise d'Histoire"
        fig.update_layout(
            plot_bgcolor="white",  # Fond blanc pur pour faire ressortir la frise
            paper_bgcolor="white",
            height=250,
            margin=dict(l=10, r=40, t=20, b=60),
            showlegend=True,
            legend_title_text="Statut du Logement",
            legend=dict(orientation="h", yanchor="bottom", y=-0.6, xanchor="center", x=0.5)
        )
        
        # Axe X : Une belle ligne droite continue noire
        fig.update_xaxes(
            range=[temps_min, temps_marge_droite],
            showgrid=False,
            showline=True,
            linewidth=3,
            linecolor='#2C3E50',
            title_text=""
        )
        
        # Supprimer l'axe Y pour ne garder que le ruban de l'histoire
        fig.update_yaxes(showgrid=False, showticklabels=False, title_text="")
        
        # Ajustement esthétique des blocs colorés (séparateurs blancs fins)
        fig.update_traces(
            textposition="inside", 
            insidetextanchor="middle",
            marker=dict(line=dict(color="white", width=2))
        )
        
        # L'élément clé : Ajout de la flèche de chronologie au bout de la ligne
        fig.add_annotation(
            x=temps_marge_droite,
            y="Frise Historique",
            text="➤",
            showarrow=False,
            font=dict(size=20, color="#2C3E50"),
            xanchor="center",
            yanchor="middle"
        )
        
        st.subheader("📈 Rendu de la Frise Visuelle")
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error("Vérifie bien le format de remplissage des dates et heures.")
else:
    st.warning("Ajoute au moins une nuisance pour voir la frise.")
