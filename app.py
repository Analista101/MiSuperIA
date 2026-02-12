import streamlit as st
import pandas as pd # Para manejar Excel
from groq import Groq
import PyPDF2
from gtts import gTTS
import base64
import io

st.set_page_config(page_title="Diana IA: Edición Oficina", layout="wide")

# --- SEGURIDAD ---
api_key_groq = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else ""

st.title("🚀 Diana Súper IA: Modo Excel Pro")

pestanas = st.tabs(["💬 Chat & Voz", "📊 Excel Pro", "📸 Editor", "🎨 Artista"])

# --- PESTAÑA 1: CHAT (Lo mantenemos igual) ---
with pestanas[0]:
    st.info("El chat ahora también puede responder dudas sobre los Excel que subas.")

# --- PESTAÑA 2: EXCEL PRO (¡NUEVO!) ---
with pestanas[1]:
    st.header("Análisis y Creación de Excel")
    
    opcion = st.radio("¿Qué quieres hacer?", ["Leer un Excel", "Crear un Excel nuevo"])
    
    if opcion == "Leer un Excel":
        archivo_ex = st.file_uploader("Sube tu archivo .xlsx", type=['xlsx'])
        if archivo_ex:
            df = pd.read_excel(archivo_ex)
            st.write("### Vista previa de tus datos:")
            st.dataframe(df) # Muestra la tabla en la app
            
            if st.button("🔍 Analizar datos con IA"):
                resumen = f"Tengo esta tabla: {df.head().to_string()}. Resúmela."
                client = Groq(api_key=api_key_groq)
                resp = client.chat.completions.create(messages=[{"role":"user","content":resumen}], model="llama-3.3-70b-versatile").choices[0].message.content
                st.success(resp)

    else:
        st.write("### Crea una tabla rápida")
        nombre_col = st.text_input("Nombres de columnas (separados por coma):", "Nombre, Edad, Ciudad")
        datos_fila = st.text_area("Datos de la fila (separados por coma):", "Diana, 25, Madrid")
        
        if st.button("📥 Generar y Descargar Excel"):
            columnas = [c.strip() for c in nombre_col.split(",")]
            datos = [[d.strip() for d in datos_fila.split(",")]]
            nuevo_df = pd.DataFrame(datos, columns=columnas)
            
            # Crear el archivo en memoria para descargar
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                nuevo_df.to_excel(writer, index=False)
            st.download_button("Descargar archivo Excel", data=output.getvalue(), file_name="tabla_diana.xlsx")