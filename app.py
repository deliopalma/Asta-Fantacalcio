import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="FantaAsta Stats Engine 2026/2027", page_icon="⚽", layout="wide")

@st.cache_data
def carica_e_calcola_modello():
    try:
        # Legge il file Excel
        df = pd.read_excel('Tutti_2027.xlsx', sheet_name=0, engine='openpyxl')
        df.columns = [str(col).strip() for col in df.columns]

        cols_lower = {str(col).lower(): col for col in df.columns}
        col_nome = next((cols_lower[k] for k in ['nome', 'giocatore', 'calciatore', 'player', 'cognome'] if k in cols_lower), None)

        if col_nome:
            df['nome_completo'] = df[col_nome].astype(str)
        else:
            text_cols = [c for c in df.columns if df[c].dtype == 'object']
            df['nome_completo'] = df[text_cols[0]].astype(str) if text_cols else df.iloc[:, 0].astype(str)

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

        # Dati statistici per il calcolo
        col_gol = next((cols_lower[k] for k in ['gol', 'goals', 'reti', 'g', 'gf'] if k in cols_lower), None)
        col_assist = next((cols_lower[k] for k in ['assist', 'a', 'ast'] if k in cols_lower), None)
        col_pres = next((cols_lower[k] for k in ['presenze', 'partite', 'pg', 'p'] if k in cols_lower), None)

        gol_val = pd.to_numeric(df[col_gol], errors='coerce').fillna(0) if col_gol else pd.Series(0, index=df.index)
        assist_val = pd.to_numeric(df[col_assist], errors='coerce').fillna(0) if col_assist else pd.Series(0, index=df.index)
        pres_val = pd.to_numeric(df[col_pres], errors='coerce').fillna(20) if col_pres else pd.Series(20, index=df.index)

        # Calcolo FantaScore pesato
        df['fanta_score'] = (gol_val * 4.0) + (assist_val * 1.5) + (pres_val * 0.3)
        
        if df['fanta_score'].max() == 0 or df['fanta_score'].nunique() <= 1:
            # Fallback se non ci sono colonne numeriche nel file: ordina in base alla posizione originale
            df['fanta_score'] = np.linspace(100, 5, len(df))

        # ---------------------------------------------------------------------
        # MODELLO ASTERI REALI (1000 CREDITI / LEGA A 12)
        # Budget totale reparti per lega a 12: A=4800, C=4200, D=2040, P=960
        # ---------------------------------------------------------------------
        budgets = {'P': 960, 'D': 2040, 'C': 4200, 'A': 4800}
        slots_count = {'P': 36, 'D': 96, 'C': 96, 'A': 72}
        
        # Esponente aggressivo per accentuare il valore dei Top Player
        gamma_power = {'A': 3.8, 'C': 3.2, 'D': 2.5, 'P': 2.2}

        elenco_finali = []
        for r in ['P', 'D', 'C', 'A']:
            sub = df[df['Ruolo'] == r].sort_values(by='fanta_score', ascending=False).reset_index(drop=True)
            if len(sub) == 0:
                continue
            
            top_n = sub.head(min(slots_count[r], len(sub))).copy()
            scores = top_n['fanta_score']
            
            # Normalizzazione
            min_s, max_s = scores.min(), scores.max()
            if max_s > min_s:
                scores_norm = (scores - min_s) / (max_s - min_s) + 0.05
            else:
                scores_norm = np.ones(len(scores))

            # Curva esponenziale di ripartizione
            exp_scores = np.power(scores_norm, gamma_power[r])
            sum_exp = exp_scores.sum()

            if sum_exp > 0:
                top_n['prezzo_consigliato'] = np.round((exp_scores / sum_exp) * budgets[r]).astype(int)
                top_n['prezzo_consigliato'] = np.maximum(1, top_n['prezzo_consigliato'])
            else:
                top_n['prezzo_consigliato'] = 1

            # Assegnazione Slot d'Asta Reali
            total = len(top_n)
            for idx in range(total):
                if idx < max(1, int(total * 0.08)):
                    s_val = "Slot 1 (Super Top)"
                elif idx < max(2, int(total * 0.20)):
                    s_val = "Slot 2 (Top Player)"
                elif idx < max(4, int(total * 0.40)):
                    s_val = "Slot 3-4 (Semimolare / Titolare Forte)"
                elif idx < max(6, int(total * 0.70)):
                    s_val = "Slot 5-6 (Titolare / Buona Copertura)"
                else:
                    s_val = "Slot 7-8 (Low Cost / Scommessa)"
                top_n.at[idx, 'slot'] = s_val

            elenco_finali.append(top_n)

        if elenco_finali:
            df_finale = pd.concat(elenco_finali, ignore_index=True)
            df_finale['prezzo_massimo'] = np.round(df_finale['prezzo_consigliato'] * 1.25).astype(int)
            return df_finale
        else:
            return df

    except Exception as e:
        st.error(f"Errore durante il caricamento del file Excel: {e}")
        return pd.DataFrame()

