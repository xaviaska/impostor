"""Mode 2: amic invisible."""
import secrets

import streamlit as st

from comu import desa_noms, entrada_noms, error_noms, flux_revelacio, reinicia_revelacio
from config import clau_enllacos, comptador, url_base
from enllacos import crea_token, id_enllac, url_participant, url_whatsapp
from sorteig import sorteig_amic_invisible

P = "ai"  # prefix de les claus de session_state d'aquest mode
MODE_MOBIL = "Passant-nos el mòbil"
MODE_ENLLACOS = "Enllaços privats (WhatsApp)"


def nou_sorteig(noms: list[str], mode: str, nom_sorteig: str) -> None:
    ss = st.session_state
    assignacio = sorteig_amic_invisible(noms)
    ss[f"{P}_assignacio"] = assignacio
    ss[f"{P}_noms"] = noms
    ss[f"{P}_mode"] = mode
    ss[f"{P}_nom_sorteig_desat"] = nom_sorteig
    if mode == MODE_ENLLACOS:
        id_sorteig = secrets.token_hex(4)
        ss[f"{P}_id"] = id_sorteig
        clau, base = clau_enllacos(), url_base()
        ss[f"{P}_enllacos"] = {
            nom: url_participant(base, crea_token(clau, {"s": nom_sorteig, "i": id_sorteig, "d": nom, "a": a}))
            for nom, a in assignacio.items()
        }
    desa_noms(P, noms)
    reinicia_revelacio(P)
    ss[f"{P}_fase"] = "revelacio"


def torna_a_config() -> None:
    st.session_state[f"{P}_fase"] = "config"


def mostra_enllacos() -> None:
    """Llista per a l'organitzador: només enllaços, mai els resultats."""
    ss = st.session_state
    nom_sorteig, id_sorteig = ss[f"{P}_nom_sorteig_desat"], ss[f"{P}_id"]
    st.success("Sorteig fet. Envia a cada persona el seu enllaç.")
    st.caption("Tu no veus els resultats. Si obres un enllaç que no és teu, el destinatari en serà avisat.")

    for nom, enllac in ss[f"{P}_enllacos"].items():
        obert = comptador().vegades(id_enllac(id_sorteig, nom)) > 0
                text = f"Hola {nom}! Aquí tens el teu amic invisible de «{nom_sorteig}». És només per a tu:\n\n{enllac}"
        with st.container(border=True):
            c1, c2 = st.columns([3, 2])
            estat = "✅ Ja l'ha obert" if obert else "⏳ Encara no l'ha obert"
            c1.markdown(f"**{nom}**  \n{estat}")
            c2.link_button("Enviar per WhatsApp", url_whatsapp(text))
            with st.expander("Copiar l'enllaç"):
                st.code(enllac, language=None)

    c1, c2 = st.columns(2)
    c1.button("🔄 Actualitzar estat")  # qualsevol clic torna a executar la pàgina
    c2.button("Nou sorteig", on_click=torna_a_config)


st.title("🎁 Amic invisible")
fase = st.session_state.get(f"{P}_fase", "config")

if fase == "config":
    nom_sorteig = st.text_input(
        "Nom del sorteig", value=st.session_state.get(f"{P}_nom_sorteig_desat", "Amic invisible")
    ).strip() or "Amic invisible"
    noms = entrada_noms(P, "Participant", "participants")
    mode = st.radio("Com es reparteix?", [MODE_MOBIL, MODE_ENLLACOS], horizontal=True)
    if mode == MODE_ENLLACOS and not clau_enllacos():
        st.warning("Falta la clau `clau_enllacos` als secrets. Mira el README.")

    if st.button("Fes el sorteig", type="primary"):
        error = error_noms(noms)
        if error:
            st.error(error)
        elif mode == MODE_ENLLACOS and not clau_enllacos():
            st.error("No es poden crear enllaços sense la clau secreta.")
        else:
            nou_sorteig(noms, mode, nom_sorteig)
            st.rerun()

elif st.session_state[f"{P}_mode"] == MODE_ENLLACOS:
    mostra_enllacos()

else:
    ss = st.session_state
    assignacio = ss[f"{P}_assignacio"]

    def mostra_receptor(nom: str) -> None:
        st.success("Has de fer un regal a:")
        st.markdown(f"# {assignacio[nom]}")

    acabat = flux_revelacio(P, ss[f"{P}_noms"], mostra_receptor)

    if acabat:
        st.success("Tothom ja sap a qui ha de regalar. 🎉")
        st.button("Nou sorteig", on_click=torna_a_config, type="primary")
    else:
        st.sidebar.button("Cancel·lar sorteig", on_click=torna_a_config)
