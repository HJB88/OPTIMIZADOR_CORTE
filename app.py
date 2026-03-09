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