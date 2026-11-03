"""Configuració llegida de st.secrets (fitxer .streamlit/secrets.toml en local,
o el quadre "Secrets" a Streamlit Cloud)."""
from pathlib import Path

import streamlit as st

from enllacos import Comptador

ARREL = Path(__file__).resolve().parent


def _secret(nom: str, defecte=None):
    try:
        return st.secrets.get(nom, defecte)
    except Exception:  # no hi ha cap fitxer de secrets
        return defecte


def clau_enllacos() -> str | None:
    return _secret("clau_enllacos")


def url_base() -> str:
    """URL pública de l'app. Si no està configurada, es dedueix de la petició."""
    configurada = _secret("url_base")
    if configurada:
        return configurada
    host = st.context.headers.get("Host", "localhost:8501")
    local = host.startswith(("localhost", "127.", "192.168.", "10."))
    return f"{'http' if local else 'https'}://{host}"


@st.cache_resource
def comptador() -> Comptador:
    return Comptador(_secret("ruta_bd", str(ARREL / "dades" / "obertures.sqlite")))
