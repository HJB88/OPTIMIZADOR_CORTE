import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io

DENSIDAD_ACERO = 0.00000785

def optimizar_despiece(ancho_c, largo_c, espesor, pedidos, kerf, metodo):
    piezas_pendientes = []
    for p in pedidos:
        for _ in range(p['cant']):
            w, l = max(p['ancho'], p['largo']), min(p['ancho'], p['largo'])
            piezas_pendientes.append({'w': w, 'l': l, 'nombre': f"{p['ancho']}x{p['largo']}"})
    
    piezas_pendientes.sort(key=lambda x: x['l'], reverse=True)
    chapas_finales = []
    peso_util_total = 0
    
    while piezas_pendientes:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_xlim(0, ancho_c)
        ax.set_ylim(0, largo_c)
        ax.set_aspect('equal')
        ax.add_patch(patches.Rectangle((0, 0), ancho_c, largo_c, color='#B0BEC5', ec='#263238', lw=2))
        
        x, y, h_estante = 0, 0, 0
        colocadas_indices = []
        
        for i, p in enumerate(piezas_pendientes):
            if x + p['w'] > ancho_c:
                x = 0
                y += h_estante + kerf
                h_estante = 0
            if y + p['l'] <= largo_c:
                color_p = '#1565C0' if metodo == "Cizalla" else '#2E7D32'
                ax.add_patch(patches.Rectangle((x, y), p['w'], p['l'], facecolor=color_p, edgecolor='white', lw=0.5))
                ax.text(x + p['w']/2, y + p['l']/2, p['nombre'], color='white', ha='center', va='center', fontsize=7, fontweight='bold')
                if metodo == "Cizalla":
                    ax.axhline(y + p['l'], color='red', ls='--', lw=0.8, alpha=0.5)
                peso_util_total += (p['w'] * p['l'] * espesor) * DENSIDAD_ACERO
                x += p['w'] + kerf
                h_estante = max(h_estante, p['l'])
                colocadas_indices.append(i)
        
        for index in sorted(colocadas_indices, reverse=True):
            piezas_pendientes.pop(index)
        chapas_finales.append(fig)
        if len(chapas_finales) > 50: break
    return chapas_finales, peso_util_total

st.set_page_config(page_title="HierroOptimizador Pro", layout="wide")
st.title("🛡️ Optimizador de Chapa de Hierro")

if 'pedidos' not in st.session_state:
    st.session_state.pedidos = []

with st.sidebar:
    st.header("⚙️ Configuración")
    metodo = st.radio("Método de corte:", ["Cizalla", "Chorro de Agua"])
    ancho_ch = st.number_input("Ancho Chapa (mm)", value=3000)
    largo_ch = st.number_input("Largo Chapa (mm)", value=1500)
    espesor_ch = st.number_input("Espesor (mm)", value=6.0)
    kerf_sugerido = 0.0 if metodo == "Cizalla" else 2.5
    kerf = st.number_input("Sangría (mm)", value=kerf_sugerido)
    st.divider()
    p_w = st.number_input("Ancho pieza", value=500)
    p_l = st.number_input("Largo pieza", value=200)
    p_c = st.number_input("Cantidad", value=1, min_value=1)
    if st.button("Añadir"):
        st.session_state.pedidos.append({'ancho': p_w, 'largo': p_l, 'cant': p_c})
        st.rerun()

col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("📋 Lista")
    for idx, p in enumerate(st.session_state.pedidos):
        c1, c2 = st.columns([4, 1])
        c1.write(f"{p['cant']}x {p['ancho']}x{p['largo']}")
        if c2.button("🗑️", key=f"del_{idx}"):
            st.session_state.pedidos.pop(idx)
            st.rerun()

with col2:
    if st.session_state.pedidos:
        chapas, peso_u = optimizar_despiece(ancho_ch, largo_ch, espesor_ch, st.session_state.pedidos, kerf, metodo)
        st.metric("Peso Útil Total", f"{peso_u:.2f} kg")
        for i, fig in enumerate(chapas):
            st.pyplot(fig)
            buf = io.BytesIO()
            fig.savefig(buf, format="pdf")
            st.download_button(f"Descargar PDF {i+1}", buf.getvalue(), f"p_{i+1}.pdf")