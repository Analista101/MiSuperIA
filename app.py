import streamlit as st
from groq import Groq
import requests
import docx
import pandas as pd
import PyPDF2
from PIL import Image, ImageOps, ImageFilter
from streamlit_paste_button import paste_image_button as paste_button
from streamlit_mic_recorder import mic_recorder
import io, base64

# --- 1. ESTÉTICA DE LA TORRE STARK ---
st.set_page_config(page_title="JARVIS v134", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #010409; color: #00f2ff; }
    .arc-reactor {
        width: 55px; height: 55px; border-radius: 50%; margin: 10px auto;
        background: radial-gradient(circle, #fff 0%, #00f2ff 40%, transparent 70%);
        box-shadow: 0 0 20px #00f2ff; border: 2px solid #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    .stTabs [data-baseweb="tab"] { color: #00f2ff !important; font-size: 16px; }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- 2. NÚCLEO DE INTELIGENCIA (GROQ) ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    modelo_texto = "llama-3.3-70b-versatile"
    modelo_vision = "llama-3.2-11b-vision-preview"
else:
    st.error("🚨 SRTA. DIANA: ACCESO DENEGADO. REVISE SECRETS.")
    st.stop()

# --- 3. INTERFAZ TÁCTICA MULTI-MÓDULO ---
tabs = st.tabs(["💬 COMANDO HÍBRIDO", "📊 ANÁLISIS DOCS", "🎨 LABORATORIO"])

# --- PESTAÑA 0: COMANDO (CHAT + VOZ + PEGAR) ---
with tabs[0]:
    st.subheader("🎙️ Centro de Mando e Imagen")
    
    col_a, col_b, col_c = st.columns([1, 2, 2])
    with col_a:
        mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_134")
    with col_b:
        pasted_image = paste_button(label="📋 PEGAR CAPTURA (CTRL+V)", key="paster_134")
    with col_c:
        if st.button("🗑️ LIMPIAR SISTEMA"):
            st.rerun()

    chat_msg = st.chat_input("Órdenes para JARVIS...")

    if pasted_image.image_data is not None:
        img = pasted_image.image_data
        st.image(img, caption="Imagen en memoria de JARVIS", width=400)
        if chat_msg:
            with st.chat_message("assistant"):
                try:
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    res = client.chat.completions.create(
                        model=modelo_vision,
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": f"JARVIS, atiende a la Srta. Diana: {chat_msg}"},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                        ]}]
                    )
                    st.write(res.choices[0].message.content)
                except Exception as e: st.error(f"Falla: {e}")
    elif chat_msg:
        with st.chat_message("assistant"):
            res = client.chat.completions.create(
                model=modelo_texto,
                messages=[{"role": "system", "content": "Eres JARVIS. Responde elegante a la Srta. Diana."},
                          {"role": "user", "content": chat_msg}]
            )
            st.write(res.choices[0].message.content)

# --- PESTAÑA 1: ANÁLISIS DE DOCUMENTOS (RESTAURADA) ---
with tabs[1]:
    st.subheader("📊 Lector de Inteligencia Multiformato")
    file = st.file_uploader("Cargar informe (PDF, DOCX, XLSX, TXT)", type=['pdf', 'docx', 'xlsx', 'txt', 'csv'])
    
    if file and st.button("🔍 INICIAR ESCANEO DE DOC"):
        with st.spinner("JARVIS procesando archivo..."):
            try:
                text_content = ""
                if file.name.endswith('.docx'):
                    doc = docx.Document(file)
                    text_content = "\n".join([p.text for p in doc.paragraphs])
                elif file.name.endswith('.pdf'):
                    pdf_reader = PyPDF2.PdfReader(file)
                    text_content = "\n".join([page.extract_text() for page in pdf_reader.pages])
                elif file.name.endswith('.xlsx') or file.name.endswith('.csv'):
                    df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
                    text_content = f"Datos del archivo:\n{df.head(20).to_string()}"
                else:
                    text_content = file.read().decode()

                res = client.chat.completions.create(
                    model=modelo_texto,
                    messages=[{"role": "user", "content": f"Analiza este informe para la Srta. Diana: {text_content[:8000]}"}]
                )
                st.success(res.choices[0].message.content)
            except Exception as e: st.error(f"Error en lectura: {e}")

# --- PESTAÑA 2: LABORATORIO (RESTAURADO) ---
with tabs[2]:
    st.subheader("🎨 Estación de Diseño Mark 64")
    idea = st.text_input("Describa el prototipo a sintetizar:")
    estilo = st.selectbox("Acabado Visual:", ["Cinematic Marvel", "Blueprint Técnico", "Cyberpunk Neón", "Industrial Stark"])
    
    if st.button("🚀 INICIAR SÍNTESIS"):
        if idea:
            with st.spinner("Sintetizando imagen..."):
                url = f"https://image.pollinations.ai/prompt/{idea.replace(' ', '%20')}%20{estilo.replace(' ', '%20')}?nologo=true"
                st.image(url, caption=f"Prototipo: {idea} | Modo: {estilo}")