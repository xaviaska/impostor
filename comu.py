"""Components d'interfície compartits pels dos modes."""
import streamlit as st


def entrada_noms(prefix: str, singular: str, plural: str, minim: int = 3, maxim: int = 30) -> list[str]:
    """Demana quants participants i el nom de cadascun.

    Els noms es desen en una clau pròpia (no de widget) perquè Streamlit
    esborra l'estat dels widgets que deixen de mostrar-se durant la partida.
    """
    desats = st.session_state.get(f"{prefix}_noms_desats", [])
    n = st.number_input(
        f"Nombre de {plural}",
        min_value=minim,
        max_value=maxim,
        value=max(minim, len(desats)),
        step=1,
        key=f"{prefix}_n",
    )
    noms = []
    columnes = st.columns(2)
    for i in range(int(n)):
        nom = columnes[i % 2].text_input(
            f"{singular} {i + 1}",
            value=desats[i] if i < len(desats) else "",
            placeholder=f"Nom del {singular.lower()} {i + 1}",
            key=f"{prefix}_nom_{i}",
        )
        noms.append(nom.strip())
    return noms


def desa_noms(prefix: str, noms: list[str]) -> None:
    st.session_state[f"{prefix}_noms_desats"] = list(noms)


def error_noms(noms: list[str]) -> str | None:
    """Retorna un missatge d'error, o None si els noms són vàlids."""
    if any(not n for n in noms):
        return "Hi ha algun nom buit."
    if len({n.lower() for n in noms}) != len(noms):
        return "Hi ha noms repetits."
    return None


def reinicia_revelacio(prefix: str) -> None:
    st.session_state[f"{prefix}_idx"] = 0
    st.session_state[f"{prefix}_vist"] = False


def flux_revelacio(prefix: str, noms: list[str], mostra_secret) -> bool:
    """Revela el secret de cada persona d'una en una.

    Per a cada persona: 1) passa el dispositiu, 2) revela, 3) amaga i passa.
    `mostra_secret(nom)` dibuixa el contingut secret.
    Retorna True quan tothom ja ho ha vist.
    """
    k_idx, k_vist = f"{prefix}_idx", f"{prefix}_vist"
    st.session_state.setdefault(k_idx, 0)
    st.session_state.setdefault(k_vist, False)

    idx = st.session_state[k_idx]
    if idx >= len(noms):
        return True

    def _revela():
        st.session_state[k_vist] = True

    def _seguent():
        st.session_state[k_idx] += 1
        st.session_state[k_vist] = False

    nom = noms[idx]
    st.progress(idx / len(noms), text=f"{idx} de {len(noms)} ja ho han vist")

    if not st.session_state[k_vist]:
        st.markdown(f"### Passa el dispositiu a **{nom}**")
        st.caption("Que ningú més miri la pantalla.")
        st.button(f"Sóc {nom}: mostra-m'ho", on_click=_revela, type="primary", key=f"{prefix}_btn_revela")
    else:
        with st.container(border=True):
            mostra_secret(nom)
        st.button("Ja ho he vist: amaga i passa", on_click=_seguent, type="primary", key=f"{prefix}_btn_seguent")
    return False
