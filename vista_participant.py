"""Pantalla que veu un participant quan obre el seu enllaç privat."""
from zoneinfo import ZoneInfo

import streamlit as st

from config import clau_enllacos, comptador
from enllacos import id_enllac, llegeix_token

ZONA = ZoneInfo("Europe/Madrid")


def mostra(token: str) -> None:
    clau = clau_enllacos()
    dades = llegeix_token(clau, token) if clau else None
    if not dades:
        st.error("Aquest enllaç no és vàlid. Demana'n un de nou a l'organitzador.")
        return

    st.title(f"🎁 {dades['s']}")
    st.markdown(f"Hola **{dades['d']}**! Has de fer un regal a:")
    st.markdown(f"# {dades['a']}")
    st.caption("No ho comparteixis amb ningú 🤫")

    # Comptem una sola obertura per sessió del navegador (Streamlit torna a
    # executar l'script a cada clic, i això no ha de sumar).
    clau_sessio = f"comptat_{token[-24:]}"
    if clau_sessio not in st.session_state:
        st.session_state[clau_sessio] = comptador().registra(id_enllac(dades["i"], dades["d"]))
    vegades, primera = st.session_state[clau_sessio]

    if vegades == 1:
        st.success("✅ Ets la primera persona que obre aquest enllaç.")
    else:
        hora = primera.astimezone(ZONA).strftime("%d/%m a les %H:%M")
        st.warning(
            f"⚠️ Aquest enllaç ja s'havia obert {vegades - 1} vegada/es abans "
            f"(la primera, el {hora}). Si no has estat tu, algú l'ha mirat."
        )
