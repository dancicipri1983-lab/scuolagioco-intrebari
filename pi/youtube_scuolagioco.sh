#!/bin/bash
# Instalează scriptul „YouTube după învățat” (ScuolaGioco) ca serviciu care pornește singur.
# Pornire pe Raspberry:   bash youtube_scuolagioco.sh
set -e
if [ "$(id -u)" -eq 0 ]; then SUDO=""; else SUDO="sudo"; fi
echo "Răspunde la 4 întrebări (le găsești în ghid, Pasul 7):"
read -rp "1) Codul din ScuolaGioco (începe cu sgyt-): " CANAL </dev/tty
read -rp "2) Utilizatorul AdGuard Home: " UTIL </dev/tty
read -rsp "3) Parola AdGuard Home: " PAROLA </dev/tty; echo
read -rp "4) Numele clientului copilului din AdGuard (ex. Tableta copilului): " CLIENT </dev/tty

URL=https://raw.githubusercontent.com/dancicipri1983-lab/scuolagioco-intrebari/main/pi/youtube_dupa_invatat.py
if [ -f youtube_dupa_invatat.py ]; then $SUDO cp youtube_dupa_invatat.py /opt/; else $SUDO curl -fsSL "$URL" -o /opt/youtube_dupa_invatat.py; fi
$SUDO python3 - "$CANAL" "$UTIL" "$PAROLA" "$CLIENT" <<'PY'
import sys,re
p='/opt/youtube_dupa_invatat.py';s=open(p).read()
canal,util,parola,client=sys.argv[1:5]
def put(k,v):
    global s; s=re.sub(r'^'+k+r' = .*$', k+' = '+repr(v), s, count=1, flags=re.M)
put('CANAL',canal); put('UTILIZATOR',util); put('PAROLA',parola); put('CLIENT',client)
open(p,'w').write(s)
PY
$SUDO chmod 600 /opt/youtube_dupa_invatat.py
$SUDO tee /etc/systemd/system/sgyt.service >/dev/null <<'EOF'
[Unit]
Description=ScuolaGioco - YouTube dupa invatat
After=network-online.target AdGuardHome.service
Wants=network-online.target
[Service]
ExecStart=/usr/bin/python3 -u /opt/youtube_dupa_invatat.py
Restart=always
RestartSec=15
[Install]
WantedBy=multi-user.target
EOF
$SUDO systemctl daemon-reload
$SUDO systemctl enable --now sgyt
sleep 3
$SUDO systemctl --no-pager status sgyt | head -12
echo
echo "Gata. Din ScuolaGioco > Zona părinților > YouTube după învățat apasă „Trimite un test”."
echo "Verifici aici cu:  sudo journalctl -u sgyt -f"
