"""Verifică pack.json înainte de publicare. Rulează: python3 validate.py"""
import json,sys
L=['it','ro','en','es','fr','de','nb','pl'];SUBJ=['sci','sto','geo','dig']
j=json.load(open('pack.json'));err=[]
if not (isinstance(j.get('v'),int) and j['v']>0): err.append('v invalid')
for l in L:
    if l not in j['b']: err.append('lipsește limba '+l);continue
    for k in SUBJ:
        lines=j['b'][l].get(k,[]);seen=set()
        if len(lines)!=len(j['b']['en'].get(k,[])): err.append(f'{l}.{k}: alt număr de rânduri decât en')
        for i,ln in enumerate(lines):
            p=ln.split('|')
            if len(p)!=6: err.append(f'{l}.{k}[{i}] nu are 6 câmpuri: {ln}');continue
            if not p[0].isdigit() or not 1<=int(p[0])<=13: err.append(f'{l}.{k}[{i}] clasă greșită')
            if p[0]!=j['b']['en'][k][i].split('|')[0]: err.append(f'{l}.{k}[{i}] clasa diferă de en')
            if len(set(x.strip().lower() for x in p[2:]))!=4 or any(not x.strip() for x in p): err.append(f'{l}.{k}[{i}] variante goale/duplicate')
            if any(c in ln for c in '<>`\n'): err.append(f'{l}.{k}[{i}] caractere interzise')
            if p[1].lower() in seen: err.append(f'{l}.{k}[{i}] întrebare duplicată')
            seen.add(p[1].lower())
print('\n'.join(err[:50]) if err else f"OK v{j['v']} · {sum(len(x) for x in j['b']['en'].values())} întrebări/limbă")
sys.exit(1 if err else 0)
