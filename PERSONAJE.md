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
- Personaje de bază: bubu, tina, zor, miri, olo, pip, lulu, bruno, kiki, tomo, gogu, rosi, lup
- Personajele trebuie să fie ORIGINALE (fără personaje protejate) sau din povești clasice în domeniu public.
