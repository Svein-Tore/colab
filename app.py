import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# 1. Konfigurasjon
st.set_page_config(layout="wide", page_title="FOPDT Mobil-Mester")
st.title("FOPDT Simulator 📱🍕")

# 2. Inndata (Skuddsikker tekstfelt-metode)
st.subheader("1. Lim inn måledata")
raw_text = st.text_area("Åpne CSV-fila di, kopier alt og lim inn her:", height=150, placeholder="Tid,Nivå\n0,10.5\n1,11.2...")

df = None

# Sjekk om brukeren limer inn tekst eller vil teste
if raw_text:
    try:
        # Snuser seg frem til om det er brukt komma eller semikolon
        df = pd.read_csv(io.StringIO(raw_text), sep=None, engine='python', decimal=',')
    except:
        st.error("Feil format! Pass på at du har med to kolonner (Tid og Nivå).")

if st.checkbox("Bruk eksempedata for å teste appen"):
    t_t = np.linspace(0, 100, 100)
    y_t = 10 + 5 * (1 - np.exp(-(t_t - 5) / 20)) + np.random.normal(0, 0.05, 100)
    df = pd.DataFrame({'Tid': t_t, 'Nivå': y_t})

if df is not None:
    # Henter ut kolonnene uavhengig av hva de heter
    tid_data = df.iloc[:,0].values
    niva_data = df.iloc[:,1].values
    
    # --- 3. Auto-estimering for sliders ---
    y0_est = float(niva_data[0])
    A_est = float(niva_data[-1] - y0_est)
    
    # --- 4. Kontrollpanel (Alltid synlig under grafen på mobil) ---
    st.subheader("2. Tilpass modell")
    c1, c2 = st.columns(2)
    with c1:
        A = st.slider("Δy (Gain)", 0.0, float(max(A_est*2.5, 1.0)), float(A_est), step=0.01)
        T = st.slider("T (Tidskonstant)", 0.1, 300.0, 20.0, step=0.1)
    with c2:
        L = st.slider("L (Dødtid)", 0.0, float(tid_data[-1]/2), 5.0, step=0.1)
        y0 = st.slider("y0 (Startnivå)", float(y0_est-10), float(y0_est+10), float(y0_est), step=0.01)

    # --- 5. Beregning og Graf ---
    y_model = np.where(tid_data < L, y0, y0 + A * (1 - np.exp(-(tid_data - L) / T)))
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(tid_data, niva_data, "b.", markersize=4, alpha=0.3, label="Måling")
    ax.plot(tid_data, y_model, "r-", linewidth=2.5, label="FOPDT Modell")
    
    # Hjelpelinjer og tekst (Pedagogisk pakke)
    ax.axvline(L, color='orange', linestyle='--', linewidth=2)
    ax.text(L, y0, f' L={L:.1f}s', color='orange', fontweight='bold', ha='right', va='bottom')
    
    y63 = y0 + 0.63 * A
    t63 = L + T
    ax.axhline(y63, color='green', linestyle=':', alpha=0.6)
    ax.plot(t63, y63, 'go', markersize=8)
    ax.text(t63, y63, f' T={T:.1f}s', color='green', fontweight='bold', va='bottom')
    
    ax.set_xlabel("Tid [s]"); ax.set_ylabel("Nivå"); ax.grid(True, alpha=0.2); ax.legend()
    st.pyplot(fig)

    # --- 6. Tuning og Formler ---
    st.write("---")
    tab1, tab2 = st.columns(2)
    with tab1:
        st.markdown("**SIMC Tabell**")
        st.table(pd.DataFrame({"λ": ["T/2", "T/4", "T/6"], "Respons": ["Rolig", "Std", "Rask"]}))
    with tab2:
        st.markdown("**Regulator-formler (PI)**")
        st.latex(r"K_p = \frac{T}{K \cdot (\lambda + L)}")
        st.latex(r"T_i = \min(T, 4 \cdot (\lambda + L))")

else:
    st.info("👆 Lim inn data eller bruk eksempedata for å starte. (Dette fungerer garantert på mobil!)")
