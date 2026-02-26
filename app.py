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
import urllib.parse
from PIL import Image
from groq import Groq
from duckduckgo_search import DDGS
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from youtube_search import YoutubeSearch
import feedparser
import base64
from io import BytesIO

def get_base64_image(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            # Convertimos la imagen a Base64
            return base64.b64encode(response.content).decode()
    except:
        return None
    return None

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

# Sincronización Manual de Reloj Atómico
# Si America/Santiago falla, forzamos UTC-3 (Hora actual de Chile)
ahora = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))

fecha_actual = ahora.strftime("%d de febrero de 2026")
hora_actual = ahora.strftime("%H:%M")

# Proyección en la barra lateral
st.sidebar.metric("Sincronización Santiago", hora_actual, delta="UTC-3")

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

    /* --- PROTOCOLO EXCLUSIVO PARA PESTAÑAS (TABS) --- */
    /* Solo afecta al contenedor de pestañas superior */
    div[data-testid="stTabs"] {
        width: 100% !important;
    }
    
    /* Solo afecta a los botones que son PESTAÑAS */
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        flex: 1 !important; 
        min-width: 200px !important; 
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

    /* INPUTS Y UPLOADERS CON BORDE NEÓN */
    div[data-baseweb="input"], div[data-baseweb="textarea"], .stFileUploader {
        border: 1px solid #00f2ff !important;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.2) !important;
        border-radius: 8px !important;
        background: rgba(0, 0, 0, 0.5) !important;
    }

    /* BOTONES ESTÁNDAR (Se mantienen sin flex) */
    .stButton > button {
        background: rgba(0, 242, 255, 0.1) !important;
        color: #00f2ff !important;
        border: 1px solid #00f2ff !important;
        transition: all 0.3s ease;
    }

    /* REACTOR ARC V2 */
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

