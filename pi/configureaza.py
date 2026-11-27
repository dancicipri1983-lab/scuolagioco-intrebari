#!/usr/bin/env python3
"""
Scutul — configurează automat AdGuard Home pentru controlul parental + deblocarea după învățat (ScuolaGioco).

Ce face (întreabă tot ce trebuie, pe rând):
  1. prima configurare AdGuard Home (utilizator, parolă, porturi) — dacă nu e deja făcută
  2. filtre: reclame/urmărire, site-uri pentru adulți, jocuri de noroc, ocolirea filtrului (VPN/DNS străin)
  3. control parental + navigare sigură + căutare sigură (Google, YouTube, Bing…)
  4. clientul „Tableta copilului” (aleasă din dispozitivele Tailscale) cu serviciile blocate
  5. serviciul care deblochează după ce copilul a învățat în ScuolaGioco (scutul_deblocare.py)
Se poate rula din nou oricând, ca să schimbi setările.
"""
import base64, getpass, json, os, subprocess, sys, time, urllib.error, urllib.request

AG = "http://127.0.0.1:3000"
CLIENT = "Tableta copilului"
CONF = "/etc/scutul.json"
LISTE = [
    ("HaGeZi Pro (reclame, urmărire, site-uri periculoase)", "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.txt"),
    ("HaGeZi NSFW (site-uri pentru adulți)", "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/nsfw.txt"),
    ("HaGeZi Gambling (jocuri de noroc)", "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/gambling.medium.txt"),
    ("HaGeZi DoH/VPN/Proxy (ocolirea filtrului)", "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/doh-vpn-proxy-bypass.txt"),
]
# reguli care trebuie să meargă mereu (Tailscale, ScuolaGioco, verificarea conexiunii Android)
PERMISE = ["tailscale.com", "tailscale.io", "ts.net", "ntfy.sh", "raw.githubusercontent.com", "github.com",
           "connectivitycheck.gstatic.com", "clients3.google.com", "time.android.com"]
RETELE = ["youtube", "tiktok", "instagram", "facebook", "snapchat", "twitter", "discord", "twitch", "reddit",
          "tumblr", "vk", "pinterest", "9gag", "kik", "onlyfans", "telegram"]
JOCURI = ["roblox", "fortnite", "minecraft", "epic_games", "steam", "leagueoflegends", "blizzard_entertainment", "riot_games", "valorant"]
AUTH = None
V = "\033[1;32m"; G = "\033[1;33m"; R = "\033[1;31m"; N = "\033[0m"


def api(path, data=None, method=None, auth=True):
    h = {"Content-Type": "application/json"}
    if auth and AUTH: h["Authorization"] = AUTH
    req = urllib.request.Request(AG + "/control" + path, method=method or ("POST" if data is not None else "GET"),
                                 data=json.dumps(data).encode() if data is not None else None, headers=h)
    with urllib.request.urlopen(req, timeout=60) as r:
        b = r.read()
        try: return json.loads(b) if b.strip() else None
        except Exception: return b.decode(errors="ignore")


def intreaba(txt, implicit=""):
    v = input(f"{txt}{f' [{implicit}]' if implicit else ''}: ").strip()
    return v or implicit


def da(txt, implicit=True):
    v = input(f"{txt} ({'D/n' if implicit else 'd/N'}): ").strip().lower()
    return implicit if not v else v.startswith(("d", "y"))


def pas(t): print(f"\n{V}==> {t}{N}")


def asteapta_adguard():
    for _ in range(60):
        try: urllib.request.urlopen(AG, timeout=3); return
        except urllib.error.HTTPError: return
        except Exception: time.sleep(2)
    sys.exit(f"{R}AdGuard Home nu răspunde pe {AG}. Rulează întâi instaleaza.sh.{N}")


