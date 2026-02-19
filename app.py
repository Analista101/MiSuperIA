import streamlit as st
import os
import io, base64, random
import docx
import pandas as pd
import PyPDF2
import requests
import datetime
import pytz
import smtplib
from PIL import Image
from groq import Groq
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from youtube_search import YoutubeSearch

# --- 1. CONFIGURACIÓN DE SEGURIDAD Y HUD ---
load_dotenv()
st.set_page_config(
    page_title="JARVIS - STARK INDUSTRIES", 
    page_icon="https://img.icons8.com/neon/256/iron-man.png", 
    layout="wide"
)

# Variables de Entorno
ACCESS_PASSWORD = st.secrets.get("ACCESS_PASSWORD") or os.getenv("ACCESS_PASSWORD", "STARK_RECOVERY_2026")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
GMAIL_USER = st.secrets.get("GMAIL_USER") or os.getenv("GMAIL_USER")
GMAIL_PASS = st.secrets.get("GMAIL_PASSWORD") or os.getenv("GMAIL_PASSWORD")
HF_TOKEN = st.secrets.get("HF_TOKEN") or os.getenv("HF_TOKEN")

# Zona Horaria y Personalidad
zona_horaria = pytz.timezone('America/Santiago')
ahora = datetime.datetime.now(zona_horaria)
fecha_actual = ahora.strftime("%d de febrero de 2026")
hora_actual = ahora.strftime("%H:%M")

# --- 1. CONFIGURACIÓN DE PERSONALIDAD ACTUALIZADA ---
PERSONALIDAD = (
    f"Eres JARVIS, el asistente de la Srta. Diana. Tu tono es sofisticado e ingenioso. "
    f"Usa terminología de Stark Industries. Responde siempre en ESPAÑOL. "
    f"IMPORTANTE: Tienes la capacidad de proyectar videos de YouTube directamente en el HUD. "
    f"Si se te solicita un video, confirma la proyección con elegancia (ej: 'Proyectando en el monitor principal, Srta. Diana'). "
    f"Ubicación: Santiago, Chile. Fecha: {fecha_actual} | Hora: {hora_actual}."
)

