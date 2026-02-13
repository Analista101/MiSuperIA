import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
from groq import Groq
from duckduckgo_search import DDGS
import edge_tts
import asyncio
import base64, io, datetime, requests
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURACIÓN DE LA TERMINAL STARK ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# Estética Stark
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #0a192f 0%, #020617 100%); color: #00f2ff; }
    .arc-reactor {
        width: 80px; height: 80px; border-radius: 50%; margin: 20px auto;
        background: radial-gradient(circle, #fff 0%, #00f2ff 40%, transparent 70%);
        box-shadow: 0 0 30px #00f2ff; border: 2px solid #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    .stTabs [data-baseweb="tab"] { color: #00f2ff !important; font-weight: bold; font-size: 18px; }
    .stChatMessage { background-color: rgba(26, 28, 35, 0.8); border: 1px solid #00f2ff; border-radius: 10px; }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- MOTOR VOCAL ---
async def generar_voz(texto):
    comunicador = edge_tts.Communicate(texto, "en-GB-RyanNeural", rate="+0%", pitch="-5Hz")
    output = io.BytesIO()
    async for chunk in comunicador.stream():
        if chunk["type"] == "audio":
            output.write(chunk["data"])
    return base64.b64encode(output.getvalue()).decode()

def hablar(texto):
    try:
        b64_audio = asyncio.run(generar_voz(texto))
        st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

# --- INICIALIZACIÓN ---
if "mensajes" not in st.session_state: st.session_state.mensajes = []

st.markdown("<h1 style='text-align: center; color: #00f2ff;'>🛰️ JARVIS: SISTEMA INTEGRADO DIANA</h1>", unsafe_allow_html=True)
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS UNIVERSAL", "📸 ÓPTICO", "🎨 LABORATORIO CREATIVO"])

# --- 1. PESTAÑA: COMANDO ---
with tabs[0]:
    col_mic, col_txt = st.columns([1, 5])
    prompt_final = None
    with col_mic:
        audio_stark = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_v46")
    with col_txt:
        chat_input = st.chat_input("Diga sus órdenes, Srta. Diana...")
    
    if audio_stark:
        with st.spinner("Traduciendo frecuencia..."):
            audio_bio = io.BytesIO(audio_stark['bytes'])
            audio_bio.name = "audio.wav"
            client_w = Groq(api_key=st.secrets["GROQ_API_KEY"])
            prompt_final = client_w.audio.transcriptions.create(file=audio_bio, model="whisper-large-v3", response_format="text")
    elif chat_input:
        prompt_final = chat_input

    if prompt_final:
        st.session_state.mensajes.append({"role": "user", "content": prompt_final})
        with st.chat_message("user"): st.markdown(prompt_final)
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = client.chat.completions.create(
            messages=[{"role": "system", "content": "Eres JARVIS, elegante británico. Llama a la usuaria Srta. Diana."}] + st.session_state.mensajes,
            model="llama-3.3-70b-versatile"
        ).choices[0].message.content
        with st.chat_message("assistant"):
            st.markdown(res)
            hablar(res)
        st.session_state.mensajes.append({"role": "assistant", "content": res})

# --- 2. PESTAÑA: ANÁLISIS UNIVERSAL ---
with tabs[1]:
    st.subheader("📊 Análisis de Datos Multi-Formato")
    f = st.file_uploader("Cargar archivos (Excel, CSV, TXT)", type=['csv', 'xlsx', 'xls', 'txt'])
    if f:
        try:
            if f.name.endswith('.csv'): df = pd.read_csv(f)
            elif f.name.endswith(('.xlsx', '.xls')): df = pd.read_excel(f)
            else: df = pd.read_csv(f, sep=None, engine='python')
            st.dataframe(df, use_container_width=True)
            if st.button("🧠 ANÁLISIS IA"):
                res_ia = Groq(api_key=st.secrets["GROQ_API_KEY"]).chat.completions.create(
                    messages=[{"role": "user", "content": f"Analiza estos datos brevemente como JARVIS para la Srta. Diana: {df.head(5).to_string()}"}],
                    model="llama-3.3-70b-versatile"
                ).choices[0].message.content
                st.info(res_ia)
                hablar("Análisis de datos finalizado, Srta. Diana.")
        except Exception as e: st.error(f"Error: {e}")

# --- 3. PESTAÑA: ÓPTICO (NUEVO MODELO 90B) ---
with tabs[2]:
    st.subheader("📸 Sensores Visuales")
    cam = st.camera_input("Activar Escáner")
    if cam:
        img = Image.open(cam)
        col_i, col_a = st.columns(2)
        with col_i:
            f_modo = st.selectbox("Filtro:", ["Normal", "Grises", "Térmico", "Nocturno"])
            if f_modo == "Grises": img = ImageOps.grayscale(img)
            elif f_modo == "Térmico": img = ImageOps.colorize(ImageOps.grayscale(img), "blue", "red")
            elif f_modo == "Nocturno": img = ImageOps.colorize(ImageOps.grayscale(img), "black", "green")
            st.image(img, use_container_width=True)
        with col_a:
            if st.button("🧠 ANALIZAR ESCENA"):
                img.thumbnail((512, 512)) # Optimización de ancho de banda
                buf = io.BytesIO()
                img.convert("RGB").save(buf, format="JPEG")
                img_b64 = base64.b64encode(buf.getvalue()).decode()
                try:
                    res_vis = Groq(api_key=st.secrets["GROQ_API_KEY"]).chat.completions.create(
                        messages=[{
                            "role": "user", 
                            "content": [
                                {"type": "text", "text": "JARVIS, describe esta imagen para la Srta. Diana con elegancia."}, 
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                            ]
                        }],
                        model="llama-3.2-90b-vision-preview" # <-- ACTUALIZACIÓN DE MODELO
                    ).choices[0].message.content
                    st.info(res_vis)
                    hablar(res_vis)
                except Exception as e: st.error(f"Falla en sensor óptico: {e}")

# --- 4. PESTAÑA: LABORATORIO CREATIVO ---
with tabs[3]:
    st.subheader("🎨 Estación de Diseño")
    est = st.selectbox("Estilo Visual:", ["Cinematic", "Blueprint", "Cyberpunk", "Anime", "Retro-Futurism", "Steampunk"])
    dis = st.text_area("Descripción del prototipo:")
    if st.button("🚀 RENDER"):
        url = f"https://image.pollinations.ai/prompt/{dis.replace(' ', '%20')}%20{est}?model=flux"
        st.image(url)
        hablar("Renderizado completo, Srta. Diana.")