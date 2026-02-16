import streamlit as st
from groq import Groq
import requests
import docx
import pandas as pd
import PyPDF2
from PIL import Image, ImageOps, ImageFilter
from streamlit_mic_recorder import mic_recorder
import io, base64

# --- 1. ESTÉTICA STARK (REACTOR ARC) ---
st.set_page_config(page_title="JARVIS v127", layout="wide")
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

# --- 2. NÚCLEO DE INTELIGENCIA ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    modelo_texto = "llama-3.3-70b-versatile"
    modelo_vision = "llama-3.2-11b-vision-preview"
else:
    st.error("🚨 SRTA. DIANA: ACCESO DENEGADO. REVISE GROQ_API_KEY.")
    st.stop()

# --- 3. INTERFAZ TÁCTICA ---
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS UNIVERSAL", "🎨 LABORATORIO"])

# --- TAB 0: COMANDO (MICRÓFONO REINSTALADO) ---
with tabs[0]:
    st.subheader("🎙️ Interfaz de Voz y Texto")
    col_mic, col_chat = st.columns([1, 5])
    with col_mic:
        # Reinstalación del sensor de audio
        audio = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_127")
    
    chat_input = st.chat_input("Órdenes para JARVIS...")
    final_prompt = audio['transcript'] if audio and audio['transcript'] else chat_input

    if final_prompt:
        with st.chat_message("user"): st.write(final_prompt)
        with st.chat_message("assistant"):
            try:
                res = client.chat.completions.create(
                    model=modelo_texto,
                    messages=[{"role": "system", "content": "Eres JARVIS. Responde elegante a la Srta. Diana."},
                              {"role": "user", "content": final_prompt}]
                )
                st.write(res.choices[0].message.content)
            except Exception as e: st.error(f"Falla: {e}")

# --- TAB 1: ANÁLISIS UNIVERSAL (MULTIFORMATO + IMÁGENES) ---
with tabs[1]:
    st.subheader("📊 Centro de Inteligencia")
    archivo = st.file_uploader("Subir informe o imagen", type=['txt', 'docx', 'xlsx', 'csv', 'pdf', 'png', 'jpg', 'jpeg'])
    
    if archivo and st.button("🔍 INICIAR ESCANEO"):
        with st.spinner("Analizando..."):
            try:
                if archivo.type in ["image/png", "image/jpeg", "image/jpg"]:
                    img = Image.open(archivo)
                    st.image(img, width=400)
                    encoded_img = base64.b64encode(archivo.getvalue()).decode('utf-8')
                    res = client.chat.completions.create(
                        model=modelo_vision,
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Analiza esta imagen técnicamente para la Srta. Diana."},
                            {"type": "image_url", "image_url": {"url": f"data:{archivo.type};base64,{encoded_img}"}}
                        ]}]
                    )
                    st.info(res.choices[0].message.content)
                else:
                    # Lógica de documentos (Excel, Word, PDF)
                    text_content = ""
                    if archivo.name.endswith('.docx'):
                        doc = docx.Document(archivo)
                        text_content = "\n".join([p.text for p in doc.paragraphs])
                    elif archivo.name.endswith('.pdf'):
                        pdf_reader = PyPDF2.PdfReader(archivo)
                        text_content = "\n".join([page.extract_text() for page in pdf_reader.pages])
                    elif archivo.name.endswith('.xlsx'):
                        df = pd.read_excel(archivo)
                        text_content = f"Excel Data: {df.head().to_string()}"
                    else:
                        text_content = archivo.read().decode()

                    res = client.chat.completions.create(
                        model=modelo_texto,
                        messages=[{"role": "user", "content": f"Analiza esto: {text_content[:8000]}"}]
                    )
                    st.success(res.choices[0].message.content)
            except Exception as e: st.error(f"Error: {e}")

# --- TAB 2: LABORATORIO (FILTROS REINSTALADOS) ---
with tabs[2]:
    st.subheader("🎨 Estación de Diseño Mark 62")
    idea = st.text_input("¿Qué diseño desea sintetizar?")
    
    # Filtros creativos para el renderizado
    filtro_estilo = st.selectbox("Efecto de Renderizado:", 
                                ["Original", "Cinematic Marvel", "Blueprint Técnico", "Cyberpunk Neón", "Estructura de Alambre"])
    
    if st.button("🚀 INICIAR SÍNTESIS"):
        if idea:
            with st.spinner("JARVIS sintetizando..."):
                prompt_estilo = f"{idea}, {filtro_estilo} style, high quality"
                url = f"https://image.pollinations.ai/prompt/{prompt_estilo.replace(' ', '%20')}?nologo=true"
                st.image(url, caption=f"Prototipo: {idea} | Modo: {filtro_estilo}")