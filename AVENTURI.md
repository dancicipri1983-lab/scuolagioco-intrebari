# Aventuri ("av") și teme ("tm") – fără AI pe telefon

## Aventuri cu ramificații ("av" în pack.json)
Format ca poveștile (story1.py), plus:
- "gmin"/"gmax": clasele pentru care e aventura (0 = grădiniță … 13). Fă aventuri pentru grupe diferite: 0–2, 1–4, 3–6, 5–9, 8–13.
- Scene-alegere: "o": [{"t":{8 limbi},"g":indexScenă}, …] (2–3 variante). Copilul alege drumul; "g" = indexul scenei la care sare.
- "go": indexScenă = salt direct după scena aceasta (pentru a uni ramurile). "end": true = finalul (poate fi mai multe finaluri).
- Provocări pe drum: "q": "mat" | "lang" | "log" | "sci" | "geo" | "sto" | "ing" | "dig" — aplicația pune o problemă din acea materie, potrivită clasei copilului. Textul scenei doar cere ajutorul („Poarta se deschide doar dacă rezolvăm ghicitoarea!”), FĂRĂ numere sau răspunsuri concrete.
- 12–24 de scene, 2–3 alegeri, 3–5 provocări pe fiecare drum, 2–3 finaluri diferite (toate pozitive). "qz" e opțional (poate fi {}). La final copilul primește +10 ⭐.
- Teme: comori, spațiu, ocean, jungla, castel, munte, oraș, timp, dinozauri, laborator, cursă, detectiv…

## Teme ("tm" în pack.json)
`"tm": {"dino": {"ic":"🦖","n":{8 limbi},"gmin":1}}` + întrebările la `b.<limbă>.t_dino` (format obișnuit, 8 limbi, aceeași ordine). Minimum 20 de întrebări de la clase diferite. Teme atractive: dinozauri, spațiu, oceane, fotbal, animale, corpul uman, vulcani, roboți, castele, pirați, insecte, vremea, mâncare, munți, inventatori, muzică, olimpiade, Egiptul antic…
