import streamlit as st
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# 1. Configuración de la página
st.set_page_config(
    page_title='Tablero de Dibujo & Collage 🎨',
    page_icon='🎨',
    layout='wide',
    initial_sidebar_state='expanded'
)

# 2. Estilos Neón Cyberpunk (Textos e Inputs Neón Corregidos)
st.markdown("""
    <style>
    /* Fondo principal oscuro cibernético */
    .stApp {
        background-color: #0A0E17 !important;
        color: #E2E8F0 !important;
    }
    #MainMenu, footer, header {visibility: hidden;}

    /* Título principal */
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
        margin-top: 0.8rem !important;
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

    /* ESTILO PARA INPUT DE TEXTO Y LABELS EN AZUL NEÓN */
    div[data-testid="stTextInput"] label {
        color: #00F0FF !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        text-shadow: 0 0 8px rgba(0, 240, 255, 0.6) !important;
    }

    div[data-testid="stTextInput"] input {
        background-color: #1A2232 !important;
        color: #00F0FF !important;
        border: 2px solid #00F0FF !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.2) !important;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: #90CDF4 !important;
        opacity: 0.8 !important;
    }

    /* Marco para el lienzo del canvas */
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

    /* Tarjeta contenedora de información */
    .info-card {
        background: #181E2A;
        border: 1px solid #00F0FF;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Inicialización del estado de sesión
if "saved_sketches" not in st.session_state:
    st.session_state.saved_sketches = []

if "selected_color" not in st.session_state:
    st.session_state.selected_color = "#00F0FF"

# --- BARRA LATERAL (PALETA Y PARÁMETROS) ---
with st.sidebar:
    st.markdown('<div class="cyan-sub-title">🎨 Paleta de Colores</div>', unsafe_allow_html=True)
    
    # Selector de color de Streamlit
    picker_color = st.color_picker("Selecciona tu color", st.session_state.selected_color)
    if picker_color != st.session_state.selected_color:
        st.session_state.selected_color = picker_color

    st.markdown("**Atajos de Colores Neón:**")
    col1, col2, col3, col4 = st.columns(4)
    if col1.button("🩵"): st.session_state.selected_color = "#00F0FF"
    if col2.button("🩷"): st.session_state.selected_color = "#FF007F"
    if col3.button("💚"): st.session_state.selected_color = "#00FF66"
    if col4.button("💛"): st.session_state.selected_color = "#FFE600"

    col5, col6, col7, col8 = st.columns(4)
    if col5.button("💜"): st.session_state.selected_color = "#A855F7"
    if col6.button("🤍"): st.session_state.selected_color = "#FFFFFF"
    if col7.button("🖤"): st.session_state.selected_color = "#000000"
    if col8.button("🧡"): st.session_state.selected_color = "#FF7700"

    st.markdown(f"**Color activo:** `{st.session_state.selected_color}`")

    st.markdown("---")
    st.markdown('<div class="cyan-sub-title">🛠️ Parámetros del Trazo</div>', unsafe_allow_html=True)
    stroke_width = st.slider('Ancho del pincel', 1, 40, 8)
    bg_color = st.color_picker("Color del fondo del lienzo", "#0A0E17")

    st.markdown("---")
    if st.button("🗑️ Vaciar Collage"):
        st.session_state.saved_sketches = []
        st.rerun()

# --- ENCABEZADO ---
st.markdown('<h1 class="neon-title">⚡ TABLERO MULTICOLOR Y COLLAGE PARA ARTISTAS MELOS🖌️</h1>', unsafe_allow_html=True)

st.markdown("""
    <div class="info-card">
        <p style="margin:0;">
            ✏️ ¡Bienvenido bro! Pon a prueba tu creatividad tan aspera, ponle un título a tu obra en el recuadro superior, dibuja con todos los colores que quieras y guárdala para armar tu collage interactivo.
        </p>
    </div>
""", unsafe_allow_html=True)

# --- ÁREA PRINCIPAL: CANVAS DE CLAVE FIJA, TÍTULO Y BOTÓN ---
col_canvas, col_actions = st.columns([2, 1])

with col_canvas:
    # Campo para el título personalizado del dibujo
    sketch_title = st.text_input(
        "🏷️ Título de tu dibujo:", 
        placeholder="Ej: Robot Neón, Mi Gato Cyberpunk, Noche Estrellada..."
    )

    st.markdown('<div class="cyan-sub-title">🎨 Lienzo de Dibujo</div>', unsafe_allow_html=True)
    
    # Clave estática ("main_canvas") para evitar reinicios al cambiar el color
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 127, 0.3)",
        stroke_width=stroke_width,
        stroke_color=st.session_state.selected_color,
        background_color=bg_color,
        height=380,
        width=500,
        drawing_mode="freedraw",
        key="main_canvas",
    )

with col_actions:
    st.markdown('<div class="cyan-sub-title">🕹️ Acciones</div>', unsafe_allow_html=True)
    save_button = st.button("💾 GUARDAR AL COLLAGE", type="primary")

    if save_button:
        if canvas_result.image_data is not None and np.max(canvas_result.image_data) > 0:
            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
            
            # Asignar nombre ingresado o uno por defecto
            final_title = sketch_title.strip() if sketch_title.strip() else f"Obra #{len(st.session_state.saved_sketches) + 1}"

            # Guardar diccionario con imagen y título
            st.session_state.saved_sketches.append({
                "image": input_image.copy(),
                "title": final_title
            })

            st.success(f"🎉 ¡'{final_title}' se guardó exitosamente en el collage!")
            st.rerun()
        else:
            st.warning("⚠️ Dibuja algo en el tablero antes de guardar.")

# --- SECCIÓN: COLLAGE DE DIBUJOS (ROBUSTO ANTE FORMATOS VIEJOS) ---
if st.session_state.saved_sketches:
    st.markdown("---")
    st.markdown('<div class="cyan-sub-title">🖼️ Collage Galería de Obras Guardadas</div>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    for idx, item in enumerate(st.session_state.saved_sketches):
        with cols[idx % 3]:
            # Verificar si el elemento es un diccionario o una imagen directa de la sesión anterior
            if isinstance(item, dict):
                img_to_show = item.get("image")
                caption_text = f"🎨 {item.get('title', f'Obra #{idx+1}')}"
            else:
                img_to_show = item
                caption_text = f"🎨 Obra #{idx+1}"

            if img_to_show is not None:
                st.image(img_to_show, caption=caption_text, use_container_width=True)
