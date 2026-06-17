import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Configuration de la page pour un rendu compact et percutant
st.set_page_config(page_title="Rapport Nuisances - Maulini", layout="wide")

# CSS pour éliminer le blanc et maximiser l'impact visuel
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=400;600;700&display=swap');
    
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
        font-size: 26px;
        font-weight: 700;
        color: #000000;
        line-height: 1.2;
    }
    .sub-header {
        font-size: 14px;
        color: #333333;
        margin-bottom: 15px;
    }
    .custom-legend {
        background-color: #F8F9FA;
        border: 2px solid #1A1A1A;
        padding: 15px;
        border-radius: 5px;
        margin-top: 15px;
    }
    .legend-item {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 5px;
    }
    </style>
    <div class="main-header">Suivi Chronologique des Nuisances Chantier</div>
    <div class="sub-header">Générateur de frise d'impact — Document officiel de synthèse</div>
""", unsafe_allow_html=True)

# 1. Base de données initiale (entièrement en français)
if 'nuisances_db' not in st.session_state:
    st.session_state.nuisances_db = pd.DataFrame([
        {
            "Date": datetime.date(2026, 6, 15), 
            "Début": "08:30", 
            "Fin": "10:15", 
            "Intensité": "🔴 Très fort", 
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
            "Intensité": "🔴 Très fort", 
            "Nature": "VIBRATIONS", 
            "Description": "Tremblements continus dans le sol."
        }
    ])

# 2. Section d'édition dynamique
with st.expander("📝 Ajouter / Modifier des événements", expanded=False):
    config_colonnes = {
        "Date": st.column_config.DateColumn("Date", required=True, format="DD.MM.YYYY"),
        "Début": st.column_config.TextColumn("Début (HH:MM)", required=True),
        "Fin": st.column_config.TextColumn("Fin (HH:MM)", required=True),
        "Intensité": st.column_config.SelectboxColumn("Intensité", options=["🔴 Très fort", "🟠 Fort", "🟡 Modéré"], required=True),
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

# 3. Traitement et Rendu Graphique
if not df_edite.empty:
    try:
        # Nettoyage strict
        df_events = df_edite.copy()
        df_events = df_events.dropna(subset=['Date', 'Début', 'Fin', 'Intensité', 'Nature'])
        
        for col in ['Début', 'Fin']:
            df_events[col] = df_events[col].astype(str).str.strip().str.replace('h', ':', case=False)
        
        df_events = df_events[(df_events['Début'] != "") & (df_events['Fin'] != "")]
        
        if not df_events.empty:
            df_events['Start'] = pd.to_datetime(df_events['Date'].astype(str) + ' ' + df_events['Début'], errors='coerce')
            df_events['Finish'] = pd.to_datetime(df_events['Date'].astype(str) + ' ' + df_events['Fin'], errors='coerce')
            df_events = df_events.dropna(subset=['Start', 'Finish'])
            
            # Correction des inversions de chronologie au vol
            inversed = df_events['Start'] > df_events['Finish']
            if inversed.any():
                df_events.loc[inversed, ['Start', 'Finish']] = df_events.loc[inversed, ['Finish', 'Start']].values
            
            df_events = df_events.sort_values('Start').reset_index(drop=True)
            
        if not df_events.empty:
            # DÉCOMPTE DYNAMIQUE POUR LA LÉGENDE INTERACTIVE
            count_tres_fort = len(df_events[df_events['Intensité'] == "🔴 Très fort"])
            count_fort = len(df_events[df_events['Intensité'] == "🟠 Fort"])
            count_modere = len(df_events[df_events['Intensité'] == "🟡 Modéré"])
            
            # Algorithme de complétion des plages vides avec du Vert Pétant
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
            
            # Libellés enrichis pour la légende Plotly en français
            lbl_tres_fort = f"🔴 Très fort ({count_tres_fort})"
            lbl_fort = f"🟠 Fort ({count_fort})"
            lbl_modere = f"🟡 Modéré ({count_modere})"
            lbl_vert = "🟢 Jouissance normale"

            df_plot['Légende'] = df_plot['Intensité'].map({
                "🔴 Très fort": lbl_tres_fort,
                "🟠 Fort": lbl_fort,
                "🟡 Modéré": lbl_modere,
                "🟢 Jouissance normale": lbl_vert
            })

            # PALETTE DE COULEURS FLASHY ET CONTRASTÉES
            couleurs_legend_map = {
                lbl_tres_fort: "#FF0000",  # Rouge Pur Flash
                lbl_fort: "#FF6600",       # Orange Éclatant
                lbl_modere: "#FFD700",     # Jaune Pétant
                lbl_vert: "#2ECC71"        # Vert Émeraude Vif (Reste du temps)
            }

            fig = px.timeline(
                df_plot, 
                x_start="Start", 
                x_end="Finish", 
                y="Axe", 
                color="Légende",
                color_discrete_map=couleurs_legend_map,
                hover_name="Nature",
                custom_data=['Start', 'Finish'],
                category_orders={"Légende": [lbl_vert, lbl_modere, lbl_fort, lbl_tres_fort]}
            )
            
            fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                height=180,
                margin=dict(l=10, r=25, t=55, b=45),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.05,
                    xanchor="left",
                    x=0,
                    title_text=""
                ),
                font=dict(family="Inter, sans-serif", size=12, color="#000000")
            )
            
            # CONFIGURATION DE L'AXE DES ABSCISSES JOUR PAR JOUR EN FRANÇAIS
            fig.update_xaxes(
                showgrid=True,
                gridcolor="#EAEAEA",
                showline=True,
                linewidth=1.5,
                linecolor='#000000',
                dtick=86400000,  # Un repère strict toutes les 24 heures
                tickformat="%d.%m\n%H:%M",  # Format standard CH/FR numérique (ex: 15.06) pour contourner la langue du serveur
                title_text=""
            )
            
            fig.update_yaxes(showgrid=False, showticklabels=False, title_text="")
            
            fig.update_traces(
                width=0.6, 
                marker=dict(line=dict(color="#FFFFFF", width=1)),
                hovertemplate="<b>%{hovertext}</b><br>%{customdata[0]|%H:%M} à %{customdata[1]|%H:%M}<extra></extra>"
            )
            
            # Logo MAULINI
            fig.add_annotation(
                x=1, y=1.38,
                xref="paper", yref="paper",
                text="<b>MAULINI</b><br><span style='font-size:8px; letter-spacing:1px; color:#555555;'>MAÎTRE CONSTRUCTEUR</span>",
                showarrow=False,
                align="right",
                font=dict(family="Arial, sans-serif", size=13, color="#000000"),
                bgcolor="rgba(255, 255, 255, 1)",
                bordercolor="#000000",
                borderwidth=1.5,
                borderpad=4
            )
            
            st.plotly_chart(
                fig, 
                use_container_width=True, 
                config={
                    'locale': 'fr', # Force la langue de l'interface Plotly en français
                    'displayModeBar': True,
                    'displaylogo': False,
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'rapport_nuisances_maulini',
                        'height': 450,
                        'width': 1200,
                        'scale': 2
                    }
                }
            )
            
            # BLOC LÉGENDE INTERACTIF ET SYNCHRONISÉ EN FRANÇAIS
            st.markdown(f"""
                <div class="custom-legend">
                    <div style="font-weight: 700; font-size: 16px; margin-bottom: 10px; color: #000000; text-transform: uppercase; letter-spacing: 0.5px;">📋 Légende dynamique des seuils d'impact</div>
                    <div class="legend-item"><span style="color: #FF0000; font-size: 16px;">■</span> <b style="color: #FF0000;">Niveau Très fort ({count_tres_fort} événement(s)) :</b> Seuils réglementaires franchis. Travaux lourds bloquant toute activité.</div>
                    <div class="legend-item"><span style="color: #FF6600; font-size: 16px;">■</span> <b style="color: #FF6600;">Niveau Fort ({count_fort} événement(s)) :</b> Nuisance perturbante continue (vibrations, poussière, accès limités).</div>
                    <div class="legend-item"><span style="color: #FFD700; font-size: 16px;">■</span> <b style="color: #FFD700;">Niveau Modéré ({count_modere} événement(s)) :</b> Bruits de chantier de fond ou opérations courantes légères.</div>
                    <div class="legend-item"><span style="color: #2ECC71; font-size: 16px;">■</span> <b style="color: #2ECC71;">Jouissance Normale / Calme :</b> Aucune nuisance reportée. Cadre de vie conforme.</div>
                </div>
            """, unsafe_allow_html=True)
            
        else:
            st.warning("Complète les lignes du tableau avec des heures valides (ex: 08:30) pour générer le visuel.")
            
    except Exception as e:
        st.error(f"Erreur technique rencontrée : {e}")
else:
    st.warning("Ajoute des données pour afficher la frise.")
