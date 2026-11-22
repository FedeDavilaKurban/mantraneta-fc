# ⚽ Sorteo de equipos

App en Python (Streamlit) para sortear equipos a partir de la lista del grupo de WhatsApp.

## Cómo se usa
1. En WhatsApp, mantené apretado el mensaje con la lista → **Copiar**.
2. Abrí el link de la app, pegá la lista y tocá **🎲 Sortear**.
3. Tocá **📲 Mandar al grupo por WhatsApp** (o copiá el texto) para pasar los equipos al grupo.

La app entiende listas tipo:
```
Fútbol jueves 21hs
1. Juan
2. Pedro (arq)
3. Martín 🧤
4.
```
- Si la lista está numerada, ignora los títulos y los lugares vacíos.
- Saca emojis, negritas y nombres repetidos.
- `(arq)`, `arquero` o 🧤 marcan al arquero: hay uno por equipo.
- Cada equipo se llama como una canción de Tool elegida al azar (sin repetir). La lista está en `CANCIONES_TOOL` dentro de `sorteo.py`, por si querés sacar o agregar alguna.
- En **Opciones**: cantidad de equipos y cupo por equipo (los que sobran quedan de suplentes).

## Probar en tu compu
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Ponerla online gratis (Streamlit Community Cloud)
1. Creá un repositorio en GitHub (puede ser público) y subí `app.py`, `sorteo.py` y `requirements.txt`.
2. Entrá a https://share.streamlit.io con tu cuenta de GitHub → **Create app** → elegí el repo, branch `main`, archivo `app.py`.
3. En *App URL* elegí un nombre corto, p. ej. `futbol-jueves` → queda `https://futbol-jueves.streamlit.app`.
4. Pegá ese link en la descripción del grupo de WhatsApp.

> Nota: en el plan gratis, si nadie entra por varios días la app "se duerme". La primera persona que entra
> toca "Yes, get this app back up!" y en unos segundos vuelve a andar.
