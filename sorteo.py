"""Lógica para leer la lista de WhatsApp y sortear equipos (sin Streamlit, fácil de testear)."""

import random
import re

# "1. Juan", "1- Juan", "1) Juan", "1 Juan", "1: Juan"
_NUMERADA = re.compile(r"^\s*\d{1,3}\s*[\.\-\)\:]?\s*(.*)$")
# Marcas de arquero: "(arq)", "(arquero)", "🧤", "arquero"
_ARQUERO = re.compile(r"\(\s*arq\w*\s*\)|🧤|\barquero\b|\barq\b", re.IGNORECASE)


CANCIONES_TOOL = [
    # Opiate (1992)
    "Sweat", "Hush", "Part of Me", "Cold and Ugly", "Jerk-Off", "Opiate",
    # Undertow (1993)
    "Intolerance", "Prison Sex", "Sober", "Bottom", "Crawl Away", "Swamp Song",
    "Undertow", "4°", "Flood", "Disgustipated",
    # Ænima (1996)
    "Stinkfist", "Eulogy", "H.", "Useful Idiot", "Forty Six & 2", "Message to Harry Manback",
    "Hooker with a Penis", "Intermission", "Jimmy", "Die Eier von Satan", "Pushit",
    "Cesaro Summability", "Ænema", "(-) Ions", "Third Eye",
    # Lateralus (2001)
    "The Grudge", "Eon Blue Apocalypse", "The Patient", "Mantra", "Schism", "Parabol",
    "Parabola", "Ticks & Leeches", "Lateralus", "Disposition", "Reflection", "Triad",
    "Faaip de Oiad",
    # 10,000 Days (2006)
    "Vicarious", "Jambi", "Wings for Marie", "10,000 Days", "The Pot", "Lipan Conjuring",
    "Lost Keys", "Rosetta Stoned", "Intension", "Right in Two", "Viginti Tres",
    # Fear Inoculum (2019)
    "Fear Inoculum", "Pneuma", "Litanie contre la Peur", "Invincible", "Legion Inoculant",
    "Descending", "Culling Voices", "Chocolate Chip Trip", "7empest", "Mockingbeat",
]


def nombres_tool(n: int, rng: random.Random | None = None) -> list[str]:
    """Elige n canciones de Tool distintas al azar para usar como nombres de equipo."""
    return (rng or random.Random()).sample(CANCIONES_TOOL, n)


def _limpiar(texto: str) -> str:
    """Saca emojis, asteriscos de negrita, viñetas, etc. Deja letras (con tildes), números, espacios, . ' -"""
    texto = re.sub(r"[^\w\s\.'\-]", " ", texto)
    texto = texto.replace("_", " ")
    texto = re.sub(r"\s+", " ", texto).strip(" .-'")
    return texto


def leer_lista(texto: str) -> tuple[list[str], set[str], list[str]]:
    """
    Recibe la lista copiada de WhatsApp y devuelve (jugadores, arqueros, repetidos).

    - Si hay líneas numeradas, sólo se toman esas (así se ignoran títulos como
      "Partido jueves 21hs" o "Suplentes:"). Si no hay números, se toma cada línea.
    - Los lugares vacíos ("7." sin nombre) se ignoran.
    - Respeta el orden en que se anotaron.
    """
    lineas = [l for l in texto.splitlines() if l.strip()]
    matches = [_NUMERADA.match(l) for l in lineas]
    if any(matches):
        candidatos = [m.group(1) for m in matches if m]
    else:
        candidatos = lineas

    jugadores, arqueros, repetidos = [], set(), []
    vistos = set()
    for c in candidatos:
        es_arquero = bool(_ARQUERO.search(c))
        nombre = _limpiar(_ARQUERO.sub(" ", c))
        if not nombre:
            continue
        clave = nombre.casefold()
        if clave in vistos:
            repetidos.append(nombre)
            continue
        vistos.add(clave)
        jugadores.append(nombre)
        if es_arquero:
            arqueros.add(nombre)
    return jugadores, arqueros, repetidos


def sortear(
    jugadores: list[str],
    n_equipos: int = 2,
    cupo_por_equipo: int = 0,
    arqueros: set[str] | None = None,
    respetar_orden: bool = True,
    rng: random.Random | None = None,
) -> tuple[list[list[str]], list[str]]:
    """
    Devuelve (equipos, suplentes).

    - cupo_por_equipo = 0 → sin límite, juegan todos.
    - respetar_orden = True → si sobra gente, quedan de suplentes los últimos en anotarse.
      Si es False, los suplentes también se sortean.
    - Los arqueros se reparten primero, uno por equipo; si sobran, juegan de campo.
    """
    rng = rng or random.Random()
    arqueros = arqueros or set()
    jugadores = list(jugadores)

    suplentes: list[str] = []
    if cupo_por_equipo > 0:
        total = n_equipos * cupo_por_equipo
        if not respetar_orden:
            rng.shuffle(jugadores)
        jugadores, suplentes = jugadores[:total], jugadores[total:]

    arq = [j for j in jugadores if j in arqueros]
    campo = [j for j in jugadores if j not in arqueros]
    rng.shuffle(arq)
    rng.shuffle(campo)

    equipos: list[list[str]] = [[] for _ in range(n_equipos)]
    for i, a in enumerate(arq):
        if i < n_equipos:
            equipos[i].append(a)
        else:
            campo.append(a)

    # Arrancamos a repartir por un equipo al azar para que no siempre
    # el "Equipo 1" se lleve el jugador de más cuando el número es impar.
    orden = list(range(n_equipos))
    rng.shuffle(orden)
    for j in campo:
        destino = min(orden, key=lambda k: len(equipos[k]))
        equipos[destino].append(j)

    return equipos, suplentes


def texto_para_whatsapp(nombres_equipos: list[str], equipos: list[list[str]],
                        suplentes: list[str], arqueros: set[str]) -> str:
    """Arma el mensaje listo para pegar en el grupo (usa *negrita* de WhatsApp)."""
    partes = ["⚽ *EQUIPOS* ⚽", ""]
    for nombre, equipo in zip(nombres_equipos, equipos):
        partes.append(f"*{nombre}* ({len(equipo)})")
        for j in equipo:
            partes.append(f"- {j}{' 🧤' if j in arqueros else ''}")
        partes.append("")
    if suplentes:
        partes.append("*Suplentes*")
        partes.extend(f"- {s}" for s in suplentes)
    return "\n".join(partes).strip()
