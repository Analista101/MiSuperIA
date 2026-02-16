import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps, ImageFilter
from streamlit_mic_recorder import mic_recorder
import requests, io, base64, docx, pandas as pd

# --- 1. CONFIGURACIÓN ESTÉTICA DE LA TORRE STARK ---
st.set_page_config(page_title="JARVIS v120", layout="wide", page_icon="🛰️")

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

# --- 2. NÚCLEO DE INTELIGENCIA (AUTO-ESCANEO DE MODELOS) ---
model = None
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Escaneamos modelos disponibles para evitar el error 404
    for m_name in ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']:
        try:
            temp = genai.GenerativeModel(m_name)
            temp.generate_content("test", generation_config={"max_output_tokens": 1})
            model = temp
            st.toast(f"✅ Conectado a frecuencia: {m_name}")
            break
        except: continue
else:
    st.error("🚨 SRTA. DIANA: NO SE DETECTA LA LLAVE MAESTRA.")

# --- 3. INTERFAZ TÁCTICA MULTI-PESTAÑA ---
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS DOCS", "📸 ÓPTICO", "🎨 LABORATORIO"])

# --- PESTAÑA 0: COMANDO (VOZ + TEXTO) ---
with tabs[0]:
    st.subheader("🎙️ Interfaz de Voz y Texto")
    col_mic, col_chat = st.columns([1, 5])
    
    with col_mic:
        audio = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="jarvis_mic")
    
    chat_input = st.chat_input("Órdenes, Srta. Diana...")
    # Prioridad al audio si existe transcripción
    prompt = audio['transcript'] if audio and audio['transcript'] else chat_input

    if prompt and model:
        with st.chat_message("user"): st.write(prompt)
        with st.chat_message("assistant"):
            try:
                res = model.generate_content(f"Eres JARVIS. Responde elegante a la Srta. Diana: {prompt}")
                st.write(res.text)
            except Exception as e: st.error(f"Falla de enlace: {e}")

# --- PESTAÑA 1: ANÁLISIS UNIVERSAL (EXCEL/DOCX/TXT) ---
with tabs[1]:
    st.subheader("📊 Procesador de Datos Tácticos")
    file = st.file_uploader("Cargar Inteligencia", type=['txt', 'docx', 'xlsx', 'csv'])
    
    if file and st.button("🔍 INICIAR EXTRACCIÓN"):
        content = ""
        try:
            if file.name.endswith('.docx'):
                doc = docx.Document(file)
                content = "\n".join([p.text for p in doc.paragraphs])
            elif file.name.endswith('.xlsx') or file.name.endswith('.csv'):
                df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
                content = f"Datos de tabla: {df.head().to_string()}"
            else:
                content = file.read().decode()

            if model:
                res = model.generate_content(f"Resume esto para la Srta. Diana: {content[:10000]}")
                st.info(res.text)
        except Exception as e: st.error(f"Error procesando archivo: {e}")

# --- PESTAÑA 2: ÓPTICO (CON FILTROS AVANZADOS) ---
with tabs[2]:
    st.subheader("📸 Sensores Frontales")
    cam = st.camera_input("Activar Lente", key="cam_120")
    if cam:
        img_raw = Image.open(cam)
        filtro = st.radio("Filtro de Visión:", ["Normal", "Infrarrojo (B&W)", "Térmico (Falso Color)", "Contorno Táctico"], horizontal=True)
        
        # Aplicación de filtros mediante Pillow
        processed_img = img_raw.copy()
        if filtro == "Infrarrojo (B&W)": processed_img = ImageOps.grayscale(processed_img)
        elif filtro == "Térmico (Falso Color)": processed_img = ImageOps.colorize(ImageOps.grayscale(processed_img), "blue", "red")
        elif filtro == "Contorno Táctico": processed_img = processed_img.filter(ImageFilter.CONTOUR)
        
        st.image(processed_img, width=500, caption=f"Modo: {filtro}")
        
        if st.button("🔍 ANALIZAR OBJETIVO"):
            if model:
                try:
                    # Enviamos la imagen original para mejor análisis
                    res = model.generate_content(["Describe esta imagen para la Srta. Diana.", img_raw])
                    st.success(res.text)
                except Exception as e: st.error(f"Error de visión: {e}")

# --- PESTAÑA 3: LABORATORIO CREATIVO (POLLINATIONS) ---
with tabs[3]:
    st.subheader("🎨 Generador de Prototipos")
    idea = st.text_input("Describa el diseño que desea sintetizar:")
    estilo = st.selectbox("Estilo Visual:", ["Industrial Stark", "Cinematic Marvel", "Cyberpunk Night City", "Blueprint Técnico"])
    
    if st.button("🚀 INICIAR SÍNTESIS"):
        if idea:
            with st.spinner("Sintetizando imagen..."):
                final_prompt = f"{idea} in {estilo} style, high resolution, detailed"
                url = f"https://image.pollinations.ai/prompt/{final_prompt.replace(' ', '%20')}?nologo=true"
                st.image(url, caption=f"Prototipo Generado: {idea}")