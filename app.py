import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
from groq import Groq
from duckduckgo_search import DDGS
import edge_tts
import asyncio
import base64, io, datetime, requests
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURACIÓN DE LA TERMINAL ---
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
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS UNIVERSAL", "📸 ÓPTICO INTELIGENTE", "🎨 LABORATORIO CREATIVO"])

# (Omitimos COMANDO y ANÁLISIS para centrarnos en sus peticiones)

# --- 3. PESTAÑA: ÓPTICO INTELIGENTE (NUEVO ANÁLISIS IA) ---
with tabs[2]:
    st.subheader("📸 Sensores Visuales con Análisis de IA")
    cam = st.camera_input("Activar Escáner")
    if cam:
        img = Image.open(cam)
        col_img, col_an = st.columns([1, 1])
        
        with col_img:
            modo = st.selectbox("Filtro de Espectro:", ["Normal", "Grises", "Térmico", "Nocturno"])
            if modo == "Grises": img = ImageOps.grayscale(img)
            elif modo == "Térmico": img = ImageOps.colorize(ImageOps.grayscale(img), "blue", "red")
            elif modo == "Nocturno": img = ImageOps.colorize(ImageOps.grayscale(img), "black", "green")
            st.image(img, use_container_width=True)
        
        with col_an:
            st.write("🔍 **Protocolo de Reconocimiento Activo**")
            if st.button("🧠 ANALIZAR ESCENA"):
                # Convertimos imagen a base64 para la IA (Groq Vision)
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                img_b64 = base64.b64encode(buffered.getvalue()).decode()
                
                with st.spinner("Analizando patrones visuales..."):
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    # Usamos el modelo Llama Vision para describir la imagen
                    res = client.chat.completions.create(
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Describe lo que ves en esta imagen de forma profesional y elegante como JARVIS para la Srta. Diana."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                            ]
                        }],
                        model="llama-3.2-11b-vision-preview"
                    ).choices[0].message.content
                    st.info(res)
                    hablar(res)

# --- 4. PESTAÑA: LABORATORIO CREATIVO (BIBLIOTECA EXPANDIDA) ---
with tabs[3]:
    st.subheader("🎨 Estación de Diseño Mark 44")
    c1, c2 = st.columns([2, 1])
    with c2:
        # Biblioteca de estilos ampliada
        estilo = st.selectbox("Estilo Visual:", [
            "Cinematic", "Blueprint (Technical Drawing)", "Cyberpunk 2077", 
            "Hyper-Realistic", "Steampunk", "Watercolor Art", 
            "Retro-Futurism (1950s)", "Low-Poly Digital", "Anime Studio Ghibli",
            "Oil Painting", "Concept Art", "Neon Lights"
        ])
        calidad = st.select_slider("Nivel de Detalle:", options=["Draft", "Standard", "Ultra High Res"])
        iluminacion = st.radio("Iluminación:", ["Natural", "Cinematic Gold", "Cold Neon", "Dramatic Shadow"])
    
    with c1:
        diseno = st.text_area("Descripción del prototipo:", placeholder="Describa su visión, Srta. Diana...")
        if st.button("🚀 INICIAR SÍNTESIS VISUAL"):
            with st.spinner("Generando render..."):
                full_prompt = f"{diseno}, {estilo} style, {iluminacion} lighting, {calidad}, masterpiece"
                url = f"https://image.pollinations.ai/prompt/{full_prompt.replace(' ', '%20')}?model=flux"
                st.image(url, caption=f"Sintetizador completado: Estilo {estilo}")
                hablar(f"El prototipo ha sido renderizado en estilo {estilo}, Srta. Diana.")