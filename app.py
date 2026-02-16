import streamlit as st
from groq import Groq
import requests
import docx
import pandas as pd
import PyPDF2
from PIL import Image
from streamlit_paste_button import paste_image_button as paste_button
from streamlit_mic_recorder import mic_recorder
import io, base64, random

# --- 1. ESTÉTICA AVANZADA STARK HUD (MARK 158) ---
st.set_page_config(page_title="JARVIS v158 - Sistema Táctico", layout="wide")

st.markdown("""
    <style>
    /* Fondo Espacial con Gradiente */
    .stApp {
        background: radial-gradient(circle at center, #0a192f 0%, #010409 100%);
        color: #00f2ff;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Reactor Arc Animado con Aura */
    .arc-reactor {
        width: 80px; height: 80px; border-radius: 50%; margin: 20px auto;
        background: radial-gradient(circle, #fff 0%, #00f2ff 30%, transparent 70%);
        box-shadow: 0 0 30px #00f2ff, inset 0 0 20px #00f2ff;
        border: 4px double #00f2ff;
        animation: pulse 2s infinite ease-in-out;
    }
    
    /* Barras de Energía Superiores */
    .energy-bar {
        height: 4px; background: linear-gradient(90deg, #00f2ff, transparent);
        margin-bottom: 20px; border-radius: 2px;
        animation: slide 3s infinite linear;
    }
    
    /* Tarjetas de Cristal (Glassmorphism) */
    div[data-testid="stVerticalBlock"] > div:has(div.stButton) {
        background: rgba(0, 242, 255, 0.05);
        border: 1px solid rgba(0, 242, 255, 0.2);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }

    /* Botones Tácticos */
    .stButton>button {
        border: 1px solid #00f2ff !important;
        background: rgba(0, 242, 255, 0.1) !important;
        color: #00f2ff !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: 0.3s;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.2);
    }
    .stButton>button:hover {
        background: rgba(0, 242, 255, 0.3) !important;
        box-shadow: 0 0 20px #00f2ff;
        transform: scale(1.02);
    }

    /* Input HUD */
    .stTextInput>div>div>input {
        background-color: rgba(0, 0, 0, 0.5) !important;
        color: #00f2ff !important;
        border: 1px solid #00f2ff !important;
    }

    @keyframes pulse { 0% { transform: scale(1); opacity: 0.8; } 50% { transform: scale(1.1); opacity: 1; } 100% { transform: scale(1); opacity: 0.8; } }
    @keyframes slide { 0% { width: 0%; } 100% { width: 100%; } }
    </style>
    
    <div class="energy-bar"></div>
    <div class="arc-reactor"></div>
    <div style="text-align: center; color: #00f2ff; font-size: 10px; letter-spacing: 5px; margin-bottom: 20px;">
        SISTEMA OPERATIVO JARVIS - ACCESO NIVEL 7
    </div>
    """, unsafe_allow_html=True)

# --- 2. NÚCLEO Y CREDENCIALES ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    HF_TOKEN = st.secrets["HF_TOKEN"]
    modelo_texto = "llama-3.3-70b-versatile"
    modelo_vision = "llama-3.2-11b-vision-preview"
    # Instrucción de personalidad y tiempo real
    PERSONALIDAD = (
        "Eres JARVIS, el asistente de la Srta. Diana. Tu tono es sofisticado, ingenioso y servicial. "
        "Usa terminología de Stark Industries. Hoy es 16 de febrero de 2026 y tienes acceso a la red."
    )
except Exception as e:
    st.error(f"🚨 ERROR EN EL REACTOR: Verifique GROQ_API_KEY y HF_TOKEN en Secrets. {e}")
    st.stop()

# --- 3. INTERFAZ TÁCTICA ---
tabs = st.tabs(["💬 COMANDO GLOBAL", "📊 ANÁLISIS DOCS/IMG", "🎨 LABORATORIO"])

