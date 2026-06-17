import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Configuration de la page
st.set_page_config(page_title="Frise Chronologique Premium", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: 700; color: #2C3E50; margin-bottom: 20px; }
    </style>
    <div class="main-title">⏳ Chronologie Historique des Nuisances de Voisinage</div>
""", unsafe_allow_html=True)

st.write("Saisis uniquement les événements critiques. Le système génère une frise épurée style infographie.")

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
st.subheader("📝 Registre des événements")
config_colonnes = {
    "Date": st.column_config.DateColumn("Date", required=True),
    "Début": st.column_config.TextColumn("Début (HH:MM)", required=True),
    "Fin": st.column_config.TextColumn("Fin (HH:MM)", required=True),
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

# 3. Génération du Design Infographique
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
                    "Start": df_events.loc[i-1, 'Finish'],
                    "Finish": df_events.loc[i, 'Start'],
                    "Intensité": "🟢 Calme normal",
                    "Étiquette": "RÀS"
                })
            chronologie_complete.append({
                "Start": df_events.loc[i, 'Start'],
                "Finish": df_events.loc[i, 'Finish'],
                "Intensité": df_events.loc[i, 'Intensité'],
                "Étiquette": df_events.loc[i, 'Étiquette']
            })
            
        df_plot = pd.DataFrame(chronologie_complete)
        df_plot['Ligne'] = "Frise"
        
        # Palette de couleurs "Architectural & Muted" (plus douce et élégante)
        couleurs_map = {
            "🔴 Rouge (Critique)": "#CD5C5C",      # Rouge terre cuite doux
            "🟠 Orange (Fort)": "#E6A15C",         # Ambre doux
            "🟡 Jaune (Modéré)": "#F3D266",        # Or mat
            "🟢 Calme normal": "#F2F5F3"           # Fond lin/off-white ultra-pro
        }

        fig = px.timeline(
            df_plot, 
            x_start="Start", 
            x_end="Finish", 
            y="Ligne", 
            color="Intensité",
            color_discrete_map=couleurs_map
        )
        
        # Configuration de la mise en page de base
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=380,  # Plus grand pour laisser de la place aux bulles historiques
            margin=dict(l=20, r=40, t=180, b=40), # Énorme marge en haut pour les bulles
            showlegend=False
        )
        
        fig.update_xaxes(showgrid=False, showline=True, linewidth=2, linecolor='#BDC3C7', title_text="")
        fig.update_yaxes(showgrid=False, showticklabels=False, title_text="")
        fig.update_traces(width=0.15, marker=dict(line=dict(color="#FFFFFF", width=1))) # Ligne fine et distinguée
        
        # AJOUT DES BULLES DE TEXTE STYLE HISTOIRE (Uniquement pour les crises)
        couleurs_hex = {
            "🔴 Rouge (Critique)": "#CD5C5C",
            "🟠 Orange (Fort)": "#E6A15C",
            "🟡 Jaune (Modéré)": "#F3D266"
        }
        
        hauteurs_stagger = [-50, -110, -170] # Différentes hauteurs pour éviter les collisions de texte
        
        idx_crise = 0
        for _, row in df_events.iterrows():
            # Calcul du milieu de l'événement pour planter la flèche
            milieu = row['Start'] + (row['Finish'] - row['Start']) / 2
            couleur_bulle = couleurs_hex.get(row['Intensité'], "#2C3E50")
            ay_val = hauteurs_stagger[idx_crise % len(hauteurs_stagger)]
            
            fig.add_annotation(
                x=milieu,
                y="Frise",
                text=f"<b>{row['Étiquette']}</b><br><span style='font-size:10px; color:#7F8C8D;'>{row['Début']} - {row['Fin']}</span>",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1.5,
                arrowcolor="#BDC3C7",
                ax=0,
                ay=ay_val,
                bordercolor=couleur_bulle,
                borderwidth=2,
                borderpad=6,
                bgcolor="white",
                font=dict(size=11, color="#2C3E50", family="Arial")
            )
            idx_crise += 1

        st.subheader("📈 Rendu Infographique")
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error("Vérifie la cohérence des heures saisies (ex: 08:30).")
else:
    st.warning("Ajoute des données pour dessiner l'infographie.")
