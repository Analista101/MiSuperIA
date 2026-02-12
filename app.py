import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS # Nueva herramienta de búsqueda

# --- FUNCIÓN DE BÚSQUEDA JARVIS ---
def buscar_en_internet(consulta):
    with DDGS() as ddgs:
        # Busca los 3 mejores resultados
        resultados = [r for r in ddgs.text(consulta, max_results=3)]
        return str(resultados)

# --- LÓGICA DE RESPUESTA INTELIGENTE ---
def respuesta_pro(prompt, api_key):
    client = Groq(api_key=api_key)
    
    # Decidimos si necesita buscar en internet
    if "quién es" in prompt.lower() or "clima" in prompt.lower() or "noticias" in prompt.lower():
        datos_web = buscar_en_internet(prompt)
        contexto_extra = f"\nDatos actuales encontrados en la red: {datos_web}"
    else:
        contexto_extra = ""

    instruccion = f"""Eres JARVIS. Tu tono es sofisticado y profesional. 
    Usa estos datos si son relevantes: {contexto_extra}. 
    Responde siempre con elegancia a la Srta. Diana."""

    mensajes = [{"role": "system", "content": instruccion}] + st.session_state.messages
    
    completion = client.chat.completions.create(
        messages=mensajes,
        model="llama-3.3-70b-versatile",
        temperature=0.4
    )
    return completion.choices[0].message.content

# --- EN TU PESTAÑA DE CHAT ---
if prompt := st.chat_input("Sistemas listos. ¿En qué puedo ayudarla, Srta. Diana?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("Accediendo a la red de datos..."):
        respuesta = respuesta_pro(prompt, api_key_groq)
        with st.chat_message("assistant"):
            st.markdown(respuesta)
            hablar(respuesta) # Tu función de voz
        st.session_state.messages.append({"role": "assistant", "content": respuesta})