import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Configuration de la page pour un rendu compact et élégant
st.set_page_config(page_title="Rapport Nuisances - Maulini", layout="wide")

# CSS pour éliminer au maximum les espaces blancs superflus de Streamlit
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        padding-bottom: 0px !important;
    }
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #FFFFFF;
    }
    .main-header {
        font-size: 24px;
        font-weight: 700;
        color: #1A1A1A;
        line-height: 1.2;
    }
    .sub-header {
        font-size: 13px;
        color: #555555;
        margin-bottom: 15px;
    }
    </style>
    <div class="main-header">Suivi Chronologique des Nuisances Chantier</div>
    <div class="sub-header">Générateur de frise d'impact — Document officiel de synthèse</div>
""", unsafe_allow_html=True)

# 1. Base de données initiale
if 'nuisances_db' not in st.session_state:
    st.session_state.nuisances_db = pd.DataFrame([
        {
            "Date": datetime.date(2026, 6, 15), 
            "Début": "08:30", 
            "Fin": "10:15", 
            "Intensité": "🔴 Critique", 
            "Nature": "BRUIT : CHOCS", 
            "Description": "Marteau-piqueur dalle adjacente."
        },
        {
            "Date": datetime.date(2026, 6, 15), 
            "Début": "14:00", 
            "Fin": "15:30", 
            "Intensité": "🟠 Fort", 
            "Nature": "ACCÈS ENTRAVÉ", 
            "Description": "Ascenseur bloqué par les livraisons."
        },
        {
            "Date": datetime.date(2026, 6, 16), 
            "Début": "09:00", 
            "Fin": "11:30", 
            "Intensité": "🔴 Critique", 
            "Nature": "VIBRATIONS", 
            "Description": "Tremblements continus dans le sol."
        }
    ])

# 2. Section d'édition (Repliable pour gagner de l'espace)
with st.expander("📝 Ajouter / Modifier des événements", expanded=False):
    config_colonnes = {
        "Date": st.column_config.DateColumn("Date", required=True),
        "Début": st.column_config.TextColumn("Début (HH:MM)", required=True),
        "Fin": st.column_config.TextColumn("Fin (HH:MM)", required=True),
        "Intensité": st.column_config.SelectboxColumn("Intensité", options=["🔴 Critique", "🟠 Fort", "🟡 Modéré"], required=True),
        "Nature": st.column_config.SelectboxColumn("Nature", options=["BRUIT : CHOCS", "BRUIT : PERCEMENT", "BRUIT : CONTINU", "VIBRATIONS", "POUSSIÈRE", "ACCÈS ENTRAVÉ", "COUPURE SYNCHRO"], required=True),
        "Description": st.column_config.TextColumn("Description")
    }
    df_edite = st.data_editor(
        st.session_state.nuisances_db, 
        column_config=config_colonnes,
        num_rows="dynamic", 
        use_container_width=True
    )
    st.session_state.nuisances_db = df_edite

# 3. Traitement robuste et Rendu Graphique
if not df_edite.empty:
    try:
        # --- NETTOYAGE STRICT DES DONNÉES INCOMPLÈTES ---
        df_events = df_edite.copy()
        
        # Élimination des lignes vides ou non encore remplies (évite le crash au clic sur "+")
        df_events = df_events.dropna(subset=['Date', 'Début', 'Fin', 'Intensité', 'Nature'])
        
        # Suppression des chaînes de texte vides
        df_events = df_events[
            (df_events['Début'].astype(str).str.strip() != "") & 
            (df_events['Fin'].astype(str).str.strip() != "")
        ]
        
        if not df_events.empty:
            # Conversion sécurisée (les formats corrompus deviennent 'NaT' au lieu de faire planter le script)
            df_events['Start'] = pd.to_datetime(df_events['Date'].astype(str) + ' ' + df_events['Début'].astype(str), errors='coerce')
            df_events['Finish'] = pd.to_datetime(df_events['Date'].astype(str) + ' ' + df_events['Fin'].astype(str), errors='coerce')
            
            # Nettoyage final des erreurs de parsing
            df_events = df_events.dropna(subset=['Start', 'Finish'])
            
            # Tri chronologique de la ligne du temps
            df_events = df_events.sort_values('Start').reset_index(drop=True)
            
        # Génération finale si des données valides existent
        if not df_events.empty:
            # Algorithme de complétion automatique des plages de calme (Vert)
            chronologie_complete = []
            for i in range(len(df_events)):
                if i > 0 and df_events.loc[i, 'Start'] > df_events.loc[i-1, 'Finish']:
                    chronologie_complete.append({
                        "Start": df_events.loc[i-1, 'Finish'],
                        "Finish": df_events.loc[i, 'Start'],
                        "Intensité": "🟢 Jouissance normale",
                        "Nature": "Normal"
                    })
                chronologie_complete.append({
                    "Start": df_events.loc[i, 'Start'],
                    "Finish": df_events.loc[i, 'Finish'],
                    "Intensité": df_events.loc[i, 'Intensité'],
                    "Nature": df_events.loc[i, 'Nature']
                })
                
            df_plot = pd.DataFrame(chronologie_complete)
            df_plot['Axe'] = "Impact"
            
            # Palette de couleurs mates et professionnelles
            couleurs_map = {
                "🔴 Critique": "#D9534F",
                "🟠 Fort": "#F0AD4E",
                "🟡 Modéré": "#F0DE4C",
                "🟢 Jouissance normale": "#E8F5E9"
            }

            # Construction de la frise linéaire
            fig = px.timeline(
                df_plot, 
                x_start="Start", 
                x_end="Finish", 
                y="Axe", 
                color="Intensité",
                color_discrete_map=couleurs_map,
                hover_name="Nature",
                custom_data=['Start', 'Finish'],
                category_orders={"Intensité": ["🟢 Jouissance normale", "🟡 Modéré", "🟠 Fort", "🔴 Critique"]}
            )
            
            # Configuration épurée du canevas
            fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                height=180,
                margin=dict(l=10, r=25, t=50, b=45),
                
                # Légende claire et alignée en haut à gauche
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.05,
                    xanchor="left",
                    x=0,
                    title_text=""
                ),
                font=dict(family="Inter, sans-serif", size=11, color="#333333")
            )
            
            # Axe des temps avec les dates exactes et les repères clairs
            fig.update_xaxes(
                showgrid=True,
                gridcolor="#F5F5F5",
                showline=True,
                linewidth=1.2,
                linecolor='#1A1A1A',
                tickformat="%d %b\n%H:%M",
                title_text=""
            )
            
            fig.update_yaxes(showgrid=False, showticklabels=False, title_text="")
            
            # Configuration des barres et du format de survol
            fig.update_traces(
                width=0.5, 
                marker=dict(line=dict(color="#FFFFFF", width=1.5)),
                hovertemplate="<b>%{hovertext}</b><br>%{customdata[0]|%H:%M} à %{customdata[1]|%H:%M}<extra></extra>"
            )
            
            # INCRUSTATION DU BLOC DE MARQUE MAULINI
            fig.add_annotation(
                x=1, y=1.35,
                xref="paper", yref="paper",
                text="<b>MAULINI</b><br><span style='font-size:8px; letter-spacing:1px; color:#7F8C8D;'>MAÎTRE CONSTRUCTEUR</span>",
                showarrow=False,
                align="right",
                font=dict(family="Arial, sans-serif", size=13, color="#1A1A1A"),
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="#1A1A1A",
                borderwidth=1,
                borderpad=4
            )
            
            # Affichage avec barre d'outils et configuration d'export PNG HD activée
            st.plotly_chart(
                fig, 
                use_container_width=True, 
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'rapport_nuisances_maulini',
                        'height': 400,
                        'width': 1200,
                        'scale': 2
                    }
                }
            )
        else:
            st.warning("Complète les lignes du tableau (Date, Début, Fin) pour générer le visuel.")
            
    except Exception as e:
        st.error("Une erreur interne est survenue lors de la mise en forme du graphique.")
else:
    st.warning("Ajoute des données pour afficher la frise.")
