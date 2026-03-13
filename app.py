import pandas as pd
import re
from datetime import datetime
from docxtpl import DocxTemplate, InlineImage
import io
from docx.shared import Mm
import matplotlib.pyplot as plt
import textwrap
import streamlit as st
import json
import os
import requests
import streamlit as st
import json
import os
import re

# --- 1. NÚCLEO DE MEMORIA Y CONFIGURACIÓN ---
def inicializar_sistema_friday():
    archivo_config = 'friday_settings.json'
    if not os.path.exists(archivo_config):
        base = {
            "config": {"boton_limpiar": False, "mayusculas_auto": True},
            "historial": []
        }
        with open(archivo_config, 'w') as f:
            json.dump(base, f)
        return base
    try:
        with open(archivo_config, 'r') as f:
            return json.load(f)
    except:
        return {"config": {"boton_limpiar": False}, "historial": []}

def guardar_cambios_friday(datos):
    with open('friday_settings.json', 'w') as f:
        json.dump(datos, f)

# Carga inicial de datos
datos_maestros = inicializar_sistema_friday()
config_nube = datos_maestros["config"]
memoria_historia = datos_maestros["historial"]

# --- 2. CONFIGURACIÓN VISUAL Y CSS (EL CUERPO) ---
if "key_carta" not in st.session_state:
    st.session_state.key_carta = 0

if "memoria_historia" not in st.session_state:
    st.session_state.memoria_historia = []

