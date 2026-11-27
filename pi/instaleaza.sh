#!/bin/bash
# =====================================================================
#  Scutul — filtru pentru casă pe Raspberry Pi
#  AdGuard Home (blochează YouTube, rețele sociale, reclame, site-uri rele)
#  + Tailscale (filtrul merge și pe date mobile)
#  + ScuolaGioco: YouTube deblocat după ce copilul învață (opțional)
#
#  Pornire pe Raspberry:   bash instaleaza.sh
# =====================================================================
set -e
VERDE='\033[1;32m'; GALBEN='\033[1;33m'; ROSU='\033[1;31m'; NORMAL='\033[0m'
pas(){ echo; echo -e "${VERDE}==> $1${NORMAL}"; }
atentie(){ echo -e "${GALBEN}$1${NORMAL}"; }

if [ "$(id -u)" -eq 0 ]; then SUDO=""; else SUDO="sudo"; fi

pas "1/6  Actualizez sistemul (poate dura 5-10 minute)"
$SUDO apt-get update -y
$SUDO DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
$SUDO apt-get install -y curl python3 ca-certificates

pas "2/6  Instalez AdGuard Home"
if [ -x /opt/AdGuardHome/AdGuardHome ]; then
  echo "AdGuard Home este deja instalat."
else
  curl -s -S -L https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts/install.sh | $SUDO sh -s -- -v
fi

pas "3/6  Instalez Tailscale"
if ! command -v tailscale >/dev/null; then
  curl -fsSL https://tailscale.com/install.sh | $SUDO sh
fi

pas "4/6  Permit Raspberry-ului să fie „ieșire spre internet” pentru tabletă"
echo 'net.ipv4.ip_forward = 1' | $SUDO tee /etc/sysctl.d/99-tailscale.conf >/dev/null
echo 'net.ipv6.conf.all.forwarding = 1' | $SUDO tee -a /etc/sysctl.d/99-tailscale.conf >/dev/null
$SUDO sysctl -p /etc/sysctl.d/99-tailscale.conf >/dev/null

pas "5/6  Pornesc Tailscale"
atentie "Va apărea un link (https://login.tailscale.com/...). Deschide-l pe telefon și conectează-te cu contul tău Google."
$SUDO tailscale up --advertise-exit-node --accept-dns=false --hostname=scutul

curl -fsSL https://raw.githubusercontent.com/dancicipri1983-lab/scuolagioco-intrebari/main/pi/configureaza.py -o ~/configureaza.py || true
curl -fsSL https://raw.githubusercontent.com/dancicipri1983-lab/scuolagioco-intrebari/main/pi/scutul_deblocare.py -o ~/scutul_deblocare.py || true
pas "6/6  Gata!"
IP_LOCAL=$(hostname -I | awk '{print $1}')
IP_TS=$(tailscale ip -4 2>/dev/null | head -1)
echo
echo "------------------------------------------------------------"
echo -e " Adresa Raspberry acasă:        ${VERDE}${IP_LOCAL}${NORMAL}"
echo -e " Adresa Raspberry prin Tailscale: ${VERDE}${IP_TS}${NORMAL}"
echo
echo " Urmează: pune Tailscale pe tableta copilului (ghidul, Pasul 4),"
echo " apoi rulează configurarea automată (ghidul, Pasul 5)."
echo "------------------------------------------------------------"
echo
atentie "Notează cele două adrese de mai sus — îți trebuie în pașii următori."
