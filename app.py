# --- 3. PESTAÑA: ÓPTICO (RESTORED ANALYTICS) ---
with tabs[2]:
    st.subheader("📸 Sensores Visuales y Escaneo Biométrico")
    
    # 1. Activación de Cámara
    cam = st.camera_input("Activar Escáner Térmico/Óptico", key="stark_cam")
    
    if cam:
        img_cam = Image.open(cam)
        
        col_view, col_diag = st.columns([1, 1])
        
        with col_view:
            st.markdown("### 🛰️ Vista de Campo")
            # Selector de filtros (Grises, Térmico, Nocturno)
            f_modo = st.selectbox("Cambiar Espectro:", ["Normal", "Grises", "Térmico", "Nocturno"], key="filter_opt")
            
            img_display = img_cam.copy()
            if f_modo == "Grises": 
                img_display = ImageOps.grayscale(img_display)
            elif f_modo == "Térmico": 
                img_display = ImageOps.colorize(ImageOps.grayscale(img_display), "blue", "red")
            elif f_modo == "Nocturno": 
                img_display = ImageOps.colorize(ImageOps.grayscale(img_display), "black", "green")
            
            st.image(img_display, use_container_width=True, caption=f"Modo: {f_modo}")

        with col_diag:
            st.markdown("### 🧠 Diagnóstico de JARVIS")
            # 2. Botón de Análisis Específico para la Cámara
            if st.button("🔍 INICIAR ANÁLISIS TÁCTICO", type="primary", use_container_width=True):
                with st.spinner("JARVIS analizando entorno..."):
                    try:
                        # Enviamos la imagen de la cámara a Gemini
                        prompt_cam = "Actúa como JARVIS. Analiza esta imagen capturada por la cámara. Si es una planta, identifícala y da consejos. Si es un objeto o persona, descríbelo con precisión Stark."
                        res_cam = model_chat.generate_content([prompt_cam, img_cam])
                        
                        st.success("Escaneo completado.")
                        st.info(res_cam.text)
                        hablar("Escaneo de campo finalizado, Srta. Diana. Los resultados están en pantalla.")
                    except Exception as e:
                        st.error(f"Falla en el enlace de visión: {e}")
            else:
                st.write("Esperando confirmación para iniciar el escaneo de la imagen capturada.")