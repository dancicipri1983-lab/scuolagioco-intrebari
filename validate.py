"""Verifică pack.json înainte de publicare. Rulează: python3 validate.py"""
import json,sys
L=['it','ro','en','es','fr','de','nb','pl'];SUBJ=['sci','sto','geo','dig','rel','relo','relc']
j=json.load(open('pack.json'));err=[]
import re as _re
BASE=['mat','ita','rom','log','ing','sci','sto','geo','dig','inf','eco','rel']
for sid,sj in j.get('sj',{}).items():
    if not _re.fullmatch(r'[a-z]{3,10}',sid) or sid in BASE: err.append(f'materie id invalid/rezervat: {sid}')
    if not sj.get('ic') or len(sj['ic'])>4 or _re.search(r'[A-Za-z0-9<>]',sj['ic']): err.append(f'{sid}: ic trebuie să fie 1 emoji')
    if not _re.fullmatch(r'#[0-9a-fA-F]{6}',sj.get('col','')): err.append(f'{sid}: col #rrggbb')
    if not isinstance(sj.get('min'),int) or not 0<=sj['min']<=13: err.append(f'{sid}: min 0-13')
    if set(sj.get('n',{}))!=set(['it','ro','en','es','fr','de','nb','pl']): err.append(f'{sid}: n în toate cele 8 limbi')
SUBJ=SUBJ+list(j.get('sj',{}).keys())+['ing']+[k for k in j['b'].get('en',{}) if k.startswith('t_')]+['t_'+x for x in j.get('tm',{})]
for tid,tm in j.get('tm',{}).items():
    if not _re.fullmatch(r'[a-z]{3,12}',tid): err.append(f'temă id invalid: {tid}')
    if not tm.get('ic') or len(tm['ic'])>4 or _re.search(r'[A-Za-z0-9<>]',tm['ic']): err.append(f'temă {tid}: ic = 1 emoji')
    if set(tm.get('n',{}))!=set(['it','ro','en','es','fr','de','nb','pl']): err.append(f'temă {tid}: n în 8 limbi')
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
CH=['bubu','tina','zor','miri','olo','pip','lulu','bruno','kiki','tomo','gogu','rosi','lup','rufo','bambu','koko','stelina','rex','hubu','pingo','ella','leo','momo','ranu','otto','delfi','lento','lolo','ondi','gira','spini','scutel','batran','batrana','barbat','femeie','inger','prunc','porumbel','oita','camila','magar','balena','bou']
BG=['meadow','forest','night','sea','house','space','castle','snow','school','desert']
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
for s in j.get('st',[])+j.get('dz',[])+j.get('bz',[])+j.get('av',[]):
    sid=s.get('id','?')
    if not re.fullmatch(r'[a-z0-9-]{1,30}',sid) or sid in ids: e2.append(f'poveste id invalid/duplicat: {sid}')
    ids.add(sid)
    if not re.fullmatch(r'\d{4}-\d\d-\d\d',s.get('from','')): e2.append(f'{sid}: from invalid')
    if s.get('ch') not in CH: e2.append(f'{sid}: ch invalid')
    if len(s.get('acc',''))>3: e2.append(f'{sid}: acc prea lung')
    if set(s.get('title',{}))!=set(L): e2.append(f'{sid}: title nu are toate limbile')
    if not 5<=len(s.get('sc',[]))<=30: e2.append(f'{sid}: 5-30 scene')
    if s in j.get('av',[]) and not any(x.get('end') for x in s.get('sc',[])): e2.append(f'{sid}: aventura are nevoie de cel puțin o scenă cu end:true')
    for i,x in enumerate(s.get('sc',[])):
        if x.get('bg') not in BG: e2.append(f'{sid}.sc{i}: bg invalid')
        c=x.get('c',[])
        if not 1<=len(c)<=4 or any(a[0] not in CH or not isinstance(a[1],(int,float)) or a[2] not in AN for a in c): e2.append(f'{sid}.sc{i}: c invalid')
        if x.get('w') and x['w'] not in [a[0] for a in c]: e2.append(f'{sid}.sc{i}: w nu e în scenă')
        if set(x.get('t',{}))!=set(L) or any(any(ch in v for ch in '<>`') or len(v)>400 for v in x['t'].values()): e2.append(f'{sid}.sc{i}: t invalid')
        if x.get('fx','') not in ('','confetti','hearts','stars'): e2.append(f'{sid}.sc{i}: fx invalid')
        if x.get('q','') not in ('','mat','lang','log','sci','geo','sto','ing','dig'): e2.append(f'{sid}.sc{i}: q invalid')
        for o in x.get('o',[]):
            if not isinstance(o.get('g'),int) or not 0<=o['g']<len(s['sc']) or set(o.get('t',{}))!=set(L): e2.append(f'{sid}.sc{i}: alegere invalidă (g index de scenă, t în 8 limbi)')
        if 'go' in x and (not isinstance(x['go'],int) or not 0<=x['go']<len(s['sc'])): e2.append(f'{sid}.sc{i}: go invalid')
    qz=s.get('qz',{})
    for l in L:
        q=qz.get(l,[])
        if (len(q)<3 and s not in j.get('av',[])) or len(q)!=len(qz.get('en',[])): e2.append(f'{sid}: qz {l} lipsă/alt număr')
        for ln in q:
            p=ln.split('|')
            if len(p)!=6 or not p[0].isdigit() or len(set(p[2:]))!=4 or any(c in ln for c in '<>`'): e2.append(f'{sid}: qz {l} rând invalid: {ln}')
print('\n'.join(e2[:50]) if e2 else f"OK povești: {len(j.get('st',[]))} · povești ale zilei: {len(j.get('dz',[]))}")
sys.exit(1 if (err or e2) else 0)
