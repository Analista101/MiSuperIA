import streamlit as st
from groq import Groq
import requests
import docx
import pandas as pd
from PIL import Image, ImageOps, ImageFilter
from streamlit_mic_recorder import mic_recorder

# --- 1. ESTÉTICA DE LA TORRE STARK (AUDITADA) ---
st.set_page_config(page_title="JARVIS v125", layout="wide")

# CSS para mantener el look neón y el reactor
st.markdown("""
    <style>
    .stApp { background-color: #010409; color: #00f2ff; }
    .stTabs [data-baseweb="tab"] { color: #00f2ff !important; font-size: 16px; }
    .stButton>button { border: 1px solid #00f2ff; background-color: transparent; color: #00f2ff; width: 100%; }
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

# --- 2. CONEXIÓN A LA RED INDEPENDIENTE (GROQ) ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    # Usamos Llama-3.3-70b: un modelo masivo y extremadamente inteligente
    modelo_ia = "llama-3.3-70b-versatile"
else:
    st.error("🚨 SRTA. DIANA: ACCESO DENEGADO. FALTA GROQ_API_KEY EN SECRETS.")
    st.stop()

# --- 3. INTERFAZ TÁCTICA ---
st.title("🛰️ JARVIS: SISTEMA AUTÓNOMO v125")
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS DOCS", "📸 ÓPTICO", "🎨 LABORATORIO"])

# --- PESTAÑA 0: COMANDO (VOZ + TEXTO) ---
with tabs[0]:
    col_mic, col_chat = st.columns([1, 5])
    with col_mic:
        audio = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_125")
    
    prompt_input = st.chat_input("Órdenes para JARVIS...")
    final_prompt = audio['transcript'] if audio and audio['transcript'] else prompt_input

    if final_prompt:
        with st.chat_message("user"): st.write(final_prompt)
        with st.chat_message("assistant"):
            try:
                completion = client.chat.completions.create(
                    model=modelo_ia,
                    messages=[
                        {"role": "system", "content": "Eres JARVIS, el asistente elegante de la Srta. Diana. Responde con la precisión de Stark Industries."},
                        {"role": "user", "content": final_prompt}
                    ]
                )
                st.write(completion.choices[0].message.content)
            except Exception as e: st.error(f"Falla de enlace: {e}")

# --- PESTAÑA 1: ANÁLISIS DE DOCS (EXCEL/WORD) ---
with tabs[1]:
    st.subheader("📊 Lector de Inteligencia Multiformato")
    file = st.file_uploader("Cargar archivo táctico", type=['txt', 'docx', 'xlsx'])
    if file and st.button("🔍 INICIAR ANÁLISIS"):
        try:
            if file.name.endswith('.docx'):
                doc = docx.Document(file)
                text = "\n".join([p.text for p in doc.paragraphs])
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
                text = f"Resumen de datos: {df.head().to_string()}"
            else:
                text = file.read().decode()
            
            with st.spinner("JARVIS procesando datos..."):
                res = client.chat.completions.create(
                    model=modelo_ia,
                    messages=[{"role": "user", "content": f"Resume y analiza esto para la Srta. Diana: {text[:7000]}"}]
                )
                st.success(res.choices[0].message.content)
        except Exception as e: st.error(f"Error en el lector: {e}")

# --- PESTAÑA 3: LABORATORIO (GENERADOR DE IMÁGENES) ---
with tabs[3]:
    st.subheader("🎨 Estación de Diseño Mark 61")
    idea = st.text_input("¿Qué prototipo desea visualizar, Srta. Diana?")
    if st.button("🚀 INICIAR SÍNTESIS"):
        if idea:
            with st.spinner("Sintetizando..."):
                url = f"https://image.pollinations.ai/prompt/{idea.replace(' ', '%20')}?nologo=true"
                st.image(url, caption=f"Renderizado: {idea}")