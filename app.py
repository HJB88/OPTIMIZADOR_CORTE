import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io

# --- LÓGICA DE OPTIMIZACIÓN MULTI-CHAPA ---
def optimizar_multi_chapa(ancho_chapa, largo_chapa, pedidos, kerf):
    piezas_totales = []
    for i, p in enumerate(pedidos):
        for _ in range(p['cant']):
            # Rotación automática: el lado más largo es la base
            w, l = max(p['ancho'], p['largo']), min(p['ancho'], p['largo'])
            piezas_totales.append({'w': w, 'l': l, 'id': i})
    
    # Ordenar por altura para el algoritmo de estantes
    piezas_totales.sort(key=lambda x: x['l'], reverse=True)

    chapas_resultados = []
    
    while piezas_totales:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_xlim(0, ancho_chapa)
        ax.set_ylim(0, largo_chapa)
        ax.add_patch(patches.Rectangle((0, 0), ancho_chapa, largo_chapa, color='#F0F0F0', ec='black'))
        
        x_actual, y_actual = 0, 0
        altura_max_estante = 0
        piezas_en_esta_chapa = []
        indices_a_eliminar = []

        for i, p in enumerate(piezas_totales):
            # Verificar si cabe en el estante o requiere uno nuevo
            if x_actual + p['w'] > ancho_chapa:
                x_actual = 0
                y_actual += altura_max_estante + kerf
                altura_max_estante = 0

            # Si cabe en la chapa actual
            if y_actual + p['l'] <= largo_chapa:
                ax.add_patch(patches.Rectangle((x_actual, y_actual), p['w'], p['l'], 
                             facecolor='#4CAF50', edgecolor='white', alpha=0.8))
                ax.text(x_actual + p['w']/2, y_actual + p['l']/2, f"{p['w']}x{p['l']}", 
                        ha='center', va='center', fontsize=8, color='white')
                
                x_actual += p['w'] + kerf
                altura_max_estante = max(altura_max_estante, p['l'])
                indices_a_eliminar.append(i)
            else:
                continue # Probar la siguiente pieza pequeña si la grande no cupo

        # Quitar las piezas que ya colocamos de la lista general
        for index in sorted(indices_a_eliminar, reverse=True):
            piezas_totales.pop(index)
        
        chapas_resultados.append(fig)
        if len(chapas_resultados) > 20: # Límite de seguridad
            break
            
    return chapas_resultados

# --- INTERFAZ ---
st.set_page_config(page_title="Nesting Pro Multi-Chapa", layout="wide")
st.title("✂️ Optimizador de Corte (Multi-Chapa)")

if 'pedidos' not in st.session_state:
    st.session_state.pedidos = []

with st.sidebar:
    st.header("⚙️ Configuración")
    ancho_c = st.number_input("Ancho Chapa (mm)", value=2440)
    largo_c = st.number_input("Largo Chapa (mm)", value=1220)
    kerf = st.number_input("Grosor Corte (mm)", value=4)
    st.divider()
    st.header("➕ Nueva Pieza")
    nw = st.number_input("Ancho", value=600)
    nl = st.number_input("Largo", value=400)
    nc = st.number_input("Cantidad", value=1, min_value=1)
    if st.button("Añadir a Pedido"):
        st.session_state.pedidos.append({'ancho': nw, 'largo': nl, 'cant': nc})
        st.rerun()

# --- LISTA DE PIEZAS CON OPCIÓN DE BORRAR ---
col_lista, col_graficos = st.columns([1, 2])

with col_lista:
    st.subheader("📋 Detalle del Pedido")
    for i, p in enumerate(st.session_state.pedidos):
        c1, c2 = st.columns([3, 1])
        c1.write(f"**{p['cant']} uds** de {p['ancho']}x{p['largo']}")
        if c2.button("🗑️", key=f"del_{i}"):
            st.session_state.pedidos.pop(i)
            st.rerun()

with col_graficos:
    if st.session_state.pedidos:
        chapas = optimizar_multi_chapa(ancho_c, largo_c, st.session_state.pedidos, kerf)
        st.success(f"✅ Se necesitan **{len(chapas)} chapas** en total.")
        
        for idx, fig in enumerate(chapas):
            st.write(f"### Chapa {idx + 1}")
            st.pyplot(fig)
            
            # Botón de descarga para cada chapa
            buf = io.BytesIO()
            fig.savefig(buf, format="pdf")
            st.download_button(f"Descargar Chapa {idx+1} (PDF)", buf.getvalue(), f"chapa_{idx+1}.pdf")
    else:
        st.info("Añade piezas para calcular el despiece.")