st.markdown("""
    <style>
    .stApp { background-color: #D1D8C4 !important; }
    .section-header { 
        background-color: #004A2F !important; color: white; padding: 10px; 
        border-radius: 5px; font-weight: bold; border-left: 10px solid #C5A059; 
        margin-bottom: 20px; 
    }
    .tabla-carta { 
        width: 100%; border: 2px solid #004A2F; border-collapse: collapse; 
        background-color: white; color: black !important; font-size: 12px; 
        text-transform: uppercase; 
    }
    .tabla-carta td { border: 1.5px solid #004A2F; padding: 8px; font-weight: bold; }
    .celda-titulo { background-color: #4F6228 !important; color: white !important; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 3. MOTOR DE AUTONOMÍA ---
def aplicar_evolucion_universal(orden_usuario):
    if not orden_usuario: return False
    orden = orden_usuario.upper()
    actualizado = False
    
    if "LIMPIAR" in orden or "BOTON DE LIMPIEZA" in orden:
        config_nube["boton_limpiar"] = True
        actualizado = True
    
    if "QUITA EL BOTON" in orden or "BORRA LIMPIAR" in orden:
        config_nube["boton_limpiar"] = False
        actualizado = True

    if actualizado:
        memoria_historia.append(f"Protocolo: {orden}")
        guardar_cambios_friday({"config": config_nube, "historial": memoria_historia})
        return True
    return False

# --- 4. INTERFAZ DE USUARIO ---
st.markdown('<div class="section-header">🧠 FRIDAY: COMANDO CENTRAL DE INTELIGENCIA</div>', unsafe_allow_html=True)

with st.expander("🗣️ CONSOLA DE ÓRDENES", expanded=True):
    col_in, col_ev = st.columns([4, 1])
    nueva_orden = col_in.text_input("INSTRUCCIÓN:", placeholder="Friday, activa el botón de limpieza...")
    if col_ev.button("🚀 EVOLUCIONAR"):
        if nueva_orden:
            # Aquí usamos la función que definimos en el núcleo anterior
            if aplicar_evolucion_universal(nueva_orden):
                st.success("SISTEMA ACTUALIZADO.")
                st.rerun()

    
# --- 1. CONFIGURACIÓN VISUAL (SISTEMA STARK INDUSTRIES) ---
# Nota: st.set_page_config ya se llamó en el núcleo, así que aquí solo definimos el estilo.

st.markdown("""
    <style>
    /* El ADN Visual de FRIDAY */
    .stApp { background-color: #D1D8C4 !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: #004A2F !important; }
    
    .section-header { 
        background-color: #004A2F !important; 
        color: white; padding: 10px; border-radius: 5px; 
        font-weight: bold; border-left: 10px solid #C5A059; 
        margin-bottom: 20px; 
    }

    /* Estilo de la Tabla de Situación (Blanco/Verde Institucional) */
    .tabla-carta { 
        width: 100%; border: 2px solid #004A2F; 
        border-collapse: collapse; background-color: white; 
        color: black !important; font-family: 'Arial', sans-serif; 
        font-size: 12px; text-transform: uppercase; 
    }
    .tabla-carta td { border: 1.5px solid #004A2F; padding: 8px; font-weight: bold; }
    .celda-titulo { background-color: #4F6228 !important; color: white !important; text-align: center !important; font-size: 16px !important; }
    .celda-sub { background-color: #EBF1DE !important; text-align: center !important; }
    .celda-header-perfil { background-color: #D7E3BC !important; text-align: center !important; }
    .mini-tabla td { border: none !important; padding: 3px !important; }
    .border-inner-r { border-right: 1.5px solid #004A2F !important; width: 45%; }
    .border-inner-t { border-top: 1.5px solid #004A2F !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PROTOCOLO DE ESTADO EN BARRA LATERAL ---
# Esto reemplaza su código de sidebar para que use las variables del núcleo
if 'memoria_historia' in globals():
    st.sidebar.markdown(f"### 🛡️ NÚCLEO FRIDAY")
    if memoria_historia:
        st.sidebar.success(f"✅ {len(memoria_historia)} LECCIONES ACTIVAS")
    else:
        st.sidebar.warning("⚠️ ESPERANDO ÓRDENES")

# Función de limpieza optimizada para el sistema de Keys
def limpiar_solo_carta():
    st.session_state.key_carta += 1
    # No necesitamos st.rerun() aquí si se llama desde un botón que ya refresca

# --- 2. MOTOR DE INTELIGENCIA FRIDAY (CARTA DE SITUACIÓN) ---
# 1. Primero la función de apoyo (fuera de la otra)
def extract_value(texto, patron):
    import re
    match = re.search(patron, texto)
    return match.group(1).strip() if match else None

# 2. Luego su función de procesamiento
def procesar_relato_ia(texto):
    # Limpieza inicial y normalización
    texto_u = texto.upper().replace("Aï¿½OS", "AÑOS").replace("N°", "NRO")
    an_actual = 2026 
    
    # Aquí el resto de su código...
    # Ahora cuando llame a extract_value(texto_u, patron), funcionará perfecto.

    # 1. TIPIFICACIÓN
    tip_match = re.search(r'CODIGO DELITO\s?:\s?([^\n]+)', texto_u)
    tipificacion = tip_match.group(1).strip() if tip_match else "ROBO DE ACCESORIOS DE VEHICULOS"

    # 2. TRAMO HORARIO
    h_delito = re.search(r'HORA DEL DELITO\s?:\s?(\d{1,2})', texto_u)
    tramo_hora = f"{int(h_delito.group(1)):02d}:00 A {(int(h_delito.group(1))+1)%24:02d}:00 HRS" if h_delito else "00:00 A 01:00 HRS"

    # 3. LUGAR DE OCURRENCIA
    dir_match = re.search(r'DIRECCIÓN\s?:\s?([^\n\r]+)', texto_u)
    lugar_ocurrencia = dir_match.group(1).strip() if dir_match else "RUTA 68"

    # 4. FUNCIÓN INTERNA: BASE LEGAL (Corregida Indentación)
    def obtener_base_legal(delito):
        # Diccionario dinámico de leyes chilenas (Base: Código Penal)
        leyes = {
            "ROBO CON INTIMIDACION": "Art. 436 inciso 1º del Código Penal",
            "ROBO EN LUGAR NO HABITADO": "Art. 442 del Código Penal",
            "ROBO DE ACCESORIOS": "Art. 443 del Código Penal (Ley 20.931)",
            "HURTO": "Art. 446 del Código Penal",
            "RECEPTACION": "Art. 456 bis A del Código Penal"
        }
        
        delito_u = delito.upper()
        for clave, articulo in leyes.items():
            if clave in delito_u:
                return articulo
        return "Artículo a determinar según relato (Revisión requerida)"

    # Ejecución de base legal
    base_legal_resultado = obtener_base_legal(tipificacion)

    # 5. PERFIL VÍCTIMA (PRIMER AFECTADO)
    if re.search(r'SEXO\s?:\s?MASCULINO', texto_u) or "SR. " in texto_u:
        gv = "MASCULINO"
    elif re.search(r'SEXO\s?:\s?FEMENINO', texto_u) or "SRA. " in texto_u:
        gv = "FEMENINO"
    else:
        gv = "NO INDICA"
    
    ev = "NO INDICA"
    f_nac_vic = re.search(r'FECHA NACIMIENTO\s?:\s?(\d{2})[-/](\d{2})[-/](\d{4})', texto_u)
    if f_nac_vic:
        edad = an_actual - int(f_nac_vic.group(3))
        lim_inf = (edad // 5) * 5
        ev = f"DE {lim_inf} A {lim_inf + 5} AÑOS"
    
    tl = "VIA PUBLICA"
    if any(x in texto_u for x in ["SERVICENTRO", "SHELL", "COPEC"]): tl = "SERVICENTRO"
    elif "DOMICILIO" in texto_u: tl = "DOMICILIO PARTICULAR"

    # 6. ESPECIES
    items = []
    segmento_especies = re.search(r'(?:BIENES SUSTRAIDOS|ESPECIES SUSTRAIDAS|SUSTRACCION DE).*?(?=TESTIGOS|AVALUADOS|CITACION|$)', texto_u, re.DOTALL)
    texto_especies = segmento_especies.group(0) if segmento_especies else texto_u

    if "COMPUTADOR" in texto_especies:
        marca_pc = extract_value(texto_especies, r'MARCA\s+([A-Z]+)') or "LENOVO"
        items.append(f"01 COMPUTADOR PORTATIL {marca_pc}")
    if "TELEFONO" in texto_especies or "CELULAR" in texto_especies:
        marca_tel = extract_value(texto_especies, r'MARCA\s+([A-Z]+)') or "HUAWEI"
        items.append(f"01 TELEFONO CELULAR {marca_tel}")
    
    if "VEHICULO" in texto_u:
        marca_v = extract_value(texto_u, r'MARCA\s+([A-Z]+)') or "NO INDICADA"
        patente_v = extract_value(texto_u, r'PATENTE\s+([A-Z0-9\-]+)') or "S/P"
        if "ROBO DE VEHICULO" in tipificacion:
            items.append(f"VEHICULO PARTICULAR MARCA {marca_v} PATENTE {patente_v}")

    esp = " / ".join(items) if items else "ACCESORIOS VARIOS"

    # 7. DELINCUENTE
    gd = "MASCULINO" if any(x in texto_u for x in ["SUJETO", "INDIVIDUO", "HOMBRE"]) else "NO INDICA"
    ed = "NO INDICA"
    cd = "VESTIMENTA OSCURA" if "OSCURA" in texto_u else "NO INDICA"
    md = "VEHICULO" if "VEHICULO" in texto_u and "A PIE" not in texto_u else "A PIE"

    # 8. RESUMEN ADAPTATIVO (MODUS OPERANDI)
    if any(x in texto_u for x in ["ESTACIONADO", "APARCADO", "DEJO SU"]): est_v = "MANTENÍA SU VEHÍCULO ESTACIONADO"
    elif any(x in texto_u for x in ["CAMINANDO", "A PIE"]): est_v = "TRANSITABA A PIE"
    else: est_v = "SE ENCONTRABA"

    if any(x in texto_u for x in ["FRACTURARON", "VIDRIO"]): acc_v = "TRAS FRACTURAR UN VENTANAL DEL MÓVIL, SUSTRAJERON"
    elif any(x in texto_u for x in ["INTIMIDÓ", "AMENAZÓ"]): acc_v = "MEDIANTE INTIMIDACIÓN, LOGRARON SUSTRAER"
    else: acc_v = "PROCEDIERON A LA SUSTRACCIÓN DE"

    desc = "AL REGRESAR AL LUGAR"
    if "PERCATANDOSE" in texto_u: desc = "AL PERCATARSE DE LA SITUACIÓN"
    elif "INFORMANDOLE" in texto_u: desc = "TRAS SER ALERTADO POR TERCEROS"

    mo_final = f"EN CIRCUNSTANCIAS QUE LA VÍCTIMA {est_v} EN {tl}, {desc} NOTÓ QUE SUJETOS DESCONOCIDOS {acc_v} {esp}, PARA LUEGO DARSE A LA FUGA."

    # Retornamos 13 valores (incluyendo base legal al final)
    return tipificacion, tramo_hora, lugar_ocurrencia, gv, ev, tl, esp, gd, ed, cd, md, mo_final.upper(), base_legal_resultado

# --- 3. INTERFAZ ---
st.markdown('<div class="section-header">🧠 FRIDAY: COMANDO CENTRAL DE INTELIGENCIA</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📄 ACTA STOP", "📈 STOP TRIMESTRAL", "📍 INFORME GEO", "📋 CARTA DE SITUACIÓN"])

with t1:
    st.markdown('<div class="section-header">📝 ACTA STOP MENSUAL</div>', unsafe_allow_html=True)
    with st.form("form_acta"):
        c1, c2 = st.columns(2)
        c1.text_input("Semana de estudio", value="SEMANA 08")
        c1.text_input("Fecha de sesión", value="24-02-2026")
        c2.text_input("Compromiso Carabineros", value="INCREMENTAR PATRULLAJES")
        st.text_area("Problemática Delictual 26ª Comisaría", value="AUMENTO DE ROBO CON INTIMIDACIÓN EN SECTOR CUADRANTE 231")
        st.text_input("Nombre", value="DIANA SANDOVAL ASTUDILLO")
        st.text_input("Grado", value="C.P.R. Analista Social")
        st.text_input("Cargo", value="OFICINA DE OPERACIONES")
        st.form_submit_button("🛡️ GENERAR ACTA")

with t2:
    st.markdown('<div class="section-header">📈 STOP TRIMESTRAL: COMPROMISOS Y ACUERDOS</div>', unsafe_allow_html=True)
    
    # Iniciamos el formulario
    with st.form("form_trim"):
        ct1, ct2 = st.columns(2)
        ct1.text_input("Periodo Trimestral", value="DIC-ENE-FEB")
        ct1.text_input("Fecha Sesión STOP", value="24-02-2026")
        ct2.text_input("Unidad / Repartición", value="26ª COMISARÍA PUDAHUEL")
        
        ct1.text_input("Nombre Asistente", value="INDICAR NOMBRE")
        ct1.text_input("Grado Asistente", value="INDICAR GRADO")
       
        st.markdown('---')
        st.markdown('**🖋️ PIE DE FIRMA - VALIDACIÓN DE ACTA**')
        
        col_f1, col_f2 = st.columns(2)
        # Usamos col_f2 para mantener su diseño original
        col_f2.text_input("Analista Responsable", value="DIANA SANDOVAL ASTUDILLO")
        col_f2.text_input("Grado Analista", value="C.P.R. Analista Social")
        col_f2.text_input("Cargo Analista", value="OFICINA DE OPERACIONES")
        
        submit_trim = st.form_submit_button("🛡️ GENERAR TRIMESTRAL")

    if submit_trim:
        st.info("Sistemas FRIDAY: Procesando Acta Trimestral...")
       
# 1. FUNCIÓN DE TABLA MEJORADA (SIN CORTES Y DISEÑO INSTITUCIONAL)
def crear_tabla_profesional(df, nombre_archivo, ancho_pulgadas=10):
    alto_pulgadas = (len(df) * 0.5) + 0.8
    fig, ax = plt.subplots(figsize=(ancho_pulgadas, alto_pulgadas))
    ax.axis('off')

    tabla = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center',
        colColours=["#1E7421"] * len(df.columns) 
    )

    tabla.auto_set_font_size(False)
    tabla.set_fontsize(11)
    tabla.scale(1, 2) 

    for (row, col), cell in tabla.get_celld().items():
        cell.set_edgecolor('black')
        cell.set_linewidth(1.5)
        if row == 0:
            cell.set_text_props(weight='bold', color='white')

    plt.savefig(nombre_archivo, bbox_inches='tight', dpi=200, pad_inches=0.1)
    plt.close()

# --- ESTRUCTURA DE LA PESTAÑA INFORME GEO ---
with t3:
    st.markdown('<div class="section-header">📍 INFORME GEO: GENERACIÓN PROFESIONAL</div>', unsafe_allow_html=True)
    
    with st.form("form_geo_final"):
        col1, col2, col3 = st.columns(3)
        # DOE y Fechas
        doe_n = col1.text_input("DOE N°", value="248812153")
        doe_fecha = col1.text_input("Fecha DOE", value="03-03-2026")
        inf_fecha = col1.text_input("Fecha Informe", value="03 de marzo de 2026")
        
        # Funcionario
        funcionario = col2.text_input("Funcionario", value="JUAN ANDRES URRUTIA LOBOS")
        grado = col2.text_input("Grado", value="SARGENTO 2°")
        unidad = col2.text_input("Unidad", value="GRUPO DE ADIESTRAMIENTO CANINO")
        
        # Ubicación
        domicilio = col3.text_input("Domicilio", value="PASAJE PILCOMAYO 8501")
        subcomisaria = col3.text_input("Subcomisaría", value="26A COMISARIA PUDAHUEL")
        cuadrante = col3.text_input("Cuadrante", value="232-A")
        
        cp1, cp2, cp3 = st.columns([2, 1, 1])
        periodo_txt = cp1.text_input("Periodo", value="03-12-2025 al 03-03-2026")
        mapa_img = cp2.file_uploader("SUBIR MAPA SAIT", type=['png', 'jpg'])
        excel_geo = cp3.file_uploader("SUBIR EXCEL/CSV", type=['xlsx', 'csv'])
        
        submit_geo = st.form_submit_button("🛡️ GENERAR INFORME GEO")

## --- FUNCIÓN DE SOPORTE (Asegúrese de que esté definida antes del bloque principal) ---
def ajustar_texto_largo(texto, ancho=35):
    """Divide el texto para evitar desbordamientos en las tablas del informe."""
    import textwrap
    if not isinstance(texto, str):
        texto = str(texto)
    return "\n".join(textwrap.wrap(texto, width=ancho))

# --- LÓGICA DE PROCESAMIENTO (Fuera del Form, dependiente del botón) ---
if submit_geo:
    if not mapa_img or not excel_geo:
        st.error("❌ Faltan archivos (Mapa o Excel) para procesar.")
    else:
        try:
            # 1. PROCESAMIENTO DE DATOS
            # Soporte para CSV y Excel con limpieza de cabeceras
            df = pd.read_csv(excel_geo) if excel_geo.name.endswith('csv') else pd.read_excel(excel_geo)
            df.columns = [c.upper().strip() for c in df.columns]
            total_casos = len(df)

            # Inicializar variables de seguridad
            resumen_dmcs = pd.DataFrame()
            dia_frec, hora_frec = "NO IDENTIFICADO", "NO IDENTIFICADO"

            if 'DELITO' in df.columns:
                df['DELITO'] = df['DELITO'].astype(str).str.upper()
                resumen_dmcs = df['DELITO'].value_counts().reset_index()
                resumen_dmcs.columns = ['TIPO DE DELITO (DMCS)', 'CANTIDAD']
                
                # Aplicación corregida de la función de ajuste (usando 'ancho')
                resumen_dmcs_tabla = resumen_dmcs.copy()
                resumen_dmcs_tabla['TIPO DE DELITO (DMCS)'] = resumen_dmcs_tabla['TIPO DE DELITO (DMCS)'].apply(
                    lambda x: ajustar_texto_largo(x, ancho=35)
                )
                crear_tabla_profesional(resumen_dmcs_tabla, "img_delitos.png", ancho_pulgadas=12)

            if 'DIA' in df.columns and 'RANGO HORA' in df.columns:
                resumen_tramos = df.groupby(['DIA', 'RANGO HORA']).size().reset_index(name='CANTIDAD')
                resumen_tramos = resumen_tramos.sort_values(by=['CANTIDAD', 'DIA'], ascending=[False, True]).head(10)
                resumen_tramos.columns = ['DÍA', 'TRAMO HORARIO', 'CANTIDAD']
                
                resumen_tramos_tabla = resumen_tramos.copy()
                resumen_tramos_tabla['TRAMO HORARIO'] = resumen_tramos_tabla['TRAMO HORARIO'].apply(
                    lambda x: ajustar_texto_largo(x, ancho=20)
                )
                crear_tabla_profesional(resumen_tramos_tabla, "img_tramos.png", ancho_pulgadas=10)
                
                dia_frec = df['DIA'].mode()[0] if not df['DIA'].empty else "N/A"
                hora_frec = df['RANGO HORA'].mode()[0] if not df['RANGO HORA'].empty else "N/A"
            
            # Variables para el análisis
            delito_principal = resumen_dmcs.iloc[0]['TIPO DE DELITO (DMCS)'] if not resumen_dmcs.empty else "DMCS"
            cantidad_real = resumen_dmcs.iloc[0]['CANTIDAD'] if not resumen_dmcs.empty else 0

            analisis_ia = (f"Tras el análisis georreferencial en el cuadrante {cuadrante}, se registran {total_casos} eventos DMCS en el periodo. "
                           f"El delito con mayor prevalencia es '{delito_principal}' con {cantidad_real} casos registrados. "
                           f"La criticidad se concentra los días {dia_frec} en el tramo {hora_frec}. "
                           f"Se sugiere intensificar patrullajes preventivos en el radio de 300 mts de {domicilio}.")

            # 2. GENERACIÓN DEL DOCUMENTO WORD
            doc = DocxTemplate("INFORME GEO.docx")
            o_mapa = InlineImage(doc, mapa_img, width=Mm(150))
            o_tabla1 = InlineImage(doc, "img_delitos.png", width=Mm(145))
            o_tabla2 = InlineImage(doc, "img_tramos.png", width=Mm(130))

            # Manejo seguro del periodo
            p_split = periodo_txt.split(" al ")
            p_inicio = p_split[0] if len(p_split) > 0 else "INICIO"
            p_fin = p_split[1] if len(p_split) > 1 else "FIN"

            contexto = {
                "domicilio": domicilio.upper(), "jurisdiccion": subcomisaria.upper(), "fecha_actual": inf_fecha.upper(),
                "doe": doe_n, "fecha_doe": doe_fecha, "grado_solic": grado.upper(),
                "solicitante": funcionario.upper(), "unidad_solic": unidad.upper(),
                "periodo_inicio": p_inicio, "periodo_fin": p_fin,
                "cuadrante": cuadrante, "mapa": o_mapa, "total_dmcs": total_casos,
                "tabla": o_tabla1, "tabla_horarios": o_tabla2,
                "dia_max": dia_frec, "hora_max": hora_frec, "conclusion_ia": analisis_ia.upper()
            }

            doc.render(contexto)
            
            # Guardado en memoria
            output = io.BytesIO()
            doc.save(output)
            output.seek(0)

            st.success("✅ Informe generado exitosamente.")
            st.download_button(
                label="📥 DESCARGAR INFORME OFICIAL",
                data=output,
                file_name=f"Informe_Geo_{cuadrante}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        except Exception as e:
            st.error(f"Error en el motor FRIDAY: {e}")

# --- PESTAÑA 4: CARTA DE SITUACIÓN (ESTILO Y LÓGICA FINAL) ---
with t4:
    st.markdown('<div class="section-header">📋 GENERADOR DE CARTA DE SITUACIÓN</div>', unsafe_allow_html=True)
    
    if 'key_relato' not in st.session_state:
        st.session_state.key_relato = 0

    relato_in = st.text_area(
        "PEGUE EL PARTE POLICIAL AQUÍ:", 
        height=250, 
        key=f"relato_area_{st.session_state.key_relato}"
    )
    
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        enviar = st.button("⚡ GENERAR ANÁLISIS TÁCTICO")
    with col_btn2:
        if st.button("🗑️ BORRAR RELATO"):
            st.session_state.key_relato += 1
            st.rerun()

    if enviar and relato_in:
        with st.status("🤖 FRIDAY: Analizando naturaleza del procedimiento...", expanded=False):
            resultado = procesar_relato_ia(relato_in)
            
            # Sincronización de campos
            if len(resultado) >= 12:
                tip, tr, loc, gv, ev, tl_clase, esp, gd, ed, cd, md_ia, mo_ia = resultado[:12]
            else:
                datos_relleno = resultado + (None,) * (12 - len(resultado))
                tip, tr, loc, gv, ev, tl_clase, esp, gd, ed, cd, md_ia, mo_ia = datos_relleno

            import re
            texto_analisis = relato_in.upper()
            
            # 1. DETECCIÓN DE DELITO
            es_lesion = any(x in texto_analisis for x in ["LESION", "GOLPE", "AGRESION", "RIÑA", "PUÑO", "PATADA"])
            
            # 2. SINCRONIZACIÓN DE MEDIO DE DESPLAZAMIENTO
            md_final = "MOTOCICLETA" if "MOTO" in texto_analisis else "A PIE"
            sujeto_v = f"UN SUJETO EN MOTOCICLETA" if md_final == "MOTOCICLETA" else "UN SUJETO"

            # 3. CONSTRUCCIÓN DEL RESUMEN TÁCTICO
            if es_lesion:
                accion_v = "PROPINA GOLPES A LA VÍCTIMA" if "GOLPE" in texto_analisis else "AGREDE FÍSICAMENTE A LA VÍCTIMA"
                resumen_final = f"VICTIMA SE ENCONTRABA EN LA VIA PUBLICA, MOMENTOS EN QUE ES ABORDADA POR {sujeto_v}, QUIEN SIN PROVOCACION PREVIA {accion_v}, RESULTANDO ESTA CON LESIONES DE DIVERSA CONSIDERACION, PARA LUEGO DARSE A LA FUGA."
                especie_display = "NO REGISTRA (PROCEDIMIENTO POR LESIONES)"
            else:
                transporte_v = "A PIE"
                if "BUS" in texto_analisis or "MICRO" in texto_analisis: transporte_v = "EN TRANSPORTE PUBLICO"
                elif "VEHICULO" in texto_analisis: transporte_v = "EN SU VEHICULO"
                
                accion_v = "LE ARREBATA" if "ARREBATA" in texto_analisis else "SUSTRAE"
                especie_v = str(esp).upper() if esp else "ESPECIES"
                resumen_final = f"VICTIMA TRANSITABA {transporte_v} POR LA VIA PUBLICA, MOMENTOS EN QUE ES ABORDADA POR {sujeto_v}, QUIEN {accion_v} {especie_v}, DÁNDOSE POSTERIORMENTE A LA FUGA."
                especie_display = esp if esp else "SIN ESPECIFICAR"

            # 4. LIMPIEZA DE PRIVACIDAD
            nombres_p = r'(YESSENIA|DEL CARMEN|GARCIA|ARO|JENIPHER|SABANDO|TOLEDO|MARIVOR|DOMICILIADA|IDENTIDAD|CEDULA)'
            resumen_final = re.sub(nombres_p, 'VICTIMA', resumen_final)
            resumen_final = re.sub(r'\d{1,2}\.\d{3}\.\d{3}-[\dKk]', '', resumen_final)

            # 5. LÓGICA DE LUGAR
            if any(h in texto_analisis for h in ["HOSPITAL", "CLINICA", "POSTA"]):
                tl_final = "CENTRO DE SALUD"
                loc_final = str(loc).upper()
            else:
                tl_final = "VIA PUBLICA" if any(v in texto_analisis for v in ["AVENIDA", "CALLE", "TENIENTE CRUZ"]) else tl_clase
                loc_final = str(loc).upper()

        # --- 6. RENDERIZADO CON TAMAÑO DE LETRA CORREGIDO ---
        st.markdown(f"""
        <style>
            .tabla-final {{ width: 100%; border-collapse: collapse; font-family: 'Arial', sans-serif; color: black; border: 1px solid #333; }}
            .tabla-final td {{ border: 1px solid #333; padding: 10px; font-size: 14px !important; vertical-align: middle; background-color: white; }}
            .encabezado-verde {{ background-color: #1E7421 !important; color: white !important; text-align: center; font-weight: bold; font-size: 15px !important; }}
            .sub-encabezado {{ background-color: #D7E4BD !important; text-align: center; font-weight: bold; font-size: 14px !important; }}
            .perfil-header {{ background-color: #EBF1DE !important; text-align: center; font-weight: bold; font-size: 14px !important; }}
            .dato-negrita {{ font-weight: bold; font-size: 14px !important; }}
            .resumen-texto {{ text-align: justify; line-height: 1.5; font-size: 13px !important; }}
        </style>

        <table class="tabla-final">
            <tr>
                <td rowspan="2" class="encabezado-verde" style="width: 35%;">{tip}</td>
                <td class="sub-encabezado" style="width: 30%;">TRAMO</td>
                <td class="sub-encabezado" style="width: 35%;">LUGAR OCURRENCIA</td>
            </tr>
            <tr>
                <td style="text-align: center; height: 50px;" class="dato-negrita">{tr}</td>
                <td style="text-align: center;" class="dato-negrita">{loc_final}</td>
            </tr>
            <tr>
                <td class="perfil-header">PERFIL VÍCTIMA</td>
                <td class="perfil-header">PERFIL DELINCUENTE</td>
                <td class="perfil-header">MODUS OPERANDI</td>
            </tr>
            <tr>
                <td style="vertical-align: top;">
                    <span class="dato-negrita">GENERO:</span> {gv}<br>
                    <span class="dato-negrita">RANGO:</span> {ev}<br>
                    <span class="dato-negrita">LUGAR:</span> <span style="color:green; font-weight:bold;">{tl_final}</span><br>
                    <span class="dato-negrita">ESPECIE:</span> {especie_display}
                </td>
                <td style="vertical-align: top;">
                    <span class="dato-negrita">VICTIMARIO:</span> {gd}<br>
                    <span class="dato-negrita">EDAD:</span> {ed}<br>
                    <span class="dato-negrita">FISICO:</span> {cd}<br>
                    <span class="dato-negrita">MED. DESPL.:</span> {md_final}
                </td>
                <td class="resumen-texto">{resumen_final}</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)