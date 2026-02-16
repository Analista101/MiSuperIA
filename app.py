# --- 2. CONFIGURACIÓN DEL NÚCLEO (RECALIBRADO MARK 104) ---
model_chat = None
if "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Cambiamos a la versión específica de 8b, que es la más estable en Cloud
        model_chat = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
    except Exception as e:
        st.error(f"Falla en la inicialización del núcleo: {e}")
else:
    st.warning("🛰️ Srta. Diana, falta la GOOGLE_API_KEY en los secretos.")

# ... (El resto del código se mantiene) ...

# --- ACTUALIZACIÓN CRÍTICA EN PESTAÑA 2: ÓPTICO ---
with tabs[2]:
    st.subheader("📸 Sensores Ópticos")
    cam = st.camera_input("Escáner Activo", key="cam_v104")
    
    if cam:
        # Colocamos el botón debajo de la cámara
        if st.button("🔍 ANÁLISIS TÁCTICO", key="btn_cam_v104"):
            if model_chat:
                with st.spinner("JARVIS está analizando la captura..."):
                    try:
                        img_cam = Image.open(cam)
                        # Formateamos el prompt como una lista explícita de partes
                        prompt_parts = [
                            "Actúa como JARVIS. Describe esta imagen de forma elegante y técnica.",
                            img_cam
                        ]
                        res_c = model_chat.generate_content(prompt_parts)
                        
                        st.success("🛰️ Análisis de Campo:")
                        st.markdown(res_c.text)
                        hablar("Diagnóstico de cámara completado, Srta. Diana.")
                    except Exception as e:
                        st.error(f"Error de enlace: El modelo seleccionado no responde. Detalle: {e}")
            else:
                st.error("⚠️ El núcleo de IA no está configurado.")