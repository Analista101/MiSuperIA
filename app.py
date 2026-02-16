import streamlit as st
from groq import Groq
import requests
import docx
import pandas as pd
import PyPDF2
from PIL import Image
from streamlit_paste_button import paste_image_button as paste_button
from streamlit_mic_recorder import mic_recorder
import io, base64
from gradio_client import Client # El nuevo puente ligero

# --- 1. ESTÉTICA DE LA TORRE STARK (REACTOR ARC) ---
st.set_page_config(page_title="JARVIS v137", layout="wide")
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
    .stTabs [data-baseweb="tab"] { color: #00f2ff !important; font-size: 16px; }
    .stButton>button { border: 1px solid #00f2ff; background-color: transparent; color: #00f2ff; }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- 2. NÚCLEO DE INTELIGENCIA (GROQ - INDEPENDIENTE) ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    modelo_texto = "llama-3.3-70b-versatile"
    modelo_vision = "llama-3.2-11b-vision-preview"
else:
    st.error("🚨 SRTA. DIANA: ACCESO DENEGADO. REVISE SECRETS EN STREAMLIT CLOUD.")
    st.stop()

# --- 3. INTERFAZ TÁCTICA MULTI-MÓDULO ---
tabs = st.tabs(["💬 COMANDO HÍBRIDO", "📊 ANÁLISIS DOCS", "🎨 LABORATORIO"])

# --- PESTAÑA 0: COMANDO (CHAT + VOZ + PEGAR CAPTURAS) ---
with tabs[0]:
    st.subheader("🎙️ Centro de Mando e Inteligencia Visual")
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_a:
        audio = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_137")
    with col_b:
        # Sensor de pegado Mark 132 corregido
        pasted_image = paste_button(label="📋 PEGAR CAPTURA (CTRL+V)", key="paster_137")
    with col_c:
        if st.button("🗑️ LIMPIAR SISTEMA"):
            st.rerun()

    chat_input = st.chat_input("Escriba su orden o pegue una captura arriba...")
    
    # Procesamiento de entrada
    if pasted_image.image_data is not None:
        img = pasted_image.image_data
        st.image(img, caption="Imagen en memoria de JARVIS", width=400)
        
        if chat_input:
            with st.chat_message("assistant"):
                try:
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    res = client.chat.completions.create(
                        model=modelo_vision,
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"Actúa como JARVIS. {chat_input}"},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                            ]
                        }]
                    )
                    st.write(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Falla en sensor visual: {e}")
    
    elif chat_input or (audio and audio['transcript']):
        final_prompt = audio['transcript'] if (audio and audio['transcript']) else chat_input
        with st.chat_message("assistant"):
            try:
                res = client.chat.completions.create(
                    model=modelo_texto,
                    messages=[{"role": "system", "content": "Eres JARVIS, el asistente elegante de la Srta. Diana."},
                              {"role": "user", "content": final_prompt}]
                )
                st.write(res.choices[0].message.content)
            except Exception as e:
                st.error(f"Falla en enlace de texto: {e}")

# --- PESTAÑA 1: ANÁLISIS DE DOCUMENTOS (GRANDE / MULTIFORMATO) ---
with tabs[1]:
    st.subheader("📊 Lector de Inteligencia Mark 135")
    file = st.file_uploader("Cargar informe (PDF, DOCX, XLSX, TXT)", type=['pdf', 'docx', 'xlsx', 'txt', 'csv'])
    
    if file and st.button("🔍 INICIAR ESCANEO PROFUNDO"):
        with st.spinner("JARVIS procesando archivos pesados..."):
            try:
                full_text = ""
                if file.name.endswith('.pdf'):
                    reader = PyPDF2.PdfReader(file)
                    # Limitamos a las primeras 15 páginas para estabilidad
                    for page in reader.pages[:15]:
                        full_text += page.extract_text() + "\n"
                elif file.name.endswith('.docx'):
                    doc = docx.Document(file)
                    full_text = "\n".join([p.text for p in doc.paragraphs])
                elif file.name.endswith('.xlsx') or file.name.endswith('.csv'):
                    df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
                    full_text = f"Resumen de Tabla:\n{df.head(40).to_string()}"
                else:
                    full_text = file.read().decode()

                if full_text.strip():
                    res = client.chat.completions.create(
                        model=modelo_texto,
                        messages=[{"role": "system", "content": "Eres JARVIS. Realiza un resumen ejecutivo y técnico para la Srta. Diana."},
                                  {"role": "user", "content": f"Documento: {full_text[:12000]}"}]
                    )
                    st.success(res.choices[0].message.content)
                else:
                    st.warning("El archivo no contiene texto procesable.")
            except Exception as e:
                st.error(f"Error en protocolos de lectura: {e}")

# --- PESTAÑA 2: LABORATORIO (PUENTE TÁCTICO v143) ---
with tabs[2]:
    st.subheader("🎨 Estación de Diseño Mark 73")
    st.write("Sintetizando a través de un puente de datos seguro.")
    
    idea = st.text_input("Describa el prototipo:", key="lab_143")
    
    if st.button("🚀 INICIAR SÍNTESIS"):
        if idea:
            with st.spinner("JARVIS estableciendo conexión con el laboratorio remoto..."):
                try:
                    # Usamos un cliente de Gradio para conectar con un modelo estable
                    # Este puente es mucho más difícil de bloquear para Cloudflare
                    client_gradio = Client("black-forest-labs/FLUX.1-schnell")
                    
                    result = client_gradio.predict(
                        prompt=idea,
                        seed=0,
                        width=1024,
                        height=1024,
                        api_name="/predict"
                    )
                    
                    # El resultado es una ruta local a la imagen generada
                    # result es una tupla o lista, tomamos el primer elemento que es la ruta
                    st.image(result, caption=f"Prototipo: {idea}", use_container_width=True)
                    st.success("Diseño materializado con éxito.")
                    
                except Exception as e:
                    st.error(f"Falla en el puente de datos: {e}")
                    st.info("Srta. Diana, si el puente está saturado, intentaremos una frecuencia secundaria.")