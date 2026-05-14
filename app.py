import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="LiPo Master Tool", page_icon="🔋", layout="wide")

st.title("🔋 LiPo Master Tool & Flight Analytics")
st.markdown("""
    Benvenuto nel calcolatore avanzato per batterie LiPo. 
    Questo strumento è progettato per piloti e maker per ottimizzare la carica, 
    analizzare le prestazioni e garantire la sicurezza.
""")

# --- SIDEBAR: DATI TECNICI ---
st.sidebar.header("⚙️ Specifiche Batteria")
cap_mah = st.sidebar.number_input("Capacità (mAh)", min_value=100, max_value=30000, value=1500, step=50)
cells = st.sidebar.selectbox("Celle (S)", [1, 2, 3, 4, 5, 6, 8, 12], index=3)
c_rating = st.sidebar.slider("C-Rating di Scarica", 1, 150, 75)
v_nominal = 3.7
v_full = 4.2

# Calcoli Base
cap_ah = cap_mah / 1000
total_nominal_v = cells * v_nominal
total_full_v = cells * v_full
watt_hours = cap_ah * total_nominal_v

# --- LAYOUT PRINCIPALE A TAB ---
tab1, tab2, tab3, tab4 = st.tabs(["⚡ Carica & Scarica", "📉 Stato di Salute (IR)", "🚁 Flight Stats", "✈️ Travel & Safety"])

# --- TAB 1: CARICA E SCARICA ---
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parametri di Carica")
        charge_rate = st.select_slider("Rate di carica (C)", options=[0.5, 1.0, 1.5, 2.0, 5.0], value=1.0)
        recommended_amps = cap_ah * charge_rate
        
        st.metric("Corrente di Carica", f"{recommended_amps:.2f} A", f"{charge_rate}C")
        
        current_v = st.number_input("Voltaggio attuale (Totale V)", min_value=3.0*cells, max_value=total_full_v, value=3.7*cells)
        remaining_pct = max(0, min(100, int((current_v/cells - 3.2) / (4.2 - 3.2) * 100)))
        
        st.write(f"Stato attuale: **{remaining_pct}%**")
        st.progress(remaining_pct / 100)

    with col2:
        st.subheader("Parametri di Scarica")
        max_continuous_a = cap_ah * c_rating
        burst_a = max_continuous_a * 1.5 # Stima burst standard
        
        st.metric("Scarica Continua Max", f"{max_continuous_a:.1f} A")
        st.metric("Burst Max (3-5s)", f"{burst_a:.1f} A")
        st.warning(f"Potenza Massima Teorica: {max_continuous_a * total_nominal_v:.1f} W")

# --- TAB 2: ANALISI RESISTENZA INTERNA (IR) ---
with tab2:
    st.subheader("Analisi della Resistenza Interna (mΩ)")
    st.info("Inserisci i valori mΩ per cella letti dal caricabatterie per valutare lo stato di salute.")
    
    ir_values = []
    cols_ir = st.columns(cells)
    for i in range(cells):
        with cols_ir[i]:
            val = st.number_input(f"Cella {i+1}", min_value=0.0, max_value=50.0, value=5.0, key=f"ir_{i}")
            ir_values.append(val)
    
    avg_ir = sum(ir_values) / cells
    max_diff = max(ir_values) - min(ir_values)
    
    c1, c2 = st.columns(2)
    c1.metric("Media IR", f"{avg_ir:.2f} mΩ")
    c2.metric("Sbilanciamento Max", f"{max_diff:.2f} mΩ")
    
    if avg_ir < 10:
        st.success("Stato: Ottimo. Batteria performante.")
    elif avg_ir < 20:
        st.warning("Stato: Usurata. Adatta per voli tranquilli.")
    else:
        st.error("Stato: Critica. Rischio cali di tensione (voltage sag) o gonfiaggio.")

# --- TAB 3: FLIGHT STATISTICS ---
with tab3:
    st.subheader("Stima Autonomia Volo")
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        avg_amp_draw = st.number_input("Assorbimento medio in volo (A)", min_value=1.0, max_value=200.0, value=25.0)
        # Regola dell'80% per non rovinare la LiPo
        usable_cap = cap_ah * 0.8
        flight_time_dec = (usable_cap / avg_amp_draw) * 60
        
        st.subheader(f"Tempo di volo stimato: {int(flight_time_dec)}m {int((flight_time_dec%1)*60)}s")
        st.caption("Calcolato sull'80% della capacità totale per preservare le celle.")

    with col_f2:
        st.subheader("Efficienza")
        thrust_weight = st.slider("Rapporto Spinta/Peso stimato", 1.0, 15.0, 5.0)
        st.write(f"Con un rapporto di {thrust_weight}:1, il tuo drone avrà un comportamento {'molto aggressivo' if thrust_weight > 8 else 'bilanciato'}.")

# --- TAB 4: TRAVEL & SAFETY ---
with tab4:
    st.subheader("Trasporto Aereo (IATA)")
    if watt_hours < 100:
        st.success(f"Energia: {watt_hours:.2f} Wh. Generalmente ammessa nel bagaglio a mano.")
    elif watt_hours < 160:
        st.warning(f"Energia: {watt_hours:.2f} Wh. Potrebbe richiedere approvazione della compagnia aerea.")
    else:
        st.error(f"Energia: {watt_hours:.2f} Wh. Supera i limiti standard per il trasporto passeggeri.")

    st.divider()
    st.subheader("Guida Rapida Sicurezza")
    st.markdown("""
    1.  **Storage:** Se non le usi per più di 2 giorni, portale a **3.80V-3.85V** per cella.
    2.  **Temperatura:** Non caricare mai se la batteria è sotto i 10°C o sopra i 45°C.
    3.  **Ispezione:** Se vedi ammaccature o odori dolciastri, smetti di usarla immediatamente.
    """)

# Footer
st.divider()
st.caption("LiPo Master Tool v1.0 | Sviluppato con Streamlit")