df = carica_e_calcola_modello()

# -----------------------------------------------------------------------------
# INTERFACCIA GRAFICA STREAMLIT
# -----------------------------------------------------------------------------
if not df.empty and 'nome_completo' in df.columns:
    st.title("⚽ FantaAsta Stats Engine 2026/2027")
    st.caption("Modello calibrato su Lega a 12 squadre - Budget 1.000 Crediti")

    tab1, tab2, tab3 = st.tabs(["🔍 Cerca Giocatore", "⚡ Asta Live", "📊 Classifica e Prezzi per Ruolo"])

    with tab1:
        giocatore = st.selectbox("Seleziona Giocatore:", sorted(df['nome_completo'].unique()))
        p = df[df['nome_completo'] == giocatore].iloc[0]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Squadra e Ruolo", f"{p.get('Squadra', 'N/D')} ({p.get('Ruolo', 'N/D')})")
        c2.metric("Prezzo Consigliato", f"{p.get('prezzo_consigliato', 1)} cr")
        c3.metric("Prezzo Massimo", f"{p.get('prezzo_massimo', 1)} cr")
        c4.metric("Slot d'Asta", p.get('slot', 'N/D'))

    with tab2:
        st.subheader("Consigliere Asta Live")
        g_live = st.selectbox("Giocatore chiamato all'asta ora:", sorted(df['nome_completo'].unique()), key="live")
        pl = df[df['nome_completo'] == g_live].iloc[0]

        st.info(f"Giocatore: **{pl['nome_completo']}** | Valore consigliato: **{pl.get('prezzo_consigliato', 1)} cr** | Rilancio Max: **{pl.get('prezzo_massimo', 1)} cr**")

        offerta = st.number_input("Offerta attuale all'asta (crediti):", min_value=1, value=int(pl.get('prezzo_consigliato', 1)))

        if offerta <= pl.get('prezzo_consigliato', 1):
            st.success("🟢 COMPRALO! Prezzo ottimo rispetto alla stima reale.")
        elif offerta <= pl.get('prezzo_massimo', 1):
            st.warning("🟡 RILANCIA CON ATTENZIONE. Sei sopra la stima base ma entro la soglia di tolleranza.")
        else:
            st.error("🔴 FERMATI! L'offerta supera il valore massimo consigliato.")

    with tab3:
        st.subheader("Classifica Giocatori e Stima Prezzi per Ruolo")
        r = st.radio("Seleziona Ruolo:", ['A', 'C', 'D', 'P'], horizontal=True)
        top = df[df['Ruolo'] == r].sort_values('prezzo_consigliato', ascending=False)
        st.dataframe(top[['nome_completo', 'Squadra', 'slot', 'prezzo_consigliato', 'prezzo_massimo']], use_container_width=True)
