import streamlit as st

# Configurazione Pagina
st.set_page_config(page_title="LiPo Pro Calc", page_icon="🔋", layout="wide")

st.title("🔋 LiPo Expert Tool (Multimeter & Datasheet Ready)")

# --- SIDEBAR: DATI TECNICI (Dati da Datasheet) ---
st.sidebar.header("📋 Dati del Datasheet")
cap_mah = st.sidebar.number_input("Capacità Nominale (mAh)", min_value=100, max_value=30000, value=1500, step=50)
cells = st.sidebar.selectbox("Configurazione Celle (S)", [1, 2, 3, 4, 5, 6, 8, 12], index=3)
c_discharge_input = st.sidebar.number_input("C-Rating di Scarica (Max Cont.)", min_value=1, max_value=200, value=75)

cap_ah = cap_mah / 1000
v_nom_total = cells * 3.7

# --- LAYOUT PRINCIPALE ---
tab1, tab2, tab3 = st.tabs(["⚡ Carica & SoC", "📉 Analisi Elettronica", "🚁 Flight Stats"])

with tab1:
    # --- SEZIONE SOC (STATO DI CARICA) ---
    st.markdown("## 📊 ANALISI STATO DI CARICA (Lettura Multimetro)")
    st.info("Misura la tensione ai capi del connettore XT60/XT30 con il multimetro.")
    
    col_soc1, col_soc2 = st.columns([1, 2])
    with col_soc1:
        current_v = st.number_input("Tensione Totale Misurata (V)", 
                                    min_value=3.0*cells, 
                                    max_value=4.25*cells, 
                                    value=3.8*cells, 
                                    step=0.01)
    
    v_per_cell = current_v / cells
    # Mappatura più precisa della curva LiPo
    remaining_pct = max(0, min(100, int((v_per_cell - 3.2) / (4.2 - 3.2) * 100)))
    
    with col_soc2:
        st.write(f"### Carica Residua: **{remaining_pct}%**")
        st.progress(remaining_pct / 100)
        st.caption(f"Tensione media per cella: {v_per_cell:.2f}V")

    st.divider()

    # --- PARAMETRI DI CARICA ---
    st.subheader("⚡ Impostazione Caricatore")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        charge_amps = st.slider("Seleziona Corrente sul Caricatore (A)", 
                                min_value=0.1, 
                                max_value=15.0, 
                                value=cap_ah, 
                                step=0.1)
        calc_c_rate = charge_amps / cap_ah
        st.metric("Tasso di Carica", f"{calc_c_rate:.2f} C")

    with col_c2:
        # Calcolo tempo basato su efficienza standard (10% perdite calore)
        target_v = cells * 4.2
        if current_v < target_v:
            needed_mah = cap_mah * (1 - (remaining_pct/100))
            time_h = (needed_mah / (charge_amps * 1000)) * 1.15 # 1.15 fattore di bilanciamento celle
            st.metric("Tempo stimato fine carica", f"{int(time_h * 60)} min")

with tab2:
    st.markdown("## 🔧 Strumenti di Diagnostica Elettronica")
    
    # 1. ANALISI VOLTAGE SAG (Caduta di Tensione)
    st.subheader("1. Test della Caduta di Tensione (Voltage Sag)")
    st.write("Misura la tensione prima e durante un carico (es. motori al 50%) per valutare lo stato dei contatti.")
    col_sag1, col_sag2, col_sag3 = st.columns(3)
    
    with col_sag1:
        v_idle = st.number_input("Tensione a riposo (V)", value=current_v)
    with col_sag2:
        v_load = st.number_input("Tensione sotto carico (V)", value=current_v - 0.5)
    with col_sag3:
        i_load = st.number_input("Corrente misurata (A)", value=20.0)
        
    v_drop = v_idle - v_load
    if i_load > 0:
        resistance_total = v_drop / i_load
        st.metric("Resistenza Totale Circuito", f"{resistance_total * 1000:.1f} mΩ")
        if resistance_total * 1000 > 50:
            st.error("⚠️ Resistenza elevata: controlla saldature, connettori o usura batteria.")

    st.divider()

    # 2. CONVERSIONE DATASHEET WATT/AMPERE
    st.subheader("2. Calcolatore di Potenza (da Datasheet)")
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        input_watts = st.number_input("Potenza richiesta dal carico (W)", min_value=0.0, value=250.0)
        amps_needed = input_watts / v_nom_total
        st.write(f"Corrente richiesta: **{amps_needed:.2f} A**")
    
    with col_w2:
        # Controllo limite C-Rating
        max_a_ds = cap_ah * c_discharge_input
        if amps_needed > max_a_ds:
            st.error(f"Superi il limite del datasheet! ({max_a_ds}A max)")
        else:
            st.success(f"Carico entro i limiti del datasheet.")

with tab3:
    st.subheader("⏱️ Autonomia e Flight Analytics")
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        avg_amp_draw = st.number_input("Assorbimento medio (A)", min_value=0.5, max_value=250.0, value=20.0)
        usable_cap = cap_ah * 0.8
        flight_time_dec = (usable_cap / avg_amp_draw) * 60
        st.info(f"Tempo stimato: **{int(flight_time_dec)}m {int((flight_time_dec%1)*60)}s**")

    with col_f2:
        wh = cap_ah * v_nom_total
        st.metric("Energia Nominale", f"{wh:.2f} Wh")
        st.write(f"Limite IATA: {'✅ OK' if wh < 100 else '⚠️ Richiede Autorizzazione'}")

# Footer
st.divider()
st.caption("LiPo Master Tool v1.2 | Ideato per l'uso con Multimetro e Datasheet")
