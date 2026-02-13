def hablar(texto):
    try:
        api_key = st.secrets["ELEVEN_API_KEY"]
        voice_id = st.secrets["VOICE_ID"]
        
        # Cambiamos a la URL de alta compatibilidad
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id.strip()}"
        
        headers = {
            "xi-api-key": api_key.strip(),
            "Content-Type": "application/json"
        }
        
        data = {
            "text": texto,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        res = requests.post(url, json=data, headers=headers)
        
        if res.status_code == 200:
            b64 = base64.b64encode(res.content).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        else:
            # Si sigue saliendo 404, mostramos un mensaje más claro
            if res.status_code == 404:
                st.error(f"⚠️ Error 404: El ID de voz '{voice_id}' no existe en su cuenta. Por favor, verifíquelo en ElevenLabs.")
            else:
                st.warning(f"Aviso del sistema: {res.status_code} - {res.text}")
            
            # Respaldo gTTS
            tts = gTTS(text=texto, lang='es', tld='es')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Falla en el modulador: {e}")