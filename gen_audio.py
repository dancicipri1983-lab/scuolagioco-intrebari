"""Generează vocile poveștilor (Piper TTS, voci cu licență liberă) -> audio/<poveste>/<limbă>/<scenă>.mp3
Rulează: pip install piper-tts --break-system-packages ; python3 gen_audio.py   (necesită ffmpeg)"""
import json,os,subprocess,hashlib,urllib.request,sys
HF='https://huggingface.co/rhasspy/piper-voices/resolve/main/'
AUV=2  # versiunea vocilor (crește când se schimbă metoda de generare, ca telefoanele să descarce din nou)
CACHE=os.path.expanduser('~/.piper');os.makedirs(CACHE,exist_ok=True)
# voci pe limbă: (model, speaker) ; f = feminine, m = masculine ; prima voce f = narator
V={'ro':{'f':[],'m':[('ro_RO-mihai-medium',None)]},
   'it':{'f':[('it_IT-paola-medium',None),('it_IT-serena-medium',None)],'m':[]},
   'en':{'f':[('en_US-kristin-medium',None)],'m':[('en_US-joe-medium',None),('en_US-john-medium',None),('en_US-norman-medium',None)]},
   'es':{'f':[('es_ES-sharvard-medium',1)],'m':[('es_ES-davefx-medium',None),('es_ES-sharvard-medium',0)]},
   'fr':{'f':[('fr_FR-siwis-medium',None)],'m':[('fr_FR-mls-medium',2),('fr_FR-mls-medium',5)]},
   'de':{'f':[('de_DE-kerstin-medium',None)],'m':[('de_DE-thorsten-medium',None)]},
   'nb':{'f':[('no_NO-nvcc-medium',0),('no_NO-nvcc-medium',2)],'m':[('no_NO-talesyntese-medium',None),('no_NO-nvcc-medium',1)]},
   'pl':{'f':[('pl_PL-gosia-medium',None),('pl_PL-mc_speech-medium',None)],'m':[('pl_PL-darkman-medium',None)]}}
# personaj -> (gen, înălțime voce, viteză: >1 = mai rar)
CV={'bubu':('m',1.25,1),'tina':('f',1.12,1),'zor':('m',1.08,.95),'miri':('f',1.25,.95),'olo':('m',.92,1.08),'pip':('m',1.3,.95),'lulu':('f',1.3,.9),
 'bruno':('m',.85,1.05),'kiki':('m',1.35,1.05),'tomo':('m',.88,1.2),'gogu':('m',1.2,.95),'rosi':('f',1.2,1),'lup':('m',.8,1.05),
 'rufo':('m',1.1,1),'bambu':('m',.9,1.1),'koko':('f',1.1,1.1),'stelina':('f',1.3,1),'rex':('m',.8,1),'hubu':('f',.95,1.05),'pingo':('m',1.3,.95),
 'ella':('f',.95,1.05),'leo':('m',1.15,1),'momo':('m',1.35,.9),'ranu':('f',1.3,.95),'otto':('m',1.0,.95),'delfi':('f',1.25,1),'lento':('m',.85,1.3),
 'batran':('m',.92,1.1),'batrana':('f',.95,1.1),'barbat':('m',1.0,1),'femeie':('f',1.0,1),'inger':('f',1.15,1.05),'prunc':('f',1.2,1),'porumbel':('f',1.15,1),'oita':('f',1.15,1),'camila':('m',.95,1.05),'magar':('m',1.05,1),'balena':('m',.88,1.1),'bou':('m',.86,1.1),
 'lolo':('f',1.1,1),'ondi':('f',1.2,1),'gira':('f',1.0,1.05),'spini':('m',1.3,1),'scutel':('m',.9,1.15)}
def model(name):
    l,rest=name.split('_',1);c=name.split('-')[0];n=name.split('-')[1];q=name.split('-')[2]
    p=os.path.join(CACHE,name+'.onnx')
    for ext in ('.onnx','.onnx.json'):
        if not os.path.exists(p.replace('.onnx',ext)):
            print('descarc',name+ext);urllib.request.urlretrieve(f'{HF}{l}/{c}/{n}/{q}/{name}{ext}',p.replace('.onnx',ext))
    return p
def voice_for(lang,who,chars):
    vs=V[lang]
    if not who: g,pit,spd=('f',1.0,1.05)
    else:
        c=chars.get(who,{});vv=c.get('v') if isinstance(c,dict) else None
        g,pit,spd=(vv.get('g','f'),float(vv.get('p',1.0)),float(vv.get('s',1.0))) if vv else CV.get(who,('f' if int(hashlib.md5(who.encode()).hexdigest(),16)%2 else 'm',1.1,1))
    lst=vs[g] or vs['m' if g=='f' else 'f']
    if not vs[g]: pit*=1.22 if g=='f' else .85
    k=0 if not who else int(hashlib.md5(who.encode()).hexdigest(),16)%len(lst)
    if who and len(lst)>1 and lst[k]==lst[0] and g=='f': k=1  # personajele feminine să nu aibă vocea naratorului
    return lst[k],pit,spd
def synth(text,lang,who,chars,out):
    (m,spk),pit,spd=voice_for(lang,who,chars);os.makedirs(os.path.dirname(out),exist_ok=True)
    cmd=['piper','-m',model(m),'-f','/tmp/_a.wav','--length-scale',str(round(spd,2))]
    if spk is not None: cmd+=['--speaker',str(spk)]
    subprocess.run(cmd,input=text.encode(),check=True,capture_output=True)
    sr=json.load(open(model(m).replace('.onnx','.onnx.json')))['audio']['sample_rate']
    pit=max(.86,min(1.18,pit))  # schimbări mici = cuvinte clare
    af=f'rubberband=pitch={pit:.3f}:pitchq=quality:formant=preserved,aresample=22050' if abs(pit-1)>.01 else 'aresample=22050'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i','/tmp/_a.wav','-af',af,'-ac','1','-c:a','libmp3lame','-b:a','48k',out],check=True)
if __name__=='__main__':
    j=json.load(open('pack.json'));force='--all' in sys.argv;chars=j.get('ch',{})
    for s in j.get('st',[])+j.get('dz',[])+j.get('bz',[]):
        if s.get('au') and not force: continue
        for lang in V:
            for i,sc in enumerate(s['sc']):
                t=sc['t'].get(lang)
                if t: synth(t,lang,sc.get('w',''),chars,f"audio/{s['id']}/{lang}/{i}.mp3")
            print('ok',s['id'],lang)
        s['au']=AUV
    json.dump(j,open('pack.json','w'),ensure_ascii=False,separators=(',',':'))
