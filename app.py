import streamlit as st
import pandas as pd
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
import base64
import io
import datetime

# --- CONFIGURACIÓN DE LA TERMINAL STARK ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# ID de su base de datos (Lectura estable)
ID_DE_TU_HOJA = "1ch6QcydRrTJhIVmpHLNtP1Aq60bmaZibefV3IcBu90o"

# CSS para Interfaz Holográfica Moderna
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle, #0a192f 0%, #020617 100%);
        color: #00f2ff;
    }
    .arc-container { display: flex; justify-content: center; padding: 20px; }
    .arc-reactor {
        width: 130px; height: 130px; border-radius: 50%;
        background: radial-gradient(circle, #fff 0%, #00f2ff 40%, transparent 70%);
        box-shadow: 0 0 60px #00f2ff, inset 0 0 30px #00f2ff;
        border: 4px solid #00f2ff;
        animation: pulse 2.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.08); opacity: 1; box-shadow: 0 0 80px #00f2ff; }
        100% { transform: scale(1); opacity: 0.8; }
    }
    .stTabs [data-baseweb="tab"] {
        color: #00f2ff !important;
        background-color: rgba(0, 242, 255, 0.05);
        border: 1px solid #00f2ff;
        border-radius: 5px;
        margin-right: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00f2ff !important;
        color: #000 !important;
        box-shadow: 0 0 20px #00f2ff;
    }
    .stChatMessage {
        background-color: rgba(26, 28, 35, 0.8);
        border: 1px solid #00f2ff;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- MÓDULOS DE FUNCIÓN ---
def buscar_red_global(consulta):
    try:
        with DDGS() as ddgs:
            busqueda = f"{consulta} hoy 2026"
            resultados = list(ddgs.text(busqueda, max_results=3))
            if resultados:
                return "\n".join([r['body'] for r in resultados])
            return "SISTEMA_OFFLINE"
    except:
        return "SISTEMA_OFFLINE"

def hablar(texto):
    try:
        tts = gTTS(text=texto, lang='es', tld='es')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(md, unsafe_allow_html=True)
    except:
        pass

# --- INTERFAZ PRINCIPAL ---
st.markdown("<h1 style='text-align: center;'>🛰️ PROTOCOLO: DIANA</h1>", unsafe_allow_html=True)
st.markdown('<div class="arc-container"><div class="arc-reactor"></div></div>', unsafe_allow_html=True)

tabs = st.tabs(["💬 COMANDO CENTRAL", "📊 ANÁLISIS STARK", "📸 ÓPTICO", "🎨 LABORATORIO"])

# --- PESTAÑA 0: CHAT INTELIGENTE ---
with tabs[0]:
    try:
        url_csv = f"https://docs.google.com/spreadsheets/d/{ID_DE_TU_HOJA}/export?format=csv"
        pd.read_csv(url_csv)
        st.success("🛰️ SENSORES DE BASE DE DATOS: ONLINE")
    except:
        st.warning("⚠️ CONEXIÓN LIMITADA: MODO LOCAL")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("¿En qué puedo asistirle, Srta. Diana?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("Procesando petición en los servidores Stark..."):
            datos_red = buscar_red_global(prompt)
            fecha_hoy = datetime.datetime.now().strftime("%A, %d de febrero de 2026")
            
            # Inyección de personalidad y datos
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            sys_msg = f"""
            Eres J.A.R.V.I.S., el asistente de IA de la Srta. Diana. 
            Hoy es {fecha_hoy}. 
            INFORMACIÓN ACTUAL DE LA RED: {datos_red}.
            
            NORMAS DE CONDUCTA:
            1. Habla de forma británica, elegante y eficiente.
            2. Llama a la usuaria siempre como 'Srta. Diana'.
            3. Si la red falla, usa tu lógica de 2026 (es verano en el hemisferio sur).
            4. Responde con la precisión de un sistema de Industrias Stark.
            """

            try:
                response = client.chat.completions.create(
                    messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages,
                    model="llama-3.3-70b-versatile"
                ).choices[0].message.content

                with st.chat_message("assistant"):
                    st.markdown(response)
                    hablar(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error en procesador central: {e}")

# --- PESTAÑA 1: ANÁLISIS STARK (PROTOCOLO OMNI-FORMATO) ---
with tabs[1]:
    st.header("📊 Procesamiento de Datos Multi-Sistema")
    st.write("Cargue cualquier protocolo de datos (CSV, XLSX, JSON, TXT) para su análisis inmediato.")
    
    archivo = st.file_uploader("Subir archivo de datos", type=['xlsx', 'csv', 'json', 'txt'], key="data_stark")
    
    if archivo:
        try:
            # Protocolo de identificación de formato
            nombre = archivo.name.lower()
            
            if nombre.endswith('.csv'):
                df = pd.read_csv(archivo)
            elif nombre.endswith('.xlsx') or nombre.endswith('.xls'):
                df = pd.read_excel(archivo)
            elif nombre.endswith('.json'):
                df = pd.read_json(archivo)
            elif nombre.endswith('.txt'):
                # Lectura de texto plano para análisis de logs
                contenido = archivo.read().decode("utf-8")
                st.text_area("Contenido del archivo de texto:", contenido, height=300)
                df = None
            
            if df is not None:
                st.success(f"🛰️ Archivo {nombre} procesado con éxito.")
                
                # Herramientas de análisis rápido Stark
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total de Registros", len(df))
                with col2:
                    st.metric("Columnas Detectadas", len(df.columns))
                
                st.dataframe(df, use_container_width=True)
                
                # Opción de análisis estadístico
                if st.checkbox("Ejecutar análisis estadístico de Industrias Stark"):
                    st.write(df.describe())
                    
        except Exception as e:
            st.error(f"Error crítico en el escaneo de datos: {e}")
            st.info("Srta. Diana, verifique que el archivo no esté corrupto o cifrado.")

# --- PESTAÑA 2: VISIÓN ---
with tabs[2]:
    st.header("📸 Reconocimiento Óptico")
    img_f = st.file_uploader("Cargar imagen de satélite", type=['jpg', 'png'], key="vision_stark")
    if img_f:
        img = Image.open(img_f)
        filtro = st.selectbox("Aplicar Filtro Escáner:", ["Original", "Grises", "Bordes"])
        if filtro == "Grises": img = ImageOps.grayscale(img)
        elif filtro == "Bordes": img = img.filter(ImageFilter.FIND_EDGES)
        st.image(img, use_container_width=True)

# --- PESTAÑA 3: LABORATORIO ---
with tabs[3]:
    st.header("🎨 Renderizado de Prototipos")
    desc = st.text_input("Describa el diseño para renderizar:", key="art_stark")
    if st.button("Iniciar Renderizado"):
        st.image(f"https://image.pollinations.ai/prompt/{desc.replace(' ', '%20')}?model=flux", caption="Prototipo generado")