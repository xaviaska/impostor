"""Punt d'entrada: una sola app amb dos modes (pàgines)."""
import streamlit as st

st.set_page_config(page_title="Jocs de grup", page_icon="🎲", layout="centered")

# Si l'URL porta ?t=..., és un participant obrint el seu enllaç privat:
# només li mostrem el seu resultat, sense menú ni res més de l'app.
if "t" in st.query_params:
    from vista_participant import mostra

    mostra(st.query_params["t"])
    st.stop()

pagines = [
    st.Page("pagines/impostor.py", title="Impostor", icon="🕵️", default=True),
    st.Page("pagines/amic_invisible.py", title="Amic invisible", icon="🎁"),
]
st.navigation(pagines).run()
