import os
import re
import pandas as pd
import streamlit as st

# ==========================================
# 1. CONFIGURAZIONE PAGINA STREAMLIT
# ==========================================
st.set_page_config(
    page_title="FantaBooster® Engine",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 2. CSS PERSONALIZZATO (DARK & PULITO)
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
        margin-bottom: 0px;
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

st.title("⚽ FantaBooster® Engine")
st.caption("Listone Asta Ordinato per Valore Crediti — Delio Palma")
st.markdown("---")


# ==========================================
# 3. LETTURA DATI
# ==========================================
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", "tutti_2027.csv")

    if not os.path.exists(file_path):
        st.error(f"❌ Impossibile trovare il file in '{file_path}'.")
        return pd.DataFrame()

    try:
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig")
            if df.shape[1] <= 1:
                df = pd.read_csv(file_path, sep=";", encoding="utf-8-sig")
        except Exception:
            try:
                df = pd.read_csv(file_path, sep=";", encoding="latin1")
            except Exception:
                df = pd.read_csv(file_path, sep=",", encoding="latin1")

        df.columns = df.columns.astype(str).str.strip()

        # Funzione pulizia numeri
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
                ]
            ):
                df[col] = df[col].apply(clean_val)

        col_r = next((c for c in df.columns if "ruolo" in c.lower()), None)
        if col_r:
            df["RUOLO_CLEAN"] = df[col_r].astype(str).str.strip().str.upper()
        else:
            df["RUOLO_CLEAN"] = ""

        return df

    except Exception as e:
        st.error(f"❌ Errore lettura CSV: {e}")
        return pd.DataFrame()


df = load_data()

if df.empty:
    st.stop()


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
    ["goal fatti", "gol fatti", "goal", "gol", "gf"], exclude=["subit"]
)
col_assist = find_col(["assist", "ass", "ast"])
col_badge = find_col(["badge", "tag", "note"])
col_verdetto = find_col(["verdetto", "prendi o lascia", "consiglio"])

# ==========================================
# 4. FILTRI SIDEBAR
# ==========================================
st.sidebar.header("🔍 Ricerca e Filtri")

ricerca_nome = st.sidebar.text_input("🔎 Cerca per Nome:", "")

ruoli_disponibili = ["TUTTI"] + [
    r for r in sorted(df["RUOLO_CLEAN"].unique()) if r and r != "NAN"
]
ruolo_selezionato = st.sidebar.selectbox("Filtra per Ruolo", ruoli_disponibili)

if col_squadra:
    squadre = ["TUTTE"] + sorted(
        list(df[col_squadra].dropna().astype(str).unique())
    )
    squadra_selezionata = st.sidebar.selectbox("Filtra per Squadra", squadre)
else:
    squadra_selezionata = "TUTTE"

if col_slot:
    slots = ["TUTTI"] + sorted(
        list(
            df[col_slot]
            .dropna()
            .apply(lambda x: str(int(x)) if isinstance(x, float) else str(x))
            .unique()
        )
    )
    slot_selezionato = st.sidebar.selectbox("Filtra per Slot", slots)
else:
    slot_selezionato = "TUTTI"

if col_verdetto:
    verdetti = ["TUTTI"] + sorted(
        list(df[col_verdetto].dropna().astype(str).unique())
    )
    verdetto_selezionato = st.sidebar.selectbox("Filtra per Verdetto", verdetti)
else:
    verdetto_selezionato = "TUTTI"

# ==========================================
# 5. APPLICAZIONE FILTRI
# ==========================================
df_filtered = df.copy()

if ricerca_nome and col_nome:
    df_filtered = df_filtered[
        df_filtered[col_nome]
        .astype(str)
        .str.contains(ricerca_nome, case=False, na=False)
    ]

if ruolo_selezionato != "TUTTI":
    df_filtered = df_filtered[df_filtered["RUOLO_CLEAN"] == ruolo_selezionato]

if squadra_selezionata != "TUTTE" and col_squadra:
    df_filtered = df_filtered[
        df_filtered[col_squadra].astype(str) == squadra_selezionata
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
# 6. ORDINAMENTO PER PREZZO (DAL PIÙ COSTOSO)
# ==========================================
sort_col = (
    col_p_cons
    if col_p_cons
    else (col_p_max if col_p_max else df_filtered.columns[0])
)
df_filtered = df_filtered.sort_values(by=sort_col, ascending=False)

# ==========================================
# 7. TABELLA PRINCIPALE
# ==========================================
cols_to_display = []
possible_cols = [
    col_ruolo,
    col_nome,
    col_squadra,
    col_slot,
    col_p_cons,
    col_p_max,
    col_badge,
    col_verdetto,
]

# Aggiungiamo le statistiche storiche solo se è attivo un filtro specifico (es. ricerca nome o ruolo)
if ricerca_nome or ruolo_selezionato != "TUTTI":
    possible_cols.extend([col_pres, col_gol, col_assist])

for c in possible_cols:
    if c is not None and c in df_filtered.columns and c not in cols_to_display:
        cols_to_display.append(c)

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
        "Prezzo Consigliato", format="%d cr"
    )
if col_p_max:
    column_configuration[col_p_max] = st.column_config.NumberColumn(
        "Prezzo Max", format="%d cr"
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
if col_badge:
    column_configuration[col_badge] = st.column_config.TextColumn("Badge 🎖️")

st.dataframe(
    df_filtered[cols_to_display],
    use_container_width=True,
    hide_index=True,
    column_config=column_configuration,
)
