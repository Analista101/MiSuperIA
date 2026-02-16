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

# --- 1. CONFIGURACIÓN DE SISTEMAS Y ESTÉTICA STARK ---
st.set_page_config(page_title="JARVIS v153 - Stark Industries", layout="wide")
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
    .stButton>button { border: 1px solid #00f2ff; background: rgba(0, 242, 255, 0.1); color: #00f2ff; font-weight: bold; }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- 2. VERIFICACIÓN DE CREDENCIALES ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    HF_TOKEN = st.secrets["HF_TOKEN"]
    modelo_texto = "llama-3.3-70b-versatile"
    modelo_vision = "llama-3.2-11b-vision-preview"
except Exception as e:
    st.error(f"🚨 ERROR CRÍTICO DE CREDENCIALES: {e}")
    st.info("Asegúrese de tener GROQ_API_KEY y HF_TOKEN en sus Secrets.")
    st.stop()

# --- 3. INTERFAZ DE COMANDO ---
tabs = st.tabs(["💬 COMANDO HÍBRIDO", "📊 ANÁLISIS DE INTELIGENCIA", "🎨 LABORATORIO DE DISEÑO"])

# --- PESTAÑA 0: COMANDO (VOZ + PEGAR IMAGEN) ---
with tabs[0]:
    st.subheader("🎙️ Centro de Control Multimodal")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1: mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_153")
    with c2: pasted_img = paste_button(label="📋 PEGAR CAPTURA", key="paste_153")
    with c3: 
        if st.button("🗑️ RESET"): st.rerun()

    chat_input = st.chat_input("Escriba su orden, Srta. Diana...")
    
    if pasted_img.image_data is not None:
        img_pasted = pasted_img.image_data
        st.image(img_pasted, caption="Imagen en Memoria", width=400)
        if chat_input:
            with st.chat_message("assistant"):
                buffered = io.BytesIO()
                img_pasted.save(buffered, format="PNG")
                img_b64 = base64.b64encode(buffered.getvalue()).decode()
                res = client.chat.completions.create(
                    model=modelo_vision,
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": chat_input},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                    ]}]
                )
                st.write(res.choices[0].message.content)
    elif chat_input:
        with st.chat_message("assistant"):
            res = client.chat.completions.create(model=modelo_texto, messages=[{"role": "user", "content": chat_input}])
            st.write(res.choices[0].message.content)

# --- PESTAÑA 1: ANÁLISIS (CARGA DE ARCHIVOS PESADOS) ---
with tabs[1]:
    st.subheader("📊 Análisis de Datos y Evidencia")
    uploaded_file = st.file_uploader("Subir Doc (PDF, DOCX, XLSX) o Imagen", type=['pdf','docx','xlsx','png','jpg','jpeg'])
    
    if uploaded_file and st.button("🔍 ESCANEAR"):
        with st.spinner("JARVIS procesando archivos..."):
            try:
                if uploaded_file.type.startswith('image/'):
                    img_ready = Image.open(uploaded_file)
                    st.image(img_ready, width=400)
                    buffered = io.BytesIO()
                    img_ready.save(buffered, format="PNG")
                    img_b64 = base64.b64encode(buffered.getvalue()).decode()
                    res = client.chat.completions.create(
                        model=modelo_vision,
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Analiza esta imagen y resume los puntos clave."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                        ]}]
                    )
                    st.success(res.choices[0].message.content)
                else:
                    text_content = ""
                    if uploaded_file.name.endswith('.pdf'):
                        reader = PyPDF2.PdfReader(uploaded_file)
                        # Leemos hasta 15 páginas para manejar archivos pesados
                        text_content = "\n".join([p.extract_text() for p in reader.pages[:15]])
                    elif uploaded_file.name.endswith('.docx'):
                        doc = docx.Document(uploaded_file)
                        text_content = "\n".join([p.text for p in doc.paragraphs])
                    elif uploaded_file.name.endswith('.xlsx'):
                        df = pd.read_excel(uploaded_file)
                        text_content = df.head(50).to_string()
                    
                    res = client.chat.completions.create(
                        model=modelo_texto,
                        messages=[{"role": "user", "content": f"Resume este documento técnico: {text_content[:12000]}"}]
                    )
                    st.success(res.choices[0].message.content)
            except Exception as e: st.error(f"Falla en el escaneo: {e}")

# --- PESTAÑA 2: LABORATORIO (SÍNTESIS CON LLAVE HF) ---
with tabs[2]:
    st.subheader("🎨 Estación de Diseño Mark 83")
    idea = st.text_input("Defina el prototipo:")
    estilo = st.selectbox("Estética:", ["Cinematic Marvel", "Technical Blueprint", "Cyberpunk", "Industrial Stark"])
    
    if st.button("🚀 MATERIALIZAR", key="btn_final"):
        if idea:
            with st.spinner("Sintetizando a través de Hugging Face..."):
                try:
                    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
                    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                    payload = {"inputs": f"{idea}, {estilo}, highly detailed, 8k", "options": {"wait_for_model": True}}
                    
                    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
                    if response.status_code == 200:
                        img_bytes = io.BytesIO(response.content)
                        st.image(Image.open(img_bytes), caption=f"Prototipo: {idea}", use_container_width=True)
                        st.success("Diseño materializado exitosamente.")
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e: st.error(f"Falla de síntesis: {e}")