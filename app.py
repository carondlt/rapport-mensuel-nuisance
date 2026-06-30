import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Configuration de la page pour un rendu compact et haut de gamme
st.set_page_config(page_title="Rapport Nuisances - Maulini", layout="wide")

# CSS pour un design épuré, moderne et professionnel (Palette Pastel)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=400;500;600;700&display=swap');
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #FFFFFF;
        color: #1A1A1A;
    }
    .main-header {
        font-size: 28px;
        font-weight: 700;
        color: #111111;
        line-height: 1.2;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 14px;
        color: #666666;
        margin-bottom: 25px;
        font-weight: 400;
    }
    .custom-legend {
        background-color: #FAFAFA;
        border: 1px solid #E5E5E5;
        padding: 20px;
        border-radius: 8px;
        margin-top: 25px;
    }
    .legend-title {
        font-weight: 700; 
        font-size: 14px; 
        margin-bottom: 12px; 
        color: #111111; 
        text-transform: uppercase; 
        letter-spacing: 0.5px;
    }
    .legend-item {
        font-size: 13px;
        color: #444444;
        margin-bottom: 8px;
        line-height: 1.5;
    }
    .legend-item:last-child {
        margin-bottom: 0px;
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
        df_events = df_edite.copy()
        df_events = df_events.dropna(subset=['Date', 'Début', 'Fin', 'Intensité', 'Nature'])
        
        for col in ['Début', 'Fin']:
            df_events[col] = df_events[col].astype(str).str.strip().str.replace('h', ':', case=False)
        
        df_events = df_events[(df_events['Début'] != "") & (df_events['Fin'] != "")]
        
        if not df_events.empty:
            df_events['Start'] = pd.to_datetime(df_events['Date'].astype(str) + ' ' + df_events['Début'], errors='coerce')
            df_events['Finish'] = pd.to_datetime(df_events['Date'].astype(str) + ' ' + df_events['Fin'], errors='coerce')
            df_events = df_events.dropna(subset=['Start', 'Finish'])
            
            # Correction des inversions de chronologie
            inversed = df_events['Start'] > df_events['Finish']
            if inversed.any():
                df_events.loc[inversed, ['Start', 'Finish']] = df_events.loc[inversed, ['Finish', 'Start']].values
            
            df_events = df_events.sort_values('Start').reset_index(drop=True)
            
        if not df_events.empty:
            count_tres_fort = len(df_events[df_events['Intensité'] == "🔴 Très fort"])
            count_fort = len(df_events[df_events['Intensité'] == "🟠 Fort"])
            count_modere = len(df_events[df_events['Intensité'] == "🟡 Modéré"])
            
            # Algorithme de complétion continue en Vert Pastel pour le reste du temps
            chronologie_complete = []
            
            # Bornes temporelles globales calées sur les journées encodées (de 07:00 à 18:00)
            min_date = df_events['Start'].min().replace(hour=7, minute=0, second=0)
            max_date = df_events['Finish'].max().replace(hour=18, minute=0, second=0)
            
            current_time = min_date
            
            for i in range(len(df_events)):
                # Si un espace vide existe avant l'événement, on injecte le vert pâle pastel
                if df_events.loc[i, 'Start'] > current_time:
                    chronologie_complete.append({
                        "Start": current_time,
                        "Finish": df_events.loc[i, 'Start'],
                        "Intensité": "🟢 Jouissance normale",
                        "Nature": "Période calme",
                        "Description": "Aucun incident ou nuisance"
                    })
                
                # Ajout de l'événement de nuisance actuel
                chronologie_complete.append({
                    "Start": df_events.loc[i, 'Start'],
                    "Finish": df_events.loc[i, 'Finish'],
                    "Intensité": df_events.loc[i, 'Intensité'],
                    "Nature": df_events.loc[i, 'Nature'],
                    "Description": df_events.loc[i, 'Description']
                })
                current_time = df_events.loc[i, 'Finish']
            
            # Combler en vert pastel jusqu'à la fin de la dernière amplitude horaire
            if current_time < max_date:
                chronologie_complete.append({
                    "Start": current_time,
                    "Finish": max_date,
                    "Intensité": "🟢 Jouissance normale",
                    "Nature": "Période calme",
                    "Description": "Aucun incident ou nuisance"
                })
                
            df_plot = pd.DataFrame(chronologie_complete)
            df_plot['Axe'] = "Impact"
            
            # Libellés épurés pour la légende
            lbl_tres_fort = f"Niveau Très fort ({count_tres_fort})"
            lbl_fort = f"Niveau Fort ({count_fort})"
            lbl_modere = f"Niveau Modéré ({count_modere})"
            lbl_vert = "Jouissance normale (Périodes calmes)"

            df_plot['Légende'] = df_plot['Intensité'].map({
                "🔴 Très fort": lbl_tres_fort,
                "🟠 Fort": lbl_fort,
                "🟡 Modéré": lbl_modere,
                "🟢 Jouissance normale": lbl_vert
            })

            # Palette exclusive de tons pastels doux et sophistiqués
            couleurs_legend_map = {
                lbl_tres_fort: "#F2D7D5",  # Rouge bordeaux pastel doux
                lbl_fort: "#FDEBD0",       # Orange ambre pastel très clair
                lbl_modere: "#FCF3CF",     # Jaune sablon / crème pastel
                lbl_vert: "#E2F0D9"        # Vert pâle pastel parfait pour le calme
            }

            fig = px.timeline(
                df_plot, 
                x_start="Start", 
                x_end="Finish", 
                y="Axe", 
                color="Légende",
                color_discrete_map=couleurs_legend_map,
                hover_name="Nature",
                custom_data=['Start', 'Finish', 'Description'],
                category_orders={"Légende": [lbl_vert, lbl_modere, lbl_fort, lbl_tres_fort]}
            )
            
            fig.update_layout(
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                height=220,
                margin=dict(l=20, r=20, t=60, b=40),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.1,
                    xanchor="left",
                    x=0,
                    title_text="",
                    font=dict(size=11, color="#444444")
                ),
                font=dict(family="Inter, sans-serif", size=12, color="#1A1A1A")
            )
            
            # Configuration fine de l'axe temporel (Frise chronologique fluide)
            fig.update_xaxes(
                showgrid=True,
                gridcolor="#F5F5F5",
                showline=True,
                linewidth=1,
                linecolor='#1A1A1A',
                type='date',
                tickformat="%d %b\n%H:%M",
                ticklabelmode="instant",
                title_text=""
            )
            
            fig.update_yaxes(showgrid=False, showticklabels=False, title_text="")
            
            fig.update_traces(
                width=0.5, 
                marker=dict(line=dict(color="#FFFFFF", width=1.5)), # Délineation blanche discrète
                hovertemplate="<b>%{hovertext}</b><br>⏱ %{customdata[0]|%H:%M} à %{customdata[1]|%H:%M}<br>📝 %{customdata[2]}<extra></extra>"
            )
            
            # Signature Maulini minimaliste
            fig.add_annotation(
                x=1, y=1.45,
                xref="paper", yref="paper",
                text="<b>MAULINI</b><br><span style='font-size:7.5px; letter-spacing:1.5px; color:#666666;'>MAÎTRE CONSTRUCTEUR</span>",
                showarrow=False,
                align="right",
                font=dict(family="Arial, sans-serif", size=14, color="#111111"),
                bgcolor="rgba(255, 255, 255, 0)",
                bordercolor="#111111",
                borderwidth=1,
                borderpad=6
            )
            
            st.plotly_chart(
                fig, 
                use_container_width=True, 
                config={
                    'locale': 'fr',
                    'displayModeBar': False,
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'rapport_nuisances_maulini',
                        'height': 500,
                        'width': 1300,
                        'scale': 3
                    }
                }
            )
            
            # Bloc Légende d'impact statique épuré
            st.markdown(f"""
                <div class="custom-legend">
                    <div class="legend-title">📋 Seuils réglementaires et impacts d'exploitation</div>
                    <div class="legend-item"><span style="color: #F2D7D5; font-size: 14px;">■</span> <b>Niveau Très fort ({count_tres_fort} évt(s)) :</b> Seuils critiques franchis. Travaux lourds impactant significativement l'activité.</div>
                    <div class="legend-item"><span style="color: #FDEBD0; font-size: 14px;">■</span> <b>Niveau Fort ({count_fort} évt(s)) :</b> Nuisances continues ou répétées (vibrations continues, poussières denses).</div>
                    <div class="legend-item"><span style="color: #FCF3CF; font-size: 14px;">■</span> <b>Niveau Modéré ({count_modere} évt(s)) :</b> Opérations courantes de second œuvre ou bruits de fond diffus.</div>
                    <div class="legend-item"><span style="color: #E2F0D9; font-size: 14px;">■</span> <b>Jouissance Normale :</b> Périodes de calme préservées. Environnement conforme aux exigences d'exploitation.</div>
                </div>
            """, unsafe_allow_html=True)
            
        else:
            st.warning("Veuillez renseigner des horaires valides (ex: 08:30) pour générer le visuel.")
            
    except Exception as e:
        st.error(f"Une erreur technique est survenue lors du traitement des dates : {e}")
else:
    st.warning("Ajoutez des lignes de données pour afficher la frise chronologique.")
