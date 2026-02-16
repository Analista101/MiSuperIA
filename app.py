import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps, ImageFilter
from streamlit_mic_recorder import mic_recorder
import requests, io, base64, docx, pandas as pd

# --- 1. ESTÉTICA AVANZADA (EL REGRESO DEL REACTOR) ---
st.set_page_config(page_title="JARVIS v122", layout="wide", page_icon="🛰️")

st.markdown("""
    <style>
    .stApp { background-color: #010409; color: #00f2ff; }
    .stTabs [data-baseweb="tab"] { color: #00f2ff !important; font-size: 16px; }
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
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Usamos Flash como predeterminado por su velocidad
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("🚨 SRTA. DIANA: ACCESO DENEGADO. REVISE SU API KEY.")
    st.stop()

# --- 3. INTERFAZ TÁCTICA ---
st.title("🛰️ SISTEMA INTEGRADO DIANA v122")
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS DOCS", "📸 ÓPTICO", "🎨 LABORATORIO"])

# --- TAB 0: COMANDO (CHAT + VOZ) ---
with tabs[0]:
    st.subheader("🎙️ Centro de Comunicaciones")
    col_mic, col_chat = st.columns([1, 5])
    with col_mic:
        audio = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_122")
    
    # Usamos text_input para mayor fiabilidad si el chat_input falla
    prompt_input = st.text_input("Órdenes para JARVIS (Presione Enter):", key="txt_122")
    
    # Procesar audio o texto
    final_prompt = audio['transcript'] if audio and audio['transcript'] else prompt_input

    if final_prompt:
        with st.spinner("JARVIS procesando..."):
            try:
                res = model.generate_content(f"Eres JARVIS. Responde a la Srta. Diana: {final_prompt}")
                st.info(f"**JARVIS:** {res.text}")
            except Exception as e:
                st.error(f"Falla de enlace: {e}")

# --- TAB 1: ANÁLISIS DE DOCUMENTOS ---
with tabs[1]:
    st.subheader("📊 Lector de Inteligencia")
    file = st.file_uploader("Cargar archivo táctico", type=['txt', 'docx', 'xlsx', 'csv'])
    if file and st.button("🔍 EXTRAER DATOS"):
        try:
            if file.name.endswith('.docx'):
                doc = docx.Document(file)
                contenido = "\n".join([p.text for p in doc.paragraphs])
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
                contenido = df.to_string()
            else:
                contenido = file.read().decode()
            
            res = model.generate_content(f"Analiza este informe para la Srta. Diana: {contenido[:8000]}")
            st.success(res.text)
        except Exception as e: st.error(f"Error: {e}")

# --- TAB 2: ÓPTICO (CON FILTROS) ---
with tabs[2]:
    st.subheader("📸 Sensores Frontales")
    cam = st.camera_input("Escanear", key="cam_122")
    if cam:
        img_raw = Image.open(cam)
        filtro = st.radio("Modo:", ["Normal", "Infrarrojo", "Térmico", "Táctico"], horizontal=True)
        
        proc_img = img_raw.copy()
        if filtro == "Infrarrojo": proc_img = ImageOps.grayscale(proc_img)
        elif filtro == "Térmico": proc_img = ImageOps.colorize(ImageOps.grayscale(proc_img), "blue", "red")
        elif filtro == "Táctico": proc_img = proc_img.filter(ImageFilter.CONTOUR)
        
        st.image(proc_img, width=500)
        if st.button("🔍 ANALIZAR OBJETIVO"):
            try:
                res_v = model.generate_content(["Actúa como JARVIS. Analiza esta imagen técnica.", img_raw])
                st.info(res_v.text)
            except Exception as e: st.error(f"Error de visión: {e}")

# --- TAB 3: LABORATORIO (GENERADOR) ---
with tabs[3]:
    st.subheader("🎨 Estación de Diseño")
    idea = st.text_input("¿Qué prototipo desea visualizar?")
    if st.button("🚀 SINTETIZAR"):
        if idea:
            url = f"https://image.pollinations.ai/prompt/{idea.replace(' ', '%20')}?nologo=true"
            st.image(url, caption=f"Renderizado: {idea}")