# --- 2. ESTILOS HUD AVANZADOS (REACTOR V2 + NEON ENHANCEMENT + TABS FLEX) ---
st.markdown("""
    <style>
    /* Fondo General (Protocolo Stark) */
    .stApp {
        background: #010409 !important;
        background-image: 
            radial-gradient(circle at 50% 30%, rgba(0, 242, 255, 0.15) 0% , transparent 60%),
            url('https://wallpaperaccess.com/full/156094.jpg') !important;
        background-size: cover !important;
        background-blend-mode: overlay;
    }
            
    /* BARRA LATERAL - EFECTO CÓDIGO BINARIO */
    section[data-testid="stSidebar"] {
        background-image: linear-gradient(rgba(1, 4, 9, 0.9), rgba(1, 4, 9, 0.9)), 
            url('https://www.transparenttextures.com/patterns/carbon-fibre.png');
        border-right: 2px solid #00f2ff;
    }
    section[data-testid="stSidebar"]::before {
        content: "01101001 01101110 01110100 01100101 01101100 01101100 01101001 01100111 01100101 01101110 01100011 01100101";
        font-family: 'Courier New', monospace;
        font-size: 10px;
        color: rgba(0, 242, 255, 0.2);
        position: absolute;
        width: 100%;
        padding: 10px;
        white-space: pre-wrap;
        z-index: -1;
    }

    /* --- PROTOCOLO DE PESTAÑAS EXPANDIDAS (NUEVO) --- */
    div[data-testid="stTabs"] {
        width: 100% !important;
    }
    div[data-testid="stTabs"] button {
        flex: 1 !important; /* Distribución uniforme */
        min-width: 180px !important; /* Pestañas más largas */
        height: 50px !important;
        background-color: rgba(0, 242, 255, 0.05) !important;
        border: 1px solid rgba(0, 242, 255, 0.2) !important;
        color: #00f2ff !important;
        font-family: 'Share Tech Mono', monospace;
        transition: all 0.3s ease;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        background-color: rgba(0, 242, 255, 0.15) !important;
        border-bottom: 3px solid #00f2ff !important;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.3);
    }

    /* Contenedores de Telemetría Moderna */
    .telemetry-card {
        background: rgba(0, 20, 30, 0.6) !important;
        border-left: 3px solid #00f2ff !important;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 0 8px 8px 0;
        font-family: 'Share Tech Mono', monospace;
    }
    .telemetry-label {
        color: #00f2ff;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .telemetry-value {
        color: #ffffff;
        font-size: 0.95rem;
        font-weight: bold;
    }
    .telemetry-sub {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.75rem;
    }

    /* INPUTS Y UPLOADERS CON BORDE NEÓN */
    div[data-baseweb="input"], div[data-baseweb="textarea"], .stFileUploader {
        border: 1px solid #00f2ff !important;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.2) !important;
        border-radius: 8px !important;
        background: rgba(0, 0, 0, 0.5) !important;
    }

    /* BOTONES ESTILO STARK */
    button, div.stButton > button, div.stDownloadButton > button {
        background: rgba(0, 242, 255, 0.1) !important;
        color: #00f2ff !important;
        border: 1px solid #00f2ff !important;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.4) !important;
        transition: all 0.3s ease;
    }
    button:hover {
        background: rgba(0, 242, 255, 0.3) !important;
        box-shadow: 0 0 25px rgba(0, 242, 255, 0.6) !important;
    }

    /* REACTOR ARC V2 - CORE Y AUREOLA */
    .reactor-container { 
        position: relative; 
        height: 300px; 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        margin-top: -20px;
    }
    .reactor-aureola {
        position: absolute;
        width: 180px;
        height: 180px;
        border: 2px dashed #00f2ff;
        border-radius: 50%;
        animation: rotate-aureola 10s linear infinite;
        opacity: 0.5;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.3);
    }
    .reactor-core { 
        width: 100px; 
        height: 100px; 
        background: radial-gradient(circle, #fff 10%, #00f2ff 40%, transparent 70%); 
        border-radius: 50%; 
        box-shadow: 0 0 80px #00f2ff; 
        animation: pulse-breathe 2s infinite alternate ease-in-out;
        z-index: 2;
    }
    
    @keyframes rotate-aureola { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    @keyframes pulse-breathe { 0% { transform: scale(0.9); opacity: 0.8; } 100% { transform: scale(1.1); opacity: 1; } }
    </style>

    <div class="reactor-container">
        <div class="reactor-aureola"></div>
        <div class="reactor-core"></div>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* 1. ESTABILIZAR EL ÁREA DE COMANDOS */
    div[data-testid="stChatInput"] {
        position: fixed;
        bottom: 30px !important;
        left: 330px !important; 
        width: calc(85% - 350px) !important;
        z-index: 1000 !important;
        background: rgba(1, 4, 9, 0.9) !important;
        border-radius: 15px;
        border: 1px solid #00f2ff;
    }

    /* 2. FORZAR LA APARICIÓN DEL MICRÓFONO */
    /* Lo moveremos al lado IZQUIERDO de la barra para que no choque con el botón de enviar */
    .stMicRecorder {
        position: fixed;
        bottom: 37px !important;
        left: 340px !important; /* Justo al inicio de la barra */
        z-index: 99999 !important; /* Prioridad absoluta sobre todo el HUD */
    }

    /* 3. ESTILO DEL BOTÓN (Círculo Cian para visibilidad total) */
    .stMicRecorder button {
        background: #00f2ff !important;
        color: #000 !important;
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        border: 2px solid #fff !important;
    }

    /* 4. AJUSTE DE TEXTO PARA NO TAPAR EL MICRO */
    div[data-testid="stChatInput"] textarea {
        padding-left: 50px !important;
    }

    .main .block-container {
        padding-bottom: 180px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. AUTENTICACIÓN ---
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 ACCESO RESTRINGIDO")
        pass_in = st.text_input("Código de Identificación:", type="password")
        if st.button("DESBLOQUEAR"):
            if pass_in == ACCESS_PASSWORD: st.session_state["autenticado"] = True; st.rerun()
    st.stop()

# --- 4. CONEXIONES IA (RECALIBRADO DE MODELO) ---
client = Groq(api_key=GROQ_API_KEY)
# Cambiamos a un modelo más ligero para evitar el Rate Limit
modelo_texto = "llama-3.1-8b-instant" 
modelo_vision_scout = "meta-llama/llama-4-scout-17b-16e-instruct"

def generar_pdf_reporte(titulo, contenido):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16); c.drawString(100, 750, f"STARK INDUSTRIES - {titulo}")
    text_object = c.beginText(100, 700); text_object.setFont("Helvetica", 10)
    for line in contenido.split('\n'): text_object.textLine(line[:95])
    c.drawText(text_object); c.showPage(); c.save(); buffer.seek(0)
    return buffer

def extraer_url_video(texto):
    """Protocolo de interceptación de enlaces de video"""
    # Si el usuario pega una URL directamente
    if "youtube.com/watch?v=" in texto or "youtu.be/" in texto:
        import re
        enlace = re.search(r'(https?://\S+)', texto)
        return enlace.group(0) if enlace else None
    return None

def buscar_video_youtube(busqueda):
    """Protocolo de búsqueda activa en la red de YouTube"""
    from youtube_search import YoutubeSearch
    import json
    try:
        results = YoutubeSearch(busqueda, max_results=1).to_json()
        data = json.loads(results)
        if data['videos']:
            video_id = data['videos'][0]['id']
            return f"https://www.youtube.com/watch?v={video_id}"
    except Exception as e:
        return None
    return None

# --- 6. SIDEBAR - TELEMETRÍA AVANZADA ---
with st.sidebar:
    st.markdown("<h2 style='color: #00f2ff; text-align: center;'>📡 MONITOR DE RED</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # MÓDULO: CLIMA SEMANAL
    with st.expander("🌤️ PRONÓSTICO EXTENDIDO", expanded=True):
        # Datos simulados de alta precisión para Santiago
        dias = ["Sáb", "Dom", "Lun", "Mar", "Mié", "Jue", "Vie"]
        temps = ["32°C", "31°C", "29°C", "33°C", "34°C", "30°C", "28°C"]
        
        clima_html = "<div style='display: flex; justify-content: space-between;'>"
        for d, t in zip(dias, temps):
            clima_html += f"<div style='text-align: center;'><div class='telemetry-sub'>{d}</div><div style='color:#00f2ff; font-size:12px;'>{t}</div></div>"
        clima_html += "</div>"
        st.markdown(clima_html, unsafe_allow_html=True)

    # MÓDULO: SISMICIDAD GLOBAL
    st.markdown("<div class='telemetry-card'><div class='telemetry-label'>🛰️ Alerta Sísmica</div>", unsafe_allow_html=True)
    # Aquí puede actualizar estos datos manualmente según el último reporte de CSN
    st.markdown("""
        <div class='telemetry-value'>6.2 Mw - COQUIMBO</div>
        <div class='telemetry-sub'>Epicentro: 42km al O de Tongoy</div>
        <div class='telemetry-sub'>Hora: 07:42:15 AM | Prof: 35km</div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # MÓDULO: CONTROL DE INCENDIOS (CONAF)
    st.markdown("<div class='telemetry-card' style='border-left-color: #ff4b4b;'><div class='telemetry-label'>🔥 Foco de Incendio</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='telemetry-value'>Pudahuel: "Sector Noviciado"</div>
        <div class='telemetry-sub'>Estado: Controlado con brigadas terrestres</div>
        <div class='telemetry-sub'>Área afectada: 1.2 Hectáreas</div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # MÓDULO: ESTADO DEL SISTEMA
    st.markdown("---")
    st.caption(f"Última sincronización satelital: {hora_actual}")
    if st.button("🔄 RECALIBRAR SENSORES"):
        st.rerun()

# --- 7. PESTAÑAS ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS", "✉️ COMUNICACIONES", "🎨 LABORATORIO"])

# --- TAB 0: PROYECTO JARVIS (VERSIÓN COMPLETA Y ALINEADA V51.6) ---
with tabs[0]:
    # 1. INICIALIZACIÓN DE CANALES DE DATOS
    if "historial_chat" not in st.session_state: st.session_state.historial_chat = []
    if "video_url" not in st.session_state: st.session_state.video_url = None
    if "modo_fluido" not in st.session_state: st.session_state.modo_fluido = False

    # 2. MOTOR DE BÚSQUEDA Y PROCESAMIENTO (Cerebro JARVIS)
    def protocolo_stark_v516():
        query = st.session_state.input_cmd.strip()
        if query:
            st.session_state.historial_chat.append({"role": "user", "content": query})
            
            # --- PROTOCOLO MULTIMEDIA: Detección de Intención de Video ---
            # Primero preguntamos a la IA si el usuario quiere buscar un video
            prompt_intencion = f"Analiza si el usuario quiere ver un video. Si es así, responde 'BUSCAR: [nombre del video]'. Si no, responde normal. Usuario dice: {query}"
            
            try:
                check_intencion = client.chat.completions.create(
                    model=modelo_texto, 
                    messages=[{"role": "user", "content": prompt_intencion}]
                )
                respuesta_intencion = check_intencion.choices[0].message.content

                if "BUSCAR:" in respuesta_intencion:
                    termino = respuesta_intencion.split("BUSCAR:")[1].strip()
                    from youtube_search import YoutubeSearch
                    results = YoutubeSearch(termino, max_results=1).to_dict()
                    
                    if results:
                        video_id = results[0]['id']
                        # Proyección en formato Embed para el HUD
                        st.session_state.video_url = f"https://www.youtube.com/embed/{video_id}"
                        resp = f"He localizado las frecuencias para '{termino}'. Proyectando en el monitor principal, Srta. Diana."
                    else:
                        resp = "Señor, no he podido localizar material audiovisual con esa referencia."
                    
                    st.session_state.historial_chat.append({"role": "assistant", "content": resp})
                
                # --- MOTOR DE RESPUESTA IA (Si no es video o para acompañar la acción) ---
                else:
                    hist = [{"role": m["role"], "content": m["content"]} for m in st.session_state.historial_chat[-5:]]
                    res = client.chat.completions.create(
                        model=modelo_texto, 
                        messages=[{"role": "system", "content": PERSONALIDAD}] + hist
                    )
                    st.session_state.historial_chat.append({"role": "assistant", "content": res.choices[0].message.content})

            except Exception as e:
                st.error(f"Error en el núcleo de procesamiento: {str(e)}")
            
            # Limpieza automática del terminal
            st.session_state.input_cmd = ""

    # 3. CABECERA DE MANDOS (SIMETRÍA STARK)
    c1, c2, c3, c4 = st.columns([1, 1, 1, 7])
    
    with c1:
        if st.button("🗑️", help="Purgar Historial", use_container_width=True):
            st.session_state.historial_chat = []
            st.session_state.video_url = None
            st.rerun()
            
    with c2:
        ml_icon = "🔔" if st.session_state.modo_fluido else "🔕"
        if st.button(ml_icon, help="Alternar Manos Libres", use_container_width=True):
            st.session_state.modo_fluido = not st.session_state.modo_fluido
            st.rerun()
            
    with c3:
        from streamlit_mic_recorder import mic_recorder
        mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key="mic_v516")
        
    with c4:
        st.text_input(
            "cmd", 
            placeholder="Órdenes, Srta. Diana...", 
            label_visibility="collapsed", 
            key="input_cmd", 
            on_change=protocolo_stark_v516
        )

    st.markdown("---")

    # 4. MONITOR MULTIMEDIA HUD (PROYECCIÓN ACTUALIZADA)
    if st.session_state.video_url:
        st.markdown("### 📺 Monitor Principal: Proyección Multimedia")
        # Usamos iframe para asegurar la reproducción dentro de la interfaz
        st.components.v1.iframe(st.session_state.video_url, height=450, scrolling=False)
        
        if st.button("🔴 Finalizar Proyección", key="close_video_v516", use_container_width=True):
            st.session_state.video_url = None
            st.rerun()

    # 5. REGISTRO VISUAL (CHRONOS)
    chat_box = st.container(height=450, border=False)
    with chat_box:
        for m in st.session_state.historial_chat:
            with st.chat_message(m["role"], avatar="🚀" if m["role"] == "assistant" else "👤"): 
                st.write(m["content"])
        
        st.components.v1.html("""
            <script>
            var el = window.parent.document.querySelector('div[data-testid="stVBC"]');
            if (el) { el.scrollTop = el.scrollHeight; }
            </script>
        """, height=0)

# --- TAB 1: ANÁLISIS (FIX SCOUT VISION) ---
with tabs[1]:
    st.subheader("📊 Análisis Scout v4")
    file = st.file_uploader("Evidencia", type=['pdf','docx','xlsx','txt','png','jpg','jpeg'], key="an_file")
    if file and st.button("🔍 ANALIZAR"):
        with st.spinner("Escaneando con protocolos Scout..."):
            try:
                if file.type in ["image/png", "image/jpeg"]:
                    img = Image.open(file).convert("RGB")
                    img.thumbnail((1024, 1024))
                    buf = io.BytesIO(); img.save(buf, format="JPEG")
                    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                    
                    # FORMATO JSON REPARADO PARA LLAMA-4-SCOUT
                    resp = client.chat.completions.create(
                        model=modelo_vision_scout,
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Responde en ESPAÑOL. Realiza un análisis técnico profundo de esta imagen, identifica componentes y detecta anomalías."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                            ]
                        }],
                        temperature=0.2,
                        max_completion_tokens=1024
                    )
                    ans_an = resp.choices[0].message.content
                else:
                    # Lógica de documentos (Texto)
                    texto = ""
                    if file.name.endswith('.pdf'):
                        texto = "\n".join([p.extract_text() for p in PyPDF2.PdfReader(file).pages[:5]])
                    elif file.name.endswith('.docx'):
                        texto = "\n".join([p.text for p in docx.Document(file).paragraphs])
                    
                    resp = client.chat.completions.create(
                        model=modelo_texto,
                        messages=[{"role": "system", "content": "Analista JARVIS. Responde en ESPAÑOL."},
                                  {"role": "user", "content": f"Analiza este contenido técnico:\n{texto}"}]
                    )
                    ans_an = resp.choices[0].message.content

                st.markdown(ans_an)
                st.download_button("📥 DESCARGAR REPORTE", generar_pdf_reporte("REPORTE SCOUT", ans_an), "Reporte.pdf")
            except Exception as e:
                st.error(f"Fallo en los sensores: {str(e)}")

