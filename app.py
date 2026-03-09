import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io

# --- LÓGICA DE OPTIMIZACIÓN Y DIBUJO ---
def generar_nesting(ancho_chapa, largo_chapa, pedidos, kerf):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, ancho_chapa)
    ax.set_ylim(0, largo_chapa)
    ax.set_aspect('equal')
    
    # Dibujar la chapa base (Gris claro)
    ax.add_patch(patches.Rectangle((0, 0), ancho_chapa, largo_chapa, color='#F0F0F0', ec='#333333', lw=2))

    # Expandir pedidos y normalizar (Rotación automática para que el lado largo sea la base)
    piezas_a_cortar = []
    for p in pedidos:
        for _ in range(p['cant']):
            # Rotación automática: orientamos la pieza para que 'ancho' sea la dimensión mayor
            w, l = max(p['ancho'], p['largo']), min(p['ancho'], p['largo'])
            piezas_a_cortar.append({'w': w, 'l': l, 'nombre': f"{p['ancho']}x{p['largo']}"})
    
    # Ordenar piezas por altura (largo) de mayor a menor (Algoritmo FFDH)
    piezas_a_cortar.sort(key=lambda x: x['l'], reverse=True)

    x_actual, y_actual = 0, 0
    altura_max_estante = 0
    piezas_colocadas = 0
    area_piezas = 0

    for p in piezas_a_cortar:
        # ¿Cabe en el estante actual a lo ancho?
        if x_actual + p['w'] > ancho_chapa:
            # No cabe, saltar al siguiente estante (arriba)
            x_actual = 0
            y_actual += altura_max_estante + kerf
            altura_max_estante = 0

        # ¿Cabe en la chapa a lo largo (altura)?
        if y_actual + p['l'] <= largo_chapa:
            # Dibujar la pieza
            ax.add_patch(patches.Rectangle((x_actual, y_actual), p['w'], p['l'], 
                                         edgecolor='#004d40', facecolor='#81c784', alpha=0.9, lw=1))
            
            # Etiqueta de medidas
            ax.text(x_actual + p['w']/2, y_actual + p['l']/2, p['nombre'], 
                    color='black', ha='center', va='center', fontsize=7, fontweight='bold')
            
            area_piezas += (p['w'] * p['l'])
            x_actual += p['w'] + kerf
            altura_max_estante = max(altura_max_estante, p['l'])
            piezas_colocadas += 1

    eficiencia = (area_piezas / (ancho_chapa * largo_chapa)) * 100
    plt.title(f"Plan de Corte: {piezas_colocadas} piezas | Eficiencia: {eficiencia:.2f}%", pad=20)
    plt.xlabel("Ancho (mm)")
    plt.ylabel("Largo (mm)")
    
    return fig, piezas_colocadas, eficiencia

# --- INTERFAZ DE USUARIO (STREAMLIT) ---
st.set_page_config(page_title="Optimizador de Chapa Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #4CAF50; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("✂️ Nesting App: Optimización de Cortes")

# Inicializar lista de piezas en la sesión
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = []

# --- COLUMNA LATERAL: ENTRADA DE DATOS ---
with st.sidebar:
    st.header("📏 Medidas Chapa Madre")
    ch_ancho = st.number_input("Ancho Total (mm)", value=2440)
    ch_largo = st.number_input("Largo Total (mm)", value=1220)
    kerf = st.number_input("Espesor del disco (mm)", value=4, help="Ancho de la sierra que se pierde en cada corte")
    
    st.divider()
    
    st.header("🧩 Añadir Piezas")
    p_ancho = st.number_input("Ancho de pieza", value=500)
    p_largo = st.number_input("Largo de pieza", value=300)
    p_cant = st.number_input("Cantidad", value=1, min_value=1)
    
    if st.button("Añadir a la lista"):
        st.session_state.pedidos.append({'ancho': p_ancho, 'largo': p_largo, 'cant': p_cant})
        st.rerun()

    if st.button("🗑️ Limpiar Todo", type="secondary"):
        st.session_state.pedidos = []
        st.rerun()

# --- ÁREA DE RESULTADOS ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Lista de Corte")
    if st.session_state.pedidos:
        for idx, p in enumerate(st.session_state.pedidos):
            st.info(f"**{p['cant']} uds** de {p['ancho']} x {p['largo']} mm")
    else:
        st.write("No hay piezas añadidas aún.")

with col2:
    st.subheader("📊 Mapa de Aprovechamiento")
    if st.session_state.pedidos:
        fig, total_p, rendimiento = generar_nesting(ch_ancho, ch_largo, st.session_state.pedidos, kerf)
        st.pyplot(fig)
        
        # Métricas rápidas
        m1, m2 = st.columns(2)
        m1.metric("Piezas Colocadas", total_p)
        m2.metric("Aprovechamiento", f"{rendimiento:.2f}%")

        # --- BOTÓN DE DESCARGA PDF ---
        buf = io.BytesIO()
        fig.savefig(buf, format="pdf", bbox_inches='tight')
        buf.seek(0)
        
        st.download_button(
            label="📥 Descargar Plano en PDF",
            data=buf,
            file_name="plano_despiece.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Agrega dimensiones en el panel de la izquierda para generar el mapa.")

st.divider()
st.caption("Desarrollado para optimización de procesos industriales de corte recto.")