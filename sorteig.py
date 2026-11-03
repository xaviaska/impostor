"""Lògica pura de sorteig (sense Streamlit), fàcil de provar."""
import random

# Generador criptogràficament segur: ningú pot predir el resultat.
rng = random.SystemRandom()


def tria_impostors(noms: list[str], n_impostors: int) -> set[str]:
    """Tria n_impostors noms diferents a l'atzar."""
    if not 1 <= n_impostors < len(noms):
        raise ValueError("Nombre d'impostors no vàlid")
    return set(rng.sample(noms, n_impostors))


def tria_tema(temes: list[str], usats: set[str]) -> str:
    """Tria un tema no usat; quan s'esgoten, torna a començar."""
    disponibles = [t for t in temes if t not in usats]
    if not disponibles:
        usats.clear()
        disponibles = list(temes)
    tema = rng.choice(disponibles)
    usats.add(tema)
    return tema


def sorteig_amic_invisible(noms: list[str]) -> dict[str, str]:
    """Retorna {qui_regala: a_qui}. Ningú es regala a si mateix.

    Barreja i repeteix fins que no hi ha cap coincidència (desarranjament).
    Calen de mitjana ~2,7 intents, i cada permutació vàlida és igual de probable.
    """
    if len(noms) < 2:
        raise ValueError("Calen almenys 2 participants")
    while True:
        receptors = noms[:]
        rng.shuffle(receptors)
        if all(a != b for a, b in zip(noms, receptors)):
            return dict(zip(noms, receptors))
