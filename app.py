import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests, io, base64

# --- 1. CONFIGURACIÓN DEL SISTEMA ---
st.set_page_config(page_title="JARVIS v121", layout="wide")

# Forzar la configuración de la llave
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    # FORZAMOS el modelo Pro, que es el más estable para texto y visión combinados
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("🚨 LLAVE NO DETECTADA EN SECRETS")
    st.stop()

st.title("🛰️ TERMINAL DE EMERGENCIA DIANA")

# --- 2. PRUEBA DE COMUNICACIÓN DIRECTA ---
st.subheader("💬 Canal de Texto Directo")
user_msg = st.text_input("Escriba su orden aquí y presione ENTER:")

if user_msg:
    with st.spinner("JARVIS respondiendo..."):
        try:
            # Petición simplificada al máximo
            response = model.generate_content(user_msg)
            st.write(f"**JARVIS:** {response.text}")
        except Exception as e:
            st.error(f"Falla en comunicación: {e}")
            st.info("Srta. Diana, si el error dice '404', su llave no tiene acceso a este modelo.")

st.divider()

# --- 3. PRUEBA DE VISIÓN DIRECTA ---
st.subheader("📸 Canal Óptico Directo")
foto = st.camera_input("Capturar para análisis")

if foto:
    img = Image.open(foto)
    if st.button("🔍 ANALIZAR AHORA"):
        with st.spinner("Procesando imagen..."):
            try:
                # Intento de visión directa
                res_vision = model.generate_content(["Describe esta imagen de forma técnica.", img])
                st.success(res_vision.text)
            except Exception as e:
                st.error(f"Falla de visión: {e}")