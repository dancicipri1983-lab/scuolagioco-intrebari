# Întrebări ScuolaGioco

`pack.json` – pachetul de întrebări descărcat zilnic de aplicația ScuolaGioco. Personaje: PERSONAJE.md · Voci: VOCI.md, generate cu `python3 gen_audio.py`.

Format: `b.<limbă>.<materie>` = listă de rânduri `clasa|întrebare|corect|greșit1|greșit2|greșit3`
(limbi: it, ro, en, es, fr, de, nb, pl · materii: sci, sto, geo, dig, ing). La fiecare pachet nou crește `v`.
Pachetul nou conține și întrebările vechi (se adaugă, nu se înlocuiesc).

## Aplicația
`apk/ScuolaGioco.apk` – ultima versiune (fără chei API). `version.json` – versiunea curentă: aplicațiile instalate verifică fișierul și anunță copiii când apare o versiune nouă.

## pv.json
Fișier mic cu versiunea pachetului, scris automat de validate.py. Telefoanele îl verifică la fiecare deschidere a jocului; dacă e mai nou, descarcă pack.json. Commit-ul trebuie să includă și pv.json (git add -A).
