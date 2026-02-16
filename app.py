import streamlit as st
from groq import Groq
import requests
import docx
import pandas as pd
import PyPDF2 # Añadido para soporte PDF
from PIL import Image
import io, base64

# --- 1. ESTÉTICA STARK INDUSTRIES ---
st.set_page_config(page_title="JARVIS v126", layout="wide")
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
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- 2. NÚCLEO DE INTELIGENCIA (GROQ + VISION) ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    modelo_texto = "llama-3.3-70b-versatile"
    modelo_vision = "llama-3.2-11b-vision-preview" # Especialista en imágenes
else:
    st.error("🚨 SRTA. DIANA: ACCESO DENEGADO. FALTA GROQ_API_KEY.")
    st.stop()

# --- 3. INTERFAZ TÁCTICA CENTRALIZADA ---
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS UNIVERSAL", "🎨 LABORATORIO"])

# --- TAB 0: COMANDO ---
with tabs[0]:
    prompt = st.chat_input("Órdenes para JARVIS...")
    if prompt:
        with st.chat_message("user"): st.write(prompt)
        with st.chat_message("assistant"):
            try:
                res = client.chat.completions.create(
                    model=modelo_texto,
                    messages=[{"role": "system", "content": "Eres JARVIS. Responde elegante a la Srta. Diana."},
                              {"role": "user", "content": prompt}]
                )
                st.write(res.choices[0].message.content)
            except Exception as e: st.error(f"Falla: {e}")

# --- TAB 1: ANÁLISIS UNIVERSAL (MULTIFORMATO) ---
with tabs[1]:
    st.subheader("📊 Centro de Inteligencia y Escaneo")
    st.write("Cargue documentos (PDF, DOCX, XLSX) o imágenes (JPG, PNG) para análisis táctico.")
    
    archivo = st.file_uploader("Subir archivo de inteligencia", type=['txt', 'docx', 'xlsx', 'csv', 'pdf', 'png', 'jpg', 'jpeg'])
    
    if archivo and st.button("🔍 INICIAR ANÁLISIS INTEGRAL"):
        with st.spinner("JARVIS procesando datos multiformato..."):
            try:
                # Caso A: IMÁGENES
                if archivo.type in ["image/png", "image/jpeg", "image/jpg"]:
                    img = Image.open(archivo)
                    st.image(img, width=400, caption="Captura Analizada")
                    
                    # Convertir imagen a base64 para Groq Vision
                    encoded_img = base64.b64encode(archivo.getvalue()).decode('utf-8')
                    
                    res = client.chat.completions.create(
                        model=modelo_vision,
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Actúa como JARVIS. Analiza esta imagen con detalle técnico para la Srta. Diana."},
                                {"type": "image_url", "image_url": {"url": f"data:{archivo.type};base64,{encoded_img}"}}
                            ]
                        }]
                    )
                    st.info(res.choices[0].message.content)

                # Caso B: DOCUMENTOS
                else:
                    text_content = ""
                    if archivo.name.endswith('.docx'):
                        doc = docx.Document(archivo)
                        text_content = "\n".join([p.text for p in doc.paragraphs])
                    elif archivo.name.endswith('.pdf'):
                        pdf_reader = PyPDF2.PdfReader(archivo)
                        text_content = "\n".join([page.extract_text() for page in pdf_reader.pages])
                    elif archivo.name.endswith('.xlsx'):
                        df = pd.read_excel(archivo)
                        text_content = f"Datos de tabla Excel:\n{df.head(20).to_string()}"
                    else:
                        text_content = archivo.read().decode()

                    res = client.chat.completions.create(
                        model=modelo_texto,
                        messages=[{"role": "user", "content": f"Analiza este informe para la Srta. Diana: {text_content[:8000]}"}]
                    )
                    st.success(res.choices[0].message.content)

            except Exception as e:
                st.error(f"Error en el protocolo de escaneo: {e}")

# --- TAB 2: LABORATORIO ---
with tabs[2]:
    st.subheader("🎨 Estación de Diseño")
    idea = st.text_input("¿Qué diseño desea sintetizar hoy?")
    if st.button("🚀 INICIAR"):
        if idea:
            st.image(f"https://image.pollinations.ai/prompt/{idea.replace(' ', '%20')}?nologo=true")