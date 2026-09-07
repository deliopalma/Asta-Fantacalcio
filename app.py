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
# 3. FUNZIONE CARICAMENTO DATI (CON GESTIONE BOM E SEPARATORI)
# ==========================================
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", "tutti_2027.csv")

    if not os.path.exists(file_path):
        st.error(
            f"❌ Impossibile trovare il file in '{file_path}'. Verifica che il file 'tutti_2027.csv' sia presente nella cartella 'data/'."
        )
        return pd.DataFrame()

    try:
        # utf-8-sig rimuove l'eventuale carattere invisibile BOM all'inizio del file
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig")
            if df.shape[1] <= 1:
                df = pd.read_csv(file_path, sep=";", encoding="utf-8-sig")
        except Exception:
            df = pd.read_csv(file_path, sep=";", encoding="latin1")

        # Rimuove spazi vuoti e mappa tutti i nomi colonna
        df.columns = df.columns.str.strip()

        # Ricerca della colonna Ruolo indipendente dalle maiuscole/minuscole
        col_ruolo = [c for c in df.columns if c.upper() == "RUOLO"]
        if col_ruolo:
            df["RUOLO"] = df[col_ruolo[0]].astype(str).str.strip().str.upper()
        else:
            st.error("❌ Colonna 'RUOLO' non trovata all'interno del file CSV.")
            return pd.DataFrame()

        # Normalizzazione colonne numeriche
        map_colonne = {
            "PREZZO CONSIGLIATO": "Prezzo consigliato",
            "PREZZO MASSIMO": "Prezzo Massimo",
            "PRESENZE": "Presenze",
            "GOAL SUBITI": "Goal subiti",
            "CLEAN SHEET": "Clean Sheet",
            "GOAL FATTI": "Goal fatti",
            "ASSIST": "Assist",
        }

        # Crea un dizionario in maiuscolo per fare il match sicuro
        cols_upper = {c.upper(): c for c in df.columns}

        for col_key_upper, target_name in map_colonne.items():
            if col_key_upper in cols_upper:
                orig_col = cols_upper[col_key_upper]
                df[target_name] = pd.to_numeric(
                    df[orig_col], errors="coerce"
                ).fillna(0)
            else:
                df[target_name] = 0

        return df

    except Exception as e:
        st.error(
            f"❌ Si è verificato un errore durante la lettura del file CSV: {e}"
        )
        return pd.DataFrame()


df = load_data()

if df.empty:
    st.warning(
        "Caricamento dati non riuscito. Controlla il file CSV nella cartella 'data/' e riprova."
    )
    st.stop()

# ==========================================
# 4. SIDEBAR: FILTRI & CONTROLLI
# ==========================================
st.sidebar.header("🔍 Filtri Ricerca & Asta")

# Filtro Ruolo
ruoli_disponibili = ["TUTTI"] + sorted(
    [r for r in df["RUOLO"].unique() if r and r != "NAN"]
)
ruolo_selezionato = st.sidebar.selectbox("Seleziona Ruolo", ruoli_disponibili)

# Filtro Squadra
col_squadra = [
    c
    for c in df.columns
    if c.upper() in ["SQUADRA", "NOME SQUADRA", "CLUB", "TEAM"]
]
if col_squadra:
    nome_col_squadra = col_squadra[0]
    squadre = ["TUTTE"] + sorted(
        list(df[nome_col_squadra].dropna().astype(str).unique())
    )
    squadra_selezionata = st.sidebar.selectbox("Seleziona Squadra", squadre)
else:
    squadra_selezionata = "TUTTE"
    nome_col_squadra = None

# Ricerca Nome
ricerca_nome = st.sidebar.text_input("Cerca Calciatore per Nome:", "")

# Filtro Slot
col_slot = [c for c in df.columns if c.upper() == "SLOT"]
if col_slot:
    nome_col_slot = col_slot[0]
    slot_disponibili = ["TUTTI"] + sorted(
        [str(s) for s in df[nome_col_slot].dropna().unique()]
    )
    slot_selezionato = st.sidebar.selectbox("Filtra per Slot", slot_disponibili)
else:
    nome_col_slot = None
    slot_selezionato = "TUTTI"

# Filtro Verdetto Algoritmo
col_verdetto = [c for c in df.columns if "PRENDI O LASCIA" in c.upper()]
if col_verdetto:
    nome_col_verdetto = col_verdetto[0]
    verdetti = ["TUTTI"] + sorted(
        list(df[nome_col_verdetto].dropna().astype(str).unique())
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

if squadra_selezionata != "TUTTE" and nome_col_squadra:
    df_filtered = df_filtered[
        df_filtered[nome_col_squadra].astype(str) == squadra_selezionata
    ]

if ricerca_nome:
    col_nome = [c for c in df_filtered.columns if "NOME" in c.upper()]
    if col_nome:
        df_filtered = df_filtered[
            df_filtered[col_nome[0]]
            .astype(str)
            .str.contains(ricerca_nome, case=False, na=False)
        ]

if slot_selezionato != "TUTTI" and nome_col_slot:
    df_filtered = df_filtered[
        df_filtered[nome_col_slot].astype(str) == slot_selezionato
    ]

if verdetto_selezionato != "TUTTI" and nome_col_verdetto:
    df_filtered = df_filtered[
        df_filtered[nome_col_verdetto].astype(str) == verdetto_selezionato
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

# Individuazione colonne da mostrare
cols_base = [c for c in df_filtered.columns if c.upper() in ["RUOLO", "NOME"]]

if nome_col_squadra and nome_col_squadra not in cols_base:
    cols_base.append(nome_col_squadra)

if nome_col_slot and nome_col_slot not in cols_base:
    cols_base.append(nome_col_slot)

if ruolo_selezionato == "P":
    cols_stats = ["Prezzo consigliato", "Prezzo Massimo", "Presenze", "Goal subiti", "Clean Sheet"]
else:
    cols_stats = ["Prezzo consigliato", "Prezzo Massimo", "Presenze", "Goal fatti", "Assist"]

if nome_col_verdetto:
    cols_stats.append(nome_col_verdetto)

cols_to_display = [c for c in cols_base + cols_stats if c in df_filtered.columns]

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
