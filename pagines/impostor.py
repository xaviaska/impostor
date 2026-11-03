"""Mode 1: joc de l'impostor."""
from pathlib import Path

import streamlit as st

from comu import desa_noms, entrada_noms, error_noms, flux_revelacio, reinicia_revelacio
from sorteig import rng, tria_impostors, tria_tema

P = "imp"  # prefix de les claus de session_state d'aquest mode
FITXER_TEMES = Path(__file__).resolve().parent.parent / "dades" / "temes.txt"


@st.cache_data
def carrega_temes(ruta: str) -> list[str]:
    """Un tema per línia; ignora línies buides i les que comencen per #."""
    linies = Path(ruta).read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in linies if l.strip() and not l.strip().startswith("#")]


def nova_ronda(noms: list[str], n_impostors: int) -> None:
    ss = st.session_state
    usats = ss.setdefault(f"{P}_temes_usats", set())
    ss[f"{P}_tema"] = tria_tema(carrega_temes(str(FITXER_TEMES)), usats)
    ss[f"{P}_impostors"] = tria_impostors(noms, n_impostors)
    ss[f"{P}_comenca"] = rng.choice(noms)
    ss[f"{P}_noms"] = noms
    ss[f"{P}_n_imp_desat"] = n_impostors
    desa_noms(P, noms)
    reinicia_revelacio(P)
    ss[f"{P}_fase"] = "revelacio"


def torna_a_config() -> None:
    st.session_state[f"{P}_fase"] = "config"


st.title("🕵️ Impostor")
fase = st.session_state.get(f"{P}_fase", "config")

if fase == "config":
    noms = entrada_noms(P, "Jugador", "jugadors")
    max_imp = max(1, (len(noms) - 1) // 2)  # sempre més jugadors normals que impostors
    n_imp = st.number_input(
        "Nombre d'impostors",
        min_value=1,
        max_value=max_imp,
        value=min(st.session_state.get(f"{P}_n_imp_desat", 1), max_imp),
        step=1,
    )
    if st.button("Sorteja i comença", type="primary"):
        error = error_noms(noms)
        if error:
            st.error(error)
        else:
            nova_ronda(noms, int(n_imp))
            st.rerun()

else:
    ss = st.session_state
    noms, tema, impostors = ss[f"{P}_noms"], ss[f"{P}_tema"], ss[f"{P}_impostors"]

    def mostra_paper(nom: str) -> None:
        if nom in impostors:
            st.error("### 🤫 Ets l'IMPOSTOR")
            st.write("No saps el tema. Escolta els altres i dissimula.")
        else:
            st.success("El tema és:")
            st.markdown(f"# {tema}")

    acabat = flux_revelacio(P, noms, mostra_paper)

    if acabat:
        st.success("Tothom ja sap el seu paper. A jugar!")
        st.info(f"Comença a parlar: **{ss[f'{P}_comenca']}**")
        with st.expander("Veure la solució (al final de la ronda)"):
            st.write(f"**Tema:** {tema}")
            st.write(f"**Impostor(s):** {', '.join(sorted(impostors))}")
        c1, c2 = st.columns(2)
        c1.button("Nova ronda (mateixos jugadors)", on_click=nova_ronda,
                  args=(noms, ss[f"{P}_n_imp_desat"]), type="primary")
        c2.button("Canviar jugadors", on_click=torna_a_config)
    else:
        st.sidebar.button("Cancel·lar ronda", on_click=torna_a_config)