def prima_configurare(conf):
    global AUTH
    nou = True
    try: api("/install/get_addresses", auth=False)
    except urllib.error.HTTPError: nou = False
    except Exception: nou = False
    if nou:
        pas("Prima configurare AdGuard Home")
        u = intreaba("Alege un nume de utilizator pentru AdGuard", conf.get("user", "admin"))
        while True:
            p = getpass.getpass("Alege o parolă (minim 8 caractere): ")
            if len(p) >= 8 and p == getpass.getpass("Scrie parola încă o dată: "): break
            print(f"{G}Parola e prea scurtă sau nu se potrivește. Mai încearcă.{N}")
        api("/install/configure", {"web": {"ip": "0.0.0.0", "port": 3000}, "dns": {"ip": "0.0.0.0", "port": 53},
                                   "username": u, "password": p}, auth=False)
        time.sleep(4)
    else:
        pas("AdGuard Home e deja configurat — intră cu utilizatorul și parola lui")
        u = intreaba("Utilizator AdGuard", conf.get("user", "admin"))
        p = getpass.getpass("Parola AdGuard: ")
    AUTH = "Basic " + base64.b64encode(f"{u}:{p}".encode()).decode()
    try: api("/status")
    except urllib.error.HTTPError as e:
        sys.exit(f"{R}Utilizator sau parolă greșită ({e.code}).{N}")
    conf["user"], conf["pass"] = u, p


def filtre():
    pas("Filtre: reclame, adulți, jocuri de noroc, ocolirea filtrului")
    st = api("/filtering/status")
    are = {f["url"] for f in (st.get("filters") or [])}
    for nume, url in LISTE:
        if url in are: print("  ✓", nume, "(există)"); continue
        try: api("/filtering/add_url", {"name": nume, "url": url, "whitelist": False}); print("  +", nume)
        except urllib.error.HTTPError as e: print(f"  {G}! {nume}: {e.read().decode(errors='ignore')[:120]}{N}")
    ale_mele = {f"@@||{d}^" for d in PERMISE} | {"! Scutul: domenii permise mereu"}
    reguli = [r for r in (st.get("user_rules") or []) if r not in ale_mele]
    reguli += ["! Scutul: domenii permise mereu"] + [f"@@||{d}^" for d in PERMISE]
    api("/filtering/set_rules", {"rules": reguli})
    print("  ✓ domenii permise mereu:", ", ".join(PERMISE))
    pas("Control parental, navigare sigură, căutare sigură")
    for path, body in (("/parental", {"enabled": True}), ("/safebrowsing", {"enabled": True}),
                       ("/safesearch/settings", {"enabled": True, "bing": True, "duckduckgo": True, "ecosia": True, "google": True, "pixabay": True, "yandex": True, "youtube": True})):
        try: api(path, body, method="PUT"); print("  ✓", path.strip("/"))
        except urllib.error.HTTPError:
            try: api(path + "/enable", {}); print("  ✓", path.strip("/"))
            except Exception as e: print(f"  {G}! {path}: {e}{N}")


def dispozitive_tailscale():
    try:
        j = json.loads(subprocess.run(["tailscale", "status", "--json"], capture_output=True, text=True, timeout=20).stdout)
        out = []
        for p in (j.get("Peer") or {}).values():
            ips = [i for i in p.get("TailscaleIPs", []) if "." in i]
            if ips: out.append((p.get("HostName") or p.get("DNSName", "?"), ips[0], p.get("OS", "")))
        return out
    except Exception:
        return []


def client(conf):
    pas(f"Clientul „{CLIENT}”")
    dev = dispozitive_tailscale()
    ip = conf.get("tablet_ip", "")
    if dev:
        print("Dispozitive în Tailscale:")
        for i, (n, a, os_) in enumerate(dev, 1): print(f"  {i}. {n} ({os_}) — {a}")
        x = intreaba("Care e tableta copilului? Scrie numărul", "")
        if x.isdigit() and 1 <= int(x) <= len(dev): ip = dev[int(x) - 1][1]
    if not ip:
        print(f"{G}Nu văd tableta în Tailscale. Instalează Tailscale pe tabletă (ghid, Pasul 5) și rulează din nou scriptul.{N}")
        ip = intreaba("Sau scrie adresa ei (100.x.x.x ori 192.168.x.x)", "")
    if not ip: print(f"{R}Fără adresă nu pot crea clientul. Îl faci mai târziu rulând din nou scriptul.{N}"); return
    ids = [ip]
    extra = intreaba("Adresa tabletei din Wi-Fi-ul de acasă (opțional, Enter ca să sari)", conf.get("tablet_lan", ""))
    if extra: ids.append(extra)
    toate = {s["id"] for s in (api("/blocked_services/all") or {}).get("blocked_services", [])}
    bl = [s for s in RETELE if s in toate]
    if da("Blochez și jocurile online (Roblox, Fortnite, Minecraft, Steam…)?", True): bl += [s for s in JOCURI if s in toate]
    if not da("Las WhatsApp deblocat (ca să te poată suna)?", True) and "whatsapp" in toate: bl.append("whatsapp")
    body = {"name": CLIENT, "ids": ids, "use_global_settings": False, "filtering_enabled": True, "parental_enabled": True,
            "safebrowsing_enabled": True, "safe_search": {"enabled": True, "bing": True, "duckduckgo": True, "ecosia": True, "google": True, "pixabay": True, "yandex": True, "youtube": True},
            "use_global_blocked_services": False, "blocked_services": sorted(set(bl)), "blocked_services_schedule": {"time_zone": "Europe/Rome"},
            "upstreams": [], "tags": ["user_child"], "ignore_querylog": False, "ignore_statistics": False}
    exista = any(c.get("name") == CLIENT for c in (api("/clients").get("clients") or []))
    if exista: api("/clients/update", {"name": CLIENT, "data": body})
    else: api("/clients/add", body)
    conf["tablet_ip"], conf["tablet_lan"], conf["blocate"] = ip, extra, sorted(set(bl))
    print(f"  ✓ {CLIENT} ({', '.join(ids)}): {len(set(bl))} servicii blocate")


