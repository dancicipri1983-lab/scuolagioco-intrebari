#!/usr/bin/env python3
"""
ScuolaGioco -> AdGuard Home: deblochează YouTube pe dispozitivul copilului după ce a învățat.

Cum funcționează:
  - Jocul trimite pe canalul ntfy (codul din Zona părinților, ex. sgyt-abcd...) un mesaj „SGYT 30 | ...”.
  - Scriptul ascultă canalul, scoate YouTube din serviciile blocate ale clientului (copilului)
    în AdGuard Home pentru 30 de minute, apoi îl blochează din nou.

Ce trebuie completat mai jos: CANAL, ADGUARD, UTILIZATOR, PAROLA, CLIENT.
Pornire: python3 youtube_dupa_invatat.py   (sau ca serviciu systemd, vezi la final)
"""
import base64, json, re, threading, time, urllib.request

CANAL = "sgyt-COPIAZA-CODUL-DIN-JOC"      # din ScuolaGioco > Zona părinților > YouTube după învățat
ADGUARD = "http://127.0.0.1:3000"          # adresa AdGuard Home
UTILIZATOR = "admin"
PAROLA = "parola-ta"
CLIENT = "Tableta copilului"               # numele clientului din AdGuard Home > Setări > Clienți
SERVICIU = "youtube"
MAX_MINUTE = 120                           # limită de siguranță

AUTH = "Basic " + base64.b64encode(f"{UTILIZATOR}:{PAROLA}".encode()).decode()
_timer = None
_lock = threading.Lock()


def api(path, data=None):
    req = urllib.request.Request(ADGUARD + path, method="POST" if data is not None else "GET",
                                 data=json.dumps(data).encode() if data is not None else None,
                                 headers={"Authorization": AUTH, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        body = r.read()
        return json.loads(body) if body.strip() else None


def set_youtube(blocat):
    clients = api("/control/clients").get("clients") or []
    c = next((x for x in clients if x.get("name") == CLIENT), None)
    if not c:
        print(f"[!] Nu găsesc clientul „{CLIENT}” în AdGuard Home"); return
    bs = set(c.get("blocked_services") or [])
    bs.add(SERVICIU) if blocat else bs.discard(SERVICIU)
    c["blocked_services"] = sorted(bs)
    c["use_global_blocked_services"] = False
    api("/control/clients/update", {"name": CLIENT, "data": c})
    print(time.strftime("%H:%M"), "YouTube", "BLOCAT" if blocat else "DEBLOCAT")


def deblocheaza(minute):
    global _timer
    with _lock:
        if _timer: _timer.cancel()
        set_youtube(False)
        _timer = threading.Timer(minute * 60, lambda: set_youtube(True))
        _timer.daemon = True
        _timer.start()


def asculta():
    url = f"https://ntfy.sh/{CANAL}/json"
    while True:
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                for linie in r:
                    m = json.loads(linie)
                    if m.get("event") != "message": continue
                    g = re.match(r"^SGYT (\d{1,3})\b", m.get("message", ""))
                    if g:
                        deblocheaza(min(int(g.group(1)), MAX_MINUTE))
                    elif m.get("message", "").startswith("SGTEST"):
                        print("Mesaj de test primit, legătura funcționează.")
        except Exception as e:
            print("reconectare…", e); time.sleep(10)


if __name__ == "__main__":
    set_youtube(True)   # la pornire YouTube rămâne blocat
    asculta()

# Serviciu systemd (pornește singur la fiecare pornire a Raspberry):
#   sudo cp youtube_dupa_invatat.py /opt/
#   sudo nano /etc/systemd/system/sgyt.service
#     [Unit]
#     Description=ScuolaGioco YouTube
#     After=network-online.target
#     [Service]
#     ExecStart=/usr/bin/python3 /opt/youtube_dupa_invatat.py
#     Restart=always
#     [Install]
#     WantedBy=multi-user.target
#   sudo systemctl enable --now sgyt
