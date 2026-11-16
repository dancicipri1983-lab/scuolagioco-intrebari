# Ilustrații ScuolaGioco

Sloturi: hero, harta, povesti, biblie, aventuri, jocuri, concurs, misiuni, surpriza (WebP, ~1100 px lățime).
În aplicație (de la versiunea 10.0) sunt deja 3 variante pentru fiecare slot: `<slot>.webp`, `<slot>-2.webp`, `<slot>-3.webp`.
La fiecare deschidere a jocului, aplicația alege la întâmplare una dintre variante.

Pentru a ADĂUGA ilustrații noi fără APK nou:
1. Pune imaginea aici cu un nume nou, de exemplu `il/hero-4.webp` (doar litere mici, cifre și cratimă).
2. În pack.json adaugă numele (fără .webp) la lista slotului: "il": {"hero": ["hero-4"], "povesti": ["povesti-4", "povesti-5"]}.
3. Mărește "v" în pack.json. Telefoanele descarcă imaginile noi, le păstrează local și le adaugă la cele existente.

Sursa: ilustrații generate de utilizator cu ChatGPT. Harta de fundal (mapbg): Kenney Hexagon Pack, CC0.
