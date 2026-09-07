import os
import re
import base64
import pandas as pd
import streamlit as st

# ==========================================
# 1. CONFIGURAZIONE PAGINA STREAMLIT
# ==========================================
st.set_page_config(
    page_title="FantaBooster® Engine - Pro Edition",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 2. CARICAMENTO SFONDO IN BASE64
# ==========================================
def get_base64_background():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    
    # Cerca l'immagine "Fantabooster" con qualsiasi estensione
    extensions = [".png", ".jpg", ".jpeg", ".webp"]
    bg_path = None
    
    for ext in extensions:
        temp_path = os.path.join(data_dir, f"Fantabooster{ext}")
        if os.path.exists(temp_path):
            bg_path = temp_path
            break
            
    if not bg_path:
        # Fallback nel caso il nome sia scritto in minuscolo
        for file in os.listdir(data_dir) if os.path.exists(data_dir) else []:
            if file.lower().startswith("fantabooster"):
                bg_path = os.path.join(data_dir, file)
                break

    if bg_path and os.path.exists(bg_path):
        with open(bg_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        ext = os.path.splitext(bg_path)[1].replace(".", "")
        return f"data:image/{ext};base64,{encoded_string}"
    return None

bg_base64 = get_base64_background()

# ==========================================
# 3. CSS STYLING DEDICATO (STILE FANTALAB CON SFONDO CUSTOM)
# ==========================================
bg_css_rule = f"""
    .stApp {{
        background: linear-gradient(rgba(11, 14, 20, 0.82), rgba(11, 14, 20, 0.92)), url("{bg_base64}") !important;
        background-size: cover !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
        color: #f1f5f9;
    }}
""" if bg_base64 else """
    .stApp {
        background: radial-gradient(circle at 50% 10%, #151a26 0%, #0b0e14 100%);
        color: #f1f5f9;
    }
"""

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800;900&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
    }}

    {bg_css_rule}

    /* HEADER TITOLO CON GLOW EFFECT */
    .main-title {{
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00E676 0%, #00B0FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 20px rgba(0, 230, 118, 0.3);
        margin-bottom: 0px;
        letter-spacing: -0.5px;
    }}
    
    .sub-title {{
        color: #cbd5e1;
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 25px;
    }}

    /* SIDEBAR MODERNA */
    section[data-testid="stSidebar"] {{
        background: rgba(15, 19, 28, 0.92) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 5px 0 25px rgba(0,0,0,0.5);
    }}

    /* INPUT E SELECTBOX GLOSSY */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {{
        background: rgba(22, 28, 41, 0.85) !important;
        border: 1px solid rgba(0, 230, 118, 0.35) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.4), 0 0 10px rgba(0,230,118,0.1);
        transition: all 0.3s ease;
    }}

    .stTextInput > div > div > input:focus, .stSelectbox > div > div > div:focus {{
        border-color: #00E676 !important;
        box-shadow: 0 0 15px rgba(0, 230, 118, 0.4) !important;
    }}

    /* CARDS SCHEDA CALCIATORE (GLASSMORPHISM) */
    .player-card {{
        background: rgba(19, 24, 37, 0.82);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-top: 1px solid rgba(0, 230, 118, 0.6);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255,255,255,0.1);
    }}

    /* METRICHE CUSTOM CON EFFETTO LUCIDO */
    [data-testid="stMetric"] {{
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 12px 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}

    [data-testid="stMetricLabel"] {{
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    [data-testid="stMetricValue"] {{
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1.4rem !important;
        text-shadow: 0 2px 8px rgba(0,0,0,0.8), 0 0 10px rgba(0,230,118,0.25);
    }}

    /* BADGES PREMIUM STILE FANTALAB */
    .badge-tag {{
        display: inline-block;
        background: linear-gradient(135deg, rgba(0,230,118,0.2) 0%, rgba(0,176,255,0.2) 100%);
        color: #00E676;
        border: 1px solid rgba(0, 230, 118, 0.5);
        border-radius: 20px;
        padding: 5px 14px;
        margin: 4px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.3px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        text-shadow: 0 1px 3px rgba(0,0,0,0.9);
    }}

    /* TABELLA CON TESTO BIANCO E HIGH CONTRAST */
    [data-testid="stDataFrame"] {{
        background: rgba(15, 19, 28, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        padding: 8px;
    }}

    hr {{
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, rgba(0,230,118,0) 0%, rgba(0,230,118,0.5) 50%, rgba(0,230,118,0) 100%);
        margin: 25px 0;
    }}
    </style>
""",
    unsafe_allow_html=True,
)

# Header Principale
st.markdown('<div class="main-title">⚽ FantaBooster® Engine v6.1</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Listone Asta Ordinato per Valore Crediti — Delio Palma</div>', unsafe_allow_html=True)
st.markdown("---")


# ==========================================
# 4. LETTURA CSV E TRATTAMENTO POSIZIONALE
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

        # Memorizza l'indice originale per tracciare i portieri
        df["ORIGINAL_ROW_INDEX"] = df.index + 1

        # Mappatura della Colonna A (Indice 0) come Ruolo Pulito
        col_ruolo_raw = df.columns[0]
        df["RUOLO_CLEAN"] = df[col_ruolo_raw].astype(str).str.strip().str.upper()

        return df

    except Exception as e:
        st.error(f"❌ Errore lettura CSV: {e}")
        return pd.DataFrame()


df = load_data()

if df.empty:
    st.stop()


# ==========================================
# 5. PARSER E INDIVIDUAZIONE COLONNE
# ==========================================
def parse_num(val):
    if pd.isna(val):
        return 0
    val_str = str(val).strip()
    match = re.search(r"\d+", val_str)
    if match:
        try:
            return int(match.group())
        except ValueError:
            return 0
    return 0


def get_col_by_index_or_name(index, keywords, exclude=None):
    if exclude is None:
        exclude = []
    for c in df.columns:
        if c in ["RUOLO_CLEAN", "ORIGINAL_ROW_INDEX"]:
            continue
        c_low = c.lower()
        if any(ex in c_low for ex in exclude):
            continue
        if any(kw in c_low for kw in keywords):
            return c
    if index < len(df.columns):
        return df.columns[index]
    return None


col_ruolo = df.columns[0]  # Colonna A
col_nome = get_col_by_index_or_name(1, ["nome", "calciatore", "giocatore", "player"])
col_squadra = get_col_by_index_or_name(2, ["squadra", "club", "team"])
col_slot = get_col_by_index_or_name(3, ["slot"])

col_p_cons = get_col_by_index_or_name(4, ["prezzo consigliato", "p_cons", "p.cons", "consigliato"])
col_p_max = get_col_by_index_or_name(5, ["prezzo massimo", "prezzo max", "p_max", "p.max", "massimo"])
col_pres = get_col_by_index_or_name(6, ["presenze", "presenz", "pres", "partite", "pg"])

col_gol = get_col_by_index_or_name(7, ["goal", "gol", "gf"], exclude=["subiti", "prezzo", "max", "consigliato"])
col_assist = get_col_by_index_or_name(8, ["assist", "ast"], exclude=["max", "massimo", "prezzo", "consigliato", "costo", "crediti", "asta", "slot"])

col_subiti = get_col_by_index_or_name(9, ["subiti", "gs"])
col_clean = get_col_by_index_or_name(10, ["clean", "cs"])
col_badge = get_col_by_index_or_name(11, ["badge", "tag", "caratteristiche", "note"])
col_verdetto = get_col_by_index_or_name(12, ["verdetto", "consiglio"])


# ==========================================
# 6. SIDEBAR: FILTRI E RICERCA DINAMICA
# ==========================================
st.sidebar.markdown("### 🔍 Centro di Ricerca")

ricerca_nome = st.sidebar.text_input("🔎 Cerca Calciatore:", "", placeholder="Es. Lautaro, Dybala...")

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
    slots_disponibili = ["TUTTI", "1", "2", "3", "4", "5", "6", "7", "8"]
    slot_selezionato = st.sidebar.selectbox("Filtra per Slot", slots_disponibili)
else:
    slot_selezionato = "TUTTI"

if col_verdetto:
    verdetti = ["TUTTI"] + sorted(list(df[col_verdetto].dropna().astype(str).unique()))
    verdetto_selezionato = st.sidebar.selectbox("Filtra per Verdetto", verdetti)
else:
    verdetto_selezionato = "TUTTI"


# ==========================================
# 7. APPLICAZIONE FILTRI & ORDINAMENTO
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
    def match_slot(val):
        if pd.isna(val):
            return False
        val_str = str(val).lower()
        numbers = re.findall(r"\d+", val_str)
        return slot_selezionato in numbers

    df_filtered = df_filtered[df_filtered[col_slot].apply(match_slot)]

if verdetto_selezionato != "TUTTI" and col_verdetto:
    df_filtered = df_filtered[df_filtered[col_verdetto].astype(str) == verdetto_selezionato]

# Ordina per prezzo consigliato
sort_col = col_p_cons if col_p_cons else (col_p_max if col_p_max else df_filtered.columns[0])
df_filtered["SORT_VAL"] = df_filtered[sort_col].apply(parse_num) if sort_col else 0
df_filtered = df_filtered.sort_values(by="SORT_VAL", ascending=False)


# ==========================================
# 8. SCHEDA DETTAGLIO RICERCA DYNAMIC GLOSSY
# ==========================================
if ricerca_nome and not df_filtered.empty:
    st.markdown("### 👤 Schede Calciatori Trovati")

    for _, player in df_filtered.head(3).iterrows():
        row_num = player["ORIGINAL_ROW_INDEX"]
        p_nome = player[col_nome] if col_nome else "N/A"
        p_ruolo = player["RUOLO_CLEAN"]
        p_squadra = str(player[col_squadra]).strip() if col_squadra and pd.notna(player[col_squadra]) else "N/A"

        p_cons = parse_num(player[col_p_cons]) if col_p_cons else 0
        p_max = parse_num(player[col_p_max]) if col_p_max else 0
        p_pres = parse_num(player[col_pres]) if col_pres else 0

        val_gol = str(player[col_gol]).strip() if col_gol and pd.notna(player[col_gol]) else "0"
        val_ast = str(player[col_assist]).strip() if col_assist and pd.notna(player[col_assist]) else "0"

        p_subiti = parse_num(player[col_subiti]) if col_subiti else 0
        p_clean = parse_num(player[col_clean]) if col_clean else 0

        st.markdown('<div class="player-card">', unsafe_allow_html=True)
        st.markdown(f"### **{p_nome}** <span style='color: #00E676; font-size: 1.1rem;'>({p_ruolo} - {p_squadra})</span>", unsafe_allow_html=True)

        if row_num <= 62 or p_ruolo == "P":
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
            c4.metric("Goal (2025/2026) ⚽", val_gol)
            c5.metric("Assist (2025/2026) 🅰️", val_ast)

        if col_badge and pd.notna(player[col_badge]):
            raw_badges = str(player[col_badge]).strip()
            if raw_badges and raw_badges.lower() != "nan":
                badge_list = [b.strip() for b in re.split(r"[,;|/\n]+", raw_badges) if b.strip()]
                if badge_list:
                    badge_html = " ".join([f'<span class="badge-tag">🎖️ {b}</span>' for b in badge_list])
                    st.markdown(f"<div style='margin-top: 15px;'>{badge_html}</div>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

# ==========================================
# 9. TABELLA GENERALE HIGH CONTRAST
# ==========================================
st.markdown("### 📋 Listone Calciatori (Ordinato per Crediti)")

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
    column_configuration[col_slot] = st.column_config.TextColumn("Slot")
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
