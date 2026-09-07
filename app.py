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
# 3. FUNZIONE CARICAMENTO DATI DINAMICA
# ==========================================
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", "tutti_2027.csv")

    if not os.path.exists(file_path):
        st.error(
            f"❌ Impossibile trovare il file in '{file_path}'. Verifica che 'tutti_2027.csv' sia nella cartella 'data/'."
        )
        return pd.DataFrame()

    try:
        # Tenta la lettura con utf-8-sig e diversi separatori
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig")
            if df.shape[1] <= 1:
                df = pd.read_csv(file_path, sep=";", encoding="utf-8-sig")
        except Exception:
            df = pd.read_csv(file_path, sep=";", encoding="latin1")

        # Pulizia intestazioni (rimozione spazi extra)
        df.columns = df.columns.str.strip()

        # Funzione helper per identificare colonne indipendentemente dalla sintassi esatta
        def find_column(patterns):
            for col in df.columns:
                for pattern in patterns:
                    if pattern.lower() in col.lower():
                        return col
            return None

        # Mappatura e pulizia campi chiave
        col_ruolo = find_column(["ruolo"])
        if col_ruolo:
            df["RUOLO"] = df[col_ruolo].astype(str).str.strip().str.upper()

        # Pulizia e conversione numerica per tutte le colonne numeriche
        for col in df.columns:
            # Se la colonna contiene dati numerici o statistiche, li convertiamo pulendo eventuali caratteri extra
            if any(k in col.lower() for k in ["prezzo", "presenz", "goal", "gol", "assist", "clean", "slot"]):
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", ".").str.extract(r"(-?\d+\.?\d*)")[0],
                    errors="coerce",
                ).fillna(0)

        return df

    except Exception as e:
        st.error(f"❌ Si è verificato un errore durante la lettura del file CSV: {e}")
        return pd.DataFrame()


df = load_data()

if df.empty:
    st.warning("Caricamento dati non riuscito. Controlla il file CSV e riprova.")
    st.stop()

# ==========================================
# 4. SIDEBAR: FILTRI & CONTROLLI
# ==========================================
st.sidebar.header("🔍 Filtri Ricerca & Asta")

# 1. Filtro Ruolo
ruoli_disponibili = ["TUTTI"] + sorted([r for r in df["RUOLO"].unique() if r and r != "NAN"])
ruolo_selezionato = st.sidebar.selectbox("Seleziona Ruolo", ruoli_disponibili)

# 2. Filtro Squadra
col_squadra = next((c for c in df.columns if c.lower() in ["squadra", "nome squadra", "club", "team"]), None)
if col_squadra:
    squadre = ["TUTTE"] + sorted(list(df[col_squadra].dropna().astype(str).unique()))
    squadra_selezionata = st.sidebar.selectbox("Seleziona Squadra", squadre)
else:
    squadra_selezionata = "TUTTE"

# 3. Ricerca Nome
ricerca_nome = st.sidebar.text_input("Cerca Calciatore per Nome:", "")

# 4. Filtro Slot
col_slot = next((c for c in df.columns if "slot" in c.lower()), None)
if col_slot:
    slots = ["TUTTI"] + sorted([str(int(s)) if isinstance(s, (int, float)) and s == s else str(s) for s in df[col_slot].unique()])
    slot_selezionato = st.sidebar.selectbox("Filtra per Slot", slots)
else:
    slot_selezionato = "TUTTI"

# 5. Filtro Verdetto Algoritmo
col_verdetto = next((c for c in df.columns if "prendi o lascia" in c.lower() or "verdetto" in c.lower()), None)
if col_verdetto:
    verdetti = ["TUTTI"] + sorted(list(df[col_verdetto].dropna().astype(str).unique()))
    verdetto_selezionato = st.sidebar.selectbox("Verdetto Algoritmo 🎲", verdetti)
else:
    verdetto_selezionato = "TUTTI"

# ==========================================
# 5. APPLICAZIONE FILTRI AL DATAFRAME
# ==========================================
df_filtered = df.copy()

