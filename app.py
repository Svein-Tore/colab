import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# Konfigurer siden for LearnLab-innbygging
st.set_page_config(layout="wide", page_title="FOPDT Simulator")

# Skjul Streamlit-menyer for en renere iFrame-opplevelse
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("FOPDT Simulator & Identifikasjon")

# --- 1. Filopplasting ---
uploaded_file = st.file_uploader("Last opp måledata (.csv eller .txt)", type=["csv", "txt"])

if uploaded_file is not None:
    # Les data robust
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python', decimal=',')
        tid_data = df.iloc[:,0].values
        niva_data = df.iloc[:,1].values
    except:
        st.error("Feil ved lesing av fil. Sjekk at det er en gyldig CSV.")
        st.stop()

    # --- 2. Automatisk estimering (10/85-regelen) ---
    y0_est = float(niva_data[0])
    A_est = float(niva_data[-1] - y0_est)
    
    t10 = tid_data[np.where(niva_data > y0_est + 0.10 * A_est)[0][0]] if len(np.where(niva_data > y0_est + 0.10 * A_v)[0]) > 0 else tid_data[0]
    t85 = tid_data[np.where(niva_data > y0_est + 0.85 * A_est)[0][0]] if len(np.where(niva_data > y0_est + 0.85 * A_v)[0]) > 0 else tid_data[-1]
    t63 = tid_data[np.where(niva_data > y0_est + 0.63 * A_est)[0][0]] if len(np.where(niva_data > y0_est + 0.63 * A_v)[0]) > 0 else tid_data[-1]
    
    L_auto = max(0, float(t10 - 0.05 * (t85 - t10)))
    T_auto = max(0.1, float(t63 - L_auto))

    # --- 3. Sidebar Kontrollpanel ---
    st.sidebar.header("Juster modell")
    A = st.sidebar.slider("Forsterkning (Δy)", 0.0, float(A_est*2), float(A_est), step=0.01)
    T = st.sidebar.slider("Tidskonstant (T)", 0.1, float(T_auto*3), float(T_auto), step=0.1)
    L = st.sidebar.slider("Dødtid (L)", 0.0, float(tid_data[-1]/2), float(L_auto), step=0.1)
    y0 = st.sidebar.slider("Startnivå (y0)", float(y0_est-5), float(y0_est+5), float(y0_est), step=0.01)

    # --- 4. Plott-logikk ---
    y_model = np.where(tid_data < L, y0, y0 + A * (1 - np.exp(-(tid_data - L) / T)))
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(tid_data, niva_data, "b.", markersize=3, alpha=0.3, label="Måledata")
    ax.plot(tid_data, y_model, "r-", linewidth=2, label="FOPDT Modell")
    
    # Pedagogiske hjelpelinjer
    ax.axhline(y0, color='black', linestyle='--', alpha=0.4)
    ax.text(tid_data[0], y0, f' y0={y0:.1f}', fontweight='bold', va='bottom')
    
    ax.axvline(L, color='orange', linestyle=':', linewidth=2)
    ax.text(L, y0, f' L={L:.1f}s ', color='orange', fontweight='bold', ha='right')
    
    y63 = y0 + 0.63 * A
    ax.axhline(y63, color='green', linestyle=':', alpha=0.4)
    ax.axvline(L + T, color='green', linestyle=':', alpha=0.4)
    ax.plot(L + T, y63, 'go', markersize=8)
    ax.text(L + T, y63, f' y63={y63:.1f}\n T={T:.1f}s', color='green', fontweight='bold', va='top')
    
    ax.vlines(tid_data[-1], y0, y0+A, color='purple', linewidth=3)
    ax.text(tid_data[-1], y0+A/2, f' Δy={A:.1f}', color='purple', fontweight='bold', ha='left')

    ax.grid(True, alpha=0.2)
    ax.set_xlabel("Tid [s]")
    ax.set_ylabel("Nivå / Respons")
    ax.legend(loc='lower right')
    
    st.pyplot(fig)

    # --- 5. Info-tabell og Formler ---
    st.write("---")
    col_tab, col_form = st.columns([2, 1])
    
    with col_tab:
        st.markdown("**SIMC Reguleringstuning**")
        tuning_df = pd.DataFrame({
            "Valg av λ": ["T / 2", "T / 4", "T / 6"],
            "Respons": ["Rolig", "Standard", "Rask"],
            "Observasjon": ["Robust, ingen oversving", "God balanse", "Aggressiv, noe oversving"]
        })
        st.table(tuning_df)

    with col_form:
        st.markdown("**Formler (PI-regulator)**")
        st.latex(r"K = \frac{\Delta y}{\Delta u}")
        st.latex(r"K_p = \frac{T}{K \cdot (\lambda + L)}")
        st.latex(r"T_i = \min(T, 4 \cdot (\lambda + L))")

else:
    st.info("👋 Velkommen! Last opp en CSV-fil for å starte analysen.")
