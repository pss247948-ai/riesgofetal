import streamlit as st
import requests

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
# ESTILOS CSS PERSONALIZADOS (UI/UX)
# =========================================
estilos_css = """
<style>
/* 1. Ocultar botones de incremento/decremento */
[data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"] {
    display: none !important;
}

/* 2. Estilizar el título principal para darle un toque médico/profesional */
h1 {
    color: #2E86C1 !important;
    text-align: center;
    font-weight: 700;
    margin-bottom: 10px;
}

/* 3. Efecto hover para el botón principal */
.stButton > button {
    transition: all 0.3s ease;
    border-radius: 8px;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
}

/* 4. Alinear sutilmente el subtítulo */
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
st.markdown("<p class='subtitulo'>Ingrese los valores obtenidos del monitor fetal para predecir el estado de salud de manera instantánea.</p>", unsafe_allow_html=True)

mensaje_ejemplo = st.empty()

# =========================================
# FORMULARIO EN TIPO "TARJETA" (CONTENEDOR)
# =========================================
with st.container(border=True):
    st.subheader("📝 Datos del Paciente")
    col1, col2 = st.columns(2)

    with col1:
        lb = st.number_input("LB (Frecuencia Basal)", format="%.2f", value=None, placeholder="120.00")
        ac = st.number_input("AC (Aceleraciones)", format="%.8f", value=None, placeholder="0.00000000")
        astv = st.number_input("ASTV (% Tiempo Variabilidad Anormal)", format="%.2f", value=None, placeholder="73.00")
        mstv = st.number_input("MSTV (Variabilidad Media)", format="%.2f", value=None, placeholder="0.50")
        altv = st.number_input("ALTV (% Tiempo Variabilidad Alta)", format="%.2f", value=None, placeholder="43.00")

    with col2:
        mltv = st.number_input("MLTV (Variabilidad Media Largo Plazo)", format="%.2f", value=None, placeholder="2.40")
        dp = st.number_input("DP (Desaceleraciones Prolongadas)", format="%.8f", value=None, placeholder="0.00000000")
        mean = st.number_input("Mean (Media)", format="%.2f", value=None, placeholder="137.00")
        median = st.number_input("Median (Mediana)", format="%.2f", value=None, placeholder="121.00")
        mode = st.number_input("Mode (Moda)", format="%.2f", value=None, placeholder="120.00")

# Agrupamos todos los valores para evaluar si están vacíos
valores_inputs = [lb, ac, astv, mstv, altv, mltv, dp, mean, median, mode]

# Si todos los campos están vacíos, mostramos mensaje
if all(v is None for v in valores_inputs):
    mensaje_ejemplo.info(
        "💡 **Guía:** Los campos muestran valores de referencia. Digite los datos reales para comenzar la evaluación."
    )

st.write("") # Espacio en blanco para respirar

# =========================================
# BOTÓN DE PREDICCIÓN MEJORADO
# =========================================
# Usamos type="primary" y use_container_width para que resalte
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
                confianza_str = str(res["confianza"]).replace("%", "")
                confianza_num = float(confianza_str)

                # =========================================
                # RESULTADO EN CAJA VISUAL
                # =========================================
                with st.container(border=True):
                    st.subheader("📊 Resultado del Análisis Diagnóstico")
                    
                    if nsp == 1:
                        st.success(
                            f"""
                            ### ✅ Estado Normal
                            **Recomendación:** No hay riesgo alguno detectado. Continuar con el control prenatal habitual.
                            
                            *Confianza del modelo predictivo: {confianza_num:.2f}%*
                            """
                        )
                    elif nsp == 2:
                        st.warning(
                            f"""
                            ### ⚠️ Estado Sospechoso
                            **Recomendación:** Requiere un chequeo por parte del médico para monitoreo preventivo.
                            
                            *Confianza del modelo predictivo: {confianza_num:.2f}%*
                            """
                        )
                    else:
                        st.error(
                            f"""
                            ### 🚨 Estado Patológico
                            **Recomendación:** Se requiere atención de alta prioridad por parte del médico especialista de inmediato.
                            
                            *Confianza del modelo predictivo: {confianza_num:.2f}%*
                            """
                        )
                    
                    # Progreso visual de confianza (Opcional pero le da un toque muy pro)
                    st.progress(int(confianza_num))

            else:
                st.error(f"Error de comunicación con el servidor: {response.status_code}")

        except Exception as e:
            st.error(f"No se pudo conectar con el motor de predicción.\n\nDetalle técnico: {e}")

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
