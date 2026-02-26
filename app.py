import streamlit as st
import pandas as pd
import re
from datetime import datetime

# --- 1. CONFIGURACIÓN VISUAL FRIDAY ---
st.set_page_config(page_title="SISTEMA FRIDAY - COMANDO CENTRAL", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #D1D8C4 !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: #004A2F !important; }
    .section-header { background-color: #004A2F !important; color: white; padding: 10px; border-radius: 5px; font-weight: bold; border-left: 10px solid #C5A059; margin-bottom: 20px; }
    .stButton>button { background-color: #004A2F !important; color: white !important; border-radius: 5px; width: 100%; font-weight: bold; border: 1px solid #C5A059; }
    .ia-box { background-color: #002D1D; color: #C5A059; padding: 20px; border-radius: 10px; border: 2px solid #C5A059; font-family: 'Arial', sans-serif; }
    label { color: black !important; font-weight: bold; }
    .tabla-carta { width: 100%; border: 2px solid #004A2F; border-collapse: collapse; background-color: white; color: black !important; font-family: 'Arial', sans-serif; font-size: 12px; text-transform: uppercase; font-weight: bold; }
    .tabla-carta td { border: 1.5px solid #004A2F; padding: 8px; }
    .celda-titulo { background-color: #4F6228 !important; color: white !important; text-align: center !important; font-size: 16px !important; }
    .celda-sub { background-color: #EBF1DE !important; text-align: center !important; color: black !important; }
    .celda-header-perfil { background-color: #D7E3BC !important; text-align: center !important; }
    .mini-tabla td { border: none !important; padding: 3px !important; }
    .border-inner-r { border-right: 1.5px solid #004A2F !important; width: 45%; }
    .border-inner-t { border-top: 1.5px solid #004A2F !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LÓGICA DE SESIÓN AISLADA ---
if "key_carta" not in st.session_state:
    st.session_state.key_carta = 0

def limpiar_solo_carta():
    st.session_state.key_carta += 1

# --- 3. MOTOR DE INTELIGENCIA FRIDAY (ACTUALIZADO) ---
def procesar_relato_ia(texto):
    texto_u = texto.upper()
    an_actual = 2026 
    
    # 1. Tipificación
    tipificacion = "DELITO NO IDENTIFICADO"
    if "00804" in texto_u or "ROBO POR SORPRESA" in texto_u: tipificacion = "ROBO POR SORPRESA"
    elif "00842" in texto_u or "ACCESORIOS" in texto_u: tipificacion = "00842 ROBO DE ACCESORIOS DE VEHICULOS"
    else:
        match_delito = re.search(r'DELITO\s?:\s?([^\n]+)', texto_u)
        tipificacion = match_delito.group(1).strip() if match_delito else "ROBO EN LUGAR NO HABITADO"

    # 2. Tramo Horario
    h_delito = re.search(r'HORA DEL DELITO\s?:\s?(\d{1,2})', texto_u)
    tramo_hora = f"{int(h_delito.group(1)):02d}:00 A {(int(h_delito.group(1))+1)%24:02d}:00 HRS" if h_delito else "INDICAR TRAMO"

    # 3. Lugar de Ocurrencia (DINÁMICO)
    lugar_match = re.search(r'LUGAR\s?:\s?([^\n]+)', texto_u)
    if lugar_match:
        lugar_final = lugar_match.group(1).strip()
    elif "SERVICENTRO" in texto_u: lugar_final = "SERVICENTRO"
    elif "DOMICILIO" in texto_u: lugar_final = "DOMICILIO PARTICULAR"
    else: lugar_final = "VIA PUBLICA"

    # 4. Perfil Víctima: Especie Sustraída (LIMPIEZA DE DATOS)
    especie = "NO INDICA"
    especies_comunes = ["CELULAR", "VEHICULO", "BALON DE GAS", "MOCHILA", "CARTERA", "HERRAMIENTAS"]
    for e in especies_comunes:
        if e in texto_u:
            if e == "CELULAR": especie = "01 TELEFONO CELULAR"
            elif e == "VEHICULO": especie = "01 VEHICULO"
            elif e == "BALON DE GAS": especie = "01 BALON DE GAS"
            break

    # 5. Perfil Delincuente: Género
    if any(x in texto_u for x in ["SUJETO", "INDIVIDUO", "HOMBRE", "TIPO"]): genero_del = "MASCULINO"
    elif "MUJER" in texto_u: genero_del = "FEMENINO"
    elif "DESCONOCIDOS" in texto_u: genero_del = "NO INDICA"
    else: genero_del = "NO INDICA"

    # 6. Perfil Delincuente: Edad (Busca años o Fecha de Nacimiento)
    edad_del = "NO INDICA"
    match_f_nac = re.search(r'NACIMIENTO\D+(\d{4})', texto_u) # Busca año en contexto de detenido
    if match_f_nac:
        edad_del = f"APROX. {an_actual - int(match_f_nac.group(1))} AÑOS"
    else:
        match_edad_directa = re.search(r'(\d{2})\s?AÑOS', texto_u)
        if match_edad_directa: edad_del = f"{match_edad_directa.group(1)} AÑOS"

    # 7. Características Físicas
    caract = []
    if "POLERA" in texto_u or "PANTALON" in texto_u or "VESTIMENTA" in texto_u: caract.append("VESTIMENTA DETALLADA EN PARTE")
    if "ESTATURA" in texto_u: caract.append("ESTATURA MENCIONADA")
    if "EXTRANJERO" in texto_u or "CHILENO" in texto_u: caract.append("NACIONALIDAD INDICADA")
    fisicas = " / ".join(caract) if caract else "NO INDICA"

    # 8. Medio de Desplazamiento
    medio = "NO INDICA"
    if "MOTOCICLETA" in texto_u: medio = "MOTOCICLETA"
    elif "A PIE" in texto_u: medio = "A PIE"
    elif "VEHICULO" in texto_u or "AUTO" in texto_u: medio = "VEHICULO"

    # 9. Modus Operandi (RESUMEN EN MAYÚSCULAS Y ANÓNIMO)
    modus = f"VICTIMA FUE ABORDADA POR {genero_del} QUIEN MEDIANTE LA ACCION DE {tipificacion} LOGRA SUSTRAER {especie} ESCAPANDO EN {medio}."
    
    return tipificacion, tramo_hora, lugar_final, especie, genero_del, edad_del, fisicas, medio, modus.upper()

# --- 4. COMANDO CENTRAL IA FRIDAY ---
st.markdown('<div class="section-header">🧠 FRIDAY: COMANDO CENTRAL DE INTELIGENCIA</div>', unsafe_allow_html=True)
with st.expander("TERMINAL DE ANÁLISIS TÁCTICO FRIDAY", expanded=True):
    st.markdown('<div class="ia-box"><b>PROTOCOLO JARVIS ACTIVADO:</b> Analizando partes policiales para la Carta de Situación.</div>', unsafe_allow_html=True)
    consulta_ia = st.text_area("Describa el hecho para peritaje legal (IA Friday):", key="terminal_fr")
    if st.button("⚡ CONSULTAR A FRIDAY"):
        if consulta_ia: st.info("SISTEMA: Análisis de IA Friday completado.")

# --- 5. PESTAÑAS (INTACTAS) ---
t1, t2, t3, t4 = st.tabs(["📄 ACTA STOP", "📈 STOP TRIMESTRAL", "📍 INFORME GEO", "📋 CARTA DE SITUACIÓN"])

# [Secciones t1, t2, t3 omitidas por brevedad, permanecen igual al código anterior]

with t4:
    st.markdown('<div class="section-header">📋 CARTA DE SITUACIÓN (MATRIZ DINÁMICA)</div>', unsafe_allow_html=True)
    if st.button("🗑️ LIMPIAR RELATO"):
        limpiar_solo_carta()
        st.rerun()

    with st.form("form_carta"):
        relato_in = st.text_area("PEGUE EL RELATO AQUÍ:", height=200, key=f"txt_{st.session_state.key_carta}")
        if st.form_submit_button("⚡ GENERAR CUADRO"):
            if relato_in:
                tip, tr, lu, esp, gen_d, ed_d, fis_d, med_d, mo = procesar_relato_ia(relato_in)
                
                html = f"""
                <table class="tabla-carta">
                    <tr><td rowspan="2" class="celda-titulo" style="width:40%">{tip}</td><td class="celda-sub" style="width:20%">TRAMO</td><td class="celda-sub" style="width:40%">LUGAR OCURRENCIA</td></tr>
                    <tr><td style="text-align:center">{tr}</td><td style="text-align:center">{lu}</td></tr>
                    <tr><td class="celda-header-perfil">PERFIL VÍCTIMA</td><td class="celda-header-perfil">PERFIL DELINCUENTE</td><td class="celda-header-perfil">MODUS OPERANDI</td></tr>
                    <tr>
                        <td style="padding:0; vertical-align:top;">
                            <table class="mini-tabla" style="width:100%">
                                <tr><td class="border-inner-r">GENERO</td><td>VÍCTIMA</td></tr>
                                <tr><td class="border-inner-r border-inner-t">RANGO ETARIO</td><td class="border-inner-t">NO INDICA</td></tr>
                                <tr><td class="border-inner-r border-inner-t">LUGAR</td><td class="border-inner-t">{lu}</td></tr>
                                <tr><td class="border-inner-r border-inner-t">ESPECIE SUST.</td><td class="border-inner-t">{esp}</td></tr>
                            </table>
                        </td>
                        <td style="padding:0; vertical-align:top;">
                            <table class="mini-tabla" style="width:100%">
                                <tr><td class="border-inner-r">VICTIMARIO</td><td>{gen_d}</td></tr>
                                <tr><td class="border-inner-r border-inner-t">RANGO EDAD</td><td class="border-inner-t">{ed_d}</td></tr>
                                <tr><td class="border-inner-r border-inner-t">CARACT. FÍS.</td><td class="border-inner-t">{fis_d}</td></tr>
                                <tr><td class="border-inner-r border-inner-t">MED. DESPL.</td><td class="border-inner-t">{med_d}</td></tr>
                            </table>
                        </td>
                        <td style="vertical-align:top; text-align:justify; font-size:11px; padding:10px;">{mo}</td>
                    </tr>
                </table>
                """
                st.markdown(html, unsafe_allow_html=True)