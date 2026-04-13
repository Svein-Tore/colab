import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# 1. Konfigurasjon for PC (Bred layout)
st.set_page_config(layout="wide", page_title="FOPDT Simulator")

st.title("FOPDT Simulator & Identifikasjon 🚀")

# 2. Filopplasting (Fungerer perfekt på PC)
st.markdown("### 1. Last opp måledata")
uploaded_file = st.file_uploader("Velg .csv eller .txt fil fra PCen", type=["csv", "txt"])

# Mulighet for test-data hvis man vil se funksjonalitet uten fil
if st.checkbox("Vis eksempeldata"):
    t_t = np.linspace(0, 100, 100)
    y_t = 10 + 5 * (1 - np.exp(-(t_t - 5) / 20)) + np.random.normal(0, 0.05, 100)
    df = pd.DataFrame({'Tid': t_t, 'Nivå': y_t})
elif uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python', decimal=',')
    except:
        st.error("Feil format på fila. Sjekk at den har to kolonner.")
        df = None
else:
    df = None

if df is not None:
    t_d = df.iloc[:,0].values
    n_d = df.iloc[:,1].values
    
    # --- 3. Automatisk estimering for sliders ---
    y0_est = float(n_d[0])
    A_est = float(n_d[-1] - y0_est)
    
    # --- 4. Sidebar Kontrollpanel (Perfekt for PC) ---
    st.sidebar.header("Modell-parametre")
    A = st.sidebar.slider("Forsterkning (Δy)", 0.0, float(max(A_est*2.5, 1.0)), float(A_est), 0.01)
    T = st.sidebar.slider("Tidskonstant (T)", 0.1, 300.0, 20.0, 0.1)
    L = st.sidebar.slider("Dødtid (L)", 0.0, float(t_d[-1]/2), 5.0, 0.1)
    y0 = st.sidebar.slider("Startnivå (y0)", float(y0_est-10), float(y0_est+10), float(y0_est), 0.01)

    # --- 5. Graf med alle linjer og verdier ---
    y_m = np.where(t_d < L, y0, y0 + A * (1 - np.exp(-(t_d - L) / T)))
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(t_d, n_d, "b.", markersize=4, alpha=0.3, label="Måledata")
    ax.plot(t_d, y_m, "r-", linewidth=2.5, label="FOPDT Modell")
    
    # Hjelpelinjer og tekst (Gull-standard)
    ax.axhline(y0, color='black', linestyle='--', alpha=0.3)
    ax.text(t_d[0], y0, f' y0={y0:.1f}', fontweight='bold', va='bottom')
    
    ax.axvline(L, color='orange', linestyle='--', linewidth=2)
    ax.text(L, y0, f' L={L:.1f}s', color='orange', fontweight='bold', ha='right')
    
    y63 = y0 + 0.63 * A
    t63 = L + T
    ax.axhline(y63, color='green', linestyle=':', alpha=0.6)
    ax.plot(t63, y63, 'go', markersize=8)
    ax.text(t63, y63, f' T={T:.1f}s (v/{y63:.1f})', color='green', fontweight='bold', va='bottom')
    
    ax.vlines(t_d[-1], y0, y0+A, color='purple', linewidth=3)
    ax.text(t_d[-1], y0+A/2, f' Δy={A:.1f}', color='purple', fontweight='bold')

    ax.set_xlabel("Tid [s]"); ax.set_ylabel("Nivå"); ax.grid(True, alpha=0.2); ax.legend()
    st.pyplot(fig)

    # --- 6. Symmetrisk Tabell og Ligninger ---
    st.write("---")
    col_tab, col_form = st.columns([1.5, 1])
    
    with col_tab:
        st.markdown("#### SIMC Reguleringstabell")
        st.table(pd.DataFrame({
            "Valg av λ": ["T / 2", "T / 4", "T / 6"],
            "Respons": ["Rolig", "Standard", "Rask"],
            "Observasjon": ["Robust, ingen oversving", "God balanse", "Aggressiv, oversving"]
        }))

    with col_form:
        st.markdown("#### PID Formler (PI)")
        st.latex(r"K = \frac{\Delta y}{\Delta u}")
        st.latex(r"K_p = \frac{T}{K \cdot (\lambda + L)}")
        st.latex(r"T_i = \min(T, 4 \cdot (\lambda + L))")

else:
    st.info("👆 Last opp en måleserie for å begynne identifikasjonen.")