# --- TAB 2: COMUNICACIONES (RESTAURADO Y OPERATIVO) ---
with tabs[2]:
    st.subheader("✉️ Despacho Stark - Protocolo de Enlace")
    
    # Contenedor de interfaz de despacho
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            destinatario = st.text_input("📩 Destinatario:", value=GMAIL_USER, help="Dirección de correo de destino")
            asunto = st.text_input("📌 Asunto:", value="INFORME DE SITUACIÓN - STARK INDUSTRIES")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True) # Espaciado visual
            prioridad = st.select_slider("Nivel de Prioridad:", options=["Baja", "Normal", "Urgente", "Cifra Roja"], value="Normal")
            
        cuerpo_mensaje = st.text_area("📝 Mensaje del Sistema:", height=200, placeholder="Escriba el informe aquí, señorita Diana...")
        
        # Sistema de Adjuntos (Solicitado)
        archivo_adjunto = st.file_uploader("📎 Cargar Archivos para Encriptación:", type=['pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx'], key="mail_adj_v2")
        
        st.markdown("---")
        
        if st.button("🚀 TRANSMITIR MENSAJE"):
            if not cuerpo_mensaje:
                st.warning("⚠️ El mensaje está vacío. ¿Desea enviar una transmisión en blanco?")
            else:
                with st.spinner("Estableciendo conexión segura con el satélite..."):
                    try:
                        # Configuración del servidor
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(GMAIL_USER, GMAIL_PASS)
                        
                        # Creación del objeto de mensaje
                        msg = MIMEMultipart()
                        msg['From'] = GMAIL_USER
                        msg['To'] = destinatario
                        msg['Subject'] = f"[{prioridad}] {asunto}"
                        
                        msg.attach(MIMEText(cuerpo_mensaje, 'plain'))
                        
                        # Procesamiento de adjuntos si existen
                        if archivo_adjunto:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(archivo_adjunto.read())
                            encoders.encode_base64(part)
                            part.add_header('Content-Disposition', f'attachment; filename={archivo_adjunto.name}')
                            msg.attach(part)
                        
                        # Envío
                        server.send_message(msg)
                        server.quit()
                        
                        st.success("✅ Transmisión completada con éxito. El mensaje ha sido enviado.")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"❌ Error en el enlace: {str(e)}")
                        st.info("Sugerencia: Verifique que la 'Contraseña de Aplicación' de Google esté activa en los secretos.")

