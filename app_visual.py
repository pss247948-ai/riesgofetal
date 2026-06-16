import streamlit as st
import requests
import pandas as pd
import time

# =========================================
# CONFIGURACIÓN DE LA PÁGINA
# =========================================
st.set_page_config(
    page_title="Predicción Riesgo Fetal",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# =========================================
# CONFIGURACIÓN DE LA API (Cambiar aquí)
# =========================================
# Para pruebas locales usa: ""
# Para producción en la nube usa: "https://apifetal.onrender.com/predecir"
API_URL = "https://apifetal.onrender.com/predecir"

# =========================================
# INICIALIZACIÓN DE HISTORIAL (MEMORIA)
# =========================================
if "historial" not in st.session_state:
    st.session_state["historial"] = []

# =========================================
# ESTILOS CSS PERSONALIZADOS (UI/UX)
# =========================================
estilos_css = """
<style>
[data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"] {
    display: none !important;
}
h1 {
    color: #2E86C1 !important;
    text-align: center;
    font-weight: 700;
    margin-bottom: 10px;
}
.stButton > button {
    transition: all 0.3s ease;
    border-radius: 8px;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
}
.subtitulo {
    text-align: center;
    font-size: 1.1rem;
    color: #555;
    margin-bottom: 30px;
}
</style>
"""
st.markdown(estilos_css, unsafe_allow_html=True)

# =========================================
# BARRA LATERAL (SIDEBAR) - INFO DEL MANUSCRITO
# =========================================
with st.sidebar:
    st.image("https://i.imgur.com/BKQqYiH.png", width=100)
    st.header("Sobre el Sistema")
    st.markdown("""
    Este sistema evalúa la cardiotocografía (CTG) para detectar la **hipoxia fetal**, una deficiencia de oxígeno que compromete al feto.
    
    ### 🧠 Motor Predictivo
    Utiliza un modelo **XGBoost** optimizado mediante *Machine Learning* y validado clínicamente.
    
    ### 📊 Rendimiento del Modelo
    * **Exactitud Global:** 95.77%
    * **Sensibilidad (Patológico):** 100%
    * **F1-Score (Patológico):** 96.7%
    """)
    st.success("✅ **Alta Fiabilidad:** El modelo identifica correctamente el 100% de los casos de sufrimiento fetal severo (cero falsos negativos en la clase patológica).")
    st.markdown("---")
    st.markdown("<div style='font-size: 0.8em; color: gray;'>Basado en el estudio: <i>Clasificación del estado fetal mediante XGBoost y atributos de Cardiotocografía</i></div>", unsafe_allow_html=True)

# =========================================
# ENCABEZADO
# =========================================
st.title("👶 Sistema de Análisis de Cardiotocografía")
st.markdown("<p class='subtitulo'>Ingrese los valores del monitor fetal para predecir el estado de salud de manera instantánea y reducir la subjetividad clínica.</p>", unsafe_allow_html=True)

# CREACIÓN DE PESTAÑAS
tab1, tab2 = st.tabs(["🧑‍⚕️ Análisis Individual", "📁 Carga Masiva (CSV)"])

# =========================================
# PESTAÑA 1: ANÁLISIS INDIVIDUAL
# =========================================
with tab1:
    mensaje_ejemplo = st.empty()

    with st.container(border=True):
        st.subheader("📝 Datos del Paciente (Cardiotocografía)")
        col1, col2 = st.columns(2)

        # TOOLTIPS (help) DETALLADOS Y PLACEHOLDERS CORTOS
        with col1:
            dp = st.number_input("DP (Desaceleraciones Prolongadas)", format="%.8f", value=None, 
                                 placeholder="Desaceleraciones prolongadas por segundo.", 
                                 help="Las desaceleraciones prolongadas son caídas de la frecuencia cardíaca fetal por debajo de la línea base que duran entre 2 y 10 minutos. Una tasa alta advierte de un riesgo agudo de hipoxia severa.")
            
            altv = st.number_input("ALTV (% Variabilidad Alta)", format="%.2f", value=None, 
                                   placeholder="Porcentaje de tiempo con variabilidad anormal a largo plazo.", 
                                   help="Representa el porcentaje de tiempo con variabilidad alterada a largo plazo. Esta métrica evalúa las fluctuaciones macroscópicas; su pérdida constante puede sugerir un compromiso del sistema nervioso autónomo del feto.")
            
            ac = st.number_input("AC (Aceleraciones)", format="%.8f", value=None, 
                                 placeholder="Aceleraciones por segundo.", 
                                 help="Las aceleraciones son incrementos transitorios de la frecuencia cardíaca (usualmente ≥ 15 latidos durante ≥ 15 segundos). Su presencia normal es un signo muy tranquilizador de bienestar y buena oxigenación fetal.")
            
            mean = st.number_input("Mean (Media)", format="%.2f", value=None, 
                                   placeholder="Media del histograma.", 
                                   help="Es el valor promedio del ritmo cardíaco fetal procesado matemáticamente a partir del histograma. Ayuda a visualizar la tendencia sostenida de los latidos durante todo el examen.")
            
            astv = st.number_input("ASTV (% Variabilidad Anormal)", format="%.2f", value=None, 
                                   placeholder="Porcentaje de tiempo con variabilidad anormal a corto plazo.", 
                                   help="Mide el tiempo en el que la variación latido a latido (micro-fluctuaciones) se encuentra reducida o anormal. Una variabilidad a corto plazo disminuida es una de las principales señales de alarma de acidosis fetal.")

        with col2:
            median = st.number_input("Median (Mediana)", format="%.2f", value=None, 
                                     placeholder="Mediana del histograma.", 
                                     help="Es el valor de frecuencia cardíaca que se ubica exactamente en el medio de toda la distribución. Es clínicamente útil porque ignora picos irreales o posibles interferencias cortas del sensor.")
            
            mode = st.number_input("Mode (Moda)", format="%.2f", value=None, 
                                   placeholder="Moda del histograma.", 
                                   help="Es el ritmo cardíaco que más tiempo ha marcado el monitor (el pico más alto de la distribución). Generalmente coincide de forma casi exacta con la Frecuencia Basal real del feto.")
            
            min_val = st.number_input("Min (Mínimo)", format="%.2f", value=None, 
                                      placeholder="Mínimo del histograma.", 
                                      help="Representa la lectura de frecuencia cardíaca más baja detectada en toda la sesión. Sirve para evaluar rápidamente la magnitud y profundidad de las bradicardias sufridas.")
            
            nzeros = st.number_input("Nzeros (Ceros)", format="%.2f", value=None, 
                                     placeholder="Ceros del histograma.", 
                                     help="Mide la cantidad de lecturas nulas en la señal digitalizada. Usualmente se vincula a pérdidas de contacto del transductor Doppler por movimientos bruscos o señal inestable.")
            
            lb = st.number_input("LB (Frecuencia Basal)", format="%.2f", value=None, 
                                 placeholder="Frecuencia cardíaca del feto (generalmente entre 106 y 160 latidos).", 
                                 help="Es el nivel de reposo del ritmo cardíaco del feto. Se considera normal cuando se sitúa en el rango de 110 a 160 latidos por minuto. Valores sostenidos muy altos (taquicardia) o bajos (bradicardia) indican problemas.")

    valores_inputs = [dp, altv, ac, mean, astv, median, mode, min_val, nzeros, lb]

    st.write("")

    if st.button("🔍 Predecir Estado Fetal", type="primary", use_container_width=True):
        if any(v is None for v in valores_inputs):
            st.warning("⚠️ Por favor, complete todos los campos numéricos antes de predecir.")
        else:
            payload = {
                "DP": dp, "ALTV": altv, "AC": ac, "Mean": mean, "ASTV": astv,
                "Median": median, "Mode": mode, "Min": min_val, "Nzeros": nzeros, "LB": lb
            }

            try:
                with st.spinner("Analizando datos con el modelo de IA..."):
                    response = requests.post(API_URL, json=payload)

                if response.status_code == 200:
                    res = response.json()
                    estado = res["estado"]
                    nsp = res["NSP"]
                    confianza_num = float(str(res["confianza"]).replace("%", ""))

                    nuevo_registro = {
                        "DP": dp, "ALTV": altv, "AC": ac, "Mean": mean, "ASTV": astv,
                        "Median": median, "Mode": mode, "Min": min_val, "Nzeros": nzeros, "LB": lb,
                        "Diagnóstico": estado.upper(),
                        "Confianza": f"{confianza_num:.2f}%"
                    }
                    st.session_state["historial"].append(nuevo_registro)

                    with st.container(border=True):
                        st.subheader("📊 Resultado del Análisis Diagnóstico")
                        if nsp == 1:
                            st.success(f"### ✅ Estado Normal\n*Recomendación:* No hay riesgo evidente de hipoxia detectado.\n\n*Confianza del modelo predictivo: {confianza_num:.2f}%*")
                        elif nsp == 2:
                            st.warning(f"### ⚠️ Estado Sospechoso\n*Recomendación:* Ambigüedad clínica detectada. Requiere vigilancia y chequeo médico detallado.\n\n*Confianza del modelo predictivo: {confianza_num:.2f}%*")
                        else:
                            st.error(f"### 🚨 Estado Patológico\n*Recomendación:* Riesgo severo de sufrimiento fetal. Atención de alta prioridad inmediata requerida.\n\n*Confianza del modelo predictivo: {confianza_num:.2f}%*")
                        st.progress(int(confianza_num))

                else:
                    st.error(f"Error de comunicación con el servidor: {response.status_code}")

            except Exception as e:
                st.error(f"No se pudo conectar con el motor de predicción.\n\nDetalle técnico: {e}")

    # HISTORIAL DE PACIENTES
    if len(st.session_state["historial"]) > 0:
        st.write("")
        with st.container(border=True):
            st.subheader("📋 Historial de Análisis Recientes")
            st.dataframe(pd.DataFrame(st.session_state["historial"]), use_container_width=True)
            if st.button("🗑️ Limpiar Historial", type="secondary"):
                st.session_state["historial"] = []
                st.rerun()

# =========================================
# PESTAÑA 2: CARGA MASIVA AVANZADA (CSV)
# =========================================
with tab2:
    st.info("💡 *Instrucciones:* Sube tu archivo CSV. Usa las herramientas para seleccionar rangos (ej. 1 a 50), o marca/desmarca pacientes manualmente en la tabla.")
    
    archivo_subido = st.file_uploader("Sube tu archivo de pacientes (.csv)", type=["csv"])

    if archivo_subido is not None:
        try:
            if ("archivo_actual" not in st.session_state) or (st.session_state["archivo_actual"] != archivo_subido.name):
                df_temp = pd.read_csv(archivo_subido, sep=None, engine='python')
                df_temp.columns = df_temp.columns.str.strip()
                
                columnas_requeridas = ["DP", "ALTV", "AC", "Mean", "ASTV", "Median", "Mode", "Min", "Nzeros", "LB"]
                
                if not set(columnas_requeridas).issubset(set(df_temp.columns)):
                    st.error(f"⚠️ El archivo no tiene las columnas correctas. Faltan: {set(columnas_requeridas) - set(df_temp.columns)}")
                    st.session_state["df_masivo"] = None
                else:
                    df_limpio = df_temp[columnas_requeridas].copy()
                    df_limpio.insert(0, "Paciente_ID", range(1, len(df_limpio) + 1))
                    df_limpio.insert(0, "Analizar", False) 
                    
                    st.session_state["df_masivo"] = df_limpio
                    st.session_state["archivo_actual"] = archivo_subido.name

            if "df_masivo" in st.session_state and st.session_state["df_masivo"] is not None:
                df_masivo = st.session_state["df_masivo"]
                total_filas = len(df_masivo)

                with st.container(border=True):
                    st.write("### 🛠️ Herramientas de Selección Rápida")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("☑️ Seleccionar Todos", use_container_width=True):
                            df_masivo["Analizar"] = True
                    with col_btn2:
                        if st.button("🔲 Deseleccionar Todos", use_container_width=True):
                            df_masivo["Analizar"] = False

                    st.markdown("---")
                    
                    st.write("*Añadir pacientes por intervalo:* (Ej: del 80 al 110)")
                    col_int1, col_int2, col_int3 = st.columns([1, 1, 1])
                    with col_int1:
                        inicio = st.number_input("Desde paciente N°:", min_value=1, max_value=total_filas, value=1, step=1)
                    with col_int2:
                        valor_seguro_fin = max(inicio, min(inicio, total_filas))
                        fin = st.number_input("Hasta paciente N°:", min_value=inicio, max_value=total_filas, value=valor_seguro_fin, step=1)
                    with col_int3:
                        st.write("") 
                        if st.button("➕ Marcar Intervalo", use_container_width=True, type="secondary"):
                            st.session_state["df_masivo"].loc[inicio-1 : fin-1, "Analizar"] = True
                            st.rerun()

                st.write("### 📋 Tabla de Pacientes (Edición Manual)")
                
                columnas_deshabilitadas = [col for col in df_masivo.columns if col != "Analizar"]
                
                df_editado = st.data_editor(
                    df_masivo,
                    column_config={
                        "Analizar": st.column_config.CheckboxColumn(
                            "Seleccionar", default=False, help="Marca para incluir en el análisis"
                        ),
                        "Paciente_ID": st.column_config.NumberColumn(
                            "ID Paciente", format="%d" 
                        )
                    },
                    disabled=columnas_deshabilitadas,
                    hide_index=True,
                    use_container_width=True
                )
                
                st.session_state["df_masivo"] = df_editado

                df_seleccionados = df_editado[df_editado["Analizar"] == True].copy()
                
                st.write(f"*Total de pacientes listos para analizar:* {len(df_seleccionados)} / {total_filas}")

                if st.button(f"🚀 Analizar {len(df_seleccionados)} Pacientes", type="primary", use_container_width=True, disabled=len(df_seleccionados)==0):
                    diagnosticos = []
                    confianzas = []
                    
                    barra_progreso = st.progress(0)
                    texto_progreso = st.empty()
                    
                    total_analizar = len(df_seleccionados)

                    for i, (index, row) in enumerate(df_seleccionados.iterrows()):
                        payload = {
                            "DP": row["DP"], "ALTV": row["ALTV"], "AC": row["AC"], 
                            "Mean": row["Mean"], "ASTV": row["ASTV"], "Median": row["Median"], 
                            "Mode": row["Mode"], "Min": row["Min"], "Nzeros": row["Nzeros"], "LB": row["LB"]
                        }
                        
                        try:
                            response = requests.post(API_URL, json=payload)
                            if response.status_code == 200:
                                res = response.json()
                                diagnosticos.append(res["estado"].upper())
                                confianzas.append(res["confianza"])
                            else:
                                diagnosticos.append("ERROR API")
                                confianzas.append("0%")
                        except:
                            diagnosticos.append("ERROR CONEXIÓN")
                            confianzas.append("0%")
                            
                        progreso_actual = (i + 1) / total_analizar
                        barra_progreso.progress(progreso_actual)
                        texto_progreso.text(f"Analizando paciente {i + 1} de {total_analizar}...")
                        time.sleep(0.1)

                    texto_progreso.success("✅ Análisis completado con éxito.")
                    
                    df_resultados = df_seleccionados.drop(columns=["Analizar"])
                    df_resultados["DIAGNÓSTICO"] = diagnosticos
                    df_resultados["CONFIANZA"] = confianzas
                    
                    st.subheader("📊 Resultados Finales")
                    st.dataframe(df_resultados, hide_index=True, use_container_width=True)

                    csv = df_resultados.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Descargar Reporte Clínico (CSV)",
                        data=csv,
                        file_name='reporte_pacientes_analizados.csv',
                        mime='text/csv',
                        type="primary"
                    )

        except Exception as e:
            st.error(f"Hubo un error al procesar el archivo. Detalle: {e}")

# =========================================
# FOOTER ESTILIZADO
# =========================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.9em;'>"
    "Sistema Inteligente de Predicción de Riesgo Fetal potenciado con FastAPI, Streamlit y XGBoost"
    "</div>", 
    unsafe_allow_html=True
)