# --- 6. SIDEBAR - MONITOR DE RED MODULAR (V11 - PRONÓSTICO EXTENDIDO) ---
with st.sidebar:
    st.markdown("<h3 style='color: #00f2ff; text-align: center; letter-spacing: 2px;'>📡 MONITOR DE RED</h3>", unsafe_allow_html=True)
    st.markdown("---")

    # MÓDULO 1: ALERTAS GLOBALES (NOTICIAS)
    with st.expander("🌐 ALERTAS GLOBALES", expanded=False):
        try:
            import feedparser
            import requests
            query = "terremoto+OR+incendio+OR+tsunami+OR+emergencia"
            url_news = f"https://news.google.com/rss/search?q={query}&hl=es-419&gl=CL&ceid=CL:es-419"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url_news, headers=headers, timeout=5)
            feed = feedparser.parse(resp.content)
            
            if feed.entries:
                for entry in feed.entries[:3]:
                    titulo = entry.title.rsplit(' - ', 1)[0]
                    st.markdown(f"""
                        <div style='border-left: 2px solid #ff4b4b; padding-left: 8px; margin-bottom: 10px; background: rgba(255,0,0,0.05);'>
                            <div style='color: #ff4b4b; font-size: 0.6rem; font-weight: bold;'>{entry.published[:12]}</div>
                            <div style='color: #ffffff; font-size: 0.72rem; line-height: 1.1;'>{titulo}</div>
                            <a href='{entry.link}' target='_blank' style='color: #00f2ff; font-size: 0.6rem; text-decoration: none;'>[ VER SEÑAL ]</a>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("No se detectan anomalías.")
        except:
            st.error("Error de enlace satelital.")

    # MÓDULO 2: TELEMETRÍA SÍSMICA
    with st.expander("🛰️ REGISTRO SÍSMICO", expanded=False):
        st.markdown(f"""
            <div class='telemetry-card' style='border-left: 4px solid #00f2ff; padding: 10px;'>
                <div class='telemetry-value' style='font-size: 1rem;'>6.2 Mw - COQUIMBO</div>
                <div style='color: rgba(0,242,255,0.7); font-size: 0.7rem; margin-top: 5px;'>
                    📅 {datetime.datetime.now().strftime("%d/%m/%Y")}<br>
                    📍 42km O de Tongoy<br>
                    🌊 SIN ALERTA DE TSUNAMI
                </div>
            </div>
        """, unsafe_allow_html=True)

    # MÓDULO 3: CONTROL DE INCENDIOS
    with st.expander("🔥 REPORTE DE INCENDIOS", expanded=False):
        estado_inc = "EN COMBATE"
        color_inc = "#ff4b4b" if estado_inc == "FUERA DE CONTROL" else "#ff8800"
        st.markdown(f"""
            <div class='telemetry-card' style='border-left: 4px solid {color_inc}; padding: 10px;'>
                <div class='telemetry-value' style='font-size: 1rem;'>SECTOR: NOVICIADO</div>
                <div style='margin-top: 5px;'>
                    <span style='background: {color_inc}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: bold;'>{estado_inc}</span>
                </div>
                <div class='telemetry-sub' style='font-size: 0.7rem; margin-top: 8px;'>
                    Pudahuel bajo monitoreo aéreo activo.
                </div>
            </div>
        """, unsafe_allow_html=True)

   # MÓDULO 4: CLIMA SEMANAL (PUDAHUEL) - PROTOCOLO DE RENDERIZADO SEGURO
    with st.expander("🌤️ PRONÓSTICO SEMANAL: PUDAHUEL", expanded=False):
        dias = ["Sáb", "Dom", "Lun", "Mar", "Mié", "Jue", "Vie"]
        temps = ["32°", "31°", "29°", "33°", "34°", "30°", "28°"]
        iconos = ["☀️", "☀️", "🌤️", "🔥", "🔥", "🌤️", "☀️"]
        
        # Usamos columnas nativas de Streamlit para asegurar que no haya errores de HTML
        col1, col2, col3 = st.columns(3)
        
        for idx, (d, t, i) in enumerate(zip(dias, temps, iconos)):
            # Distribuimos los días en las 3 columnas de forma automática
            target_col = [col1, col2, col3][idx % 3]
            
            with target_col:
                st.markdown(f"""
                    <div style='text-align: center; background: rgba(0,242,255,0.05); 
                                padding: 5px; border-radius: 5px; border: 1px solid rgba(0,242,255,0.1);
                                margin-bottom: 5px;'>
                        <div style='font-size: 0.6rem; color: #888;'>{d}</div>
                        <div style='font-size: 0.9rem;'>{i}</div>
                        <div style='font-size: 0.8rem; color: #00f2ff; font-weight: bold;'>{t}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center;'>
                <span style='color: #f9d71c; font-size: 0.7rem;'>⚠️ ALERTA UV: EXTREMO</span><br>
                <span style='color: #888; font-size: 0.65rem;'>SENSACIÓN: 36°C</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
    if st.button("🔄 REFRESCAR SISTEMAS", use_container_width=True):
        st.rerun()

    st.caption(f"Sincronización: {datetime.datetime.now().strftime('%H:%M:%S')}")

# --- 7. PESTAÑAS ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS", "✉️ COMUNICACIONES", "🎨 LABORATORIO"])

# --- TAB 0: PROYECTO JARVIS (VERSIÓN COMPLETA Y ALINEADA V51.7 - REVISADA) ---
with tabs[0]:
    # 1. INICIALIZACIÓN DE CANALES DE DATOS
    if "historial_chat" not in st.session_state: st.session_state.historial_chat = []
    if "video_url" not in st.session_state: st.session_state.video_url = None
    if "modo_fluido" not in st.session_state: st.session_state.modo_fluido = False

    # 2. MOTOR DE BÚSQUEDA Y PROCESAMIENTO (Cerebro JARVIS)
    def protocolo_stark_v516():
        query = st.session_state.input_cmd.strip()
        if query:
            import requests
            import base64
            # Añadimos la orden del usuario al historial
            st.session_state.historial_chat.append({"role": "user", "content": query})
            
            try:
               # --- A. PROTOCOLO DE VISIÓN (VERSIÓN RADICAL SIN BYTES) ---
                palabras_img = ["muéstrame", "busca una foto", "proyecta", "imagen de", "foto de", "enséñame", "muestrame"]
                if any(word in query.lower() for word in palabras_img):
                    sujeto = query.lower()
                    for word in palabras_img: 
                        sujeto = sujeto.replace(word, "")
                    sujeto = sujeto.replace("un ", "").replace("una ", "").strip()
                    
                    # 1. URL DIRECTA (No descargamos nada, evitamos BytesIO totalmente)
                    url_final = f"https://image.pollinations.ai/prompt/high_quality_realistic_photo_of_{sujeto.replace(' ', '_')}?width=800&height=500&nologo=true"
                    
                    # 2. FICHA TÉCNICA (Generada por la IA)
                    meta_prompt = f"Genera una FICHA TÉCNICA para '{sujeto}': 🏰 LUGAR, 📏 ALTURA, 📅 CONSTRUCCIÓN, 💡 DATO CURIOSO. Estilo JARVIS. Máximo 50 palabras."
                    info_res = client.chat.completions.create(
                        model=modelo_texto, 
                        messages=[{"role": "user", "content": meta_prompt}]
                    )
                    datos = info_res.choices[0].message.content

                    # 3. RENDERIZADO EN EL HUD
                    with st.chat_message("assistant", avatar="🚀"):
                        st.markdown(f"### 🛰️ ESCANEO FINALIZADO: {sujeto.upper()}")
                        
                        # Mostramos la imagen usando la URL directamente
                        st.image(url_final, use_container_width=True)
                        
                        st.markdown(f"""
                        <div style="border-left: 3px solid #00f2ff; padding-left: 15px; background: rgba(0,242,255,0.05); border-radius: 10px; padding: 10px;">
                            <p style="color: #00f2ff; font-weight: bold; margin-bottom: 5px;">📋 ANÁLISIS TÉCNICO:</p>
                            <div style="color: white; font-family: monospace;">
                                {datos.replace('-', '<br>•')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.session_state.historial_chat.append({"role": "assistant", "content": f"Proyección de {sujeto.upper()} completada."})
                    
                # --- B. PROTOCOLO MULTIMEDIA (VIDEO) ---
                elif any(word in query.lower() for word in ["video", "ver en youtube", "reproduce"]):
                    prompt_intencion = f"Extrae el nombre del video. Responde solo 'BUSCAR: [nombre del video]'. Usuario: {query}"
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
                            st.session_state.video_url = f"https://www.youtube.com/embed/{video_id}"
                            resp = f"He localizado las frecuencias para '{termino}'. Proyectando en el monitor principal, Srta. Diana."
                        else:
                            resp = "Señor, no he podido localizar material audiovisual en los registros de YouTube."
                        st.session_state.historial_chat.append({"role": "assistant", "content": resp})

                # --- C. MOTOR DE RESPUESTA IA (CHAT NORMAL) ---
                else:
                    hist = [{"role": m["role"], "content": m["content"]} for m in st.session_state.historial_chat[-5:]]
                    res = client.chat.completions.create(
                        model=modelo_texto, 
                        messages=[{"role": "system", "content": PERSONALIDAD}] + hist
                    )
                    st.session_state.historial_chat.append({"role": "assistant", "content": res.choices[0].message.content})

            except Exception as e:
                st.error(f"Error en el núcleo de procesamiento: {str(e)}")
            
            st.session_state.input_cmd = "" # Limpieza del terminal para evitar ecos

    # 3. CABECERA DE MANDOS
    c1, c2, c3, c4 = st.columns([1, 1, 1, 7])
    with c1:
        if st.button("🗑️", help="Purgar Historial", key="clear_chat"):
            st.session_state.historial_chat = []
            st.session_state.video_url = None
            st.rerun()
    with c2:
        ml_icon = "🔔" if st.session_state.get("modo_fluido", False) else "🔕"
        if st.button(ml_icon, key="hands_free"):
            st.session_state.modo_fluido = not st.session_state.get("modo_fluido", False)
            st.rerun()
    with c3:
        from streamlit_mic_recorder import mic_recorder
        mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key="mic_v517")
    with c4:
        st.text_input("cmd", placeholder="Órdenes, Srta. Diana...", label_visibility="collapsed", key="input_cmd", on_change=protocolo_stark_v516)

    st.markdown("---")

    # 4. MONITOR MULTIMEDIA HUD
    if st.session_state.video_url:
        st.components.v1.iframe(st.session_state.video_url, height=450)
        if st.button("🔴 Finalizar Proyección", use_container_width=True):
            st.session_state.video_url = None
            st.rerun()

    # 5. REGISTRO VISUAL (CHRONOS)
    chat_box = st.container(height=550, border=False)
    with chat_box:
        for m in st.session_state.historial_chat:
            with st.chat_message(m["role"], avatar="🚀" if m["role"] == "assistant" else "👤"):
                st.markdown(m["content"], unsafe_allow_html=True)

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