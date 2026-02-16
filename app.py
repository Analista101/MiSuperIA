import streamlit as st
import google.generativeai as genai
from PIL import Image
import edge_tts, asyncio, base64, io

# 1. SETUP INICIAL
st.set_page_config(page_title="JARVIS", layout="wide")

# 2. CARGA DE LLAVE (PUNTO CRÍTICO)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Usamos el modelo PRO, por si el FLASH está saturado en su región
    model = genai.GenerativeModel('gemini-1.5-pro')
else:
    st.error("🚨 SRTA. DIANA: NO HAY LLAVE MAESTRA EN SECRETS.")

# 3. INTERFAZ
st.title("🛰️ SISTEMA INTEGRADO DIANA v106")
tabs = st.tabs(["💬 CHAT", "📸 ÓPTICO"])

with tabs[1]:
    st.subheader("Sensores de Visión")
    cam = st.camera_input("Captura de Campo")
    
    if cam:
        if st.button("🔍 ANALIZAR AHORA"):
            with st.spinner("JARVIS procesando..."):
                try:
                    img = Image.open(cam)
                    # El formato de envío más estable para Google
                    response = model.generate_content([
                        "Eres JARVIS. Describe esta imagen para la Srta. Diana.", 
                        img
                    ])
                    st.info(response.text)
                except Exception as e:
                    st.error(f"Error de Acceso: Su API Key no permite visión. Detalle: {e}")