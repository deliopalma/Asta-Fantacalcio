import os
import re
import pandas as pd
import streamlit as st

# ==========================================
# 1. CONFIGURAZIONE PAGINA
# ==========================================
st.set_page_config(
    page_title="FantaBooster® Engine v3.6",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 2. CSS TEMA DARK & STILE METRICHE
# ==========================================
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    h1 {
        color: #00E676 !important;
        font-weight: 800;
    }
    h2, h3 {
        color: #00B0FF !important;
    }
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
    section[data-testid="stSidebar"] {
        background-color: #131722;
        border-right: 1px solid #2e364f;
    }
    .stSelectbox label, .stTextInput label {
        color: #00B0FF !important;
        font-weight: 600;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("⚽ FantaBooster® Engine Version 3.6")
st.caption(
    "Transfermarkt Stats 25/26 & 26/27 Projections Integrated — Created by Delio Palma"
)
st.markdown("---")


# ==========================================
# 3. LETTURA & PARSING ROBUSTO CSV
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
        # Prova vari separatori ed encoding
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig")
            if df.shape[1] <= 1:
                df = pd.read_csv(file_path, sep=";", encoding="utf-8-sig")
        except Exception:
            try:
                df = pd.read_csv(file_path, sep=";", encoding="latin1")
            except Exception:
                df = pd.read_csv(file_path, sep=",", encoding="latin1")

        # Pulizia nomi colonne
        df.columns = df.columns.astype(str).str.strip()

        # Funzione pulizia valori numerici
        def clean_val(val):
            if pd.isna(val):
                return 0.0
            val_str = str(val).replace(",", ".").strip()
            match = re.search(r"[-+]?\d*\.?\d+", val_str)
            if match:
                try:
                    return float(match.group())
                except ValueError:
                    return 0.0
            return 0.0

        # Pulizia estesa per le colonne numeriche
        for col in df.columns:
            col_l = col.lower()
            if any(
                k in col_l
                for k in [
                    "prezzo",
                    "presenz",
                    "goal",
                    "gol",
                    "assist",
                    "subit",
                    "clean",
                    "slot",
                    "p_",
                ]
            ):
                df[col] = df[col].apply(clean_val)

        # Gestione Normalizzata Ruolo
        col_r = next((c for c in df.columns if "ruolo" in c.lower()), None)
        if col_r:
            df["RUOLO_CLEAN"] = df[col_r].astype(str).str.strip().str.upper()
        else:
            df["RUOLO_CLEAN"] = ""

        return df

    except Exception as e:
        st.error(f"❌ Errore nella lettura del CSV: {e}")
        return pd.DataFrame()


df = load_data()

if df.empty:
    st.warning(
        "Nessun dato trovato. Assicurati che 'tutti_2027.csv' sia presente."
    )
    st.stop()


# ==========================================
# 4. ALGORITMO DI TROVA-COLONNE
# ==========================================
def find_col(keywords, exclude=None):
    for kw in keywords:
        for c in df.columns:
            if c == "RUOLO_CLEAN":
                continue
            c_clean = c.lower().replace("_", " ")
            if kw in c_clean:
                if exclude and any(ex in c_clean for ex in exclude):
                    continue
                return c
    return None


col_ruolo = find_col(["ruolo", "role", "r"])
col_nome = find_col(["nome", "calciatore", "giocatore", "player"])
col_squadra = find_col(["squadra", "club", "team"])
col_slot = find_col(["slot"])
col_p_cons = find_col(["consigliato", "p cons", "prezzo cons", "p_cons"])
col_p_max = find_col(["massimo", "p max", "prezzo max", "p_max"])
col_pres = find_col(["presenz", "pres", "partite", "pg"])
col_gol = find_col(
    ["goal fatti", "gol fatti", "goal", "gol", "gf", "g"], exclude=["subit"]
)
col_assist = find_col(["assist", "ass", "ast", "a"])
col_subiti = find_col(["subit", "gs"])
col_clean = find_col(["clean", "cs"])
col_badge = find_col(["badge", "tag", "note"])
col_verdetto = find_col(["verdetto", "prendi o lascia", "consiglio", "decisione"])

# ==========================================
# 5. SIDEBAR: FILTRI
# ==========================================
st.sidebar.header("🔍 Filtri Asta")

# Ruolo
ruoli_disponibili = ["TUTTI"] + [
    r for r in sorted(df["RUOLO_CLEAN"].unique()) if r and r != "NAN"
]
ruolo_selezionato = st.sidebar.selectbox("Filtra Ruolo", ruoli_disponibili)

# Squadra
if col_squadra:
    squadre = ["TUTTE"] + sorted(
        list(df[col_squadra].dropna().astype(str).unique())
    )
    squadra_selezionata = st.sidebar.selectbox("Filtra Squadra", squadre)
else:
    squadra_selezionata = "TUTTE"

# Nome
ricerca_nome = st.sidebar.text_input("Cerca Giocatore:", "")

# Slot
if col_slot:
    slots = ["TUTTI"] + sorted(
        list(
            df[col_slot]
            .dropna()
            .apply(lambda x: str(int(x)) if isinstance(x, float) else str(x))
            .unique()
        )
    )
    slot_selezionato = st.sidebar.selectbox("Filtra Slot", slots)
else:
    slot_selezionato = "TUTTI"

# Verdetto
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
# 6. FILTRAGGIO DATI
# ==========================================
df_filtered = df.copy()

if ruolo_selezionato != "TUTTI":
    df_filtered = df_filtered[df_filtered["RUOLO_CLEAN"] == ruolo_selezionato]

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
        df_filtered[col_slot].astype(str).str.contains(slot_selezionato)
    ]

if verdetto_selezionato != "TUTTI" and col_verdetto:
    df_filtered = df_filtered[
        df_filtered[col_verdetto].astype(str) == verdetto_selezionato
    ]


# ==========================================
# 7. METRICHE
# ==========================================
st.subheader("📊 Panoramica Selezione")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Calciatori Filtrati", len(df_filtered))

with col2:
    if col_slot:
        top_players = len(
            df_filtered[df_filtered[col_slot].astype(str).str.startswith("1")]
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
# 8. COSTRUZIONE TABELLA FINALE
# ==========================================
st.subheader("📋 Tabella Calciatori & Consigli Asta")

# Definiamo le colonne principali
cols_to_display = []

# Mettiamo in ordine sicuro
possible_cols = [
    col_ruolo,
    col_nome,
    col_squadra,
    col_slot,
    col_p_cons,
    col_p_max,
    col_pres,
    col_gol,
    col_assist,
    col_subiti,
    col_clean,
    col_badge,
    col_verdetto,
]

for c in possible_cols:
    if c is not None and c in df_filtered.columns and c not in cols_to_display:
        cols_to_display.append(c)

# Configurazione formattazione visiva
column_configuration = {}

if col_ruolo:
    column_configuration[col_ruolo] = st.column_config.TextColumn("Ruolo")
if col_nome:
    column_configuration[col_nome] = st.column_config.TextColumn("Nome")
if col_squadra:
    column_configuration[col_squadra] = st.column_config.TextColumn("Squadra")
if col_slot:
    column_configuration[col_slot] = st.column_config.NumberColumn(
        "Slot", format="%d"
    )
if col_p_cons:
    column_configuration[col_p_cons] = st.column_config.NumberColumn(
        "Consigliato", format="%d cr"
    )
if col_p_max:
    column_configuration[col_p_max] = st.column_config.NumberColumn(
        "Massimo", format="%d cr"
    )
if col_pres:
    column_configuration[col_pres] = st.column_config.NumberColumn(
        "Presenze", format="%d"
    )
if col_gol:
    column_configuration[col_gol] = st.column_config.NumberColumn(
        "Gol ⚽", format="%d"
    )
if col_assist:
    column_configuration[col_assist] = st.column_config.NumberColumn(
        "Assist 🅰️", format="%d"
    )
if col_subiti:
    column_configuration[col_subiti] = st.column_config.NumberColumn(
        "Gol Subiti 🥊", format="%d"
    )
if col_clean:
    column_configuration[col_clean] = st.column_config.NumberColumn(
        "Clean Sheet 🧤", format="%d"
    )
if col_badge:
    column_configuration[col_badge] = st.column_config.TextColumn("Badge 🎖️")

st.dataframe(
    df_filtered[cols_to_display],
    use_container_width=True,
    hide_index=True,
    column_config=column_configuration,
)

# ==========================================
# 9. UTILITY DI DEBUG (Espandibile)
# ==========================================
with st.expander("🛠️ Strumento di Diagnostica Colonne CSV"):
    st.write("**Tutte le colonne lette dal CSV:**", list(df.columns))
    st.write("**Mappatura Riconosciuta:**")
    st.json(
        {
            "Ruolo": col_ruolo,
            "Nome": col_nome,
            "Squadra": col_squadra,
            "Slot": col_slot,
            "Prezzo Cons": col_p_cons,
            "Prezzo Max": col_p_max,
            "Presenze": col_pres,
            "Gol": col_gol,
            "Assist": col_assist,
            "Gol Subiti": col_subiti,
            "Clean Sheet": col_clean,
        }
    )

st.markdown("---")
st.caption(
    "FantaBooster® Engine v3.6 | Sviluppato per Asta Fantacalcio 2026/2027"
)
