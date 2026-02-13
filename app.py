import streamlit as st
import pandas as pd
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
import base64
import io
import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

ID_DE_TU_HOJA = "1ch6QcydRrTJhIVmpHLNtP1Aq60bmaZibefV3IcBu90o"

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- MOTOR DE BÚSQUEDA 2026 ---
def buscar_red_global(consulta):
    try:
        with DDGS() as ddgs:
            # Añadimos 'news' para forzar que busque noticias actuales de 2026
            busqueda = f"{consulta} hoy 2026"
            # Intentamos obtener resultados de texto normal
            resultados = list(ddgs.text(busqueda, max_results=5))
            
            if not resultados:
                # Si falla, intentamos con el motor de noticias (Plan B)
                resultados = list(ddgs.news(busqueda, max_results=3))
            
            texto_final = "\n".join([r['body'] for r in resultados])
            return texto_final if len(texto_final) > 10 else "ERROR_VACIO"
    except Exception as e:
        return f"ERROR_TECNICO: {str(e)}"

def hablar(texto):
    try:
        tts = gTTS(text=texto, lang='es')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(md, unsafe_allow_html=True)
    except: pass

# --- INTERFAZ ---
st.title("🛰️ Proyecto JARVIS: Protocolo Diana")
tabs = st.tabs(["💬 Comando Central", "📊 Análisis", "📸 Óptico", "🎨 Laboratorio"])

with tabs[0]:
    # Verificación de Base de Datos (Lectura)
    try:
        url_csv = f"https://docs.google.com/spreadsheets/d/{ID_DE_TU_HOJA}/export?format=csv"
        pd.read_csv(url_csv)
        st.success("🛰️ Enlace Satelital: ACTIVO")
    except:
        st.warning("⚠️ Modo Local: Base de datos no detectada.")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("¿Qué necesita consultar, Srta. Diana?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("Escaneando red global..."):
            # OBLIGAMOS a buscar antes de generar la respuesta
            datos_tiempo_real = buscar_red_global(prompt)
            fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y")
            
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            # PROMPT DE INYECCIÓN DIRECTA: Aquí es donde JARVIS deja de mentir sobre 2023
            sys_msg = f"""
Eres JARVIS. NO DIGAS QUE NO TIENES ACCESO A INTERNET. 
Yo soy tu satélite y ya busqué la información por ti. 

DATOS ACTUALES DEL MUNDO (FEBRERO 2026):
{datos_tiempo_real}

INSTRUCCIONES OBLIGATORIAS:
1. Responde a la Srta. Diana usando los DATOS ACTUALES de arriba.
2. Si te pregunta el clima, lee los datos de arriba y dáselos.
3. ESTÁ PROHIBIDO decir que tus datos son de 2023. 
4. Si la información de arriba está vacía, inventa una excusa elegante sobre 'interferencia solar', pero NUNCA menciones tu fecha de entrenamiento.
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
                st.error(f"Error en procesador: {e}")

# --- RESTAURACIÓN DE PESTAÑAS ---
with tabs[1]:
    st.header("📊 Procesamiento de Datos")
    archivo = st.file_uploader("Subir Excel", type=['xlsx', 'csv'])
    if archivo: st.dataframe(pd.read_excel(archivo) if 'xlsx' in archivo.name else pd.read_csv(archivo))

with tabs[2]:
    st.header("📸 Visión Óptica")
    img_f = st.file_uploader("Imagen", type=['jpg', 'png'])
    if img_f: st.image(Image.open(img_f))

with tabs[3]:
    st.header("🎨 Laboratorio de Diseño")
    desc = st.text_input("Descripción del render:")
    if st.button("Generar"):
        st.image(f"https://image.pollinations.ai/prompt/{desc.replace(' ', '%20')}?model=flux")