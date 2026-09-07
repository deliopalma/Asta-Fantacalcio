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
# 2. CSS PERSONALIZZATO (TEMA GRAFICO DARK & PREMIUM)
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
# 3. FUNZIONE CARICAMENTO DATI
# ==========================================
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", "tutti_2027.csv")

    if not os.path.exists(file_path):
        st.error(
            f"❌ Impossibile trovare il file in '{file_path}'. Verifica che 'tutti_2027.csv' sia presente nella cartella 'data/'."
        )
        return pd.DataFrame()

    try:
        # Lettura del CSV gestendo i vari codici di caratteri
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig")
            if df.shape[1] <= 1:
                df = pd.read_csv(file_path, sep=";", encoding="utf-8-sig")
        except Exception:
            df = pd.read_csv(file_path, sep=";", encoding="latin1")

        # Pulizia nomi colonne
        df.columns = df.columns.str.strip()

        # Identificazione colonna Ruolo
        col_ruolo = next((c for c in df.columns if "ruolo" in c.lower()), None)
        if col_ruolo:
            df["RUOLO"] = df[col_ruolo].astype(str).str.strip().str.upper()

        # Identificazione precisa delle colonne statistiche
        col_subiti = next((c for c in df.columns if "subit" in c.lower()), None)
        col_clean = next((c for c in df.columns if "clean" in c.lower()), None)

        # Pulizia numerica standard
        for col in df.columns:
            if any(
                k in col.lower()
                for k in ["prezzo", "presenz", "goal", "gol", "assist", "clean"]
            ):
                df[col] = pd.to_numeric(
                    df[col]
                    .astype(str)
                    .str.replace(",", ".")
                    .str.extract(r"(-?\d+\.?\d*)")[0],
                    errors="coerce",
                ).fillna(0)

        # FIX SICUREZZA: azzera Gol Subiti e Clean Sheet per tutti i non-portieri
        if col_ruolo:
            if col_subiti:
                df.loc[df["RUOLO"] != "P", col_subiti] = 0
            if col_clean:
                df.loc[df["RUOLO"] != "P", col_clean] = 0

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


# Helper per la ricerca delle colonne nel CSV
def find_col(keywords):
    for kw in keywords:
        for c in df.columns:
            if kw.lower() in c.lower():
                return c
    return None


col_ruolo = find_col(["ruolo"])
col_nome = find_col(["nome calciatore", "nome"])
col_squadra = find_col(["squadra", "club", "team"])
col_slot = find_col(["slot"])
col_p_cons = find_col(["prezzo consigliato", "consigliato"])
col_p_max = find_col(["prezzo massimo", "massimo"])
col_pres = find_col(["presenze", "pres"])
col_gol = find_col(["goal fatti", "gol fatti", "goal", "gol"])
col_assist = find_col(["assist"])
col_subiti = find_col(["goal subiti", "gol subiti", "subiti"])
col_clean = find_col(["clean sheet", "clean"])
col_badge = find_col(["badge"])
col_verdetto = find_col(["prendi o lascia", "verdetto"])

# ==========================================
# 4. SIDEBAR: FILTRI & CONTROLLI
# ==========================================
st.sidebar.header("🔍 Filtri Ricerca & Asta")

# 1. Filtro Ruolo
ruoli_disponibili = ["TUTTI"] + sorted(
    [r for r in df["RUOLO"].unique() if r and r != "NAN"]
)
ruolo_selezionato = st.sidebar.selectbox("Seleziona Ruolo", ruoli_disponibili)

# 2. Filtro Squadra
if col_squadra:
    squadre = ["TUTTE"] + sorted(
        list(df[col_squadra].dropna().astype(str).unique())
    )
    squadra_selezionata = st.sidebar.selectbox("Seleziona Squadra", squadre)
else:
    squadra_selezionata = "TUTTE"

# 3. Ricerca Nome
ricerca_nome = st.sidebar.text_input("Cerca Calciatore per Nome:", "")

# 4. Filtro Slot
if col_slot:
    slots = ["TUTTI"] + sorted(
        [
            str(int(s)) if isinstance(s, (int, float)) and s == s else str(s)
            for s in df[col_slot].unique()
        ]
    )
    slot_selezionato = st.sidebar.selectbox("Filtra per Slot", slots)
else:
    slot_selezionato = "TUTTI"

# 5. Filtro Verdetto Algoritmo
if col_verdetto:
    verdetti = ["TUTTI"] + sorted(
        list(df[col_verdetto].dropna().astype(str).unique())
    )
    verdetto_selezionato = st.sidebar.selectbox(
        "Verdetto Algoritmo 🎲", verdetti
    )
