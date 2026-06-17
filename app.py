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
        # Nettoyage des lignes incomplètes
        df_events = df_edite.copy()
        df_events = df_events.dropna(subset=['Date', 'Début', 'Fin', 'Intensité', 'Nature'])
        
        # Nettoyage des espaces et uniformisation des formats d'heure (ex: '08h30' -> '08:30')
        for col in ['Début', 'Fin']:
            df_events[col] = df_events[col].astype(str).str.strip().str.replace('h', ':', case=False)
        
        df_events = df_events[(df_events['Début'] != "") & (df_events['Fin'] != "")]
        
        if not df_events.empty:
            df_events['Start'] = pd.to_datetime(df_events['Date'].astype(str) + ' ' + df_events['Début'], errors='coerce')
            df_events['Finish'] = pd.to_datetime(df_events['Date'].astype(str) + ' ' + df_events['Fin'], errors='coerce')
            df_events = df_events.dropna(subset=['Start', 'Finish'])
            
            # Correction des inversions de chronologie Début/Fin au vol
            inversed = df_events['Start'] > df_events['Finish']
            if inversed.any():
                df_events.loc[inversed, ['Start', 'Finish']] = df_events.loc[inversed, ['Finish', 'Start']].values
            
            df_events = df_events.sort_values('Start').reset_index(drop=True)
            
        if not df_events.empty:
            # Algorithme de complétion des plages vertes
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
            
            couleurs_map = {
                "🔴 Critique": "#D9534F",
                "🟠 Fort": "#F0AD4E",
                "🟡 Modéré": "#F0DE4C",
                "🟢 Jouissance normale": "#E8F5E9"
            }

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
            
            fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                height=180,
                margin=dict(l=10, r=25, t=50, b=45),
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
            
            fig.update_traces(
                width=0.5, 
                marker=dict(line=dict(color="#FFFFFF", width=1.5)),
                hovertemplate="<b>%{hovertext}</b><br>%{customdata[0]|%H:%M} à %{customdata[1]|%H:%M}<extra></extra>"
            )
            
            # Logo MAULINI incrusté vectoriellement
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
            st.warning("Complète les lignes du tableau avec des heures valides (ex: 08:30) pour générer le visuel.")
            
    except Exception as e:
        st.error(f"Erreur technique rencontrée : {e}")
else:
    st.warning("Ajoute des données pour afficher la frise.")
