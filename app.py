# --- 2. NÚCLEO GEMINI Y VOCAL (RECALIBRADO MARK 102) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Cambiamos a 'gemini-1.5-flash-latest' para evitar el error NotFound
    model_chat = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    st.error("⚠️ Error Crítico: Falta la GOOGLE_API_KEY en los secretos.")

# ... (Mantenga las funciones generar_voz y hablar igual) ...

# --- ACTUALIZACIÓN EN PESTAÑA 1 (ANÁLISIS UNIVERSAL) ---
# Sustituya el bloque del botón por este:
if st.button("🔍 INICIAR ESCANEO", key="btn_ana"):
    if 'temp_data' in st.session_state:
        with st.spinner("Analizando con redes neuronales..."):
            try:
                # Usamos una lista para asegurar que Gemini entienda el prompt multimodal
                resp = model_chat.generate_content([
                    "Actúa como JARVIS. Analiza esta imagen o texto detalladamente. "
                    "Si es una planta, dame cuidados. Sé elegante y británico.", 
                    st.session_state.temp_data
                ])
                st.info(resp.text)
                hablar("Escaneo finalizado, Srta. Diana.")
            except Exception as e:
                st.error(f"Falla en el motor visual: {e}")
    else:
        st.warning("⚠️ Sin datos en los sensores.")

# --- ACTUALIZACIÓN EN PESTAÑA 2 (ÓPTICO) ---
# Sustituya el bloque del botón ANÁLISIS TÁCTICO por este:
if st.button("🔍 ANÁLISIS TÁCTICO", key="btn_cam"):
    with st.spinner("Procesando imagen capturada..."):
        try:
            # Forzamos la configuración de contenido para evitar el error de librería
            res_c = model_chat.generate_content([
                "Analiza esta captura de cámara como JARVIS. "
                "Identifica objetos, entorno y riesgos potenciales.", 
                img_cam
            ])
            st.success("Diagnóstico completado:")
            st.write(res_c.text)
            hablar("Diagnóstico de cámara completado.")
        except Exception as e:
            st.error(f"Falla de comunicación: {e}")
            st.info("Sugerencia: Intente refrescar la clave API si el error persiste.")