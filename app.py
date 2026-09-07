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

st.title("⚽ FantaBooster® Engine v3.8")
st.caption("Listone Asta Ordinato per Valore Crediti — Delio Palma")
st.markdown("---")


# ==========================================
# 3. LETTURA & PARSING ROBUSTO CSV
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
# 4. FUNZIONI ESTRAZIONE VALORI & COLONNE
# ==========================================
def extract_num(val):
    """Estrae un intero valido da qualsiasi formato di stringa/numero."""
    if pd.isna(val):
        return 0
    val_str = str(val).replace(",", ".").strip()
    match = re.search(r"\d+", val_str)
    if match:
        try:
            return int(match.group())
        except ValueError:
            return 0
    return 0


def find_col(keywords, exclude=None):
    """Cerca la colonna più idonea in base alle parole chiave."""
    for kw in keywords:
        for c in df.columns:
            if c == "RUOLO_CLEAN":
                continue
            c_clean = c.lower().replace("_", " ").replace("-", " ")
            if kw in c_clean:
                if exclude and any(ex in c_clean for ex in exclude):
                    continue
                return c
    return None


col_ruolo = find_col(["ruolo", "role", "r"])
col_nome = find_col(["nome", "calciatore", "giocatore", "player"])
col_squadra = find_col(["squadra", "club", "team"])
col_slot = find_col(["slot"])

col_p_cons = find_col(["consigliato", "prezzo cons", "p_cons", "prezzo consigliato"])
col_p_max = find_col(["massimo", "prezzo max", "p_max", "prezzo massimo"], exclude=["consigliato"])

col_pres = find_col(["presenz", "pres", "partite", "pg"])
col_gol = find_col(["goal", "gol", "gf", "g"], exclude=["subit", "prezzo", "consigliato", "max"])
col_assist = find_col(["assist", "ass", "ast", "a"], exclude=["prezzo", "max", "consigliato", "presenz"])
col_subiti = find_col(["subit", "gs", "goal subiti", "gol subiti"])
col_clean = find_col(["clean", "cs", "sheet"])
col_badge = find_col(["badge", "tag", "note"])
col_verdetto = find_col(["verdetto", "prendi o lascia", "consiglio"])


# Applichiamo la pulizia numerica a tutte le colonne statistiche
numeric_cols = [col_p_cons, col_p_max, col_pres, col_gol, col_assist, col_subiti, col_clean]
for col in numeric_cols:
    if col and col in df.columns:
        df[col] = df[col].apply(extract_num)


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
            .apply(lambda x: str(int(x)) if isinstance(x, float) else str(x))
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
df_filtered = df_filtered.sort_values(by=sort_col, ascending=False)


# ==========================================
# 7. SCHEDA DETTAGLIO RICERCA
# ==========================================
if ricerca_nome and not df_filtered.empty:
    st.subheader("👤 Scheda Dettagliata Calciatore")

    for _, player in df_filtered.head(3).iterrows():
        p_nome = player[col_nome] if col_nome else "N/A"
        p_ruolo = player["RUOLO_CLEAN"]
        p_squadra = player[col_squadra] if col_squadra else "N/A"
        p_cons = player[col_p_cons] if col_p_cons else 0
        p_max = player[col_p_max] if col_p_max else 0
        p_pres = player[col_pres] if col_pres else 0
        p_gol = player[col_gol] if col_gol else 0
        p_assist = player[col_assist] if col_assist else 0
        p_subiti = player[col_subiti] if col_subiti else 0
        p_clean = player[col_clean] if col_clean else 0

        with st.container():
            st.markdown(f"### **{p_nome}** ({p_ruolo} - {p_squadra})")

            # Layout Metriche in base al ruolo
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
                c4.metric("Goal Fatti ⚽", p_gol)
                c5.metric("Assist 🅰️", p_assist)

            # Gestione Badges Singoli
            if col_badge and pd.notna(player[col_badge]):
                raw_badges = str(player[col_badge])
                badge_list = [b.strip() for b in re.split(r"[,;|/\n]+", raw_badges) if b.strip()]
                if badge_list:
                    badge_html = " ".join([f'<span class="badge-tag">🎖️ {b}</span>' for b in badge_list])
                    st.markdown(f"**Badges:** {badge_html}", unsafe_allow_html=True)

            # Debug rapido (espandibile se serve verificare le colonne trovate)
            with st.expander("🔎 Verifica Valori Colonne CSV"):
                st.write({
                    "Colonna Gol Riconosciuta": col_gol,
                    "Valore Gol": p_gol,
                    "Colonna Assist Riconosciuta": col_assist,
                    "Valore Assist": p_assist,
                    "Colonna Presenze Riconosciuta": col_pres,
                    "Valore Presenze": p_pres
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
