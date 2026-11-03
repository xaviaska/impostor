"""Enllaços privats per participant (lògica pura, sense Streamlit).

- El resultat ("qui regala a qui") va xifrat dins del mateix enllaç amb una
  clau secreta del servidor. Sense la clau no es pot llegir, i no cal cap base
  de dades perquè l'enllaç funcioni.
- Opcionalment, un comptador en SQLite registra quantes vegades s'ha obert
  cada enllaç, per detectar si algú l'ha mirat abans que el destinatari.
  Si el fitxer es perd (p. ex. en reiniciar Streamlit Cloud), els enllaços
  continuen funcionant; només es reinicia el comptador.
"""
import datetime as dt
import json
import sqlite3
import urllib.parse
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken


# ---------- Xifrat ----------

def genera_clau() -> str:
    """Clau nova per posar a secrets.toml (només cal fer-ho una vegada)."""
    return Fernet.generate_key().decode()


def crea_token(clau: str, dades: dict) -> str:
    """Xifra un diccionari i el retorna com a text apte per a una URL."""
    brut = json.dumps(dades, ensure_ascii=False, separators=(",", ":")).encode()
    # Fernet ja és base64 apte per a URL; traiem el farciment "=" per
    # evitar que alguna aplicació talle l'enllaç.
    return Fernet(clau).encrypt(brut).decode().rstrip("=")


def llegeix_token(clau: str, token: str) -> dict | None:
    """Desxifra un token. Retorna None si és invàlid o s'ha manipulat."""
    token = token.strip()
    token += "=" * (-len(token) % 4)  # restaura el farciment
    try:
        return json.loads(Fernet(clau).decrypt(token.encode()))
    except (InvalidToken, ValueError):
        return None


# ---------- URLs ----------

def url_participant(url_base: str, token: str) -> str:
    return f"{url_base.rstrip('/')}/?t={token}"


def url_whatsapp(text: str) -> str:
    """Obre WhatsApp amb el missatge escrit; només cal triar el contacte."""
    return "https://wa.me/?text=" + urllib.parse.quote(text)


# ---------- Comptador d'obertures ----------

class Comptador:
    def __init__(self, ruta: str | Path):
        self.ruta = Path(ruta)
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with self._connecta() as con:
            con.execute(
                """CREATE TABLE IF NOT EXISTS obertures (
                       id_enllac TEXT PRIMARY KEY,
                       vegades   INTEGER NOT NULL,
                       primera   TEXT NOT NULL)"""
            )

    def _connecta(self) -> sqlite3.Connection:
        # Una connexió per operació: segur amb els fils de Streamlit.
        return sqlite3.connect(self.ruta, timeout=10)

    def registra(self, id_enllac: str) -> tuple[int, dt.datetime]:
        """Suma una obertura. Retorna (total d'obertures, data de la primera, UTC)."""
        ara = dt.datetime.now(dt.timezone.utc).isoformat()
        with self._connecta() as con:
            con.execute(
                """INSERT INTO obertures (id_enllac, vegades, primera) VALUES (?, 1, ?)
                   ON CONFLICT(id_enllac) DO UPDATE SET vegades = vegades + 1""",
                (id_enllac, ara),
            )
            vegades, primera = con.execute(
                "SELECT vegades, primera FROM obertures WHERE id_enllac = ?", (id_enllac,)
            ).fetchone()
        return vegades, dt.datetime.fromisoformat(primera)

    def vegades(self, id_enllac: str) -> int:
        with self._connecta() as con:
            fila = con.execute(
                "SELECT vegades FROM obertures WHERE id_enllac = ?", (id_enllac,)
            ).fetchone()
        return fila[0] if fila else 0


def id_enllac(id_sorteig: str, nom: str) -> str:
    """Identificador estable d'un enllaç dins el comptador."""
    return f"{id_sorteig}:{nom}"
