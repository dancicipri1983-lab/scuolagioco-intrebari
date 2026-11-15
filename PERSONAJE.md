# Cum se creează un personaj nou (fără APK nou)

Personajele noi se pun în `pack.json` la `"ch"`: `{"id": {...}}` (id: 2–16 litere mici/cifre, diferit de cele de bază).

```json
"leo": {"col":"#f4a62a","bel":"#ffe6b3","mc":"#b5541c","ear":"mane","x":["tlion","snout"],
        "n":{"it":"Leo","ro":"Leo","en":"Leo","es":"Leo","fr":"Léo","de":"Leo","nb":"Leo","pl":"Leo"},
        "k":{"ro":"un pui de leu care învață să fie curajos", "...":"toate cele 8 limbi"}}
```

- `col` culoarea corpului, `bel` burtica, `hc` capul (opțional, dacă e diferit), `mc` coama / coada / părul unicornului, `sc` dungi / fular / fundă. Toate în formatul `#rrggbb`.
- `ear` (una): point, round, small, long, horn, tuft, antenna, hood, none, cat, mane, unicorn, elephant, leaf, antlers
- `x` (maximum 8): wings, tdragon, spots, whisk, tlong, snout, screen, bolts, tfox, beak, big, flip, teeth, tpuff, spikes, nose, shell, pig, tcurl, hair, snoutl, tlion, trunk, stripes, freckles, glasses, scarf, bow
- Personaje de bază desenate (clipesc, vorbesc): bubu, tina, zor, miri, olo, pip, lulu, bruno, kiki, tomo, gogu, rosi, lup
- Personaje de bază 3D (Microsoft Fluent Emoji 3D, licență MIT): rufo (vulpe), bambu (panda), koko (koala), stelina (unicorn), rex (dinozaur), hubu (bufniță), pingo (pinguin), ella (elefant), leo (leu), momo (maimuță), ranu (broască), otto (caracatiță), delfi (delfin), lento (leneș), lolo (lamă), ondi (vidră), gira (girafă), spini (arici), scutel (țestoasă)

## Personaj 3D nou (imagine)
1. Ia imaginea din depozitul public https://github.com/microsoft/fluentui-emoji (licență MIT), din `assets/<Nume>/3D/<nume>_3d.png`, de exemplu cu `git clone --depth 1 --filter=blob:none --sparse` + `git sparse-checkout set --no-cone "/assets/Cat/3D/"`.
2. Copiaz-o în `img/<nume>.png` (litere mici, fără spații, de exemplu `img/cat.png`).
3. În `pack.json` la `"ch"`: `"miau": {"img":"cat", "n":{…8 limbi}, "k":{…8 limbi}}`.
Doar imagini din Fluent Emoji (MIT) sau desenate de noi. NICIODATĂ imagini de pe alte site-uri sau personaje protejate.
- Personajele trebuie să fie ORIGINALE (fără personaje protejate) sau din povești clasice în domeniu public.
