import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------------------------------------------------------
# CONFIGURAZIONE PAGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="FantaBooster® by Delio", 
    page_icon="⚽", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# DESIGN SYSTEM: BLU SCURO DEEP + HIGH CONTRAST + BADGES
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    /* Sfondo Principale Blu Scuro Profondo */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #172554 0%, #0f172a 50%, #020617 100%);
        color: #f8fafc;
    }

    /* Sidebar Glassmorphism */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.12);
    }

    /* Titoli generali con alto contrasto */
    h1, h2, h3, h4, h5, h6, label, p {
        color: #f8fafc !important;
        text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.8);
    }

    /* Banner Principale Brandizzato */
    .brand-banner {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
        border: 1px solid rgba(59, 130, 246, 0.5);
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.7), inset 0 1px 1px rgba(255, 255, 255, 0.3);
        position: relative;
        overflow: hidden;
    }

    .brand-title {
        font-size: 2.4rem;
        font-weight: 900;
        letter-spacing: -0.5px;
        background: linear-gradient(180deg, #ffffff 0%, #e2e8f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .brand-subtitle {
        font-size: 1.05rem;
        color: #cbd5e1;
        margin-top: 6px;
        font-weight: 500;
    }

    .signature-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.3) 0%, rgba(37, 99, 235, 0.2) 100%);
        border: 1px solid rgba(96, 165, 250, 0.6);
        color: #bfdbfe;
        padding: 5px 14px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-top: 14px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.2);
    }

    /* Metric Card Lucide */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-top: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 12px 24px -6px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.15);
    }

    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* Contenitore dei Badges */
    .badge-container {
        display: flex;
        gap: 10px;
        margin-top: 10px;
        flex-wrap: wrap;
    }

    .badge-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 8px 14px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.88rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        border-top: 1px solid rgba(255, 255, 255, 0.3);
    }

    .badge-rigorista { background: rgba(16, 185, 129, 0.25); border: 1px solid #34d399; color: #a7f3d0; }
    .badge-piazzati { background: rgba(14, 165, 233, 0.25); border: 1px solid #38bdf8; color: #bae6fd; }
    .badge-stakanovista { background: rgba(234, 179, 8, 0.25); border: 1px solid #facc15; color: #fef08a; }
    .badge-cittone { background: rgba(245, 158, 11, 0.25); border: 1px solid #fbbf24; color: #fde68a; }
    .badge-macellaio { background: rgba(239, 68, 68, 0.25); border: 1px solid #f87171; color: #fca5a5; }
    .badge-assist { background: rgba(168, 85, 247, 0.25); border: 1px solid #c084fc; color: #e9d5ff; }
    .badge-bomber { background: rgba(236, 72, 153, 0.25); border: 1px solid #f472b6; color: #fbcfe8; }
    .badge-off { background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); color: #94a3b8; }

    /* Tab Evidenziate */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.8);
        padding: 8px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(147, 197, 253, 0.5) !important;
    }

    .footer-delio {
        text-align: center;
        padding: 24px;
        margin-top: 50px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        color: #94a3b8;
        font-size: 0.88rem;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CARICAMENTO DATI ED ELABORAZIONE BADGE DAL FILE EXCEL
# -----------------------------------------------------------------------------
@st.cache_data
def carica_e_calcola_modello():
    try:
        df = pd.read_excel('Tutti_2027.xlsx', sheet_name=0, engine='openpyxl')
        df.columns = [str(col).strip() for col in df.columns]

        cols_lower = {str(col).lower(): col for col in df.columns}
        
        # Mappatura Nome Giocatore
        col_nome = next((cols_lower[k] for k in ['nome', 'giocatore', 'calciatore', 'player', 'cognome'] if k in cols_lower), None)
        df['nome_completo'] = df[col_nome].astype(str) if col_nome else df.iloc[:, 0].astype(str)
        df = df[df['nome_completo'].str.len() > 1].copy()

        # Squadra e Ruolo
        col_sq = next((cols_lower[k] for k in ['squadra', 'team', 'sq'] if k in cols_lower), None)
        col_ruolo = next((cols_lower[k] for k in ['ruolo', 'role', 'r'] if k in cols_lower), None)
        df['Squadra'] = df[col_sq].astype(str) if col_sq else 'N/D'
        
        def normalizza_ruolo(r):
            r = str(r).upper().strip()
            if 'POR' in r or 'P' in r: return 'P'
            if 'DIF' in r or 'D' in r: return 'D'
            if 'CEN' in r or 'C' in r: return 'C'
            return 'A'

        df['Ruolo'] = df[col_ruolo].apply(normalizza_ruolo) if col_ruolo else 'A'

        # Specialisti Palle Inattive da Excel
        col_rig = next((cols_lower[k] for k in ['rigorista', 'rigori', 'rig', 'rigori tirati'] if k in cols_lower), None)
        col_piaz = next((cols_lower[k] for k in ['punizioni', 'piazzati', 'angoli', 'cp', 'calci piazzati'] if k in cols_lower), None)
        
        df['Is_Rigorista'] = df[col_rig].astype(str).str.lower().str.contains('si|1|vero|true|prima|primo|titolare') if col_rig else False
        df['Is_Piazzati'] = df[col_piaz].astype(str).str.lower().str.contains('si|1|vero|true|angoli|punizioni') if col_piaz else False

        # Statistiche per Badge da Excel
        col_gol = next((cols_lower[k] for k in ['gol', 'goals', 'reti', 'g', 'gf', 'gol fatti'] if k in cols_lower), None)
        col_assist = next((cols_lower[k] for k in ['assist', 'a', 'ast', 'ass'] if k in cols_lower), None)
        col_pres = next((cols_lower[k] for k in ['presenze', 'partite', 'pg', 'p', 'pres'] if k in cols_lower), None)
        col_amm = next((cols_lower[k] for k in ['amm', 'ammonizioni', 'gialli', 'ammonizione', 'am'] if k in cols_lower), None)
        col_esp = next((cols_lower[k] for k in ['esp', 'espulsioni', 'rossi', 'espulsione', 'es'] if k in cols_lower), None)

        gol_val = pd.to_numeric(df[col_gol], errors='coerce').fillna(0) if col_gol else pd.Series(0, index=df.index)
        assist_val = pd.to_numeric(df[col_assist], errors='coerce').fillna(0) if col_assist else pd.Series(0, index=df.index)
        pres_val = pd.to_numeric(df[col_pres], errors='coerce').fillna(0) if col_pres else pd.Series(0, index=df.index)
        amm_val = pd.to_numeric(df[col_amm], errors='coerce').fillna(0) if col_amm else pd.Series(0, index=df.index)
        esp_val = pd.to_numeric(df[col_esp], errors='coerce').fillna(0) if col_esp else pd.Series(0, index=df.index)

        # Calcolo dei Badge da Dati Excel
        df['is_stakanovista'] = pres_val >= 28
        df['is_cittone'] = amm_val >= 6
        df['is_macellaio'] = esp_val >= 2
        df['is_assistman'] = assist_val >= 5
        
        ratio_gol = np.where(pres_val > 0, gol_val / pres_val, 0)
        df['is_bomber'] = ratio_gol >= 0.27

        # ---------------------------------------------------------------------
        # REGOLE DI BACKUP SMART PER I TOP PLAYER SE I DATI MANCANO NEL FILE EXCEL
        # ---------------------------------------------------------------------
        rigoristi_top = ['calhanoglu', 'dybala', 'martinez l', 'lautaro', 'koopmeiners', 'retegui', 'vlahovic', 'orsolini', 'lukaku', 'gudmundsson', 'pulisic', 'berardi', 'pinamonti']
        piazzati_top = ['calhanoglu', 'dybala', 'dimarco', 'pulisic', 'koopmeiners', 'pellegrini', 'gudmundsson', 'zaccagni', 'berardi', 'politano', 'mkhitaryan']
        bomber_top = ['martinez l', 'lautaro', 'vlahovic', 'dybala', 'calhanoglu', 'thuram', 'retgui', 'lookman', 'gimenez', 'lukaku', 'zapata', 'pulisic', 'kean']
        assist_top = ['dimarco', 'pulisic', 'dybala', 'leao', 'lookman', 'calhanoglu', 'mkhitaryan', 'koopmeiners', 'tchaouna', 'saelemaekers']

        for idx, row in df.iterrows():
            nome_clean = str(row['nome_completo']).lower()

            if any(k in nome_clean for k in rigoristi_top):
                df.at[idx, 'Is_Rigorista'] = True
            if any(k in nome_clean for k in piazzati_top):
                df.at[idx, 'Is_Piazzati'] = True
            if any(k in nome_clean for k in bomber_top):
                df.at[idx, 'is_bomber'] = True
            if any(k in nome_clean for k in assist_top):
                df.at[idx, 'is_assistman'] = True

        # Generazione stringa sintetica badge per la vista a tabelle
        def genera_str_badge(row):
            b = []
            if row['Is_Rigorista']: b.append("🎯 Rigorista")
            if row['Is_Piazzati']: b.append("📐 Piazzati")
            if row['is_stakanovista']: b.append("🏋️‍♂️ Stakanovista")
            if row['is_cittone']: b.append("🟨 Cittone")
            if row['is_macellaio']: b.append("🟥 Macellaio")
            if row['is_assistman']: b.append("⚽⭐ Assist-man")
            if row['is_bomber']: b.append("💣 Bomber")
            return " | ".join(b) if b else "-"

        # FantaScore con pesi e bonus
        bonus_rigore = np.where(df['Is_Rigorista'], 15, 0)
        bonus_piazzati = np.where(df['Is_Piazzati'], 8, 0)
        df['fanta_score'] = (gol_val * 4.0) + (assist_val * 1.5) + (pres_val * 0.3) + bonus_rigore + bonus_piazzati

        if df['fanta_score'].max() == 0 or df['fanta_score'].nunique() <= 1:
            df['fanta_score'] = np.linspace(100, 5, len(df))

        # Pricing Calibrato (12.000 Crediti Totali)
        budgets = {'P': 960, 'D': 2040, 'C': 4200, 'A': 4800}
        slots_count = {'P': 36, 'D': 96, 'C': 96, 'A': 72}
        gamma_power = {'A': 3.8, 'C': 3.2, 'D': 2.5, 'P': 2.2}

        elenco_finali = []
        for r in ['P', 'D', 'C', 'A']:
            sub = df[df['Ruolo'] == r].sort_values(by='fanta_score', ascending=False).reset_index(drop=True)
            if len(sub) == 0:
                continue
            
            top_n = sub.head(min(slots_count[r], len(sub))).copy()
            scores = top_n['fanta_score']
            
            min_s, max_s = scores.min(), scores.max()
            scores_norm = (scores - min_s) / (max_s - min_s) + 0.05 if max_s > min_s else np.ones(len(scores))

            exp_scores = np.power(scores_norm, gamma_power[r])
            sum_exp = exp_scores.sum()

            if sum_exp > 0:
                top_n['prezzo_consigliato'] = np.round((exp_scores / sum_exp) * budgets[r]).astype(int)
                top_n['prezzo_consigliato'] = np.maximum(1, top_n['prezzo_consigliato'])
            else:
                top_n['prezzo_consigliato'] = 1

            total = len(top_n)
            for idx in range(total):
                if idx < max(1, int(total * 0.08)): s_val = "Slot 1 (Super Top)"
                elif idx < max(2, int(total * 0.20)): s_val = "Slot 2 (Top Player)"
                elif idx < max(4, int(total * 0.40)): s_val = "Slot 3-4 (Semimolare)"
                elif idx < max(6, int(total * 0.70)): s_val = "Slot 5-6 (Titolare)"
                else: s_val = "Slot 7-8 (Low Cost)"
                top_n.at[idx, 'slot'] = s_val

            elenco_finali.append(top_n)

        if elenco_finali:
            df_finale = pd.concat(elenco_finali, ignore_index=True)
            df_finale['prezzo_massimo'] = np.round(df_finale['prezzo_consigliato'] * 1.25).astype(int)
            df_finale['badge_summary'] = df_finale.apply(genera_str_badge, axis=1)
            return df_finale
        else:
            return df

    except Exception as e:
        st.error(f"Errore durante il caricamento del file Excel: {e}")
        return pd.DataFrame()

df = carica_e_calcola_modello()

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/soccer-ball.png", width=65)
    st.title("FantaBooster®")
    st.caption("Engine Version 3.2 Badges Fixed")
    st.markdown("---")
    st.markdown("**⚙️ Assetto Lega:**")
    st.write("👥 **Partecipanti:** 12 Squadre")
    st.write("💰 **Budget Singolo:** 1.000 Crediti")
    st.write("📈 **Curva Asta:** Gamma Power 3.8")
    st.markdown("---")
    st.markdown("✍️ **Created by Delio Palma**")

# -----------------------------------------------------------------------------
# HEADER BRANDIZZATO
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="brand-banner">
        <div class="brand-title">⚡ FantaBooster® 2026/2027</div>
        <div class="brand-subtitle">Algoritmo Predittivo d'Asta con Badge & Specialisti</div>
        <div class="signature-tag">🛡️ Official Signature Edition by Delio Palma</div>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SCHEDE E INTERFACCIA UTENTE
# -----------------------------------------------------------------------------
if not df.empty and 'nome_completo' in df.columns:
    tab1, tab2, tab3 = st.tabs(["🔍 Analisi Giocatore", "⚡ Assistente Asta Live", "📊 Listino Prezzi & Badges"])

    with tab1:
        giocatore = st.selectbox("Cerca o Seleziona Giocatore:", sorted(df['nome_completo'].unique()))
        p = df[df['nome_completo'] == giocatore].iloc[0]

        # Metric Cards
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Squadra e Ruolo", f"{p.get('Squadra', 'N/D')} — ({p.get('Ruolo', 'N/D')})")
        c2.metric("Prezzo Consigliato", f"{p.get('prezzo_consigliato', 1)} cr")
        c3.metric("Rilancio Max", f"{p.get('prezzo_massimo', 1)} cr")
        c4.metric("Slot Asta Target", p.get('slot', 'N/D'))

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 🏆 Status & Badge Speciali Attribuiti")

        # Generazione Badge Grafici Lucidi
        badges_html = []
        if p.get('Is_Rigorista', False):
            badges_html.append('<div class="badge-chip badge-rigorista">🎯 RIGORISTA TITOLARE</div>')
        if p.get('Is_Piazzati', False):
            badges_html.append('<div class="badge-chip badge-piazzati">📐 CALCI PIAZZATI / ANGOLI</div>')
        if p.get('is_stakanovista', False):
            badges_html.append('<div class="badge-chip badge-stakanovista">🏋️‍♂️ STAKANOVISTA</div>')
        if p.get('is_cittone', False):
            badges_html.append('<div class="badge-chip badge-cittone">🟨 CITTONE</div>')
        if p.get('is_macellaio', False):
            badges_html.append('<div class="badge-chip badge-macellaio">🟥 MACELLAIO</div>')
        if p.get('is_assistman', False):
            badges_html.append('<div class="badge-chip badge-assist">⚽⭐ ASSIST-MAN</div>')
        if p.get('is_bomber', False):
            badges_html.append('<div class="badge-chip badge-bomber">💣 BOMBER</div>')

        if not badges_html:
            badges_html.append('<div class="badge-chip badge-off">⚪ Nessun badge speciale attribuito</div>')

        st.markdown(f'<div class="badge-container">{"".join(badges_html)}</div>', unsafe_allow_html=True)

    with tab2:
        st.subheader("⚡ Assistente Rilanci in Tempo Reale")
        g_live = st.selectbox("Seleziona il calciatore chiamato all'asta:", sorted(df['nome_completo'].unique()), key="live")
        pl = df[df['nome_completo'] == g_live].iloc[0]

        st.info(f"**{pl['nome_completo']}** ({pl.get('Squadra', '')}) — Target: **{pl.get('prezzo_consigliato', 1)} cr** | Limite: **{pl.get('prezzo_massimo', 1)} cr**")
        
        if pl.get('badge_summary') != '-':
            st.caption(f"**Badge Attivi:** {pl.get('badge_summary')}")

        offerta = st.number_input("Offerta attuale chiamata al tavolo (crediti):", min_value=1, value=int(pl.get('prezzo_consigliato', 1)))

        if offerta <= pl.get('prezzo_consigliato', 1):
            st.success("🟢 **COMPRALO ORA!** Offerta eccellente, al sotto o pari alla stima ideale.")
        elif offerta <= pl.get('prezzo_massimo', 1):
            st.warning("🟡 **VALUTA IL RILANCIO.** Entro la soglia limite di tolleranza.")
        else:
            st.error("🔴 **STOP! LASCIA ANDARE!** Offerta superiore al valore massimo calcolato.")

    with tab3:
        st.subheader("📊 Listino Prezzi & Ranking con Badges")
        r = st.radio("Filtra per Ruolo:", ['A', 'C', 'D', 'P'], horizontal=True)
        top = df[df['Ruolo'] == r].sort_values('prezzo_consigliato', ascending=False)
        st.dataframe(
            top[['nome_completo', 'Squadra', 'slot', 'prezzo_consigliato', 'prezzo_massimo', 'badge_summary']], 
            use_container_width=True,
            height=480
        )

# Footer Autore
st.markdown("""
    <div class="footer-delio">
        FantaBooster® — Designed & Developed by <strong>Delio Palma</strong> | All Rights Reserved
    </div>
""", unsafe_allow_html=True)
