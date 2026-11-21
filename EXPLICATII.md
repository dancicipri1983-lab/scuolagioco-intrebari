# Explicații „De ce?” / „Știai că?”

De la aplicația 10.3, fiecare întrebare din `b` poate avea o explicație scurtă, arătată copilului după răspuns
(la răspuns corect: „💡 Știai că? …”; la greșit, Pico o citește cu voce).

Format: `"bx": {"<limbă>": {"<materie>": ["explicație pentru rândul 0", "explicație pentru rândul 1", ...]}}`
- Lista are EXACT același număr de elemente ca `b.<limbă>.<materie>`, în aceeași ordine. Unde nu e explicație: `""`.
- Aceeași explicație în toate cele 8 limbi, la aceeași poziție.
- Maximum 300 de caractere (ideal 80–160), fără < > ` | și fără rând nou.
- Pe înțelesul copilului din clasa întrebării: o propoziție, maximum două, care spune DE CE răspunsul e corect sau un fapt interesant legat de el. Fără să repete doar întrebarea.
- Câmpul e ignorat de versiunile mai vechi ale aplicației, deci nu strică nimic.

Când adaugi întrebări noi la `b`, adaugă și explicațiile lor la `bx` (la sfârșitul listei), ca listele să rămână aliniate.
