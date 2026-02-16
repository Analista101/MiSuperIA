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

# --- 1. ESTÉTICA Y DISEÑO ---
st.set_page_config(page_title="JARVIS v148", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #010409; color: #00f2ff; }
    .arc-reactor {
        width: 55px; height: 55px; border-radius: 50%; margin: 10px auto;
        background: radial-gradient(circle, #fff 0%, #00f2ff 40%, transparent 70%);
        box-shadow: 0 0 20px #00f2ff; border: 2px solid #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    .stButton>button { width: 100%; border: 1px solid #00f2ff; background: rgba(0, 242, 255, 0.1); color: #00f2ff; }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- 2. NÚCLEO DE INTELIGENCIA ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    modelo_texto = "llama-3.3-70b-versatile"
    modelo_vision = "llama-3.2-11b-vision-preview"
else:
    st.error("🚨 SRTA. DIANA: FALTA LA LLAVE DEL REACTOR (API KEY).")
    st.stop()

# --- 3. INTERFAZ TÁCTICA ---
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS PROFUNDO", "🎨 LABORATORIO"])

# --- PESTAÑA 0: COMANDO ---
with tabs[0]:
    st.subheader("🎙️ Terminal de Voz y Capturas")
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_a: mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_148")
    with col_b: pasted_img = paste_button(label="📋 PEGAR CAPTURA (CTRL+V)", key="paster_148")
    with col_c: 
        if st.button("🗑️ REINICIAR"): st.rerun()

    chat_input = st.chat_input("Órdenes para JARVIS...")
    
    # Procesamiento de Imagen Pegada
    if pasted_img.image_data is not None:
        img = pasted_img.image_data
        st.image(img, caption="Vista de Cámara", width=350)
        if chat_input:
            with st.chat_message("assistant"):
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                res = client.chat.completions.create(
                    model=modelo_vision,
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": f"JARVIS, analiza esto: {chat_input}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                    ]}]
                )
                st.write(res.choices[0].message.content)
    elif chat_input:
        with st.chat_message("assistant"):
            res = client.chat.completions.create(model=modelo_texto, messages=[{"role": "user", "content": chat_input}])
            st.write(res.choices[0].message.content)

# --- PESTAÑA 1: ANÁLISIS DOCS/IMG (OPTIMIZADO PARA PESO) ---
with tabs[1]:
    st.subheader("📊 Escaneo de Inteligencia Multimodal")
    file = st.file_uploader("Subir Reporte o Evidencia", type=['pdf', 'docx', 'xlsx', 'txt', 'png', 'jpg', 'jpeg'])
    
    if file and st.button("🔍 INICIAR PROTOCOLO DE LECTURA"):
        with st.spinner("JARVIS analizando suministros..."):
            try:
                if file.type.startswith('image/'):
                    img_file = Image.open(file)
                    st.image(img_file, width=400)
                    buffered = io.BytesIO()
                    img_file.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    res = client.chat.completions.create(
                        model=modelo_vision,
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Reporte técnico de la imagen de la Srta. Diana."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                        ]}]
                    )
                    st.success(res.choices[0].message.content)
                else:
                    text_data = ""
                    if file.name.endswith('.pdf'):
                        reader = PyPDF2.PdfReader(file)
                        # Gestión de archivos pesados: solo leemos fragmentos clave
                        text_data = "\n".join([p.extract_text() for p in reader.pages[:12]])
                    elif file.name.endswith('.docx'):
                        doc = docx.Document(file)
                        text_data = "\n".join([p.text for p in doc.paragraphs])
                    elif file.name.endswith('.xlsx'):
                        df = pd.read_excel(file)
                        text_data = f"Vista previa de datos:\n{df.head(40).to_string()}"
                    
                    res = client.chat.completions.create(
                        model=modelo_texto,
                        messages=[{"role": "user", "content": f"Resumen ejecutivo del documento: {text_data[:12000]}"}]
                    )
                    st.success(res.choices[0].message.content)
            except Exception as e: st.error(f"Falla en el escáner: {e}")

# --- PESTAÑA 2: LABORATORIO (SATÉLITE HUGGING FACE v150) ---
with tabs[2]:
    st.subheader("🎨 Estación de Diseño Mark 80")
    st.write("Generando a través de la Red Neuronal Hugging Face (Independiente).")
    
    idea = st.text_input("Describa el prototipo:", key="input_hf")
    estilo = st.selectbox("Acabado:", ["Cinematic", "Technical Drawing", "Cyberpunk", "Realistic"], key="style_hf")
    
    if st.button("🚀 MATERIALIZAR DISEÑO", key="btn_hf"):
        if idea:
            with st.spinner("JARVIS: Estableciendo túnel con Hugging Face..."):
                try:
                    # Usamos un modelo de alto rendimiento: Stable Diffusion XL
                    # Esta URL es una API de inferencia, no una imagen directa
                    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
                    
                    # El prompt se enriquece con el estilo
                    payload = {"inputs": f"{idea}, {estilo}, high quality, 8k resolution"}
                    
                    # JARVIS realiza la petición técnica
                    response = requests.post(API_URL, json=payload, timeout=40)
                    
                    if response.status_code == 200:
                        # Recibimos los bytes de la imagen directamente
                        image_bytes = response.content
                        img_final = Image.open(io.BytesIO(image_bytes))
                        
                        # Renderizado nativo de Streamlit
                        st.image(img_final, caption=f"Prototipo: {idea}", use_container_width=True)
                        st.success("Sintonía lograda. Imagen generada localmente en el servidor.")
                    elif response.status_code == 503:
                        st.warning("⚠️ El modelo se está cargando en el satélite. Reintente en 20 segundos.")
                    else:
                        st.error(f"Error de protocolo {response.status_code}: {response.text}")
                        
                except Exception as e:
                    st.error(f"Falla en el enlace de Hugging Face: {e}")