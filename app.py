import streamlit as st
import os
import io, base64, random
import docx
import pandas as pd
import PyPDF2
from PIL import Image
from groq import Groq
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder # Protocolo de voz mantenido
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. FUNCIÓN DE ENVÍO (Lógica de bajo nivel)
def enviar_correo_stark(destinatario, asunto, cuerpo):
    try:
        # Configuración del servidor de Stark Industries
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() 
        server.login(GMAIL_USER, GMAIL_PASS)
        
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = destinatario
        msg['Subject'] = asunto
        msg.attach(MIMEText(cuerpo, 'plain'))
        
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Falla en el servidor de correo: {e}")
        return False

# 2. INTERFAZ DE USUARIO (Pestaña de Comunicaciones)
# Puede añadir una nueva pestaña o integrarlo en la Pestaña Principal
with tabs[2]: # Asumiendo que creamos una Pestaña 3 para Correo
    st.subheader("✉️ Centro de Despacho de Correos")
    
    col1, col2 = st.columns(2)
    with col1:
        destino = st.text_input("Destinatario", value=GMAIL_USER, help="Por defecto es su propio correo")
    with col2:
        asunto = st.text_input("Asunto", value="Reporte de Estado - JARVIS")
        
    mensaje_cuerpo = st.text_area("Mensaje", placeholder="Escriba el contenido del correo aquí...")
    
    if st.button("🚀 ENVIAR CORREO"):
        if mensaje_cuerpo:
            with st.spinner("Transmitiendo mensaje a través de los servidores de Stark..."):
                exito = enviar_correo_stark(destino, asunto, mensaje_cuerpo)
                if exito:
                    st.success(f"Correo enviado con éxito a {destino}, señor.")
        else:
            st.warning("Señor, el mensaje está vacío. No puedo enviar una señal sin datos.")

# 1. CARGA DE PROTOCOLOS DE SEGURIDAD (Búnker)
load_dotenv()

# 2. RECUPERACIÓN DE LLAVES DESDE EL ENTORNO
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASSWORD")

# 3. VERIFICACIÓN DE INTEGRIDAD
if not GROQ_API_KEY:
    st.error("⚠️ ERROR DE SEGURIDAD: No se detectaron las llaves de acceso en el búnker .env")
    st.stop()

# 4. FILTRO ANTI-HACKEO (Saneamiento de entrada)
def validar_comando(prompt):
    palabras_prohibidas = ["ignore original instructions", "delete system", "reveal keys", "override protocol"]
    for palabra in palabras_prohibidas:
        if palabra in prompt.lower():
            return False
    return True

# 5. INICIALIZACIÓN DEL CLIENTE (Usando la llave protegida)
client = Groq(api_key=GROQ_API_KEY)

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
    
    # Hemos removido el receptor de imágenes para limpiar la interfaz
    prompt = st.chat_input("Escriba su comando, señor...")

    if prompt:
        with st.spinner("Consultando base de datos de Stark Industries..."):
            try:
                res = client.chat.completions.create(
                    model=modelo_texto,
                    messages=[
                        {"role": "system", "content": PERSONALIDAD},
                        {"role": "user", "content": prompt}
                    ]
                )
                # Mostramos la respuesta con el protocolo habitual
                st.chat_message("jarvis", avatar="🚀").write(res.choices[0].message.content)
            except Exception as e:
                st.error(f"Error en el enlace de comunicación: {e}")

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