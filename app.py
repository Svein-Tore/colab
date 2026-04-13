import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# 1. Konfigurasjon
st.set_page_config(layout="wide", page_title="FOPDT Simulator")
st.title("FOPDT Simulator 📱🍕")

# 2. Inndata - Tekstfeltet er sjefen (Axios-sikker)
st.subheader("1. Legg inn måledata")
st.write("Kopier kolonnene fra fila di og lim dem inn under:")

pasted_data = st.text_area("Lim inn her (Tid og Nivå):", height=150, placeholder="0,10.5\n1,11.2\n2,12.1...")

# Backup-metode for de som vil prøve filopplasting
with st.expander("Klikk her for å prøve filopplasting (kan feile på mobil)"):
    uploaded_file = st.file_uploader("Velg CSV/TXT fil", type=["csv", "txt"])

# Mulighet for eksempeldata
use_test = st.checkbox("Bruk eksempedata for å teste")

df = None
try:
    if pasted_data:
        df = pd.read_csv(io.StringIO(pasted_data), sep=None, engine='python', decimal=',')
    elif uploaded_file is not None:
        df = pd.read_csv(uploaded_file, sep=None, engine='python', decimal=',')
    elif use_test:
        t_t = np.linspace(0, 100, 100)
        y_t = 10 + 5 * (1 - np.exp(-(t_t - 5) / 20)) + np.random.normal(0, 0.05, 100)
        df = pd.DataFrame({'Tid': t_t, 'Nivå': y_t})
except:
    st.error("Klarte ikke å lese dataene. Sjekk at du har to kolonner med tall.")

if df is not None:
    tid_data = df.iloc[:,0].values
    niva_data = df.iloc[:,1].values
    
    # --- 3. Estimering ---
    y0_est = float(niva_data[0])
    A_est = float(niva_data[-1] - y0_est)
    
    # --- 4. Kontroller ---
    st.subheader("2. Tilpass modell")
    c1, c2 = st.columns(2)
    with c1:
        A = st.slider("Forsterkning (Δy)", 0.0, float(max(A_est*2.5, 1.0)), float(A_est), step=0.01)
        T = st.slider("Tidskonstant (T)", 0.1, 300.0, 20.0, step=0.1)
    with c2:
        L = st.slider("Dødtid (L)", 0.0, float(tid_data[-1]/2), 5.0, step=0.1)
        y0 = st.slider("y0 (Startnivå)", float(y0_est-10), float(y0_est+10), float(y0_est), step=0.01)

    # --- 5. Graf ---
    y_model = np.where(tid_data < L, y0, y0 + A * (1 - np.exp(-(tid_data - L) / T)))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(tid_data, niva_data, "b.", alpha=0.3, label="Måling")
    ax.plot(tid_data, y_model, "r-", linewidth=2.5, label="FOPDT Modell")
    
    # Linjer og tekst
    ax.axvline(L, color='orange', linestyle='--', linewidth=2)
    ax.text(L, y0, f' L={L:.1f}s', color='orange', fontweight='bold', ha='right', va='bottom')
    y63 = y0 + 0.63 * A
    t63 = L + T
    ax.axhline(y63, color='green', linestyle=':', alpha=0.6)
    ax.plot(t63, y63, 'go', markersize=8)
    ax.text(t63, y63, f' T={T:.1f}s', color='green', fontweight='bold', va='bottom')
    
    ax.set_xlabel("Tid [s]"); ax.set_ylabel("Nivå"); ax.grid(True, alpha=0.2); ax.legend()
    st.pyplot(fig)

    # --- 6. Tabell og Formler ---
    st.write("---")
    tab1, tab2 = st.columns(2)
    with tab1:
        st.markdown("**SIMC Tabell**")
        st.table(pd.DataFrame({"λ": ["T/2", "T/4", "T/6"], "Respons": ["Rolig", "Std", "Rask"]}))
    with tab2:
        st.markdown("**Regulator (PI)**")
        st.write(f"Kp = T / (K * (λ + L))")
        st.write(f"Ti = min(T, 4 * (λ + L))")
else:
    st.info("💡 Lim inn data over for å starte. Hvis knappen under expander-en gir feil, bruk kun tekstfeltet.")
