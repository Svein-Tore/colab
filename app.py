import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# 1. Konfigurasjon
st.set_page_config(layout="wide", page_title="FOPDT Mobil-Mester")
st.title("FOPDT Simulator 📱🚀")

# 2. Velg inndata-metode (Dette hindrer Axios-krasj ved oppstart)
st.subheader("1. Hent måledata")
metode = st.radio("Velg hvordan du vil hente data:", 
                 ("Lim inn tekst (Anbefalt for mobil)", "Last opp fil (Kan feile på enkelte mobiler)"))

df = None

if metode == "Last opp fil (Kan feile på enkelte mobiler)":
    uploaded_file = st.file_uploader("Velg .csv eller .txt fil", type=["csv", "txt"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file, sep=None, engine='python', decimal=',')
        except:
            st.error("Kunne ikke lese filen.")
else:
    raw_text = st.text_area("Lim inn kolonner fra fila di her (Tid og Nivå):", height=150)
    if raw_text:
        try:
            df = pd.read_csv(io.StringIO(raw_text), sep=None, engine='python', decimal=',')
        except:
            st.error("Feil format på teksten.")

# Mulighet for eksempeldata
if st.checkbox("Bruk eksempedata for å teste"):
    t_t = np.linspace(0, 100, 100)
    y_t = 10 + 5 * (1 - np.exp(-(t_t - 5) / 20)) + np.random.normal(0, 0.05, 100)
    df = pd.DataFrame({'Tid': t_t, 'Nivå': y_t})

if df is not None:
    t_d = df.iloc[:,0].values
    n_d = df.iloc[:,1].values
    
    # --- 3. Auto-estimering ---
    y0_est = float(n_d[0])
    A_est = float(n_d[-1] - y0_est)
    
    # --- 4. Kontrollpanel ---
    st.subheader("2. Tilpass modell")
    c1, c2 = st.columns(2)
    with c1:
        A = st.slider("Forsterkning (Δy)", 0.0, float(max(A_est*2.5, 1.0)), float(A_est), step=0.01)
        T = st.slider("Tidskonstant (T)", 0.1, 300.0, 20.0, step=0.1)
    with c2:
        L = st.slider("Dødtid (L)", 0.0, float(t_d[-1]/2), 5.0, step=0.1)
        y0 = st.slider("y0 (Startnivå)", float(y0_est-10), float(y0_est+10), float(y0_est), step=0.01)

    # --- 5. Graf med pedagogiske linjer ---
    y_m = np.where(t_d < L, y0, y0 + A * (1 - np.exp(-(t_d - L) / T)))
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(t_d, n_d, "b.", markersize=4, alpha=0.3, label="Måling")
    ax.plot(t_d, y_m, "r-", linewidth=2.5, label="FOPDT Modell")
    
    # Hjelpelinjer
    ax.axvline(L, color='orange', linestyle='--', linewidth=2)
    ax.text(L, y0, f' L={L:.1f}s', color='orange', fontweight='bold', ha='right', va='bottom')
    
    y63 = y0 + 0.63 * A
    t63 = L + T
    ax.axhline(y63, color='green', linestyle=':', alpha=0.6)
    ax.plot(t63, y63, 'go', markersize=8)
    ax.text(t63, y63, f' T={T:.1f}s', color='green', fontweight='bold', va='bottom')
    
    ax.set_xlabel("Tid [s]"); ax.set_ylabel("Nivå"); ax.grid(True, alpha=0.2); ax.legend()
    st.pyplot(fig)

    # --- 6. Symmetrisk Tabell og Ligninger ---
    st.write("---")
    tab1, tab2 = st.columns(2)
    with tab1:
        st.markdown("**SIMC Tabell**")
        st.table(pd.DataFrame({
            "Valg λ": ["T/2", "T/4", "T/6"],
            "Respons": ["Rolig", "Std", "Rask"],
            "Obs": ["Robust", "Balanse", "Aggressiv"]
        }))
    with tab2:
        st.markdown("**Regulator-formler (PI)**")
        st.latex(r"K_p = \frac{T}{K \cdot (\lambda + L)}")
        st.latex(r"T_i = \min(T, 4 \cdot (\lambda + L))")
else:
    st.info("👆 Velg metode for å starte. Hvis filopplasting gir feil på din mobil, bruk 'Lim inn tekst'.")