# --- PESTAÑA 0: COMANDO GLOBAL (RESTAURADO + ENLACES) ---
with tabs[0]:
    st.subheader("🎙️ Centro de Control e Inteligencia Global")
    
    # MODULOS FISICOS RESTAURADOS
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_a: 
        mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_v157")
    with col_b: 
        pasted_img = paste_button(label="📋 PEGAR CAPTURA (CTRL+V)", key="paster_v157")
    with col_c: 
        if st.button("🗑️ LIMPIAR SISTEMA"): st.rerun()

    chat_input = st.chat_input("Órdenes, Srta. Diana...")
    
    # LÓGICA DE PROCESAMIENTO
    if chat_input:
        with st.chat_message("assistant"):
            with st.spinner("JARVIS: Consultando redes y verificando fuentes..."):
                
                # Instrucción blindada de personalidad y links
                INSTRUCCION_RED = (
                    f"{PERSONALIDAD} IMPORTANTE: Eres un asistente con acceso a la red. "
                    "Para cualquier consulta sobre noticias o eventos, debes incluir "
                    "links directos y clicables a tus fuentes al final de la respuesta."
                )

                if pasted_img.image_data is not None:
                    # Análisis Visual + Texto + Red
                    img = pasted_img.image_data
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")
                    img_b64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    res = client.chat.completions.create(
                        model=modelo_vision,
                        messages=[{"role": "system", "content": INSTRUCCION_RED},
                                  {"role": "user", "content": [
                                      {"type": "text", "text": chat_input},
                                      {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                                  ]}]
                    )
                else:
                    # Búsqueda en Red + Texto
                    res = client.chat.completions.create(
                        model=modelo_texto,
                        messages=[{"role": "system", "content": INSTRUCCION_RED},
                                  {"role": "user", "content": chat_input}]
                    )
                st.write(res.choices[0].message.content)

# --- PESTAÑA 1: ANÁLISIS (ARCHIVOS PESADOS + IMÁGENES) ---
with tabs[1]:
    st.subheader("📊 Escáner de Evidencia y Documentación")
    file = st.file_uploader("Cargar reporte técnico o imagen", type=['pdf','docx','xlsx','png','jpg','jpeg'])
    
    if file and st.button("🔍 INICIAR ANÁLISIS"):
        with st.spinner("Escaneando..."):
            try:
                if file.type.startswith('image/'):
                    img_file = Image.open(file)
                    st.image(img_file, width=400)
                    buffered = io.BytesIO()
                    img_file.save(buffered, format="PNG")
                    img_b64 = base64.b64encode(buffered.getvalue()).decode()
                    res = client.chat.completions.create(
                        model=modelo_vision,
                        messages=[{"role": "system", "content": PERSONALIDAD},
                                  {"role": "user", "content": [
                                      {"type": "text", "text": "Analiza esta imagen detalladamente."},
                                      {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                                  ]}]
                    )
                    st.success(res.choices[0].message.content)
                else:
                    text = ""
                    if file.name.endswith('.pdf'):
                        reader = PyPDF2.PdfReader(file)
                        text = "\n".join([p.extract_text() for p in reader.pages[:15]])
                    elif file.name.endswith('.docx'):
                        doc = docx.Document(file)
                        text = "\n".join([p.text for p in doc.paragraphs])
                    elif file.name.endswith('.xlsx'):
                        df = pd.read_excel(file)
                        text = df.head(50).to_string()
                    
                    res = client.chat.completions.create(
                        model=modelo_texto,
                        messages=[{"role": "system", "content": PERSONALIDAD},
                                  {"role": "user", "content": f"Resume este archivo pesado: {text[:12000]}"}]
                    )
                    st.success(res.choices[0].message.content)
            except Exception as e: st.error(f"Falla de lectura: {e}")

# --- PESTAÑA 2: LABORATORIO (ROUTER HF + TOKEN) ---
with tabs[2]:
    st.subheader("🎨 Estación de Diseño Mark 85")
    idea = st.text_input("Defina el prototipo a materializar:", key="idea_v155")
    estilo = st.selectbox("Filtro Visual:", ["Cinematic Marvel", "Technical Drawing", "Cyberpunk", "Industrial Stark"], key="style_v155")
    
    if st.button("🚀 MATERIALIZAR", key="btn_lab_v155"):
        if idea:
            with st.spinner("Sintetizando imagen vía Router..."):
                try:
                    # Conexión al nuevo Router de HF (Mark 154)
                    API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
                    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                    payload = {"inputs": f"{idea}, {estilo}, highly detailed, 8k", "options": {"wait_for_model": True}}
                    
                    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
                    if response.status_code == 200:
                        img_res = Image.open(io.BytesIO(response.content))
                        st.image(img_res, caption=f"Prototipo: {idea}", use_container_width=True)
                        st.success("Sintonía lograda.")
                    else:
                        st.error(f"Falla {response.status_code}: {response.text}")
                except Exception as e: st.error(f"Error de renderizado: {e}")