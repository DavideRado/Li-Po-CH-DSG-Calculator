import streamlit as st

# Configurazione Pagina
st.set_page_config(page_title="LiPo CH&DGS Calc", page_icon="🔋", layout="wide")

st.title("🔋 LiPo CH&DGS Calculator")

# --- SIDEBAR: DATI TECNICI ---
st.sidebar.header("📋 Dati del Datasheet")
cap_mah = st.sidebar.number_input("Capacità Nominale (mAh)", min_value=100, max_value=30000, value=1500, step=50)
cells = st.sidebar.selectbox("Configurazione Celle (S)", [1, 2, 3, 4, 5, 6, 8, 12], index=3)
c_discharge_input = st.sidebar.number_input("C-Rating di Scarica (Max Cont.)", min_value=1, max_value=200, value=75)

cap_ah = cap_mah / 1000
v_nom_total = cells * 3.7

# --- LAYOUT PRINCIPALE ---
tab1, tab2, tab3 = st.tabs(["⚡ Carica & SoC", "📉 Diagnostica Avanzata", "🚁 Flight Stats"])

with tab1:
    st.markdown("## 📊 STATO DI CARICA")
    col_soc1, col_soc2 = st.columns([1, 2])
    with col_soc1:
        current_v = st.number_input("Tensione Totale Misurata (V)", 
                                    min_value=3.0*cells, 
                                    max_value=4.25*cells, 
                                    value=3.8*cells, 
                                    step=0.01)
    
    v_per_cell = current_v / cells
    remaining_pct = max(0, min(100, int((v_per_cell - 3.2) / (4.2 - 3.2) * 100)))
    
    with col_soc2:
        st.write(f"### Carica Residua: **{remaining_pct}%**")
        st.progress(remaining_pct / 100)

    st.divider()
    st.subheader("⚡ Impostazione Caricatore")
    charge_amps = st.slider("Corrente sul Caricatore (A)", 0.1, 15.0, cap_ah, 0.1)
    st.metric("Tasso di Carica", f"{(charge_amps / cap_ah):.2f} C")

with tab2:
    # --- GRANDE AVVISO RICHIESTO ---
    st.warning("""
    ### ⚠️ NOTA SULLA PRECISIONE DELLE MISURE
    Il calcolo della **Resistenza Interna** e del **Voltage Sag** effettuato tramite multimetro/carico elettronico è 
    **fortemente influenzato dai conduttori e dai punti di contatto**.
    
    *   **Contatti:** Clip a coccodrillo o connettori sporchi possono aggiungere oltre **50-100mΩ** da soli.
    *   **Cavi:** I conduttori del carico elettronico introducono una caduta di tensione propria.
    *   **Risultato:** La stima seguente è da considerarsi **molto peggiorativa** rispetto alla reale salute della chimica interna. 
    Per una misura reale, scansiona i terminali della batteria direttamente mentre è sotto carico.
    """)

    st.markdown("## 🔧 Test del Voltage Sag")
    col_sag1, col_sag2, col_sag3 = st.columns(3)
    
    with col_sag1:
        v_idle = st.number_input("V a riposo (V)", value=current_v)
    with col_sag2:
        v_load = st.number_input("V sotto carico (V)", value=current_v - 0.5)
    with col_sag3:
        i_load = st.number_input("Corrente Carico (A)", value=3.1)
        
    if i_load > 0:
        v_drop = v_idle - v_load
        r_total_mohm = (v_drop / i_load) * 1000
        
        st.subheader(f"Resistenza Calcolata: {r_total_mohm:.1f} mΩ")
        
        # Analisi qualitativa corretta per includere i cavi
        if r_total_mohm < 30:
            st.success("Sistema eccellente (bassa resistenza totale).")
        elif r_total_mohm < 100:
            st.info("Sistema accettabile per usi generici. Probabile influenza dei cavi di test.")
        else:
            st.error("Resistenza critica. Controlla i connettori o lo stato della batteria.")

    st.divider()
    st.subheader("📏 Stima " + "Resistenza" + " Cavi (opzionale)")
    st.write("Se conosci i tuoi cavi, puoi sottrarre la loro resistenza per isolare meglio la batteria.")
    cavo_awg = st.selectbox("Sezione Cavo di test (AWG)", [12, 14, 16, 18, 20, 22], index=2)
    lunghezza = st.slider("Lunghezza totale cavi (cm)", 10, 200, 60)
    
    # Valori approssimativi mOhm/metro per AWG
    awg_map = {12: 5.2, 14: 8.2, 16: 13.1, 18: 20.9, 20: 33.3, 22: 52.9}
    r_cavi = (awg_map[cavo_awg] * (lunghezza/100))
    
    st.write(f"Resistenza stimata dei soli cavi: **{r_cavi:.1f} mΩ**")
    st.write(f"Resistenza stimata 'Pura' della batteria: **{max(0.0, r_total_mohm - r_cavi):.1f} mΩ**")

with tab3:
    st.markdown("## 🚁 Flight Stats")
    avg_amp_draw = st.number_input("Assorbimento medio (A)", value=20.0)
    flight_time = ((cap_ah * 0.8) / avg_amp_draw) * 60
    st.metric("Autonomia Stimata (80%)", f"{int(flight_time)}m {int((flight_time%1)*60)}s")
    
    wh = cap_ah * v_nom_total
    st.metric("Energia Totale", f"{wh:.2f} Wh")

st.divider()
st.caption("LiPo Master Tool v1.3 | Risultati influenzati da setup di misura")
