import base64
from pathlib import Path
from urllib.parse import quote

import streamlit as st

from sorteo import leer_lista, nombres_tool, sortear, texto_para_whatsapp

LOGO = Path(__file__).parent / "logo.png"

st.set_page_config(page_title="Mantraneta FC", page_icon=str(LOGO), layout="centered")

logo_b64 = base64.b64encode(LOGO.read_bytes()).decode()
st.markdown(
    f"<div style='text-align:center'><img src='data:image/png;base64,{logo_b64}' width='170'></div>",
    unsafe_allow_html=True,
)
st.markdown("<h1 style='text-align:center'>Mantraneta FC</h1>", unsafe_allow_html=True)
st.caption("Copiá la lista del grupo de WhatsApp, pegala acá abajo y tocá **Sortear**.")

texto = st.text_area(
    "Lista de anotados",
    height=220,
    placeholder="Partido jueves 21hs\n1. Juan\n2. Pedro (arq)\n3. Lucas\n4. Martín 🧤\n5.\n...",
)

jugadores, arqueros_detectados, repetidos = leer_lista(texto)

if texto.strip():
    st.write(f"**{len(jugadores)} anotados:** " + ", ".join(jugadores) if jugadores else "No encontré nombres 🤔")
    if repetidos:
        st.warning("Saqué nombres repetidos: " + ", ".join(repetidos))

with st.expander("⚙️ Opciones", expanded=False):
    c1, c2 = st.columns(2)
    n_equipos = c1.number_input("Cantidad de equipos", min_value=2, max_value=6, value=2, step=1)
    cupo = c2.number_input("Jugadores por equipo (0 = todos juegan)", min_value=0, max_value=11, value=0, step=1)
    respetar_orden = st.checkbox(
        "Si sobra gente, quedan de suplentes los últimos en anotarse", value=True,
        help="Si lo destildás, los suplentes también se sortean.",
    )
    arqueros = st.multiselect(
        "Arqueros (se reparte uno por equipo)",
        options=jugadores,
        default=[j for j in jugadores if j in arqueros_detectados],
        help="Se detectan solos si en la lista ponen (arq) o 🧤 al lado del nombre.",
    )
puede_sortear = len(jugadores) >= n_equipos
if st.button("🎲 Sortear", type="primary", use_container_width=True, disabled=not puede_sortear):
    equipos, suplentes = sortear(
        jugadores, int(n_equipos), int(cupo), set(arqueros), respetar_orden
    )
    nombres_equipos = nombres_tool(int(n_equipos))
    st.session_state["resultado"] = (nombres_equipos, equipos, suplentes, set(arqueros))

if texto.strip() and not puede_sortear:
    st.info(f"Necesito al menos {int(n_equipos)} nombres para sortear.")

if "resultado" in st.session_state:
    nombres, equipos, suplentes, arqs = st.session_state["resultado"]
    cols = st.columns(len(equipos))
    for col, nombre, equipo in zip(cols, nombres, equipos):
        with col:
            st.subheader(nombre)
            for j in equipo:
                st.write(f"- {j}{' 🧤' if j in arqs else ''}")
    if suplentes:
        st.write("**Suplentes:** " + ", ".join(suplentes))

    mensaje = texto_para_whatsapp(nombres, equipos, suplentes, arqs)
    st.divider()
    st.link_button("📲 Mandar al grupo por WhatsApp", f"https://wa.me/?text={quote(mensaje)}",
                   use_container_width=True)
    st.caption("O copialo de acá (botón de copiar arriba a la derecha):")
    st.code(mensaje, language=None)
