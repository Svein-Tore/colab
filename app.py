import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# 1. Konfigurasjon
st.set_page_config(layout="wide", page_title="FOPDT Simulator")
st.title("FOPDT Simulator & Identifikasjon 🚀")

# 2. Filopplasting
uploaded_file = st.file_uploader("Last opp måledata (.csv / .txt)", type=["csv", "txt"])
use_test = st.checkbox("Vis eksempeldata")

df = None
if use_test:
    t_t = np.linspace(0, 100, 100)
    y_t = 10 + 5 * (1 - np.exp(-(t_t - 5) / 20)) + np.random.normal(0, 0.05, 100)
    df = pd.DataFrame({'Tid': t_t, 'Nivå': y_t})
elif uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python', decimal=',')
    except:
        st.error("Feil format på fila.")

if df is not None:
    t_d = df.iloc[:,0].values
    n_d = df.iloc[:,1].values
    
    # --- 3. SMART AUTOMATISK ESTIMERING (10/85-regelen) ---
    y0_v = n_d[0]
    A_v = n_d[-1] - y0_v
    
    # Finn tidspunkter for 10%, 63% og 85% av responsen
    idx10 = np.where(n_d > y0_v + 0.10 * A_v)[0][0] if len(np.where(n_d > y0_v + 0.10 * A_v)[0]) > 0 else 0
    idx63 = np.where(n_d > y0_v + 0.63 * A_v)[0][0] if len(np.where(n_d > y0_v + 0.63 * A_v)[0]) > 0 else 0
    idx85 = np.where(n_d > y0_v + 0.85 * A_v)[0][0] if len(np.where(n_d > y0_v + 0.85 * A_v)[0]) > 0 else len(t_d)-1
    
    t10, t63, t85 = t_d[idx10], t_d[idx63], t_d[idx85]
    
    # FOPDT Formler for startverdier
    L_auto = max(0.0, float(t10 - 0.05 * (t85 - t10)))
    T_auto = max(0.1, float(t63 - L_auto))
    
    # --- 4. Sidebar Kontrollpanel (NÅ MED DYNAMISKE STARTVERDIER) ---
    st.sidebar.header("Modell-parametre")
    A = st.sidebar.slider("Forsterkning (Δy)", 0.0, float(max(A_v*2, 1.0)), float(A_v), 0.01)
    T = st.sidebar.slider("Tidskonstant (T)", 0.1, float(max(T_auto*3, 10.0)), float(T_auto), 0.1)
    L = st.sidebar.slider("Dødtid (L)", 0.0, float(t_d[-1]/2), float(L_auto), 0.1)
    y0 = st.sidebar.slider("Startnivå (y0)", float(y0_v-5), float(y0_v+5), float(y0_v), 0.01)

    # --- 5. Graf ---
    y_m = np.where(t_d < L, y0, y0 + A * (1 - np.exp(-(t_d - L) / T)))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(t_d, n_d, "b.", alpha=0.3, label="Måledata")
    ax.plot(t_d, y_m, "r-", linewidth=2.5, label="FOPDT Modell")
    
    # Hjelpelinjer
    ax.axhline(y0, color='black', linestyle='--', alpha=0.3)
    ax.axvline(L, color='orange', linestyle='--', label=f'L={L:.1f}s')
    y63 = y0 + 0.63 * A
    ax.plot(L+T, y63, 'go', markersize=8)
    ax.text(L+T, y63, f' T={T:.1f}s', color='green', fontweight='bold', va='bottom')
    ax.vlines(t_d[-1], y0, y0+A, color='purple', linewidth=3, label=f'Δy={A:.1f}')
    
    ax.set_xlabel("Tid [s]"); ax.set_ylabel("Nivå"); ax.grid(True, alpha=0.2); ax.legend()
    st.pyplot(fig)

    # --- 6. Tabell og Ligninger ---
    st.write("---")
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("#### SIMC Reguleringstuning")
        st.table(pd.DataFrame({
            "Valg av λ": ["T / 2", "T / 4", "T / 6"],
            "Respons": ["Rolig", "Standard", "Rask"],
            "Observasjon": ["Robust", "God balanse", "Aggressiv"]
        }))
    with c2:
        st.markdown("#### PID Formler")
        st.latex(r"K = \Delta y / \Delta u")
        st.latex(r"K_p = \frac{T}{K \cdot (\lambda + L)}")
        st.latex(r"T_i = \min(T, 4 \cdot (\lambda + L))")
else:
    st.info("👆 Last opp en fil for å starte analysen.")