def deblocare(conf):
    pas("Deblocare după învățat (ScuolaGioco)")
    print("În ScuolaGioco: Zona părinților → YouTube după învățat → Activează. Atinge codul ca să-l copiezi.")
    c = intreaba("Codul din ScuolaGioco (începe cu sgyt-)", conf.get("canal", ""))
    if not c.startswith("sgyt-"): print(f"{G}Sar peste acest pas (fără cod). Îl poți face mai târziu.{N}"); return
    print("Ce se deblochează după ce copilul a învățat?")
    print("  1. doar YouTube")
    print("  2. YouTube și toate rețelele sociale / jocurile blocate")
    print("  3. tot internetul (fără învățat, tableta are doar ScuolaGioco)")
    m = intreaba("Alege 1, 2 sau 3", str(conf.get("mod_nr", 1)))
    mod = {"1": "youtube", "2": "retele", "3": "internet"}.get(m, "youtube")
    noapte = intreaba("Ore în care NU se deblochează nimic (noaptea), ex. 21:00-07:00 sau Enter pentru niciuna", conf.get("noapte", "21:00-07:00"))
    conf.update({"canal": c, "mod": mod, "mod_nr": int(m) if m in "123" else 1, "noapte": noapte, "client": CLIENT, "max_minute": 120})
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scutul_deblocare.py")
    if not os.path.exists(src):
        urllib.request.urlretrieve("https://raw.githubusercontent.com/dancicipri1983-lab/scuolagioco-intrebari/main/pi/scutul_deblocare.py", "/tmp/scutul_deblocare.py"); src = "/tmp/scutul_deblocare.py"
    subprocess.run(["cp", src, "/opt/scutul_deblocare.py"], check=True)
    open("/etc/systemd/system/scutul.service", "w").write("""[Unit]
Description=Scutul - deblocare dupa invatat (ScuolaGioco)
After=network-online.target AdGuardHome.service
Wants=network-online.target
[Service]
ExecStart=/usr/bin/python3 -u /opt/scutul_deblocare.py
Restart=always
RestartSec=15
[Install]
WantedBy=multi-user.target
""")
    subprocess.run(["systemctl", "disable", "--now", "sgyt"], capture_output=True)
    subprocess.run(["systemctl", "daemon-reload"]); subprocess.run(["systemctl", "enable", "--now", "scutul"]); subprocess.run(["systemctl", "restart", "scutul"])
    print(f"  ✓ serviciul „scutul” pornit, mod: {mod}. Verifici cu: sudo journalctl -u scutul -f")


def main():
    if os.geteuid() != 0: sys.exit("Rulează cu sudo:  sudo python3 configureaza.py")
    conf = {}
    try: conf = json.load(open(CONF))
    except Exception: pass
    asteapta_adguard()
    prima_configurare(conf)
    filtre()
    client(conf)
    deblocare(conf)
    json.dump(conf, open(CONF, "w"), indent=1); os.chmod(CONF, 0o600)
    ip = subprocess.run(["hostname", "-I"], capture_output=True, text=True).stdout.split()[0]
    print(f"\n{V}Gata!{N} Panoul AdGuard: http://{ip}:3000  ·  setările Scutul: {CONF}")
    print("Ca să schimbi ceva, rulează din nou:  sudo python3 configureaza.py")


if __name__ == "__main__":
    main()
