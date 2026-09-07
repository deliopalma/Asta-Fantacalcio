import os
import pandas as pd
import streamlit as st

# ==========================================
# 1. CONFIGURAZIONE PAGINA STREAMLIT
# ==========================================
st.set_page_config(
    page_title="FantaBooster® Engine v3.5",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 2. CSS PERSONALIZZATO (TEMA GRAFICO & COLORI)
# ==========================================
st.markdown(
    """
    <style>
    /* Sfondo principale e font */
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Header e Titoli */
    h1 {
        color: #00E676 !important;
        font-weight: 800;
    }
    h2, h3 {
        color: #00B0FF !important;
    }
    
    /* Container Metriche (KPI) */
    div[data-testid="stMetric"] {
        background-color: #1e222d;
        border: 1px solid #2e364f;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    div[data-testid="stMetricLabel"] {
        color: #b0bec5 !important;
        font-size: 0.9rem !important;
    }

    div[data-testid="stMetricValue"] {
        color: #00E676 !important;
        font-weight: 700;
    }

    /* Styling Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #131722;
        border-right: 1px solid #2e364f;
    }

    /* Pulsanti e Selectbox */
    .stSelectbox label, .stTextInput label {
        color: #00B0FF !important;
        font-weight: 600;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header
st.title("⚽ FantaBooster® Engine Version 3.5")
st.caption(
    "Transfermarkt Stats 25/26 & 26/27 Projections Integrated — Created by Delio Palma"
)
st.markdown("---")


# ==========================================
# 3. FUNZIONE CARICAMENTO DATI (CSV IN CARTA DATA/)
# ==========================================
@st.cache_data
def load_data():
    # Costruiamo il percorso relativo verso la cartella data/
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", "tutti_2027.csv")

    if not os.path.exists(file_path):
        st.error(
            f"❌ Impossibile trovare il file in '{file_path}'. Verifica che il file 'tutti_2027.csv' sia stato caricato dentro la cartella 'data/' su GitHub."
        )
        return pd.DataFrame()

    try:
        # Tenta prima la lettura con virgola, altrimenti con punto e virgola ';'
        try:
            df = pd.read_csv(file_path)
            if df.shape[1] <= 1:  # Se legge una sola colonna, il separatore è probabilmente ';'
                df = pd.read_csv(file_path, sep=";")
        except Exception:
            df = pd.read_csv(file_path, sep=";")

        # Pulizia intestazioni colonne
        df.columns = df.columns.str.strip()

        # Conversione numerica sicura
        cols_numeriche = [
            "Prezzo consigliato",
            "Prezzo Massimo",
            "Presenze",
            "Goal subiti",
            "Clean Sheet",
            "Goal fatti",
            "Assist",
        ]

        for col in cols_numeriche:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            else:
                df[col] = 0

        if "RUOLO" in df.columns:
            df["RUOLO"] = df["RUOLO"].astype(str).str.strip().str.upper()

        return df

    except Exception as e:
        st.error(
            f"❌ Si è verificato un errore durante la lettura del file CSV: {e}"
        )
        return pd.DataFrame()

# ==========================================
# 4. SIDEBAR: FILTRI & CONTROLLI
# ==========================================
st.sidebar.header("🔍 Filtri Ricerca & Asta")

# Filtro Ruolo
ruoli_disponibili = ["TUTTI"] + sorted(list(df["RUOLO"].unique()))
ruolo_selezionato = st.sidebar.selectbox("Seleziona Ruolo", ruoli_disponibili)

# Filtro Squadra
if "SQUADRA" in df.columns:
    squadre = ["TUTTE"] + sorted(list(df["SQUADRA"].dropna().unique()))
    squadra_selezionata = st.sidebar.selectbox("Seleziona Squadra", squadre)
else:
    squadra_selezionata = "TUTTE"

# Ricerca Nome
ricerca_nome = st.sidebar.text_input("Cerca Calciatore per Nome:", "")

# Filtro Slot
if "SLOT" in df.columns:
    slot_disponibili = ["TUTTI"] + sorted(
        [str(s) for s in df["SLOT"].dropna().unique()]
    )
    slot_selezionato = st.sidebar.selectbox("Filtra per Slot", slot_disponibili)
else:
    slot_selezionato = "TUTTI"

# Filtro Verdetto Algoritmo
col_verdetto = [c for c in df.columns if "Prendi o lascia" in c]
if col_verdetto:
    nome_col_verdetto = col_verdetto[0]
    verdetti = ["TUTTI"] + sorted(
        list(df[nome_col_verdetto].dropna().unique())
    )
    verdetto_selezionato = st.sidebar.selectbox(
        "Verdetto Algoritmo 🎲", verdetti
    )
else:
    nome_col_verdetto = None
    verdetto_selezionato = "TUTTI"

# ==========================================
# 5. APPLICAZIONE FILTRI
# ==========================================
df_filtered = df.copy()

if ruolo_selezionato != "TUTTI":
    df_filtered = df_filtered[df_filtered["RUOLO"] == ruolo_selezionato]

if squadra_selezionata != "TUTTE" and "SQUADRA" in df_filtered.columns:
    df_filtered = df_filtered[
        df_filtered["SQUADRA"] == squadra_selezionata
    ]

if ricerca_nome:
    col_nome = [c for c in df_filtered.columns if "NOME" in c.upper()][0]
    df_filtered = df_filtered[
        df_filtered[col_nome]
        .astype(str)
        .str.contains(ricerca_nome, case=False, na=False)
    ]

if slot_selezionato != "TUTTI" and "SLOT" in df_filtered.columns:
    df_filtered = df_filtered[
        df_filtered["SLOT"].astype(str) == slot_selezionato
    ]

if verdetto_selezionato != "TUTTI" and nome_col_verdetto:
    df_filtered = df_filtered[
        df_filtered[nome_col_verdetto] == verdetto_selezionato
    ]

# ==========================================
# 6. METRICHE GENERALI E KPI
# ==========================================
st.subheader("📊 Panoramica Rosa & Asta")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Calciatori Filtrati", len(df_filtered))

with col2:
    p_cons = (
        df_filtered["Prezzo consigliato"].sum()
        if "Prezzo consigliato" in df_filtered.columns
        else 0
    )
    st.metric("Tot. Prezzi Consigliati", f"{int(p_cons)} cr")

with col3:
    p_max = (
        df_filtered["Prezzo Massimo"].sum()
        if "Prezzo Massimo" in df_filtered.columns
        else 0
    )
    st.metric("Tot. Prezzi Massimi", f"{int(p_max)} cr")

with col4:
    tot_gol = (
        df_filtered["Goal fatti"].sum()
        if "Goal fatti" in df_filtered.columns
        else 0
    )
    st.metric("Totale Gol Proiettati", int(tot_gol))

st.markdown("---")

# ==========================================
# 7. TABELLA DINAMICA CON FORMATTAZIONE
# ==========================================
st.subheader("📋 Tabella Calciatori & Consigli Asta")

# Selezione colonne in base al ruolo scelto
if ruolo_selezionato == "P":
    cols_to_display = [
        col
        for col in [
            "RUOLO",
            "NOME",
            "NOME SQUADRA",
            "SQUADRA",
            "SLOT",
            "Prezzo consigliato",
            "Prezzo Massimo",
            "Presenze",
            "Goal subiti",
            "Clean Sheet",
            "Badge",
            nome_col_verdetto,
        ]
        if col in df_filtered.columns
    ]
else:
    cols_to_display = [
        col
        for col in [
            "RUOLO",
            "NOME",
            "NOME SQUADRA",
            "SQUADRA",
            "SLOT",
            "Prezzo consigliato",
            "Prezzo Massimo",
            "Presenze",
            "Goal fatti",
            "Assist",
            "Badge",
            nome_col_verdetto,
        ]
        if col in df_filtered.columns
    ]

# Configurazione formattazione colonne
column_configuration = {
    "RUOLO": st.column_config.TextColumn("Ruolo"),
    "Prezzo consigliato": st.column_config.NumberColumn(
        "Consigliato", format="%d cr"
    ),
    "Prezzo Massimo": st.column_config.NumberColumn("Massimo", format="%d cr"),
    "Presenze": st.column_config.NumberColumn("Presenze", format="%d"),
    "Goal fatti": st.column_config.NumberColumn("Gol ⚽", format="%d"),
    "Assist": st.column_config.NumberColumn("Assist 🅰️", format="%d"),
    "Goal subiti": st.column_config.NumberColumn("Gol Subiti 🥊", format="%d"),
    "Clean Sheet": st.column_config.NumberColumn("Clean Sheet 🧤", format="%d"),
}

st.dataframe(
    df_filtered[cols_to_display],
    use_container_width=True,
    hide_index=True,
    column_config=column_configuration,
)

# Footer
st.markdown("---")
st.caption(
    "FantaBooster® Engine v3.5 | Sviluppato per Asta Fantacalcio 2026/2027"
)
