import streamlit as st
import os # Nueva para manejar archivos

# --- PROTOCOLO DE MEMORIA INFINITA ---
def cargar_memoria():
    if os.path.exists("historial_jarvis.txt"):
        with open("historial_jarvis.txt", "r", encoding="utf-8") as f:
            return f.read()
    return ""

def guardar_en_memoria(usuario, bot):
    with open("historial_jarvis.txt", "a", encoding="utf-8") as f:
        f.write(f"Diana: {usuario}\nJARVIS: {bot}\n---\n")

# Al iniciar la sesión, cargamos el pasado
if "memoria_pasada" not in st.session_state:
    st.session_state.memoria_pasada = cargar_memoria()

# --- EN TU PESTAÑA DE CHAT ---
with tab1:
    st.info("Sistemas de memoria persistente: ACTIVADOS")
    
    # Botón opcional para ver qué recuerda JARVIS de ayer
    if st.checkbox("Ver memorias antiguas"):
        st.text_area("Registros pasados:", st.session_state.memoria_pasada, height=200)

    # Lógica de respuesta JARVIS
    if prompt := st.chat_input("Diga algo, Srta. Diana..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("Consultando archivos históricos..."):
            # JARVIS ahora usa el pasado como contexto
            sys_msg = f"""Eres JARVIS. Tienes acceso a esta memoria de conversaciones pasadas:
            {st.session_state.memoria_pasada}
            Responde de forma coherente con lo que ya han hablado."""
            
            # ... (Aquí va tu código de Groq y respuesta) ...
            
            # ¡EL PASO CLAVE! Guardamos la nueva interacción
            guardar_en_memoria(prompt, response)