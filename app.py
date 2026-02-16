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

# --- 1. PROTOCOLO DE ESTÉTICA AVANZADA STARK (MARK 162) ---
st.set_page_config(
    page_title="JARVIS - STARK INDUSTRIES", 
    page_icon="https://img.icons8.com/neon/256/iron-man.png", 
    layout="wide"
)

st.markdown("""
    <style>
    /* Fondo de la Terminal Stark */
    .stApp {
        background: radial-gradient(circle at center, #0a192f 0%, #010409 100%) !important;
        color: #00f2ff !important;
        font-family: 'Courier New', Courier, monospace;
    }

    /* El Reactor Arc Central */
    .arc-reactor {
        width: 100px; height: 100px; border-radius: 50%; margin: 20px auto;
        background: radial-gradient(circle, #fff 0%, #00f2ff 30%, transparent 70%);
        box-shadow: 0 0 40px #00f2ff, inset 0 0 25px #00f2ff;
        border: 4px double #00f2ff;
        animation: pulse 2s infinite ease-in-out;
    }

    /* Líneas HUD de Datos */
    .hud-line {
        height: 2px; background: linear-gradient(90deg, transparent, #00f2ff, transparent);
        margin: 10px 0; opacity: 0.5;
    }

    /* Contenedores de Cristal para las Pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px; background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: rgba(0, 242, 255, 0.05);
        border-radius: 10px 10px 0px 0px; color: #00f2ff; border: 1px solid rgba(0, 242, 255, 0.2);
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 242, 255, 0.2) !important;
        border: 1px solid #00f2ff !important;
    }

    /* Personalización de Inputs y Botones */
    input { background-color: rgba(0, 0, 0, 0.7) !important; color: #00f2ff !important; border: 1px solid #00f2ff !important; }
    .stButton>button {
        border: 1px solid #00f2ff !important; background: rgba(0, 242, 255, 0.1) !important;
        color: #00f2ff !important; font-weight: bold; text-transform: uppercase;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.3);
    }
    .stButton>button:hover { background: rgba(0, 242, 255, 0.4) !important; box-shadow: 0 0 25px #00f2ff; }

    @keyframes pulse { 0% { transform: scale(1); opacity: 0.8; } 50% { transform: scale(1.1); opacity: 1; } 100% { transform: scale(1); opacity: 0.8; } }
    </style>
    
    <div class="arc-reactor"></div>
    <div class="hud-line"></div>
    <div style="text-align: center; color: #00f2ff; font-size: 12px; letter-spacing: 4px;">
        SISTEMA DE INTELIGENCIA JARVIS | PROTOCOLO DE SEGURIDAD STARK
    </div>
    <div class="hud-line"></div>
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

# --- PESTAÑA PRINCIPAL: CHAT DINÁMICO ---
with tabs[0]:
    st.subheader("🗨️ Interfaz de Comando Central")
    
    # Añadimos un receptor discreto que permite pegar imágenes (Ctrl+V)
    # En Streamlit, el file_uploader es el único que acepta el 'paste' del navegador
    input_visual = st.file_uploader("Subir o pegar imagen (Ctrl+V)", type=['png', 'jpg', 'jpeg'], key="main_vision", label_visibility="collapsed")
    
    # El chat_input sigue para sus comandos de voz/texto
    prompt = st.chat_input("Escriba su comando o pegue una imagen arriba...")

    if prompt or input_visual:
        # Si hay una imagen, activamos el protocolo de visión
        if input_visual:
            with st.spinner("Analizando estímulo visual, señor..."):
                try:
                    img_file = Image.open(input_visual).convert("RGB")
                    buffered = io.BytesIO()
                    img_file.save(buffered, format="JPEG", quality=90)
                    img_b64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Usamos el nuevo modelo de visión que rescatamos
                    res = client.chat.completions.create(
                        model="llama-3.2-90b-vision-instant",
                        messages=[
                            {"role": "system", "content": PERSONALIDAD},
                            {"role": "user", "content": [
                                {"type": "text", "text": prompt if prompt else "Analice lo que aparece en pantalla, JARVIS."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                            ]}
                        ]
                    )
                    respuesta = res.choices[0].message.content
                    st.chat_message("jarvis", avatar="🚀").write(respuesta)
                except Exception as e:
                    st.error(f"Error en el sensor visual: {e}")
        
        # Si es solo texto
        elif prompt:
            with st.spinner("Consultando base de datos..."):
                res = client.chat.completions.create(
                    model=modelo_texto,
                    messages=[
                        {"role": "system", "content": PERSONALIDAD},
                        {"role": "user", "content": prompt}
                    ]
                )
                st.chat_message("jarvis", avatar="🚀").write(res.choices[0].message.content)

# --- PESTAÑA 1: ANÁLISIS (ARCHIVOS PESADOS + IMÁGENES) ---
with tabs[1]:
    st.subheader("📊 Escáner de Evidencia y Documentación")
    file = st.file_uploader("Cargar reporte técnico o imagen", type=['pdf','docx','xlsx','png','jpg','jpeg'])
    
    # Identificador actualizado según la última directiva de Groq (2026)
    modelo_vision_operativo = "llama-3.2-90b-vision-instant"

    if file and st.button("🔍 INICIAR ANÁLISIS"):
        with st.spinner("Escaneando con sensores de alta resolución..."):
            try:
                # --- LÓGICA PARA IMÁGENES ---
                if file.type.startswith('image/'):
                    # Conversión a RGB para evitar fallas con canales Alpha/Transparencias
                    img_file = Image.open(file).convert("RGB")
                    st.image(img_file, width=400, caption="Evidencia visual procesada")
                    
                    # Preparación de datos binarios optimizada (JPEG)
                    buffered = io.BytesIO()
                    img_file.save(buffered, format="JPEG", quality=90)
                    img_b64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Llamada al modelo Vision Instant
                    res = client.chat.completions.create(
                        model=modelo_vision_operativo,
                        messages=[
                            {"role": "system", "content": PERSONALIDAD},
                            {"role": "user", "content": [
                                {"type": "text", "text": "Señor, he procesado la imagen. Aquí tiene el análisis detallado:"},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                            ]}
                        ]
                    )
                    st.success(res.choices[0].message.content)
                
                # --- LÓGICA PARA DOCUMENTOS (FORMATOS ADICIONALES) ---
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
                    
                    # Análisis de texto con el modelo de lenguaje estándar
                    res = client.chat.completions.create(
                        model=modelo_texto,
                        messages=[
                            {"role": "system", "content": PERSONALIDAD},
                            {"role": "user", "content": f"Procedo con el resumen ejecutivo de este archivo pesado, señor: {text[:12000]}"}
                        ]
                    )
                    st.success(res.choices[0].message.content)
                    
            except Exception as e: 
                st.error(f"Falla de lectura en los sistemas: {e}")
                st.info("Sugerencia: Si el error persiste, reinicie el kernel de la aplicación para purgar la caché de modelos.")


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