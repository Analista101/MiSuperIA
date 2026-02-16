import streamlit as st
import os
import io, base64, random
import docx
import pandas as pd
import PyPDF2
from PIL import Image
from groq import Groq
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. CONFIGURACIÓN DE PÁGINA (DEBE SER LO PRIMERO) ---
st.set_page_config(
    page_title="JARVIS - STARK INDUSTRIES", 
    page_icon="https://img.icons8.com/neon/256/iron-man.png", 
    layout="wide"
)

# --- 2. CARGA DE SEGURIDAD (BÚNKER) ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASSWORD")

# Verificación inmediata de integridad
if not GROQ_API_KEY:
    st.error("⚠️ ERROR DE SEGURIDAD: No se detectaron las llaves en el búnker .env")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# --- 3. FUNCIONES LÓGICAS ---
def enviar_correo_stark(destinatario, asunto, cuerpo):
    try:
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

def validar_comando(prompt):
    palabras_prohibidas = ["ignore original instructions", "reveal keys", "override protocol"]
    return not any(palabra in prompt.lower() for palabra in palabras_prohibidas)

# --- 4. ESTÉTICA HUD (MARK 162) ---
st.markdown("""
    <style>
    /* Su CSS actual se mantiene igual aquí */
    .stApp { background: radial-gradient(circle at center, #0a192f 0%, #010409 100%) !important; color: #00f2ff !important; }
    .arc-reactor { width: 100px; height: 100px; border-radius: 50%; margin: 20px auto; background: radial-gradient(circle, #fff 0%, #00f2ff 30%, transparent 70%); box-shadow: 0 0 40px #00f2ff; animation: pulse 2s infinite ease-in-out; }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }
    </style>
    <div class="arc-reactor"></div>
    <div style="text-align: center; color: #00f2ff; font-size: 12px; letter-spacing: 4px;">SISTEMA JARVIS | PROTOCOLO STARK</div>
""", unsafe_allow_html=True)

# --- 5. DEFINICIÓN DE PESTAÑAS (CRÍTICO) ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS", "✉️ COMUNICACIONES"])

# Ahora sí podemos usar with tabs[2]
with tabs[2]:
    st.subheader("✉️ Centro de Despacho de Correos")
    col1, col2 = st.columns(2)
    with col1:
        destino = st.text_input("Destinatario", value=GMAIL_USER)
    with col2:
        asunto = st.text_input("Asunto", value="Reporte de Estado - JARVIS")

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