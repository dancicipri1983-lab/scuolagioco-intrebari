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

# ---- povești ----
CH=['bubu','tina','zor','miri','olo','pip','lulu','bruno','kiki','tomo','gogu','rosi','lup','rufo','bambu','koko','stelina','rex','hubu','pingo','ella','leo','momo','ranu','otto','delfi','lento','lolo','ondi','gira','spini','scutel']
BG=['meadow','forest','night','sea','house','space','castle','snow','school']
AN=['','walkin','walkinr','jump','happy','dance','shake','spin','sad','fly','sleep','wave','hide']
import re
e2=[];ids=set()
EARS=['point','round','small','long','horn','tuft','antenna','hood','none','cat','mane','unicorn','elephant','leaf','antlers']
XP=['wings','tdragon','spots','whisk','tlong','snout','screen','bolts','tfox','beak','big','flip','teeth','tpuff','spikes','nose','shell','pig','tcurl','hair','snoutl','tlion','trunk','stripes','freckles','glasses','scarf','bow']
col=lambda v:isinstance(v,str) and re.fullmatch(r'#[0-9a-fA-F]{6}',v)
for cid,c in j.get('ch',{}).items():
    if not re.fullmatch(r'[a-z0-9]{2,16}',cid) or cid in CH: e2.append(f'personaj id invalid/rezervat: {cid}')
    if 'img' in c:
        import os
        if not re.fullmatch(r'[a-z0-9_-]{1,40}',c['img']) or not os.path.exists(f"img/{c['img']}.png"): e2.append(f"{cid}: img lipsă în img/{c.get('img')}.png")
    else:
        if not (col(c.get('col')) and col(c.get('bel'))) or any(k in c and not col(c[k]) for k in ('hc','mc','sc')): e2.append(f'{cid}: culori invalide (#rrggbb)')
        if c.get('ear') not in EARS: e2.append(f'{cid}: ear invalid')
        if any(x not in XP for x in c.get('x',[])) or len(c.get('x',[]))>8: e2.append(f'{cid}: x invalid')
    if set(c.get('n',{}))!=set(L) or set(c.get('k',{}))!=set(L): e2.append(f'{cid}: n și k trebuie în toate cele 8 limbi')
CH=CH+list(j.get('ch',{}).keys())
for s in j.get('st',[])+j.get('dz',[]):
    sid=s.get('id','?')
    if not re.fullmatch(r'[a-z0-9-]{1,30}',sid) or sid in ids: e2.append(f'poveste id invalid/duplicat: {sid}')
    ids.add(sid)
    if not re.fullmatch(r'\d{4}-\d\d-\d\d',s.get('from','')): e2.append(f'{sid}: from invalid')
    if s.get('ch') not in CH: e2.append(f'{sid}: ch invalid')
    if len(s.get('acc',''))>3: e2.append(f'{sid}: acc prea lung')
    if set(s.get('title',{}))!=set(L): e2.append(f'{sid}: title nu are toate limbile')
    if not 5<=len(s.get('sc',[]))<=20: e2.append(f'{sid}: 5-20 scene')
    for i,x in enumerate(s.get('sc',[])):
        if x.get('bg') not in BG: e2.append(f'{sid}.sc{i}: bg invalid')
        c=x.get('c',[])
        if not 1<=len(c)<=4 or any(a[0] not in CH or not isinstance(a[1],(int,float)) or a[2] not in AN for a in c): e2.append(f'{sid}.sc{i}: c invalid')
        if x.get('w') and x['w'] not in [a[0] for a in c]: e2.append(f'{sid}.sc{i}: w nu e în scenă')
        if set(x.get('t',{}))!=set(L) or any(any(ch in v for ch in '<>`') or len(v)>400 for v in x['t'].values()): e2.append(f'{sid}.sc{i}: t invalid')
        if x.get('fx','') not in ('','confetti','hearts','stars'): e2.append(f'{sid}.sc{i}: fx invalid')
        if x.get('q','') not in ('','mat','lang','log'): e2.append(f'{sid}.sc{i}: q invalid')
    qz=s.get('qz',{})
    for l in L:
        q=qz.get(l,[])
        if len(q)<3 or len(q)!=len(qz.get('en',[])): e2.append(f'{sid}: qz {l} lipsă/alt număr')
        for ln in q:
            p=ln.split('|')
            if len(p)!=6 or not p[0].isdigit() or len(set(p[2:]))!=4 or any(c in ln for c in '<>`'): e2.append(f'{sid}: qz {l} rând invalid: {ln}')
print('\n'.join(e2[:50]) if e2 else f"OK povești: {len(j.get('st',[]))} · povești ale zilei: {len(j.get('dz',[]))}")
sys.exit(1 if (err or e2) else 0)
