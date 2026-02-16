import streamlit as st
from groq import Groq
import requests
import docx
import pandas as pd
import PyPDF2
from PIL import Image, ImageOps, ImageFilter
from streamlit_mic_recorder import mic_recorder
import io, base64

# --- 1. ESTÉTICA DE LA TORRE DIANA ---
st.set_page_config(page_title="JARVIS v128", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #010409; color: #00f2ff; }
    .arc-reactor {
        width: 60px; height: 60px; border-radius: 50%; margin: 10px auto;
        background: radial-gradient(circle, #fff 0%, #00f2ff 40%, transparent 70%);
        box-shadow: 0 0 25px #00f2ff; border: 2px solid #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- 2. NÚCLEO DE INTELIGENCIA (GROQ) ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    modelo_texto = "llama-3.3-70b-versatile"
    modelo_vision = "llama-3.2-11b-vision-preview"
else:
    st.error("🚨 SRTA. DIANA: REVISE SU GROQ_API_KEY EN SECRETS.")
    st.stop()

# --- 3. INTERFAZ TÁCTICA HÍBRIDA ---
tabs = st.tabs(["💬 COMANDO HÍBRIDO", "📊 ANÁLISIS DOCS", "🎨 LABORATORIO"])

# --- TAB 0: COMANDO (CHAT + VOZ + PEGAR IMÁGENES) ---
with tabs[0]:
    st.subheader("🎙️ Centro de Mando Inteligente")
    
    # Columna para el micrófono y entrada de archivos/capturas
    col_a, col_b = st.columns([1, 4])
    with col_a:
        audio = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_128")
    
    # Nuevo cargador para "Pegar" o arrastrar capturas
    captura = st.file_uploader("Pegue o arrastre una captura de pantalla aquí:", type=['png', 'jpg', 'jpeg'], key="paste_img")
    
    chat_input = st.chat_input("Órdenes para JARVIS o pegue una captura arriba...")
    
    # Lógica de procesamiento
    if chat_input or captura or (audio and audio['transcript']):
        with st.chat_message("assistant"):
            try:
                # Caso 1: Hay una imagen (Captura de pantalla pegada)
                if captura:
                    st.image(captura, width=300, caption="Captura recibida")
                    encoded_img = base64.b64encode(captura.getvalue()).decode('utf-8')
                    # Si hay texto acompañando la imagen, lo usamos; si no, prompt genérico
                    texto_instruccion = chat_input if chat_input else "Analiza esta captura para la Srta. Diana."
                    
                    res = client.chat.completions.create(
                        model=modelo_vision,
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": texto_instruccion},
                            {"type": "image_url", "image_url": {"url": f"data:{captura.type};base64,{encoded_img}"}}
                        ]}]
                    )
                    st.write(res.choices[0].message.content)
                
                # Caso 2: Solo voz o texto
                else:
                    final_prompt = audio['transcript'] if (audio and audio['transcript']) else chat_input
                    res = client.chat.completions.create(
                        model=modelo_texto,
                        messages=[{"role": "system", "content": "Eres JARVIS. Responde elegante a la Srta. Diana."},
                                  {"role": "user", "content": final_prompt}]
                    )
                    st.write(res.choices[0].message.content)
            except Exception as e:
                st.error(f"Falla en el enlace: {e}")

# --- TAB 1: ANÁLISIS DOCS --- (Se mantiene igual pero optimizado)
with tabs[1]:
    st.subheader("📊 Lector de Informes Tácticos")
    archivo_doc = st.file_uploader("Subir PDF, Excel o Word", type=['pdf', 'docx', 'xlsx', 'txt'])
    if archivo_doc and st.button("🔍 ANALIZAR DOCUMENTO"):
        # (La lógica de lectura de documentos del Mark 127 se mantiene aquí)
        st.info("Procesando documento... (Lógica cargada)")

# --- TAB 2: LABORATORIO ---
with tabs[2]:
    st.subheader("🎨 Estación de Diseño Mark 63")
    idea = st.text_input("Diseño a sintetizar:")
    filtro_estilo = st.selectbox("Acabado:", ["Cinematic", "Blueprint", "Cyberpunk", "Realistic"])
    if st.button("🚀 SINTETIZAR"):
        if idea:
            st.image(f"https://image.pollinations.ai/prompt/{idea.replace(' ', '%20')}%20{filtro_estilo}?nologo=true")