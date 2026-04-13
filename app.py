import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# 1. Tving Streamlit til å være mer stabil
st.set_page_config(layout="wide", page_title="FOPDT Stabil")

st.title("FOPDT Simulator 🚀")

# 2. Skuddsikker fil-leser
def process_data(file):
    try:
        df = pd.read_csv(file, sep=None, engine='python', decimal=',')
        return df.iloc[:,0].values, df.iloc[:,1].values
    except:
        return None, None

# 3. Filopplasting (med en liten forklaring for mobil)
uploaded_file = st.file_uploader("Last opp data (.csv / .txt)", type=["csv", "txt"])

# Nødknapp hvis opplasting krangler på mobil
if st.checkbox("Bruk test-data (hvis opplasting feiler)"):
    t_test = np.linspace(0, 100, 100)
    y_test = 10 + 5 * (1 - np.exp(-(t_test - 5) / 20)) + np.random.normal(0, 0.1, 100)
    tid_data, niva_data = t_test, y_test
    uploaded_file = True # For å trigge neste steg
else:
    if uploaded_file:
        tid_data, niva_data = process_data(uploaded_file)
    else:
        tid_data = None

if tid_data is not None:
    # --- Auto-estimering ---
    y0_est = float(niva_data[0])
    A_est = float(niva_data[-1] - y0_est)
    
    # 4. Kontrollpanel (Sidebar)
    st.sidebar.header("Parametere")
    A = st.sidebar.slider("Δy (Gain)", 0.0, float(max(A_est*2, 1.0)), float(A_est))
    T = st.sidebar.slider("T (Tidskonstant)", 0.1, 200.0, 20.0)
    L = st.sidebar.slider("L (Dødtid)", 0.0, float(tid_data[-1]/2), 2.0)
    y0 = st.sidebar.slider("y0 (Start)", float(y0_est-5), float(y0_est+5), float(y0_est))

    # 5. Graf
    y_model = np.where(tid_data < L, y0, y0 + A * (1 - np.exp(-(tid_data - L) / T)))
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(tid_data, niva_data, "b.", alpha=0.3, label="Måling")
    ax.plot(tid_data, y_model, "r-", linewidth=2, label="FOPDT")
    ax.axvline(L, color='orange', linestyle=':', label=f'L={L:.1f}s')
    ax.grid(True, alpha=0.2)
    ax.legend()
    st.pyplot(fig)

    # 6. Tabell og Formler (SYMMETRISK)
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**SIMC Tuning**")
        st.table(pd.DataFrame({
            "Valg": ["T/2", "T/4", "T/6"],
            "Respons": ["Rolig", "Std", "Rask"]
        }))
    with c2:
        st.markdown("**Formler (PI)**")
        st.code(f"Kp = T / (K * (λ + L))\nTi = min(T, 4 * (λ + L))")

else:
    st.warning("Venter på fil... (Tips: Hvis mobilen kaster 'Network Error', prøv å bruke test-data knappen over for å se at appen virker.)")
