import streamlit as st
from groq import Groq
import docx
import pandas as pd
import PyPDF2
from PIL import Image
from streamlit_paste_button import paste_image_button as paste_button
from streamlit_mic_recorder import mic_recorder
from gradio_client import Client
import io, base64

# --- 1. ESTÉTICA DE LA TORRE STARK ---
st.set_page_config(page_title="JARVIS v144", layout="wide")
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
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- 2. NÚCLEO (GROQ) ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    modelo_texto = "llama-3.3-70b-versatile"
    modelo_vision = "llama-3.2-11b-vision-preview"
else:
    st.error("🚨 SRTA. DIANA: ACCESO DENEGADO. REVISE SECRETS.")
    st.stop()

# --- 3. INTERFAZ TÁCTICA ---
tabs = st.tabs(["💬 COMANDO HÍBRIDO", "📊 ANÁLISIS DOCS/IMG", "🎨 LABORATORIO"])

# --- PESTAÑA 0: COMANDO (CHAT + VOZ + PEGAR) ---
with tabs[0]:
    st.subheader("🎙️ Centro de Mando e Inteligencia Visual")
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_a: mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_144")
    with col_b: pasted_img = paste_button(label="📋 PEGAR CAPTURA (CTRL+V)", key="paster_144")
    with col_c: 
        if st.button("🗑️ LIMPIAR SISTEMA"): st.rerun()

    chat_input = st.chat_input("Órdenes...")
    if pasted_img.image_data is not None:
        img = pasted_img.image_data
        st.image(img, width=350)
        if chat_input:
            with st.chat_message("assistant"):
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                res = client.chat.completions.create(
                    model=modelo_vision,
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": f"JARVIS: {chat_input}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                    ]}]
                )
                st.write(res.choices[0].message.content)
    elif chat_input:
        with st.chat_message("assistant"):
            res = client.chat.completions.create(model=modelo_texto, messages=[{"role": "user", "content": chat_input}])
            st.write(res.choices[0].message.content)

# --- PESTAÑA 1: ANÁLISIS DE DOCUMENTOS E IMÁGENES ---
with tabs[1]:
    st.subheader("📊 Análisis de Inteligencia")
    # AHORA ACEPTA IMÁGENES TAMBIÉN
    file = st.file_uploader("Cargar archivo o imagen", type=['pdf', 'docx', 'xlsx', 'txt', 'png', 'jpg', 'jpeg'])
    
    if file and st.button("🔍 INICIAR ANÁLISIS"):
        with st.spinner("JARVIS escaneando..."):
            try:
                if file.type.startswith('image/'):
                    # Análisis de imagen cargada manualmente
                    img_file = Image.open(file)
                    st.image(img_file, width=300)
                    buffered = io.BytesIO()
                    img_file.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    res = client.chat.completions.create(
                        model=modelo_vision,
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Describe y analiza esta imagen detalladamente."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                        ]}]
                    )
                    st.success(res.choices[0].message.content)
                else:
                    # Análisis de documentos (Mark 135)
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
                        messages=[{"role": "user", "content": f"Resume este documento: {text[:12000]}"}]
                    )
                    st.success(res.choices[0].message.content)
            except Exception as e: st.error(f"Falla de lectura: {e}")

# --- PESTAÑA 2: LABORATORIO (SISTEMA DE RENDERIZADO UNIVERSAL v145) ---
with tabs[2]:
    st.subheader("🎨 Estación de Diseño Mark 75")
    st.info("Utilizando el motor de síntesis de alta disponibilidad.")
    
    idea = st.text_input("Describa el prototipo a sintetizar:", key="lab_145", placeholder="Ej: Armadura estilo Valkiria...")
    estilo = st.selectbox("Filtro Visual:", 
                          ["Cinematic Marvel", "Blueprint Técnico", "Cyberpunk Neón", "Industrial Stark", "Hyper-Realistic"], 
                          key="style_145")
    
    if st.button("🚀 INICIAR SÍNTESIS"):
        if idea:
            with st.spinner("JARVIS canalizando energía al motor de renderizado..."):
                try:
                    # Limpiamos y preparamos el prompt
                    prompt_limpio = idea.replace(" ", "%20")
                    estilo_limpio = estilo.replace(" ", "%20")
                    
                    # Generamos una semilla aleatoria para evitar que la imagen se repita
                    import random
                    seed = random.randint(1, 999999)
                    
                    # Usamos una URL de renderizado directo que es inmune al RuntimeError de librerías
                    url_final = f"https://image.pollinations.ai/prompt/{prompt_limpio}%20{estilo_limpio}?width=1024&height=1024&seed={seed}&nologo=true"
                    
                    # Mostramos la imagen usando el protocolo de visualización directa
                    st.image(url_final, caption=f"Prototipo: {idea} | Estilo: {estilo}", use_container_width=True)
                    
                    # Botón opcional para descargar
                    st.success("Diseño materializado. La imagen se ha cargado a través del puente de alta disponibilidad.")
                    
                except Exception as e:
                    st.error(f"Falla en la cámara de síntesis: {e}")
        else:
            st.warning("Srta. Diana, el reactor necesita una idea para iniciar la secuencia.")