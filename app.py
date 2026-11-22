import base64
from html import escape
from pathlib import Path
from urllib.parse import quote

import streamlit as st

from sorteo import leer_lista, nombres_tool, sortear, texto_para_whatsapp

LOGO = Path(__file__).parent / "logo.png"

st.set_page_config(page_title="Mantraneta FC", page_icon=str(LOGO), layout="centered")

# ---------- Estilos pensados para celular ----------
st.markdown(
    """
<style>
/* Sacamos la barra de arriba de Streamlit y achicamos márgenes */
header[data-testid="stHeader"], #MainMenu, footer {display: none !important;}
.block-container {padding-top: 1rem !important; padding-bottom: 3rem !important;
                  padding-left: 1rem !important; padding-right: 1rem !important;}

.encabezado {display: flex; align-items: center; justify-content: center; gap: 14px; margin-bottom: .3rem;}
.encabezado img {width: 76px; height: 76px; border-radius: 50%;
                 box-shadow: 0 0 18px rgba(160, 90, 255, .45);}
.encabezado h1 {margin: 0; padding: 0; font-size: 2rem; line-height: 1.1;}

/* Tarjetas de equipos: 2 por fila incluso en el celular */
.equipos {display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
          gap: 10px; margin: .5rem 0 .8rem;}
.equipo {border-radius: 14px; overflow: hidden; background: #1c1533;
         border: 1px solid #3a2a63;}
.equipo .titulo {background: linear-gradient(135deg, #3b1f7a, #8a3fc7); color: #fff;
                 padding: 8px 10px; font-weight: 700; font-size: .98rem; line-height: 1.2;}
.equipo .titulo small {display: block; font-weight: 400; opacity: .8; font-size: .75rem;}
.equipo ul {list-style: none; margin: 0; padding: 6px 10px 10px;}
.equipo li {padding: 5px 0; border-bottom: 1px solid #2e2350; font-size: .98rem; margin: 0;}
.equipo li:last-child {border-bottom: none;}
.suplentes {font-size: .92rem; color: #b9aed3; margin-bottom: .6rem;}

/* ---------- Animación del sorteo ---------- */
@keyframes caer {
  0%   {opacity: 0; transform: translateY(-46px) scale(.75) rotate(-6deg);}
  60%  {opacity: 1; transform: translateY(5px) scale(1.06) rotate(1deg);}
  100% {opacity: 1; transform: none;}
}
@keyframes destello {
  0%   {background: rgba(190, 120, 255, .45); box-shadow: 0 0 14px rgba(190, 120, 255, .6);}
  100% {background: transparent; box-shadow: none;}
}
@keyframes aparecer {from {opacity: 0; transform: scale(.94);} to {opacity: 1; transform: none;}}
.animar .equipo {animation: aparecer .35s ease both;}
.animar li {opacity: 0; border-radius: 6px;
            animation: caer .55s cubic-bezier(.2, .8, .3, 1.2) forwards,
                       destello .9s ease-out forwards;
            animation-delay: var(--d), var(--d);}
.animar .suplentes {opacity: 0; animation: aparecer .4s ease forwards; animation-delay: var(--d);}
@media (prefers-reduced-motion: reduce) {
  .animar li, .animar .equipo, .animar .suplentes {animation: none !important; opacity: 1 !important;}
}

/* Botones más altos, cómodos para el dedo */
.stButton button, .stLinkButton a {min-height: 3rem; font-size: 1.05rem;}
</style>
""",
    unsafe_allow_html=True,
)

logo_b64 = base64.b64encode(LOGO.read_bytes()).decode()
st.markdown(
    f"<div class='encabezado'><img src='data:image/png;base64,{logo_b64}'><h1>Mantraneta FC</h1></div>",
    unsafe_allow_html=True,
)
st.caption("Copiá la lista del grupo, pegala acá y tocá **Sortear**.")

# ---------- Entrada ----------
texto = st.text_area(
    "Lista de anotados",
    height=180,
    placeholder="1. Juan\n2. Pedro (arq)\n3. Lucas\n4. Martín 🧤\n...",
    label_visibility="collapsed",
)

jugadores, arqueros_detectados, repetidos = leer_lista(texto)

if texto.strip():
    if jugadores:
        st.caption(f"**{len(jugadores)} anotados:** " + ", ".join(jugadores))
    else:
        st.caption("No encontré nombres 🤔")
    if repetidos:
        st.warning("Saqué nombres repetidos: " + ", ".join(repetidos))

with st.expander("⚙️ Opciones", expanded=False):
    n_equipos = st.number_input("Cantidad de equipos", min_value=2, max_value=6, value=2, step=1)
    cupo = st.number_input("Jugadores por equipo (0 = juegan todos)", min_value=0, max_value=11, value=0, step=1)
    respetar_orden = st.checkbox(
        "Si sobra gente, quedan de suplentes los últimos en anotarse", value=True,
        help="Si lo destildás, los suplentes también se sortean.",
    )
    arqueros = st.multiselect(
        "Arqueros (uno por equipo)",
        options=jugadores,
        default=[j for j in jugadores if j in arqueros_detectados],
        help="Se detectan solos si en la lista ponen (arq) o 🧤 al lado del nombre.",
    )

puede_sortear = len(jugadores) >= n_equipos
if st.button("🎲 Sortear", type="primary", use_container_width=True, disabled=not puede_sortear):
    equipos, suplentes = sortear(jugadores, int(n_equipos), int(cupo), set(arqueros), respetar_orden)
    st.session_state["resultado"] = (nombres_tool(int(n_equipos)), equipos, suplentes, set(arqueros))
    st.session_state["animar"] = True  # sólo se anima justo después de sortear

if texto.strip() and not puede_sortear:
    st.info(f"Necesito al menos {int(n_equipos)} nombres para sortear.")

# ---------- Resultado ----------
if "resultado" in st.session_state:
    nombres, equipos, suplentes, arqs = st.session_state["resultado"]

    # Los nombres caen alternando equipos, como repartiendo cartas.
    # El paso se achica si hay mucha gente, para que todo dure ~4 segundos como máximo.
    animar = st.session_state.pop("animar", False)
    n_eq = len(equipos)
    total = sum(len(e) for e in equipos)
    paso = min(0.38, 4.0 / max(total, 1))
    inicio = 0.3

    tarjetas = []
    for k, (nombre, equipo) in enumerate(zip(nombres, equipos)):
        items = "".join(
            f"<li style='--d:{inicio + (i * n_eq + k) * paso:.2f}s'>"
            f"{escape(j)}{' 🧤' if j in arqs else ''}</li>"
            for i, j in enumerate(equipo)
        )
        tarjetas.append(
            f"<div class='equipo'><div class='titulo'>{escape(nombre)}"
            f"<small>{len(equipo)} jugadores</small></div><ul>{items}</ul></div>"
        )
    fin = inicio + total * paso + 0.3
    html = f"<div class='equipos'>{''.join(tarjetas)}</div>"
    if suplentes:
        html += (f"<div class='suplentes' style='--d:{fin:.2f}s'><b>Suplentes:</b> "
                 f"{escape(', '.join(suplentes))}</div>")
    st.markdown(f"<div class='{'animar' if animar else ''}'>{html}</div>", unsafe_allow_html=True)

    mensaje = texto_para_whatsapp(nombres, equipos, suplentes, arqs)
    st.link_button("📲 Mandar al grupo por WhatsApp", f"https://wa.me/?text={quote(mensaje)}",
                   use_container_width=True)
    with st.expander("📋 Ver texto para copiar"):
        st.code(mensaje, language=None)
