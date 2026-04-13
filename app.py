import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# 1. Konfigurasjon
st.set_page_config(layout="wide", page_title="FOPDT Simulator")

st.title("FOPDT Simulator 🚀")

# 2. Skuddsikker fil-leser
def process_data(file):
    try:
        df = pd.read_csv(file, sep=None, engine='python', decimal=',')
        return df.iloc[:,0].values, df.iloc[:,1].values
    except:
        return None, None

# 3. Filopplasting og test-data
uploaded_file = st.file_uploader("1. Last opp data (.csv / .txt)", type=["csv", "txt"])
use_test = st.checkbox("Bruk test-data (hvis opplasting feiler på mobil)")

if use_test:
    t_test = np.linspace(0, 100, 100)
    y_test = 10 + 5 * (1 - np.exp(-(t_test - 5) / 20)) + np.random.normal(0, 0.05, 100)
    tid_data, niva_data = t_test, y_test
elif uploaded_file:
    tid_data, niva_data = process_data(uploaded_file)
else:
    tid_data = None

if tid_data is not None:
    # --- Auto-estimering for startverdier ---
    y0_est = float(niva_data[0])
    A_est = float(niva_data[-1] - y0_est)

    # --- 4. KONTROLLPANEL (Flyttet fra Sidebar til hovedskjerm) ---
    st.subheader("2. Juster modell-parametre")
    
    # Vi legger sliderne i kolonner så de ser bra ut på PC, men stabler seg på mobil
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        A = st.slider("Forsterkning (Δy)", 0.0, float(max(A_est*2.5, 1.0)), float(A_est), step=0.01)
        T = st.slider("Tidskonstant (T)", 0.1, 200.0, 20.0, step=0.1)
    with col_s2:
        L = st.slider("Dødtid (L)", 0.0, float(tid_data[-1]/2), 2.0, step=0.1)
        y0 = st.slider("Startnivå (y0)", float(y0_est-10), float(y0_est+10), float(y0_est), step=0.01)

    # --- 5. GRAF ---
    y_model = np.where(tid_data < L, y0, y0 + A * (1 - np.exp(-(tid_data - L) / T)))
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(tid_data, niva_data, "b.", markersize=4, alpha=0.3, label="Måledata")
    ax.plot(tid_data, y_model, "r-", linewidth=2.5, label="FOPDT Modell")
    
    # Hjelpelinjer for pedagogikk
    ax.axvline(L, color='orange', linestyle='--', label=f'L={L:.1f}s')
    ax.axhline(y0 + 0.63*A, color='green', linestyle=':', alpha=0.6, label='63% punkt')
    
    ax.set_xlabel("Tid [s]")
    ax.set_ylabel("Nivå")
    ax.grid(True, alpha=0.2)
    ax.legend()
    
    st.pyplot(fig)

    # --- 6. INFO-TABELL OG FORMLER ---
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**SIMC Tuning-guide**")
        st.table(pd.DataFrame({
            "Valg": ["T/2", "T/4", "T/6"],
            "Respons": ["Rolig", "Standard", "Rask"],
            "Observasjon": ["Robust", "God balanse", "Aggressiv"]
        }))
    with c2:
        st.markdown("**Formler (PI-regulator)**")
        st.latex(r"K = \frac{\Delta y}{\Delta u}")
        st.latex(r"K_p = \frac{T}{K \cdot (\lambda + L)}")
        st.latex(r"T_i = \min(T, 4 \cdot (\lambda + L))")

else:
    st.info("👋 Last opp en fil eller velg 'Bruk test-data' over for å starte.")
