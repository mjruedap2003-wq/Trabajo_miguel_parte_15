import os
import base64
import numpy as np
import streamlit as st
from PIL import Image
from openai import OpenAI
import openai
from streamlit_drawable_canvas import st_canvas

# 1. Configuración de página
st.set_page_config(
    page_title='Tablero Inteligente Cyberpunk ⚡',
    page_icon='🎨',
    layout='wide',
    initial_sidebar_state='expanded'
)

# 2. Estilos Neón Cyberpunk (CSS Completo: Izquierda y Derecha)
st.markdown("""
    <style>
    /* Fondo principal oscuro cibernético */
    .stApp {
        background-color: #0A0E17 !important;
        color: #E2E8F0 !important;
    }
    #MainMenu, footer, header {visibility: hidden;}

    /* Título con resplandor cian */
    .neon-title {
        font-size: 2.3rem;
        font-weight: 900;
        text-align: center;
        color: #00F0FF;
        text-shadow: 0 0 10px #00F0FF, 0 0 20px #00F0FF;
        margin-bottom: 0.5rem;
    }

    /* Subtítulos en azul neón */
    .cyan-sub-title {
        color: #00F0FF !important;
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        text-shadow: 0 0 8px rgba(0, 240, 255, 0.6) !important;
        margin-top: 1rem !important;
        margin-bottom: 0.8rem !important;
    }

    /* FORZAR BARRA LATERAL OSCURA Y NEÓN */
    section[data-testid="stSidebar"] {
        background-color: #121722 !important;
        border-right: 2px solid #00F0FF !important;
    }

    section[data-testid="stSidebar"] > div {
        background-color: #121722 !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown {
        color: #00F0FF !important;
        font-weight: bold !important;
        text-shadow: 0 0 5px rgba(0, 240, 255, 0.5) !important;
    }

    /* Sliders e Inputs en la barra lateral */
    div[data-testid="stSlider"] {
        background-color: #1A2232 !important;
        padding: 10px !important;
        border-radius: 8px !important;
        border: 1px solid #00F0FF !important;
    }

    /* Marco del Canvas */
    iframe[title="streamlit_drawable_canvas.canvas"] {
        border: 3px solid #00F0FF !important;
        border-radius: 10px !important;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.3) !important;
    }

    /* Botones Neón */
    div.stButton > button {
        width: 100%;
        background: transparent !important;
        color: #00FF66 !important;
        border: 2px solid #00FF66 !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        box-shadow: 0 0 10px rgba(0, 255, 102, 0.2) !important;
        transition: all 0.3s ease-in-out !important;
    }

    div.stButton > button:hover {
        background-color: #00FF66 !important;
        color: #0A0E17 !important;
        box-shadow: 0 0 20px rgba(0, 255, 102, 0.8) !important;
    }

    /* Cajas de respuesta */
    .stAlert {
        background-color: #181E2A !important;
        border: 1px solid #00F0FF !important;
        color: #00F0FF !important;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.3) !important;
    }

    /* Tarjeta contenedora de descripciones */
    .info-card {
        background: #181E2A;
        border: 1px solid #00F0FF;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Función para convertir imágenes a base64
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Inicializar galería en st.session_state
if "saved_sketches" not in st.session_state:
    st.session_state.saved_sketches = []

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown('<div class="cyan-sub-title">⚙️ Acerca de:</div>', unsafe_allow_html=True)
    st.write("En esta aplicación veremos la capacidad que tiene una IA Vision para interpretar bocetos en tiempo real.")
    
    st.markdown("---")
    st.markdown('<div class="cyan-sub-title">🛠️ Parámetros de Trazo</div>', unsafe_allow_html=True)
    stroke_width = st.slider('Ancho de línea', 1, 30, 5)

    st.markdown("---")
    # Limpiar collage
    if st.button("🗑️ Limpiar Collage"):
        st.session_state.saved_sketches = []
        st.rerun()

# --- ENCABEZADO ---
st.markdown('<h1 class="neon-title">⚡ TABLERO INTELIGENTE CYBERPUNK 🎨</h1>', unsafe_allow_html=True)

st.markdown("""
    <div class="info-card">
        <p style="margin:0;">✏️ Dibuja tu boceto en el panel de la izquierda, ingresa tu API Key y presiona el botón para analizarlo con IA.</p>
    </div>
""", unsafe_allow_html=True)

# Entrada de la API Key
secret_key = st.secrets.get("OPENAI_API_KEY", "")
ke = st.text_input('🔑 Ingresa tu API Key de OpenAI', value=secret_key, type="password")
api_key = ke if ke else secret_key

# --- ÁREA PRINCIPAL: CANVAS + BOTÓN ---
col_canvas, col_actions = st.columns([2, 1])

with col_canvas:
    st.markdown('<div class="cyan-sub-title">🎨 Lienzo de Dibujo</div>', unsafe_allow_html=True)
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=320,
        width=420,
        drawing_mode="freedraw",
        key="canvas",
    )

with col_actions:
    st.markdown('<div class="cyan-sub-title">🕹️ Acciones</div>', unsafe_allow_html=True)
    analyze_button = st.button("⚡ ANALIZAR BOCETO", type="primary")

# --- PROCESAMIENTO E INTERPRETACIONAL ---
if analyze_button:
    if not api_key:
        st.warning("⚠️ Por favor ingresa tu API key de OpenAI.")
    elif canvas_result.image_data is None or np.max(canvas_result.image_data) == 0:
        st.warning("⚠️ Dibuja algo en el tablero primero.")
    else:
        with st.spinner("🌌 Escaneando y analizando matriz de trazos..."):
            try:
                # Convertir a imagen y guardar temporalmente
                input_numpy_array = np.array(canvas_result.image_data)
                input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
                input_image.save('img.png')

                # Codificar en base64
                base64_image = encode_image_to_base64("img.png")
                prompt_text = "Describe detalladamente lo que ves en este boceto en español."

                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=500,
                )

                analysis_result = response.choices[0].message.content

                # Mostrar resultado de la IA
                st.markdown('<div class="cyan-sub-title">🤖 Interpretación de la IA:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stAlert">{analysis_result}</div>', unsafe_allow_html=True)

                # Guardar en el collage
                st.session_state.saved_sketches.append({
                    "image": input_image.copy(),
                    "description": analysis_result
                })

            except Exception as e:
                st.error(f"❌ Ocurrió un error al procesar el dibujo: {e}")

# --- FUNCIÓN ESPECIAL: COLLAGE AUTOMÁTICO DE BOCETOS ---
if st.session_state.saved_sketches:
    st.markdown("---")
    st.markdown('<div class="cyan-sub-title">🖼️ Collage Automático de Dibujos Guardados</div>', unsafe_allow_html=True)
    
    # Renderizar en grilla dinámica
    cols = st.columns(3)
    for idx, item in enumerate(st.session_state.saved_sketches):
        with cols[idx % 3]:
            st.image(item["image"], caption=f"Dibujo #{idx+1}", use_container_width=True)
            with st.expander(f"Ver Análisis #{idx+1}"):
                st.write(item["description"])
