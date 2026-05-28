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
    initial_sidebar_state="collapsed"
)

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
# ENCABEZADO
# =========================================
st.title("👶 Sistema de Análisis de Cardiotocografía")
st.markdown("<p class='subtitulo'>Ingrese los valores del monitor fetal para predecir el estado de salud de manera instantánea.</p>", unsafe_allow_html=True)

# CREACIÓN DE PESTAÑAS
tab1, tab2 = st.tabs(["🧑‍⚕️ Análisis Individual", "📁 Carga Masiva (CSV)"])

# =========================================
# PESTAÑA 1: ANÁLISIS INDIVIDUAL
# =========================================
with tab1:
    mensaje_ejemplo = st.empty()

    with st.container(border=True):
        st.subheader("📝 Datos del Paciente")
        col1, col2 = st.columns(2)

        with col1:
            lb = st.number_input("LB (Frecuencia Basal)", format="%.2f", value=None, placeholder="120.00", help="Frecuencia cardíaca fetal basal (latidos por minuto).")
            ac = st.number_input("AC (Aceleraciones)", format="%.8f", value=None, placeholder="0.00000000", help="Número de aceleraciones por segundo.")
            astv = st.number_input("ASTV (% Tiempo Variabilidad Anormal)", format="%.2f", value=None, placeholder="73.00", help="Porcentaje de tiempo con variabilidad anormal a corto plazo.")
            mstv = st.number_input("MSTV (Variabilidad Media)", format="%.2f", value=None, placeholder="0.50", help="Valor medio de la variabilidad a corto plazo.")
            altv = st.number_input("ALTV (% Tiempo Variabilidad Alta)", format="%.2f", value=None, placeholder="43.00", help="Porcentaje de tiempo con variabilidad anormal a largo plazo.")

        with col2:
            mltv = st.number_input("MLTV (Variabilidad Media Largo Plazo)", format="%.2f", value=None, placeholder="2.40", help="Valor medio de la variabilidad a largo plazo.")
            dp = st.number_input("DP (Desaceleraciones Prolongadas)", format="%.8f", value=None, placeholder="0.00000000", help="Número de desaceleraciones prolongadas por segundo.")
            mean = st.number_input("Mean (Media)", format="%.2f", value=None, placeholder="137.00", help="Media del histograma de la frecuencia cardíaca fetal.")
            median = st.number_input("Median (Mediana)", format="%.2f", value=None, placeholder="121.00", help="Mediana del histograma de la frecuencia cardíaca fetal.")
            mode = st.number_input("Mode (Moda)", format="%.2f", value=None, placeholder="120.00", help="Moda del histograma de la frecuencia cardíaca fetal.")

    valores_inputs = [lb, ac, astv, mstv, altv, mltv, dp, mean, median, mode]

    if all(v is None for v in valores_inputs):
        mensaje_ejemplo.info("💡 *Guía:* Los campos muestran valores de referencia. Digite los datos reales para comenzar la evaluación.")

    st.write("")

    if st.button("🔍 Predecir Estado Fetal", type="primary", use_container_width=True):
        if any(v is None for v in valores_inputs):
            st.warning("⚠️ Por favor, complete todos los campos numéricos antes de predecir.")
        else:
            payload = {
                "AC": ac, "LB": lb, "ASTV": astv, "MSTV": mstv, "ALTV": altv,
                "MLTV": mltv, "DP": dp, "Mean": mean, "Median": median, "Mode": mode
            }

            try:
                with st.spinner("Analizando datos con el modelo de IA..."):
                    API_URL = "https://apifetal.onrender.com/predecir"
                    response = requests.post(API_URL, json=payload)

                if response.status_code == 200:
                    res = response.json()
                    estado = res["estado"]
                    nsp = res["NSP"]
                    confianza_num = float(str(res["confianza"]).replace("%", ""))

                    nuevo_registro = {
                        "LB": lb, "AC": ac, "ASTV": astv, "DP": dp,
                        "Diagnóstico": estado.upper(),
                        "Confianza": f"{confianza_num:.2f}%"
                    }
                    st.session_state["historial"].append(nuevo_registro)

                    with st.container(border=True):
                        st.subheader("📊 Resultado del Análisis Diagnóstico")
                        if nsp == 1:
                            st.success(f"### ✅ Estado Normal\n*Recomendación:* No hay riesgo alguno detectado.\n\n*Confianza del modelo predictivo: {confianza_num:.2f}%*")
                        elif nsp == 2:
                            st.warning(f"### ⚠️ Estado Sospechoso\n*Recomendación:* Requiere chequeo por parte del médico.\n\n*Confianza del modelo predictivo: {confianza_num:.2f}%*")
                        else:
                            st.error(f"### 🚨 Estado Patológico\n*Recomendación:* Atención de alta prioridad inmediata.\n\n*Confianza del modelo predictivo: {confianza_num:.2f}%*")
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
            # 1. Crear el DataFrame en memoria si es un archivo nuevo
            if ("archivo_actual" not in st.session_state) or (st.session_state["archivo_actual"] != archivo_subido.name):
                df_temp = pd.read_csv(archivo_subido, sep=None, engine='python')
                df_temp.columns = df_temp.columns.str.strip()
                
                # Verificar columnas requeridas antes de procesar
                columnas_requeridas = ["AC", "LB", "ASTV", "MSTV", "ALTV", "MLTV", "DP", "Mean", "Median", "Mode"]
                
                if not set(columnas_requeridas).issubset(set(df_temp.columns)):
                    st.error(f"⚠️ El archivo no tiene las columnas correctas. Faltan: {set(columnas_requeridas) - set(df_temp.columns)}")
                    st.session_state["df_masivo"] = None
                else:
                    # =========================================
                    # LIMPIEZA Y PREPARACIÓN DEL DATAFRAME
                    # =========================================
                    # Nos quedamos SOLO con las columnas estrictamente necesarias
                    df_limpio = df_temp[columnas_requeridas].copy()
                    
                    # Añadir columna de ID de Paciente (empezando en 1)
                    df_limpio.insert(0, "Paciente_ID", range(1, len(df_limpio) + 1))
                    
                    # Añadir la columna de casillas para analizar
                    df_limpio.insert(0, "Analizar", False) 
                    
                    st.session_state["df_masivo"] = df_limpio
                    st.session_state["archivo_actual"] = archivo_subido.name

            # 2. Si el archivo es válido y está en memoria, mostrar la interfaz
            if "df_masivo" in st.session_state and st.session_state["df_masivo"] is not None:
                df_masivo = st.session_state["df_masivo"]
                total_filas = len(df_masivo)

                # =========================================
                # PANEL DE HERRAMIENTAS DE SELECCIÓN
                # =========================================
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
                            # Usamos loc para marcar en True ese rango específico
                            st.session_state["df_masivo"].loc[inicio-1 : fin-1, "Analizar"] = True
                            st.rerun()

                # =========================================
                # TABLA INTERACTIVA (EDICIÓN MANUAL)
                # =========================================
                st.write("### 📋 Tabla de Pacientes (Edición Manual)")
                
                # Deshabilitar edición en todas las columnas excepto "Analizar"
                columnas_deshabilitadas = [col for col in df_masivo.columns if col != "Analizar"]
                
                df_editado = st.data_editor(
                    df_masivo,
                    column_config={
                        "Analizar": st.column_config.CheckboxColumn(
                            "Seleccionar", default=False, help="Marca para incluir en el análisis"
                        ),
                        "Paciente_ID": st.column_config.NumberColumn(
                            "ID Paciente", format="%d" # Formato entero limpio
                        )
                    },
                    disabled=columnas_deshabilitadas,
                    hide_index=True,
                    use_container_width=True
                )
                
                st.session_state["df_masivo"] = df_editado

                # =========================================
                # PROCESAMIENTO Y ANÁLISIS
                # =========================================
                df_seleccionados = df_editado[df_editado["Analizar"] == True].copy()
                
                st.write(f"*Total de pacientes listos para analizar:* {len(df_seleccionados)} / {total_filas}")

                if st.button(f"🚀 Analizar {len(df_seleccionados)} Pacientes", type="primary", use_container_width=True, disabled=len(df_seleccionados)==0):
                    diagnosticos = []
                    confianzas = []
                    
                    barra_progreso = st.progress(0)
                    texto_progreso = st.empty()
                    
                    total_analizar = len(df_seleccionados)
                    API_URL = "https://apifetal.onrender.com/predecir"

                    for i, (index, row) in enumerate(df_seleccionados.iterrows()):
                        payload = {
                            "AC": row["AC"], "LB": row["LB"], "ASTV": row["ASTV"], 
                            "MSTV": row["MSTV"], "ALTV": row["ALTV"], "MLTV": row["MLTV"], 
                            "DP": row["DP"], "Mean": row["Mean"], "Median": row["Median"], "Mode": row["Mode"]
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
                    
                    # Crear tabla de resultados (quitamos la columna Checkbox, pero conservamos el ID)
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