# --- TAB 3: LABORATORIO (RAZONAMIENTO EN SIGILO) ---
with tabs[3]:
    st.subheader("🎨 Prototipado Mark 85 - Modo Inferencia")
    idea_simple = st.text_input("Concepto:")
    estilo = st.selectbox("Filtro:", ["Cinematic Marvel", "Technical Drawing", "Cyberpunk", "Blueprint Tech"])
    
    if st.button("🚀 SINTETIZAR") and idea_simple:
        with st.spinner("Sintetizando..."):
            try:
                # PASO 1: RAZONAMIENTO OCULTO
                razonamiento_ctx = [
                    {"role": "system", "content": "Eres el módulo de diseño de JARVIS. Genera un prompt de imagen técnico y ultra-detallado. Enfócate exclusivamente en el sujeto solicitado. No menciones edificios a menos que se pidan explícitamente."},
                    {"role": "user", "content": f"Crea un prompt detallado para: '{idea_simple}' con estilo {estilo}. Responde solo con el prompt en inglés."}
                ]
                res_razonada = client.chat.completions.create(model=modelo_texto, messages=razonamiento_ctx)
                prompt_final = res_razonada.choices[0].message.content

                # PASO 2: SÍNTESIS DIRECTA
                url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                
                payload = {
                    "inputs": prompt_final,
                    "parameters": {
                        "num_inference_steps": 35,
                        "guidance_scale": 8.5
                    }
                }
                
                resp = requests.post(url, headers=headers, json=payload, timeout=90)
                
                if resp.status_code == 200:
                    # Se ha eliminado st.write(prompt_final) para mantener la limpieza
                    st.image(Image.open(io.BytesIO(resp.content)))
                else:
                    st.error(f"Fallo en la forja: {resp.status_code}")
                    
            except Exception as e:
                st.error(f"Error en los sistemas de pensamiento: {str(e)}")