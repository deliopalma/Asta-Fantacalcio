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
# 2. CSS CUSTOM TEMA DARK
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
    .badge-tag {
        display: inline-block;
        background-color: #1e222d;
        color: #00E676;
        border: 1px solid #00E676;
        border-radius: 12px;
        padding: 4px 12px;
        margin: 3px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("⚽ FantaBooster® Engine v4.3")
st.caption("Listone Asta Ordinato per Valore Crediti — Delio Palma")
st.markdown("---")


# ==========================================
# 3. LETTURA CSV
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

        # Pulizia nomi colonne
        df.columns = df.columns.astype(str).str.strip()

        # Normalizzazione Ruolo
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


# ==========================================
# 4. MAPPATURA ROBUSTA DELLE COLONNE
# ==========================================
def extract_num(val):
    """Estrae un numero intero da qualsiasi formato."""
    if pd.isna(val):
        return 0
    val_str = str(val).replace(",", ".").strip()
    match = re.search(r"\d+(\.\d+)?", val_str)
    if match:
        try:
            return int(float(match.group()))
        except ValueError:
            return 0
    return 0


def find_column(patterns, exclude_patterns=None):
    """Cerca la colonna nel dataframe confrontando le stringhe pulite."""
    if exclude_patterns is None:
        exclude_patterns = []

    # 1. Match Esatto
    for col in df.columns:
        if col == "RUOLO_CLEAN":
            continue
        col_clean = col.lower().strip()
        if any(ex in col_clean for ex in exclude_patterns):
            continue
        for p in patterns:
            if col_clean == p.lower().strip():
                return col

    # 2. Match Parziale
    for col in df.columns:
        if col == "RUOLO_CLEAN":
            continue
        col_clean = col.lower().strip()
        if any(ex in col_clean for ex in exclude_patterns):
            continue
        for p in patterns:
            if p.lower().strip() in col_clean:
                return col

    return None


col_ruolo = find_column(["ruolo", "r"])
col_nome = find_column(["nome", "calciatore", "giocatore", "player"])
col_squadra = find_column(["squadra", "club", "team"])
col_slot = find_column(["slot"])

col_p_cons = find_column(["prezzo consigliato", "p_cons", "p.cons", "consigliato"])
col_p_max = find_column(["prezzo massimo", "prezzo max", "p_max", "p.max", "massimo"])

col_pres = find_column(["presenze", "presenz", "pres", "partite", "pg"])

# Gol fatti (esclude i gol subiti)
col_gol = find_column(
    ["goal fatti", "gol fatti", "goal", "gol", "gf"],
    exclude_patterns=["subit", "prezzo", "consigliato", "max", "massimo"],
)

# Assist: ricerca mirata ed esplicita per evitare conflitti con prezzi e presenze
col_assist = find_column(
    ["assist fatti", "assist", "ast", "ass", "a"],
    exclude_patterns=["max", "massimo", "prezzo", "consigliato", "presenz", "ruolo"],
)

col_subiti = find_column(["goal subiti", "gol subiti", "subiti", "gs"])
col_clean = find_column(["clean sheet", "cleansheet", "clean", "cs"])
col_badge = find_column(["badge", "badges", "tag", "tags", "note", "caratteristiche"])
col_verdetto = find_column(["verdetto", "prendi o lascia", "consiglio"])


# ==========================================
# 5. SIDEBAR: FILTRI E RICERCA
# ==========================================
st.sidebar.header("🔍 Ricerca e Filtri")

ricerca_nome = st.sidebar.text_input("🔎 Cerca per Nome:", "")

ruoli_disponibili = ["TUTTI"] + [
    r for r in sorted(df["RUOLO_CLEAN"].unique()) if r and r != "NAN"
]
ruolo_selezionato = st.sidebar.selectbox("Filtra per Ruolo", ruoli_disponibili)

if col_squadra:
    squadre = ["TUTTE"] + sorted(list(df[col_squadra].dropna().astype(str).unique()))
    squadra_selezionata = st.sidebar.selectbox("Filtra per Squadra", squadre)
else:
    squadra_selezionata = "TUTTE"

if col_slot:
    slots = ["TUTTI"] + sorted(
        list(
            df[col_slot]
            .dropna()
            .apply(lambda x: str(int(extract_num(x))) if str(x).strip() != "" else str(x))
            .unique()
        )
    )
    slot_selezionato = st.sidebar.selectbox("Filtra per Slot", slots)
else:
    slot_selezionato = "TUTTI"

if col_verdetto:
    verdetti = ["TUTTI"] + sorted(list(df[col_verdetto].dropna().astype(str).unique()))
    verdetto_selezionato = st.sidebar.selectbox("Filtra per Verdetto", verdetti)
else:
    verdetto_selezionato = "TUTTI"


# ==========================================
# 6. APPLICAZIONE FILTRI & ORDINAMENTO
# ==========================================
df_filtered = df.copy()

if ricerca_nome and col_nome:
    df_filtered = df_filtered[
        df_filtered[col_nome].astype(str).str.contains(ricerca_nome, case=False, na=False)
    ]

if ruolo_selezionato != "TUTTI":
    df_filtered = df_filtered[df_filtered["RUOLO_CLEAN"] == ruolo_selezionato]

if squadra_selezionata != "TUTTE" and col_squadra:
    df_filtered = df_filtered[df_filtered[col_squadra].astype(str) == squadra_selezionata]

if slot_selezionato != "TUTTI" and col_slot:
    df_filtered = df_filtered[df_filtered[col_slot].astype(str).str.contains(slot_selezionato)]

if verdetto_selezionato != "TUTTI" and col_verdetto:
    df_filtered = df_filtered[df_filtered[col_verdetto].astype(str) == verdetto_selezionato]

# Ordina dal più costoso al meno costoso
sort_col = col_p_cons if col_p_cons else (col_p_max if col_p_max else df_filtered.columns[0])
df_filtered["SORT_VAL"] = df_filtered[sort_col].apply(extract_num) if sort_col else 0
df_filtered = df_filtered.sort_values(by="SORT_VAL", ascending=False)


# ==========================================
# 7. SCHEDA DETTAGLIO RICERCA
# ==========================================
if ricerca_nome and not df_filtered.empty:
    st.subheader("👤 Scheda Dettagliata Calciatore")

    for _, player in df_filtered.head(3).iterrows():
        p_nome = player[col_nome] if col_nome else "N/A"
        p_ruolo = player["RUOLO_CLEAN"]
        p_squadra = str(player[col_squadra]).strip() if col_squadra and pd.notna(player[col_squadra]) else "N/A"

        p_cons = extract_num(player[col_p_cons]) if col_p_cons else 0
        p_max = extract_num(player[col_p_max]) if col_p_max else 0
        p_pres = extract_num(player[col_pres]) if col_pres else 0
        p_gol = extract_num(player[col_gol]) if col_gol else 0
        p_assist = extract_num(player[col_assist]) if col_assist else 0
        p_subiti = extract_num(player[col_subiti]) if col_subiti else 0
        p_clean = extract_num(player[col_clean]) if col_clean else 0

        with st.container():
            st.markdown(f"### **{p_nome}** ({p_ruolo} - {p_squadra})")

            # Layout Metriche
            if p_ruolo == "P":
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Prezzo Consigliato", f"{p_cons} cr")
                c2.metric("Prezzo Max", f"{p_max} cr")
                c3.metric("Presenze", p_pres)
                c4.metric("Goal Subiti 🥊", p_subiti)
                c5.metric("Clean Sheet 🧤", p_clean)
            else:
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Prezzo Consigliato", f"{p_cons} cr")
                c2.metric("Prezzo Max", f"{p_max} cr")
                c3.metric("Presenze", p_pres)
                c4.metric("Goal (2025/2026) ⚽", p_gol)
                c5.metric("Assist (2025/2026) 🅰️", p_assist)

            # Gestione Badges
            if col_badge and pd.notna(player[col_badge]):
                raw_badges = str(player[col_badge]).strip()
                if raw_badges and raw_badges.lower() != "nan":
                    badge_list = [b.strip() for b in re.split(r"[,;|/\n]+", raw_badges) if b.strip()]
                    if badge_list:
                        badge_html = " ".join([f'<span class="badge-tag">🎖️ {b}</span>' for b in badge_list])
                        st.markdown(f"**Badges:** {badge_html}", unsafe_allow_html=True)

            # Strumento per verificare il nome della colonna assist abbinata
            with st.expander("🔎 Dettaglio Mappatura Assist e Statistiche"):
                st.write({
                    "Colonna Assist identificata": col_assist,
                    "Valore Assist estratto": p_assist,
                    "Tutte le colonne nel CSV": list(df.columns),
                })

            st.markdown("---")

# ==========================================
# 8. TABELLA GENERALE ORDINATA
# ==========================================
st.subheader("📋 Listone Calciatori (Ordinato per Crediti)")

cols_to_display = []
possible_cols = [
    col_ruolo,
    col_nome,
    col_squadra,
    col_slot,
    col_p_cons,
    col_p_max,
    col_verdetto,
]

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
    column_configuration[col_slot] = st.column_config.NumberColumn("Slot", format="%d")
if col_p_cons:
    column_configuration[col_p_cons] = st.column_config.NumberColumn("Prezzo Consigliato", format="%d cr")
if col_p_max:
    column_configuration[col_p_max] = st.column_config.NumberColumn("Prezzo Max", format="%d cr")
if col_verdetto:
    column_configuration[col_verdetto] = st.column_config.TextColumn("Verdetto")

st.dataframe(
    df_filtered[cols_to_display],
    use_container_width=True,
    hide_index=True,
    column_config=column_configuration,
)
