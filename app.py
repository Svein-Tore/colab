import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# 1. Konfigurer siden for fart og iFrame
st.set_page_config(layout="wide", page_title="FOPDT Mobil")

# Skjul menyer for renere look
st.markdown("<style>#MainMenu, footer, header {visibility: hidden;}</style>", unsafe_allow_html=True)

st.title("FOPDT Simulator 🚀")

# 2. Cache funksjon for å stoppe Axios/Network Error på mobil
@st.cache_data
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python', decimal=',')
        t = df.iloc[:,0].values
        y = df.iloc[:,1].values
        return t, y
    except:
        return None, None

# 3. Filopplasting
uploaded_file = st.file_uploader("Last opp CSV/TXT", type=["csv", "txt"])

if uploaded_file:
    tid_data, niva_data = load_data(uploaded_file)
    
    if tid_data is not None:
        # --- Estimering ---
        y0_est = float(niva_data[0])
        A_est = float(niva_data[-1] - y0_est)
        
        # Finn 10, 85, 63% for auto-start
        idx10 = np.where(niva_data > y0_est + 0.10 * A_est)[0][0] if len(np.where(niva_data > y0_est + 0.10 * A_est)[0]) > 0 else 0
        idx63 = np.where(niva_data > y0_est + 0.63 * A_est)[0][0] if len(np.where(niva_data > y0_est + 0.63 * A_est)[0]) > 0 else len(tid_data)-1
        
        L_auto = float(tid_data[idx10])
        T_auto = float(tid_data[idx63] - L_auto)

        # 4. Kontrollpanel (Sidebar på PC, Topp på Mobil)
        st.sidebar.header("Innstillinger")
        A = st.sidebar.slider("Δy (Gain)", 0.0, float(A_est*2.5), float(A_est), 0.01)
        T = st.sidebar.slider("T (Tidskonstant)", 0.1, float(T_auto*4), float(T_auto), 0.1)
        L = st.sidebar.slider("L (Dødtid)", 0.0, float(tid_data[-1]/2), float(L_auto), 0.1)
        y0 = st.sidebar.slider("y0 (Start)", float(y0_est-10), float(y0_est+10), float(y0_est), 0.01)

        # 5. Beregning og Graf
        y_model = np.where(tid_data < L, y0, y0 + A * (1 - np.exp(-(tid_data - L) / T)))
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(tid_data, niva_data, "b.", markersize=2, alpha=0.3, label="Måling")
        ax.plot(tid_data, y_model, "r-", linewidth=2, label="FOPDT")
        
        # Hjelpelinjer
        ax.axvline(L, color='orange', linestyle=':', label=f'L={L:.1f}s')
        y63_val = y0 + 0.63 * A
        ax.plot(L+T, y63_val, 'go', markersize=6)
        ax.axhline(y0 + A, color='purple', linestyle='--', alpha=0.3)
        
        ax.grid(True, alpha=0.2)
        ax.set_xlabel("Tid [s]")
        ax.legend(loc='lower right')
        
        st.pyplot(fig)

        # 6. Tabell og Info
        st.markdown("### 📊 Tuning-guide")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.table(pd.DataFrame({
                "λ": ["T/2", "T/4", "T/6"],
                "Respons": ["Rolig", "Std", "Rask"]
            }))
        with col2:
            st.info(f"**Kp:** {T/(1*(A/1)*(L+0.1)):.2f} (estimert v/ λ=0)")
            st.markdown(f"**Formler:**  \nK = Δy/Δu  \nKp = T/(K·(λ+L))  \nTi = min(T, 4(λ+L))")

    else:
        st.error("Kunne ikke lese dataene. Sjekk filformatet.")
else:
    st.info("👆 Last opp en fil fra mobilen eller PC-en for å starte.")
