"""Verificare cuvinte obscene în pack.json. Folosit de validate.py (și se poate rula singur)."""
import json, os, re, unicodedata
L8 = ['it','ro','en','es','fr','de','nb','pl']
_W = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cenzura.json'), encoding='utf-8'))

def norm(s):
    s = str(s).lower().replace('ß', 'ss')
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return s

def _compile(words):
    exact = set(); stems = []
    for w in words:
        w = norm(w)
        (stems.append(w[:-1]) if w.endswith('*') else exact.add(w))
    return exact, tuple(stems)
_C = {l: _compile(_W.get(l, [])) for l in L8}
_OK = [norm(x) for x in _W.get('_ok', [])]
_TOK = re.compile(r"[^\W\d_]+", re.U)

def bad(text, lang):
    ex, st = _C.get(lang, (set(), ()))
    n = norm(text)
    for ok in _OK: n = n.replace(ok, ' ')
    for t in _TOK.findall(n):
        if t in ex or (st and t.startswith(st)):
            return t
    return None

def scan(obj, lang=None, path='pack'):
    """întoarce listă (cale, limbă, cuvânt) pentru fiecare text cu probleme"""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out += scan(v, k if k in L8 else lang, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += scan(v, lang, f'{path}[{i}]')
    elif isinstance(obj, str) and lang:
        w = bad(obj, lang)
        if w: out.append((path, lang, w))
    return out

if __name__ == '__main__':
    import sys
    j = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'pack.json', encoding='utf-8'))
    r = scan(j)
    for p, l, w in r: print(f'{p} [{l}]: „{w}”')
    print('OK: niciun cuvânt obscen' if not r else f'{len(r)} texte cu probleme')
