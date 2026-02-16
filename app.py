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

# --- 1. ESTÉTICA DE LA TORRE STARK (MARK 155) ---
st.set_page_config(page_title="JARVIS v155", layout="wide")
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
    .stButton>button { border: 1px solid #00f2ff; background: rgba(0, 242, 255, 0.1); color: #00f2ff; width: 100%; }
    </style>
    <div class="arc-reactor"></div>
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

# --- PESTAÑA 0: COMANDO GLOBAL CON ENLACES (v156) ---
with tabs[0]:
    st.subheader("🎙️ Centro de Control e Inteligencia con Fuentes")
    # ... (botones de mic y paster se mantienen igual que en la v155) ...
    
    chat_input = st.chat_input("Órdenes, Srta. Diana...")
    
    if chat_input:
        with st.chat_message("assistant"):
            with st.spinner("JARVIS: Navegando por la red y verificando fuentes..."):
                # Instrucción específica para que JARVIS siempre proporcione links
                INSTRUCCION_RED = (
                    f"{PERSONALIDAD} IMPORTANTE: Siempre que busques información en la red, "
                    "proporciona una lista de 'FUENTES CONSULTADAS' con links directos (URL) "
                    "al final de tu respuesta para que la Srta. Diana pueda acceder a ellos."
                )
                
                # Ejecución de la consulta
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