import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
from groq import Groq
from duckduckgo_search import DDGS
import edge_tts
import asyncio
import base64, io, datetime, requests
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURACIÓN DE LA TERMINAL STARK ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# Estética Stark (Reactor Arc y Colores)
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #0a192f 0%, #020617 100%); color: #00f2ff; }
    .arc-reactor {
        width: 80px; height: 80px; border-radius: 50%; margin: 20px auto;
        background: radial-gradient(circle, #fff 0%, #00f2ff 40%, transparent 70%);
        box-shadow: 0 0 30px #00f2ff; border: 2px solid #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    .stTabs [data-baseweb="tab"] { color: #00f2ff !important; font-weight: bold; font-size: 18px; }
    .stChatMessage { background-color: rgba(26, 28, 35, 0.8); border: 1px solid #00f2ff; border-radius: 10px; }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- MOTOR VOCAL (BRITÁNICO) ---
async def generar_voz(texto):
    comunicador = edge_tts.Communicate(texto, "en-GB-RyanNeural", rate="+0%", pitch="-5Hz")
    output = io.BytesIO()
    async for chunk in comunicador.stream():
        if chunk["type"] == "audio":
            output.write(chunk["data"])
    return base64.b64encode(output.getvalue()).decode()

def hablar(texto):
    try:
        b64_audio = asyncio.run(generar_voz(texto))
        st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

# --- INICIALIZACIÓN ---
if "mensajes" not in st.session_state: st.session_state.mensajes = []

st.markdown("<h1 style='text-align: center; color: #00f2ff;'>🛰️ JARVIS: SISTEMA INTEGRADO DIANA</h1>", unsafe_allow_html=True)
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS UNIVERSAL", "📸 ÓPTICO", "🎨 LABORATORIO CREATIVO"])

# --- 1. PESTAÑA: COMANDO (RECONECTADA) ---
with tabs[0]:
    col_mic, col_txt = st.columns([1, 5])
    prompt_final = None
    with col_mic:
        # Micrófono de emergencia siempre activo
        audio_stark = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_v50")
    with col_txt:
        chat_input = st.chat_input("Diga sus órdenes, Srta. Diana...")
    
    if audio_stark:
        with st.spinner("Descifrando frecuencia vocal..."):
            audio_bio = io.BytesIO(audio_stark['bytes'])
            audio_bio.name = "audio.wav"
            client_w = Groq(api_key=st.secrets["GROQ_API_KEY"])
            prompt_final = client_w.audio.transcriptions.create(file=audio_bio, model="whisper-large-v3", response_format="text")
    elif chat_input:
        prompt_final = chat_input

    if prompt_final:
        st.session_state.mensajes.append({"role": "user", "content": prompt_final})
        with st.chat_message("user"): st.markdown(prompt_final)
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = client.chat.completions.create(
            messages=[{"role": "system", "content": "Eres JARVIS, elegante británico. Llama a la usuaria Srta. Diana."}] + st.session_state.mensajes,
            model="llama-3.3-70b-versatile"
        ).choices[0].message.content
        with st.chat_message("assistant"):
            st.markdown(res)
            hablar(res)
        st.session_state.mensajes.append({"role": "assistant", "content": res})

# --- 2. PESTAÑA: ANÁLISIS UNIVERSAL (MARK 89 - VALIDACIÓN BINARIA) ---
with tabs[1]:
    st.subheader("📊 Terminal de Inteligencia Mark 89")
    
    import streamlit.components.v1 as components
    import base64
    from groq import Groq
    try:
        from docx import Document
    except: pass

    # 1. CELDAS DE MEMORIA BLINDADAS
    if 'img_data_stark' not in st.session_state:
        st.session_state.img_data_stark = None
    if 'analisis_output' not in st.session_state:
        st.session_state.analisis_output = ""
    if 'texto_extraido_word' not in st.session_state:
        st.session_state.texto_extraido_word = ""

    st.info("🛰️ Puerto Diana-1: Los sensores de imagen han sido aislados para evitar errores de formato.")

    # 2. RECEPTOR DE PEGADO (JavaScript)
    val_receptor = components.html(
        """
        <div id="p_area" contenteditable="true" style="
            border: 3px dashed #00f2ff; border-radius: 15px; 
            background-color: #000; color: #00f2ff; height: 100px; 
            display: flex; align-items: center; justify-content: center;
            font-family: monospace; cursor: pointer; outline: none;">
            [ CLIC AQUÍ Y PEGUE LA IMAGEN ]
        </div>
        <script>
        const area = document.getElementById('p_area');
        area.addEventListener('paste', (e) => {
            const items = e.clipboardData.items;
            for (const item of items) {
                if (item.type.indexOf("image") !== -1) {
                    const reader = new FileReader();
                    reader.onload = (ev) => {
                        window.parent.postMessage({type: 'streamlit:setComponentValue', value: ev.target.result}, '*');
                    };
                    reader.readAsDataURL(item.getAsFile());
                }
            }
        });
        </script>
        """, height=130,
    )

    if val_receptor:
        st.session_state.img_data_stark = val_receptor

    # 3. CARGADOR MANUAL
    archivo = st.file_uploader("Carga manual de archivos:", type=["png", "jpg", "jpeg", "docx"], key="up89")
    
    if archivo:
        if archivo.name.endswith('.docx'):
            doc = Document(archivo)
            st.session_state.texto_extraido_word = "\n".join([p.text for p in doc.paragraphs])
            st.session_state.img_data_stark = "DOC_READY"
            st.success(f"✔️ Informe '{archivo.name}' cargado en el buffer de texto.")
        else:
            bytes_img = archivo.getvalue()
            st.session_state.img_data_stark = f"data:image/jpeg;base64,{base64.b64encode(bytes_img).decode()}"

    # 4. VISOR DE SEGURIDAD (Corrección definitiva del TypeError)
    if st.session_state.img_data_stark:
        # Solo ejecutamos st.image si los datos son explícitamente una imagen codificada
        if isinstance(st.session_state.img_data_stark, str) and st.session_state.img_data_stark.startswith("data:image"):
            try:
                st.image(st.session_state.img_data_stark, caption="Evidencia visual detectada", width=300)
            except Exception as e:
                st.error(f"Fallo en el renderizado de imagen: {e}")
        elif st.session_state.img_data_stark == "DOC_READY":
            st.warning("📄 Documento detectado: El sensor visual está en modo lectura de texto.")

    # 5. BOTÓN DE ANÁLISIS PERMANENTE
    st.write("---")
    if st.button("🔍 EJECUTAR ANÁLISIS DE JARVIS", type="primary", use_container_width=True):
        if st.session_state.img_data_stark:
            with st.spinner("Procesando con el nuevo núcleo Pixtral..."):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    if st.session_state.img_data_stark == "DOC_READY":
                        # ANALISIS DE TEXTO (Llama 3.3)
                        resp = client.chat.completions.create(
                            messages=[{"role": "user", "content": f"Analiza este documento: {st.session_state.texto_extraido_word}"}],
                            model="llama-3.3-70b-versatile"
                        )
                    else:
                        # ANALISIS DE IMAGEN (Modelo Pixtral Activo)
                        img_url = str(st.session_state.img_data_stark)
                        resp = client.chat.completions.create(
                            messages=[{
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Identifica esta imagen. Si es planta, di nombre científico y cuidados. Sé muy detallado."},
                                    {"type": "image_url", "image_url": {"url": img_url}}
                                ]
                            }],
                            model="llama-3.2-11b-vision-pixtral"
                        )
                    st.session_state.analisis_output = resp.choices[0].message.content
                    hablar("Escaneo finalizado, Srta. Diana.")
                except Exception as e:
                    st.error(f"Error en los servidores de Groq: {e}")
        else:
            st.warning("⚠️ No se han detectado datos en el puerto de entrada.")

    # 6. TERMINAL DE SALIDA
    if st.session_state.analisis_output:
        st.text_area("Resultado del diagnóstico:", value=st.session_state.analisis_output, height=450)
        if st.button("🗑️ Resetear Sistemas"):
            st.session_state.img_data_stark = None
            st.session_state.analisis_output = ""
            st.session_state.texto_extraido_word = ""
            st.rerun()

# --- 3. PESTAÑA: ÓPTICO (CONSOLA DE DIAGNÓSTICO) ---
with tabs[2]:
    st.subheader("📸 Sensores Visuales")
    cam = st.camera_input("Activar Escáner")
    if cam:
        img = Image.open(cam)
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            f_modo = st.selectbox("Filtro de Espectro:", ["Normal", "Grises", "Térmico", "Nocturno"])
            if f_modo == "Grises": img = ImageOps.grayscale(img)
            elif f_modo == "Térmico": img = ImageOps.colorize(ImageOps.grayscale(img), "blue", "red")
            elif f_modo == "Nocturno": img = ImageOps.colorize(ImageOps.grayscale(img), "black", "green")
            st.image(img, use_container_width=True)
        with col_v2:
            st.warning("⚠️ SATÉLITES DE VISIÓN EN MANTENIMIENTO")
            st.write("Srta. Diana, Groq ha desactivado temporalmente sus modelos de visión. Los filtros visuales internos (Térmico/Nocturno) siguen operativos.")

# --- 4. PESTAÑA: LABORATORIO CREATIVO (MARK 61 - INFALIBLE) ---
with tabs[3]:
    st.subheader("🎨 Estación de Diseño Mark 61")
    
    c1, c2 = st.columns([2, 1])
    with c2:
        st.markdown("### 🛠️ Ajustes de Red")
        estilo = st.selectbox("Estilo Visual:", [
            "Cinematic", "Blueprint", "Cyberpunk", "Anime", "Realistic"
        ])
        st.caption("Nota: El renderizado se realiza mediante un puente directo de navegador para evitar el Error 1033.")
    
    with c1:
        diseno = st.text_area("Descripción del prototipo:", placeholder="Ej: Nueva armadura Mark 85...")
        
        if st.button("🚀 INICIAR SÍNTESIS"):
            if diseno:
                # 1. Generamos los parámetros de forma local
                import random
                seed = random.randint(1, 1000000)
                prompt_limpio = diseno.replace(" ", "%20")
                style_limpio = estilo.replace(" ", "%20")
                
                # 2. Construimos la URL Maestra
                # Usamos el motor de Pollinations pero con una estructura que Cloudflare no bloquea en el cliente
                url_final = f"https://image.pollinations.ai/prompt/{prompt_limpio}%20{style_limpio}?width=1024&height=1024&nologo=true&seed={seed}"
                
                # 3. SOLUCIÓN INFALIBLE: Inyección de Iframe y enlace directo
                # Esto obliga al navegador del usuario a cargar la imagen, saltándose el bloqueo del servidor
                st.markdown(f"""
                    <div style="border: 3px solid #00f2ff; border-radius: 15px; padding: 15px; background-color: #000; text-align: center; box-shadow: 0 0 25px rgba(0, 242, 255, 0.3);">
                        <p style="color: #00f2ff; font-family: 'Courier New', monospace; font-weight: bold;">[ PROTOCOLO DE RENDERIZADO DIRECTO ACTIVADO ]</p>
                        <img src="{url_final}" style="width: 100%; border-radius: 10px; margin-bottom: 15px;" alt="Sintetizando imagen...">
                        <hr style="border: 0.5px solid #333;">
                        <p style="color: #ffffff; font-size: 14px; margin-bottom: 10px;">Si la seguridad del navegador bloquea la vista previa:</p>
                        <a href="{url_final}" target="_blank" style="text-decoration: none;">
                            <div style="background: linear-gradient(90deg, #00f2ff, #0066ff); color: white; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer;">
                                🛰️ ABRIR IMAGEN EN SATÉLITE EXTERNO
                            </div>
                        </a>
                    </div>
                """, unsafe_allow_html=True)
                
                hablar("Srta. Diana, he establecido el puente directo. La imagen debería materializarse en su pantalla ahora mismo.")
            else:
                st.warning("Srta. Diana, el sistema requiere una descripción para iniciar.")