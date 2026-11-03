# Jocs de grup (Streamlit)

Dos modes en una sola app: **Impostor** i **Amic invisible**.
L'amic invisible es pot repartir passant-se el mòbil o amb **enllaços privats per WhatsApp**.

## Estructura

```
jocs/
├── app.py                  # entrada; si l'URL porta ?t=... mostra la vista del participant
├── comu.py                 # UI compartida: entrada de noms + flux de revelació
├── sorteig.py              # lògica pura de sorteig
├── enllacos.py             # xifrat dels enllaços + comptador d'obertures (SQLite)
├── config.py               # lectura de secrets
├── vista_participant.py    # el que veu qui obre un enllaç
├── pagines/
│   ├── impostor.py
│   └── amic_invisible.py
├── dades/temes.txt
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.exemple
└── requirements.txt
```

## Com funcionen els enllaços

1. En fer el sorteig, cada resultat ("Anna regala a Pere") es xifra amb una clau
   secreta que només té el servidor, i el text xifrat va dins l'enllaç (`?t=...`).
2. L'organitzador veu una llista amb un botó de WhatsApp per persona, però mai els resultats.
3. En obrir l'enllaç, l'app el desxifra i mostra només aquell resultat.
4. Un comptador (SQLite) registra les obertures. Si algú obre un enllaç abans
   que el destinatari, el destinatari veurà un avís. Si el comptador es perd,
   els enllaços continuen funcionant.

---

## 1. Posada en marxa en local

```bash
cd jocs
pip install -r requirements.txt
```

Crea la clau secreta (només una vegada):

```bash
python -c "from enllacos import genera_clau; print(genera_clau())"
```

Copia `.streamlit/secrets.toml.exemple` com a `.streamlit/secrets.toml` i enganxa-hi la clau.

```bash
streamlit run app.py
```

En local, els enllaços porten l'adreça del PC (p. ex. `http://192.168.1.35:8501`)
i només funcionen dins la mateixa WiFi.

---

## 2. Streamlit Community Cloud

1. Crea un repositori a GitHub (pot ser privat) i puja-hi la carpeta.
   El `.gitignore` ja evita pujar `secrets.toml`. Comprova-ho a GitHub abans de continuar.
2. Ves a https://share.streamlit.io → **Create app** → tria el repositori, la branca
   i `app.py` com a fitxer principal.
3. A **Advanced settings → Secrets** enganxa:
   ```toml
   clau_enllacos = "LA-TEUA-CLAU"
   url_base = "https://NOM-DE-LA-TEUA-APP.streamlit.app"
   ```
   (L'adreça exacta la veuràs en crear l'app; la pots canviar després a Settings → Secrets.)
4. **Deploy**.

Limitacions:
- L'app "s'adorm" si no s'usa durant un temps; la primera persona que l'obri haurà
  d'esperar uns segons (o clicar un botó per despertar-la).
- Els fitxers no són permanents: en reiniciar o redesplegar, **el comptador d'obertures
  es reinicia**. Els enllaços continuen funcionant igualment.

---

## 3. VPS Ubuntu (systemd + nginx + HTTPS)

Exemple amb el subdomini `jocs.exemple.com`; canvia'l pel teu.

### 3.1 Codi i entorn

```bash
sudo apt update && sudo apt install -y python3-venv nginx
cd ~
git clone https://github.com/USUARI/jocs.git     # o copia la carpeta amb scp
cd jocs
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 3.2 Secrets

```bash
nano .streamlit/secrets.toml
```
```toml
clau_enllacos = "LA-TEUA-CLAU"
url_base = "https://jocs.exemple.com"
```
```bash
chmod 600 .streamlit/secrets.toml
```

### 3.3 Servei systemd (s'arrenca sol i es reinicia si cau)

`sudo nano /etc/systemd/system/jocs.service`:

```ini
[Unit]
Description=Jocs de grup (Streamlit)
After=network.target

[Service]
User=EL-TEU-USUARI
WorkingDirectory=/home/EL-TEU-USUARI/jocs
ExecStart=/home/EL-TEU-USUARI/jocs/.venv/bin/streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
Restart=always

[Install]
WantedBy=multi-user.target
```

`127.0.0.1`: l'app només és accessible a través de nginx, no directament des d'internet.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now jocs
systemctl status jocs          # ha de dir "active (running)"
journalctl -u jocs -f          # registres en directe
```

### 3.4 DNS

Al proveïdor del domini, crea un registre **A**: `jocs` → IP del VPS.
Comprova-ho amb `ping jocs.exemple.com` (pot tardar uns minuts).

### 3.5 nginx (Streamlit necessita WebSockets)

`sudo nano /etc/nginx/sites-available/jocs`:

```nginx
server {
    listen 80;
    server_name jocs.exemple.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/jocs /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo ufw allow 'Nginx Full'      # si fas servir ufw
```

### 3.6 HTTPS gratuït

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d jocs.exemple.com
```

Certbot modifica la configuració de nginx i renova el certificat automàticament.

### Actualitzar l'app més endavant

```bash
cd ~/jocs && git pull && .venv/bin/pip install -r requirements.txt
sudo systemctl restart jocs
```

### Sense domini (només per provar)

Obre el port: `sudo ufw allow 8501`, i al servei canvia `127.0.0.1` per `0.0.0.0`.
Posa `url_base = "http://IP-DEL-VPS:8501"`. Funciona, però sense HTTPS.
