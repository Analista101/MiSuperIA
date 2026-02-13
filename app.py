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

# Estética Stark (Reactor Arc y Colores)
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

# --- MOTOR VOCAL (BRITÁNICO) ---
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

# --- 1. PESTAÑA: COMANDO (RECONECTADA) ---
with tabs[0]:
    col_mic, col_txt = st.columns([1, 5])
    prompt_final = None
    with col_mic:
        # Micrófono de emergencia siempre activo
        audio_stark = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_v50")
    with col_txt:
        chat_input = st.chat_input("Diga sus órdenes, Srta. Diana...")
    
    if audio_stark:
        with st.spinner("Descifrando frecuencia vocal..."):
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

# --- 2. PESTAÑA: ANÁLISIS (CARGADOR UNIVERSAL) ---
with tabs[1]:
    st.subheader("📊 Análisis de Datos Multi-Formato")
    f = st.file_uploader("Cargar archivos (Excel, CSV, TXT)", type=['csv', 'xlsx', 'xls', 'txt'])
    if f:
        try:
            if f.name.endswith('.csv'): df = pd.read_csv(f)
            elif f.name.endswith(('.xlsx', '.xls')): df = pd.read_excel(f)
            else: df = pd.read_csv(f, sep=None, engine='python')
            st.dataframe(df, use_container_width=True)
            if st.button("🧠 ANÁLISIS DE INTELIGENCIA"):
                res_ia = Groq(api_key=st.secrets["GROQ_API_KEY"]).chat.completions.create(
                    messages=[{"role": "user", "content": f"Analiza estos datos brevemente como JARVIS para la Srta. Diana: {df.head(10).to_string()}"}],
                    model="llama-3.3-70b-versatile"
                ).choices[0].message.content
                st.info(res_ia)
                hablar("Análisis de datos finalizado, Srta. Diana.")
        except Exception as e: st.error(f"Error de procesamiento: {e}")

# --- 3. PESTAÑA: ÓPTICO (CONSOLA DE DIAGNÓSTICO) ---
with tabs[2]:
    st.subheader("📸 Sensores Visuales")
    cam = st.camera_input("Activar Escáner")
    if cam:
        img = Image.open(cam)
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            f_modo = st.selectbox("Filtro de Espectro:", ["Normal", "Grises", "Térmico", "Nocturno"])
            if f_modo == "Grises": img = ImageOps.grayscale(img)
            elif f_modo == "Térmico": img = ImageOps.colorize(ImageOps.grayscale(img), "blue", "red")
            elif f_modo == "Nocturno": img = ImageOps.colorize(ImageOps.grayscale(img), "black", "green")
            st.image(img, use_container_width=True)
        with col_v2:
            st.warning("⚠️ SATÉLITES DE VISIÓN EN MANTENIMIENTO")
            st.write("Srta. Diana, Groq ha desactivado temporalmente sus modelos de visión. Los filtros visuales internos (Térmico/Nocturno) siguen operativos.")

# --- 4. PESTAÑA: LABORATORIO CREATIVO (MARK 52 - BYPASS) ---
with tabs[3]:
    st.subheader("🎨 Estación de Diseño Mark 52")
    c1, c2 = st.columns([2, 1])
    
    with c2:
        estilo = st.selectbox("Estilo Visual:", [
            "Cinematic", "Blueprint", "Cyberpunk", "Anime", 
            "Retro-Futurism", "Steampunk", "Neon Glow"
        ])
        detalles = st.select_slider("Calidad:", options=["Boceto", "Estándar", "Épico"])
    
    with c1:
        diseno = st.text_area("Descripción del prototipo:", placeholder="Ej: Gato Ninja con armadura tecnológica...")
        
        if st.button("🚀 INICIAR RENDERIZADO"):
            if diseno:
                with st.spinner("Sintetizando moléculas visuales..."):
                    try:
                        # Generamos un número aleatorio para evitar duplicados
                        import random
                        seed = random.randint(0, 999999)
                        
                        # Construimos el prompt
                        prompt_url = f"{diseno}, {estilo} style, masterpiece, high quality".replace(" ", "%20")
                        url = f"https://image.pollinations.ai/prompt/{prompt_url}?model=flux&width=1024&height=1024&seed={seed}"
                        
                        # PROTOCOLO DE DESCARGA: Intentamos obtener los datos de la imagen
                        response = requests.get(url, timeout=20)
                        
                        if response.status_code == 200:
                            # Si la descarga es exitosa, mostramos la imagen directamente
                            st.image(response.content, caption=f"Renderizado {estilo} completado, Srta. Diana.", use_container_width=True)
                            hablar(f"Prototipo finalizado, Srta. Diana. Los sistemas están listos.")
                        else:
                            st.error(f"Error de enlace: Código {response.status_code}. El servidor está saturado.")
                    except Exception as e:
                        st.error(f"Falla en el sintetizador: {e}")
            else:
                st.warning("Srta. Diana, indique qué desea que renderice.")