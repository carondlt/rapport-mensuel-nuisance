import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Configuration de la page pour un rendu moderne
st.set_page_config(page_title="Rapport de Nuisances", layout="wide")

# CSS personnalisé pour injecter un style épuré et pro
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #FAFAFA;
    }
    .main-header {
        font-size: 32px;
        font-weight: 700;
        color: #1A1A1A;
        margin-bottom: 5px;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 14px;
        color: #666666;
        margin-bottom: 30px;
    }
    </style>
    <div class="main-header">Chronologie d'Impact Environnemental</div>
    <div class="sub-header">Registre d'occupation et relevé des nuisances de chantier</div>
""", unsafe_allow_html=True)

# 1. Base de données initiale
if 'nuisances_db' not in st.session_state:
    st.session_state.nuisances_db = pd.DataFrame([
        {
            "Date": datetime.date(2026, 6, 15), 
            "Début": "08:30", 
            "Fin": "10:15", 
            "Intensité": "🔴 Critique", 
            "Étiquette": "BRUIT : CHOCS", 
            "Description": "Marteau-piqueur dalle adjacente."
        },
        {
            "Date": datetime.date(2026, 6, 15), 
            "Début": "14:00", 
            "Fin": "15:30", 
            "Intensité": "🟠 Fort", 
            "Étiquette": "ACCÈS ENTRAVÉ", 
            "Description": "Ascenseur bloqué par les livraisons."
        },
        {
            "Date": datetime.date(2026, 6, 16), 
            "Début": "09:00", 
            "Fin": "11:30", 
            "Intensité": "🔴 Critique", 
            "Étiquette": "VIBRATIONS", 
            "Description": "Tremblements continus dans le sol."
        }
    ])

# 2. Section de saisie (Discrète en bas ou repliable)
with st.expander("📝 Saisir ou modifier un événement critique", expanded=False):
    config_colonnes = {
        "Date": st.column_config.DateColumn("Date", required=True),
        "Début": st.column_config.TextColumn("Début (HH:MM)", required=True),
        "Fin": st.column_config.TextColumn("Fin (HH:MM)", required=True),
        "Intensité": st.column_config.SelectboxColumn("Intensité", options=["🔴 Critique", "🟠 Fort", "🟡 Modéré"], required=True),
        "Étiquette": st.column_config.SelectboxColumn("Nature", options=["BRUIT : CHOCS", "BRUIT : PERCEMENT", "BRUIT : CONTINU", "VIBRATIONS", "POUSSIÈRE", "ACCÈS ENTRAVÉ", "COUPURE SYNCHRO"], required=True),
        "Description": st.column_config.TextColumn("Description")
    }
    df_edite = st.data_editor(
        st.session_state.nuisances_db, 
        column_config=config_colonnes,
        num_rows="dynamic", 
        use_container_width=True
    )
    st.session_state.nuisances_db = df_edite

# 3. Traitement et Rendu Visuel
if not df_edite.empty:
    try:
        df_events = df_edite.copy()
        df_events['Start'] = pd.to_datetime(df_events['Date'].astype(str) + ' ' + df_events['Début'])
        df_events['Finish'] = pd.to_datetime(df_events['Date'].astype(str) + ' ' + df_events['Fin'])
        df_events = df_events.sort_values('Start').reset_index(drop=True)
        
        # Algorithme de complétion des plages vertes
        chronologie_complete = []
        for i in range(len(df_events)):
            if i > 0 and df_events.loc[i, 'Start'] > df_events.loc[i-1, 'Finish']:
                chronologie_complete.append({
                    "Start": df_events.loc[i-1, 'Finish'],
                    "Finish": df_events.loc[i, 'Start'],
                    "Intensité": "🟢 Jouissance normale",
                    "Étiquette": "Normal"
                })
            chronologie_complete.append({
                "Start": df_events.loc[i, 'Start'],
                "Finish": df_events.loc[i, 'Finish'],
                "Intensité": df_events.loc[i, 'Intensité'],
                "Étiquette": df_events.loc[i, 'Étiquette']
            })
            
        df_plot = pd.DataFrame(chronologie_complete)
        df_plot['Axe'] = "Chronologie"
        
        # Dashboard KPIs en haut de page pour le look "pro"
        total_crises = len(df_events)
        col1, col2, col3 = st.columns(3)
        col1.metric("Alertes Critiques", f"{total_crises} événements")
        col2.metric("Statut Actuel", "🟢 Calme" if datetime.datetime.now() > df_events['Finish'].max() else "⚠️ Nuisance en cours")
        col3.metric("Dernier relevé", df_events['Date'].max().strftime("%d %B %Y"))

        # Palette de couleurs "Luxury / Architect" (Finitions mates et contrastées)
        couleurs_map = {
            "🔴 Critique": "#D9534F",          # Rouge brique mat
            "🟠 Fort": "#F0AD4E",              # Ambre doux
            "🟡 Modéré": "#F0DE4C",            # Jaune discret
            "🟢 Jouissance normale": "#E8F5E9"  # Vert d'eau très pâle (élégant, non agressif)
        }

        # Création de la frise épurée
        fig = px.timeline(
            df_plot, 
            x_start="Start", 
            x_end="Finish", 
            y="Axe", 
            color="Intensité",
            color_discrete_map=couleurs_map,
            hover_name="Étiquette",
            category_orders={"Intensité": ["🟢 Jouissance normale", "🟡 Modéré", "🟠 Fort", "🔴 Critique"]}
        )
        
        # Design haut de gamme de la Timeline
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=200,
            margin=dict(l=10, r=20, t=10, b=60),
            
            # Légende horizontale parfaitement intégrée en haut
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.2,
                xanchor="left",
                x=0,
                title_text=""
            ),
            font=dict(family="Inter, sans-serif", size=12, color="#333333")
        )
        
        # Axe X chirurgical pour afficher les dates exactes et les heures sans encombrement
        fig.update_xaxes(
            showgrid=True,
            gridcolor="#F0F0F0",  # Grille très fine pour caler le regard sur les heures exactes
            showline=True,
            linewidth=1.5,
            linecolor='#1A1A1A',
            tickformat="%a %d %b\n%H:%M",  # Exemple : "Lun 15 Juin (nouvelle ligne) 08:30"
            ticklabelmode="instant",
            title_text=""
        )
        
        # Axe Y masqué pour ne garder que le bandeau temporel
        fig.update_yaxes(showgrid=False, showticklabels=False, title_text="")
        
        # Format des barres (hauteur fixe, sans bordures agressives)
        fig.update_traces(
            width=0.4, 
            marker=dict(line=dict(color="#FFFFFF", width=1.5)),
            hovertemplate="<b>%{hovertext}</b><br>Début: %{x|%H:%M}<br>Fin: %{customdata[0]|%H:%M}<extra></extra>"
        )
        
        st.write("")
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
    except Exception as e:
        st.error("Une erreur est survenue lors du formatage. Vérifie la cohérence des heures (HH:MM).")
else:
    st.warning("Ajoute des données pour afficher l'infographie.")
