#!/usr/bin/env python3
"""
Scutul — deblocare după învățat. Ascultă canalul ScuolaGioco (ntfy) și, când copilul a învățat destul,
deblochează pe tableta copilului, pentru minutele câștigate:
  mod "youtube"  -> doar YouTube
  mod "retele"   -> toate serviciile blocate (YouTube, rețele sociale, jocuri)
  mod "internet" -> tot internetul (în rest tableta are doar ScuolaGioco și ce e permis)
Setările sunt în /etc/scutul.json (le scrie configureaza.py). Rulează ca serviciul systemd „scutul”.
"""
import base64, json, re, threading, time, urllib.request
from datetime import datetime

CONF = json.load(open("/etc/scutul.json"))
AG = "http://127.0.0.1:3000"
AUTH = "Basic " + base64.b64encode(f"{CONF['user']}:{CONF['pass']}".encode()).decode()
CLIENT = CONF.get("client", "Tableta copilului")
MOD = CONF.get("mod", "youtube")
MAXM = int(CONF.get("max_minute", 120))
STARE = "/var/lib/scutul.json"
TOT = f"/.*/$client='{CLIENT}'"
_lock = threading.Lock()
_timer = None


def log(*a): print(time.strftime("%Y-%m-%d %H:%M"), *a, flush=True)


def api(path, data=None):
    req = urllib.request.Request(AG + "/control" + path, method="POST" if data is not None else "GET",
                                 data=json.dumps(data).encode() if data is not None else None,
                                 headers={"Authorization": AUTH, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        b = r.read()
        return json.loads(b) if b.strip() else None


def client():
    return next((c for c in api("/clients").get("clients") or [] if c.get("name") == CLIENT), None)


def set_servicii(lista):
    c = client()
    if not c: log("[!] nu găsesc clientul", CLIENT); return
    c["blocked_services"] = sorted(set(lista)); c["use_global_blocked_services"] = False
    api("/clients/update", {"name": CLIENT, "data": c})


def set_tot(blocat):
    r = [x for x in (api("/filtering/status").get("user_rules") or []) if x != TOT]
    if blocat: r.append(TOT)
    api("/filtering/set_rules", {"rules": r})


def blocheaza():
    baza = CONF.get("blocate") or ["youtube"]
    set_servicii(baza)
    if MOD == "internet": set_tot(True)
    salveaza(0); log("BLOCAT (mod", MOD + ")")


def deblocheaza_acum():
    baza = CONF.get("blocate") or ["youtube"]
    if MOD == "youtube": set_servicii([s for s in baza if s != "youtube"])
    elif MOD == "retele": set_servicii([])
    else: set_servicii([s for s in baza if s != "youtube"]); set_tot(False)


def noapte():
    m = re.match(r"^\s*(\d{1,2}):(\d\d)\s*-\s*(\d{1,2}):(\d\d)\s*$", CONF.get("noapte") or "")
    if not m: return False
    a, b = int(m[1]) * 60 + int(m[2]), int(m[3]) * 60 + int(m[4])
    t = datetime.now().hour * 60 + datetime.now().minute
    return (a <= t < b) if a < b else (t >= a or t < b)


def salveaza(pana, parinte=False):
    try: json.dump({"pana": pana, "parinte": parinte}, open(STARE, "w"))
    except Exception: pass


def programeaza(sec):
    global _timer
    if _timer: _timer.cancel()
    _timer = threading.Timer(max(1, sec), lambda: blocheaza()); _timer.daemon = True; _timer.start()


def deblocheaza(minute, parinte=False):
    with _lock:
        if noapte() and not parinte: log("cerere de deblocare ignorată: e noapte"); return
        minute = max(1, min(minute, MAXM))
        deblocheaza_acum(); pana = time.time() + minute * 60; salveaza(pana, parinte); programeaza(minute * 60)
        log(f"DEBLOCAT {minute} minute (mod {MOD}){' de părinte' if parinte else ''}")


def asculta():
    url = f"https://ntfy.sh/{CONF['canal']}/json"
    while True:
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                for linie in r:
                    m = json.loads(linie)
                    if m.get("event") != "message": continue
                    txt = m.get("message", "")
                    g = re.match(r"^SGYT (\d{1,3})\b", txt)
                    p = re.match(r"^SGPARENT (\d{1,3})\b", txt)
                    if g: deblocheaza(int(g.group(1)))
                    elif p: deblocheaza(int(p.group(1)), parinte=True)
                    elif txt.startswith("SGLOCK"):
                        with _lock:
                            if _timer: _timer.cancel()
                            blocheaza(); log("blocat de părinte")
                    elif txt.startswith("SGTEST"): log("Mesaj de test primit — legătura cu ScuolaGioco funcționează.")
        except Exception as e:
            log("reconectare…", e); time.sleep(10)


def paznic_noapte():
    while True:
        time.sleep(60)
        try:
            st = json.load(open(STARE))
            if st.get("pana", 0) > time.time() and noapte() and not st.get("parinte"):
                log("a început noaptea — blochez"); blocheaza()
        except Exception: pass


if __name__ == "__main__":
    for i in range(30):
        try: api("/status"); break
        except Exception: time.sleep(5)
    try: pana = json.load(open(STARE)).get("pana", 0)
    except Exception: pana = 0
    if pana > time.time() and not noapte():
        deblocheaza_acum(); programeaza(pana - time.time()); log("continui deblocarea încă", int((pana - time.time()) / 60), "minute")
    else: blocheaza()
    threading.Thread(target=paznic_noapte, daemon=True).start()
    asculta()
