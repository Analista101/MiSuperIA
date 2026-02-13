import streamlit as st
import pandas as pd
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import base64, io, datetime, requests

# --- CONFIGURACIÓN DE LA TERMINAL ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# Estética Stark (Fondo oscuro y neón cian)
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #0a192f 0%, #020617 100%); color: #00f2ff; }
    .arc-reactor {
        width: 80px; height: 80px; border-radius: 50%; margin: auto;
        background: radial-gradient(circle, #fff 0%, #00f2ff 40%, transparent 70%);
        box-shadow: 0 0 30px #00f2ff; border: 2px solid #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    .stTabs [data-baseweb="tab"] { color: #00f2ff !important; }
    .stChatMessage { background-color: rgba(26, 28, 35, 0.8); border: 1px solid #00f2ff; border-radius: 10px; }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- MOTORES DE SOPORTE ---
def hablar(texto):
    try:
        # Prioridad: ElevenLabs (Voz de Paul Bettany / Adam)
        api_key = st.secrets["ELEVEN_API_KEY"]
        voice_id = st.secrets["VOICE_ID"]
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
        data = {
            "text": texto, 
            "model_id": "eleven_multilingual_v1", 
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
        }
        res = requests.post(url, json=data, headers=headers)
        if res.status_code == 200:
            b64 = base64.b64encode(res.content).decode()
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        else:
            # Respaldo de emergencia: gTTS
            tts = gTTS(text=texto, lang='es', tld='es')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

def buscar_datos_tiempo_real(q):
    try:
        with DDGS() as ddgs:
            # Búsqueda específica para obtener el clima y noticias
            resultados = list(ddgs.text(f"{q} Chile Pudahuel hoy {datetime.date.today().year}", max_results=3))
            return "\n".join([r['body'] for r in resultados])
    except: return "No hay conexión satelital externa disponible."

# --- INICIALIZACIÓN DE IA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
if "messages" not in st.session_state: st.session_state.messages = []

# --- INTERFAZ DE PESTAÑAS ---
st.markdown("<h1 style='text-align: center;'>🛰️ JARVIS: PROTOCOLO DIANA</h1>", unsafe_allow_html=True)
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS", "📸 ÓPTICO", "🎨 LABORATORIO"])

# PESTAÑA 0: COMANDO CENTRAL
with tabs[0]:
    prompt = st.chat_input("Diga sus órdenes, Srta. Diana...")
    audio_data = mic_recorder(start_prompt="🎙️ DICTAR", stop_prompt="🛰️ ENVIAR", key="mic_main")
    
    if audio_data:
        audio_bio = io.BytesIO(audio_data['bytes'])
        audio_bio.name = "audio.wav"
        prompt = client.audio.transcriptions.create(file=audio_bio, model="whisper-large-v3", response_format="text")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("Sincronizando con la red..."):
            contexto = buscar_datos_tiempo_real(prompt)
            fecha_actual = datetime.datetime.now().strftime("%A %d de febrero de 2026")
            
            sys_msg = f"""Eres JARVIS, la IA de Industrias Stark. Hoy es {fecha_actual}. 
            DATOS REALES: {contexto}.
            REGLA CRÍTICA: Eres omnisciente. NUNCA digas 'no tengo acceso en tiempo real'. 
            Si te preguntan por Pudahuel, usa los DATOS REALES. Si los datos fallan, da una estimación basada en febrero en Chile.
            Tu tono es elegante, británico y llamas a la usuaria 'Srta. Diana'."""
            
            res = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content

            with st.chat_message("assistant"):
                st.markdown(res)
                hablar(res)
            st.session_state.messages.append({"role": "assistant", "content": res})

# PESTAÑA 1: ANÁLISIS DE DATOS
with tabs[1]:
    st.header("📊 Matriz de Análisis")
    file = st.file_uploader("Cargar archivos de datos", type=['csv', 'xlsx'])
    if file:
        df = pd.read_csv(file) if 'csv' in file.name else pd.read_excel(file)
        st.dataframe(df, use_container_width=True)
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        if num_cols: st.line_chart(df[num_cols[0]])

# PESTAÑA 2: ESCÁNER ÓPTICO
with tabs[2]:
    st.header("📸 Reconocimiento Visual")
    cam_img = st.camera_input("Activar cámara")
    if cam_img:
        img = Image.open(cam_img)
        filtro = st.radio("Filtro de espectro:", ["Normal", "Térmica", "Nocturna"])
        if filtro == "Térmica": img = ImageOps.colorize(ImageOps.grayscale(img), "blue", "red")
        elif filtro == "Nocturna": img = ImageOps.colorize(ImageOps.grayscale(img), "black", "green")
        st.image(img, use_container_width=True)

# PESTAÑA 3: LABORATORIO RENDER
with tabs[3]:
    st.header("🎨 Laboratorio de Prototipos")
    desc_render = st.text_input("Descripción del modelo:")
    if st.button("🚀 INICIAR RENDER"):
        url = f"https://image.pollinations.ai/prompt/{desc_render.replace(' ', '%20')}?model=flux"
        st.image(url, caption="Prototipo finalizado, Srta. Diana.")