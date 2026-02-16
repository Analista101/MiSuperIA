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

# --- PESTAÑA 2: LABORATORIO (CORRECCIÓN DE IMAGEN ROTA) ---
with tabs[2]:
    st.subheader("🎨 Estación de Diseño Mark 68 (Con Respaldo)")
    idea = st.text_input("Describa el prototipo a sintetizar:", key="lab_idea_138")
    estilo = st.selectbox("Acabado Visual:", 
                          ["Cinematic Marvel", "Blueprint Técnico", "Cyberpunk Neón", "Industrial Stark", "Digital Art"], key="lab_estilo_138")
    
    if st.button("🚀 INICIAR SÍNTESIS", key="lab_button_138"):
        if idea:
            with st.spinner("JARVIS preparando la matriz de renderizado..."):
                try:
                    prompt_render = f"{idea} {estilo}".replace(" ", "%20")
                    
                    # --- INTENTO 1: Pollinations.ai (Con validación) ---
                    url_principal = f"https://pollinations.ai/p/{prompt_render}?width=1024&height=1024&seed=123&model=flux"
                    
                    # Intentamos descargar la imagen para verificarla
                    response = requests.get(url_principal, stream=True, timeout=10) # Añadimos timeout
                    response.raise_for_status() # Lanza excepción si hay error HTTP
                    
                    # Verificamos que sea una imagen válida
                    img_data = response.content
                    try:
                        img = Image.open(io.BytesIO(img_data))
                        st.image(img, caption=f"Prototipo: {idea} | Estilo: {estilo}", use_container_width=True)
                        st.success("Renderizado principal completado.")
                    except Image.UnidentifiedImageError:
                        st.warning("⚠️ JARVIS: El servidor principal entregó una imagen corrupta. Intentando con respaldo...")
                        # Si la imagen está corrupta, intentamos con el respaldo

                        # --- INTENTO 2: Generador de respaldo (más genérico) ---
                        url_respaldo = f"https://image.pollinations.ai/prompt/{prompt_render}?nologo=true"
                        st.image(url_respaldo, caption=f"Prototipo (Respaldo): {idea} | Estilo: {estilo}", use_container_width=True)
                        st.info("Renderizado de respaldo utilizado.")
                    
                except requests.exceptions.RequestException as req_err:
                    st.error(f"🚨 Falla de red en renderizado: {req_err}. Intentando con respaldo...")
                    # Si hay un error de red, intentamos con el respaldo
                    url_respaldo = f"https://image.pollinations.ai/prompt/{prompt_render}?nologo=true"
                    st.image(url_respaldo, caption=f"Prototipo (Respaldo): {idea} | Estilo: {estilo}", use_container_width=True)
                    st.info("Renderizado de respaldo utilizado.")
                except Exception as e:
                    st.error(f"Falla crítica en estación de diseño: {e}")
        else:
            st.warning("Srta. Diana, necesito una descripción del prototipo para iniciar la síntesis.")