if ruolo_selezionato != "TUTTI":
    df_filtered = df_filtered[df_filtered["RUOLO"] == ruolo_selezionato]

if squadra_selezionata != "TUTTE" and col_squadra:
    df_filtered = df_filtered[df_filtered[col_squadra].astype(str) == squadra_selezionata]

if ricerca_nome:
    col_nome = next((c for c in df_filtered.columns if "nome" in c.lower()), None)
    if col_nome:
        df_filtered = df_filtered[df_filtered[col_nome].astype(str).str.contains(ricerca_nome, case=False, na=False)]

if slot_selezionato != "TUTTI" and col_slot:
    df_filtered = df_filtered[df_filtered[col_slot].astype(str) == slot_selezionato]

if verdetto_selezionato != "TUTTI" and col_verdetto:
    df_filtered = df_filtered[df_filtered[col_verdetto].astype(str) == verdetto_selezionato]

# ==========================================
# 6. METRICHE GENERALI E KPI
# ==========================================
st.subheader("📊 Panoramica Rosa & Asta")
col1, col2, col3, col4 = st.columns(4)

col_p_cons = next((c for c in df.columns if "consigliato" in c.lower()), None)
col_p_max = next((c for c in df.columns if "massimo" in c.lower()), None)
col_gol = next((c for c in df.columns if "goal fatti" in c.lower() or "gol fatti" in c.lower() or "goal" in c.lower()), None)

with col1:
    st.metric("Calciatori Filtrati", len(df_filtered))

with col2:
    p_cons = df_filtered[col_p_cons].sum() if col_p_cons else 0
    st.metric("Tot. Prezzi Consigliati", f"{int(p_cons)} cr")

with col3:
    p_max = df_filtered[col_p_max].sum() if col_p_max else 0
    st.metric("Tot. Prezzi Massimi", f"{int(p_max)} cr")

with col4:
    tot_gol = df_filtered[col_gol].sum() if col_gol else 0
    st.metric("Totale Gol Proiettati", int(tot_gol))

st.markdown("---")

# ==========================================
# 7. VISUALIZZAZIONE TABELLA DINAMICA
# ==========================================
st.subheader("📋 Tabella Calciatori & Consigli Asta")

# Rilevamento automatico di tutte le colonne presenti nel CSV da visualizzare
col_badge = next((c for c in df.columns if "badge" in c.lower()), None)
col_clean = next((c for c in df.columns if "clean" in c.lower()), None)
col_subiti = next((c for c in df.columns if "subit" in c.lower()), None)
col_assist = next((c for c in df.columns if "assist" in c.lower()), None)

# Costruzione intelligente delle colonne da mostrare
cols_to_display = []
for col_name in df.columns:
    # Mostriamo tutte le colonne rilevanti mantenendo l'ordine del CSV
    cols_to_display.append(col_name)

# Configurazione della visualizzazione delle colonne
column_configuration = {}
for col in cols_to_display:
    col_lower = col.lower()
    if "consigliato" in col_lower or "massimo" in col_lower:
        column_configuration[col] = st.column_config.NumberColumn(col, format="%d cr")
    elif "goal fatti" in col_lower or "gol fatti" in col_lower:
        column_configuration[col] = st.column_config.NumberColumn(col, format="%d ⚽")
    elif "assist" in col_lower:
        column_configuration[col] = st.column_config.NumberColumn(col, format="%d 🅰️")
    elif "subiti" in col_lower:
        column_configuration[col] = st.column_config.NumberColumn(col, format="%d 🥊")
    elif "clean" in col_lower:
        column_configuration[col] = st.column_config.NumberColumn(col, format="%d 🧤")
    elif "badge" in col_lower:
        column_configuration[col] = st.column_config.TextColumn("Badge 🎖️")

st.dataframe(
    df_filtered[cols_to_display],
    use_container_width=True,
    hide_index=True,
    column_config=column_configuration,
)

# Footer
st.markdown("---")
st.caption("FantaBooster® Engine v3.5 | Sviluppato per Asta Fantacalcio 2026/2027")