else:
    verdetto_selezionato = "TUTTI"

# ==========================================
# 5. APPLICAZIONE FILTRI
# ==========================================
df_filtered = df.copy()

if ruolo_selezionato != "TUTTI":
    df_filtered = df_filtered[df_filtered["RUOLO"] == ruolo_selezionato]

if squadra_selezionata != "TUTTE" and col_squadra:
    df_filtered = df_filtered[
        df_filtered[col_squadra].astype(str) == squadra_selezionata
    ]

if ricerca_nome and col_nome:
    df_filtered = df_filtered[
        df_filtered[col_nome]
        .astype(str)
        .str.contains(ricerca_nome, case=False, na=False)
    ]

if slot_selezionato != "TUTTI" and col_slot:
    df_filtered = df_filtered[
        df_filtered[col_slot].astype(str) == slot_selezionato
    ]

if verdetto_selezionato != "TUTTI" and col_verdetto:
    df_filtered = df_filtered[
        df_filtered[col_verdetto].astype(str) == verdetto_selezionato
    ]

# ==========================================
# 6. METRICHE UTILI ASTA
# ==========================================
st.subheader("📊 Panoramica Selezione")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Calciatori Filtrati", len(df_filtered))

with col2:
    if col_slot:
        top_players = len(
            df_filtered[df_filtered[col_slot].astype(str).str.contains("1")]
        )
        st.metric("Giocatori 1° Slot", top_players)
    else:
        st.metric("Giocatori 1° Slot", "-")

with col3:
    if col_p_cons and len(df_filtered) > 0:
        media_p = df_filtered[col_p_cons].mean()
        st.metric("Prezzo Consigliato Medio", f"{int(media_p)} cr")
    else:
        st.metric("Prezzo Consigliato Medio", "0 cr")

with col4:
    if col_badge:
        badge_count = len(
            df_filtered[
                df_filtered[col_badge].notna()
                & (df_filtered[col_badge].astype(str).str.strip() != "")
            ]
        )
        st.metric("Badge Speciali", badge_count)
    else:
        st.metric("Badge Speciali", "-")

st.markdown("---")

# ==========================================
# 7. TABELLA DINAMICA SPECIFICA PER RUOLO
# ==========================================
st.subheader("📋 Tabella Calciatori & Consigli Asta")

# Colonne base
cols_base = [col_ruolo, col_nome, col_squadra, col_slot]
cols_prezzi = [col_p_cons, col_p_max, col_pres]

# Selezione rigorosa delle colonne statistiche in base al ruolo selezionato
if ruolo_selezionato == "P":
    cols_stats = [col_subiti, col_clean]
else:
    # Per D, C, A e vista TUTTI mostriamo solo Goal e Assist
    cols_stats = [col_gol, col_assist]

cols_extra = [col_badge, col_verdetto]

# Unione e rimozione valori non trovati
cols_to_display = [
    c
    for c in (cols_base + cols_prezzi + cols_stats + cols_extra)
    if c is not None and c in df_filtered.columns
]

# Formattazione colonne
column_configuration = {}
if col_ruolo in cols_to_display:
    column_configuration[col_ruolo] = st.column_config.TextColumn("Ruolo")
if col_p_cons in cols_to_display:
    column_configuration[col_p_cons] = st.column_config.NumberColumn(
        "Consigliato", format="%d cr"
    )
if col_p_max in cols_to_display:
    column_configuration[col_p_max] = st.column_config.NumberColumn(
        "Massimo", format="%d cr"
    )
if col_pres in cols_to_display:
    column_configuration[col_pres] = st.column_config.NumberColumn(
        "Presenze", format="%d"
    )
if col_gol in cols_to_display:
    column_configuration[col_gol] = st.column_config.NumberColumn(
        "Gol ⚽", format="%d"
    )
if col_assist in cols_to_display:
    column_configuration[col_assist] = st.column_config.NumberColumn(
        "Assist 🅰️", format="%d"
    )
if col_subiti in cols_to_display:
    column_configuration[col_subiti] = st.column_config.NumberColumn(
        "Gol Subiti 🥊", format="%d"
    )
if col_clean in cols_to_display:
    column_configuration[col_clean] = st.column_config.NumberColumn(
        "Clean Sheet 🧤", format="%d"
    )
if col_badge in cols_to_display:
    column_configuration[col_badge] = st.column_config.TextColumn("Badge 🎖️")

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
