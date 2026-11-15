"""Patch pentru assets/index.html din ScuolaGioco (APK 9.0):
1) Informatică variată la clasele mici: robotul cu personaje diferite, ziduri, start/țintă oriunde,
   „câți pași”, „unde ajunge”, „ce săgeată lipsește”, ordinea pașilor, „ce urmează”, „ce desenează”, dacă/altfel.
2) Muzică de fundal: 6 melodii care se schimbă (alta la fiecare pornire și după două repetări).
Rulare: python3 patch_inf_music.py cale/index.html"""
import sys,re
p=sys.argv[1];s=open(p,encoding='utf-8').read()
def rep(a,b):
    global s
    assert s.count(a)==1,('nu găsesc exact o dată',a[:80]); s=s.replace(a,b)

# ---------- 1. Informatică ----------
OLD_T=" const T={1:['robot','robot','loop'],2:['robot','loop','loop'],3:['robot','loop','bin'],4:['loop','bin','code1'],5:['bin','code1','loop','robot']};\n const tp=pick(T[c]||(c<=7?['bin','code1','code2','bits']:c<=9?['code2','code3','bits','hex','code1']:['code2','code3','code4','hex','bits']));\n switch(tp){"
NEW_T=""" const T={0:['robot','rwhere','order','pattern'],1:['robot','rwhere','order','pattern','draw','rsteps'],2:['robot','rsteps','rwhere','rmiss','order','pattern','draw','loop'],3:['robot','rmiss','rwhere','ifs','draw','loop','bin','pattern'],4:['robot','rmiss','ifs','loop','bin','code1','draw'],5:['bin','code1','loop','robot','ifs','rmiss']};
 const pool=T[c]||(c<=7?['bin','code1','code2','bits','ifs']:c<=9?['code2','code3','bits','hex','code1']:['code2','code3','code4','hex','bits']);
 let tp=pick(pool);if(pool.length>1&&tp===INF_LAST)tp=pick(pool.filter(x=>x!==INF_LAST));INF_LAST=tp;
 if(INF_X[tp])return INF_X[tp](c,l);
 switch(tp){"""
rep(OLD_T,NEW_T)

JS=r"""
/* ---------- Informatica: giochi vari (robot, ordine, sequenze, se/altrimenti) ---------- */
let INF_LAST='';
const RB_TH=[['🤖','⭐'],['🐰','🥕'],['🐝','🌻'],['🚀','🪐'],['🐶','🦴'],['🐢','🍓'],['🚗','🏁'],['🐭','🧀'],['🐧','🐟'],['🦊','🍇']];
const RB_D={'⬆️':[0,-1],'⬇️':[0,1],'⬅️':[-1,0],'➡️':[1,0]};const RB_A=Object.keys(RB_D);
function rbRun(G,prog){let [x,y]=G.s;for(const a of prog){const d=RB_D[a];x+=d[0];y+=d[1];if(x<0||y<0||x>=G.W||y>=G.H||G.ob.has(x+','+y))return {ok:false,end:null}}return {ok:x===G.g[0]&&y===G.g[1],end:[x,y]}}
function rbBfs(G){const k=(x,y)=>x+','+y;const prev={};prev[k(...G.s)]=null;const qq=[G.s];while(qq.length){const [x,y]=qq.shift();if(x===G.g[0]&&y===G.g[1]){const path=[];let cur=k(x,y);while(prev[cur]){path.unshift(prev[cur][1]);cur=prev[cur][0]}return path}
 for(const a of shuffle(RB_A.slice())){const d=RB_D[a],nx=x+d[0],ny=y+d[1],kk=k(nx,ny);if(nx<0||ny<0||nx>=G.W||ny>=G.H||G.ob.has(kk)||kk in prev)continue;prev[kk]=[k(x,y),a];qq.push([nx,ny])}}return null}
function rbGrid(c,minD){const W=c<=1?4:5,H=c<=0?2:c<=1?3:4,nob=c<=1?0:c<=3?R(1,2):R(2,4);
 for(let tr=0;tr<200;tr++){const s=[R(0,W-1),R(0,H-1)],g=[R(0,W-1),R(0,H-1)];if(Math.abs(s[0]-g[0])+Math.abs(s[1]-g[1])<(minD||2))continue;
  const ob=new Set();for(let i=0;i<nob*3&&ob.size<nob;i++){const o=[R(0,W-1),R(0,H-1)];if((o[0]===s[0]&&o[1]===s[1])||(o[0]===g[0]&&o[1]===g[1]))continue;ob.add(o[0]+','+o[1])}
  const th=pick(RB_TH);const G={W,H,s,g,ob,a:th[0],b:th[1]};const p=rbBfs(G);if(p&&p.length<=(c<=1?5:7)){G.path=p;return G}}
 const th=RB_TH[0];const G={W:3,H:2,s:[0,1],g:[2,0],ob:new Set(),a:th[0],b:th[1]};G.path=['⬆️','➡️','➡️'];return G}
function rbDraw(G,marks){let rows=[];for(let y=0;y<G.H;y++){let r='';for(let x=0;x<G.W;x++){const k=x+','+y;r+=(x===G.s[0]&&y===G.s[1])?G.a:(marks&&marks[k])?marks[k]:(G.g&&x===G.g[0]&&y===G.g[1]&&!marks)?G.b:G.ob.has(k)?'🧱':'⬜'}rows.push(r)}return rows.join('<br>')}
function rbMut(p){const v=R(0,4),q=p.slice();const i=R(0,q.length-1);
 if(v===0){q[i]=pick(RB_A.filter(a=>a!==q[i]))}else if(v===1&&q.length>1){q.splice(i,1)}else if(v===2){q.splice(i,0,pick(RB_A))}else if(v===3){const opp={'⬆️':'⬇️','⬇️':'⬆️','⬅️':'➡️','➡️':'⬅️'};q[i]=opp[q[i]]}else{q.reverse();if(q.join('')===p.join(''))q[i]=pick(RB_A.filter(a=>a!==q[i]))}return q}
function rbWrong(G,ans,n){const out=[];for(let t2=0;t2<80&&out.length<n;t2++){const w=rbMut(ans);const ws=w.join('');if(ws&&ws!==ans.join('')&&!out.includes(ws)&&!rbRun(G,w).ok)out.push(ws)}return out}
const INF_ORD=[['🌰','🌱','🌿','🌳'],['🥚','🐣','🐥','🐔'],['🐛','🛌','🦋'],['🌑','🌓','🌕'],['🧦','👟','🏃'],['🛁','🧼','🧴'],['🍞','🧈','🥪'],['⛅','🌧️','🌈'],['✉️','📮','📬'],['🎂','🕯️','🥳'],['🌧️','💧','🌷'],['🦷','🪥','😁'],['🥣','🍽️','🧽']];
const INF_PAT=['🔴','🔵','🟡','🟢','⭐','❤️','🌸','🍎','🐟','🔺'];
const INF_IF=[['🚦','🟢','🔴','🚶','✋'],['🌤️','☀️','🌧️','🕶️','☂️'],['🕐','🌞','🌙','⚽','😴'],['🌡️','🥵','🥶','🩳','🧥'],['🔔','🔊','🔇','🏃','📖'],['🐶','😋','😴','🦴','🛏️']];
const INF_X={
 robot(c){const G=rbGrid(c);const ans=G.path.join('');const w=rbWrong(G,G.path,4);
  const q=t('robot_q2',{a:G.a,b:G.b})+(G.ob.size?' '+t('rb_wall'):'');return Q(q,ans,w,{vis:rbDraw(G),visc:'emo',say:q})},
 rsteps(c){const G=rbGrid(Math.max(c,2));const n=G.path.length;const q=t('steps_q',{a:G.a,b:G.b});return Q(q,n,[n+1,n-1,n+2,n+3].filter(z=>z>0&&z!==n),{vis:rbDraw(G),visc:'emo',say:q,exp:G.path.join('')})},
 rwhere(c){const W=c<=1?4:5,H=c<=0?2:3;const th=pick(RB_TH);const G={W,H,s:[R(0,W-1),R(0,H-1)],g:null,ob:new Set(),a:th[0]};
  const fr=shuffle(['🍎','🍌','🍇','🍓','🍒','🍐','🥕','🧁']).slice(0,c<=0?3:4);let x=G.s[0],y=G.s[1],prog=[],tries=0;const L2=c<=0?2:c<=2?R(2,4):R(3,6);
  while(prog.length<L2&&tries++<100){const a=pick(RB_A),d=RB_D[a],nx=x+d[0],ny=y+d[1];if(nx<0||ny<0||nx>=W||ny>=H||(nx===G.s[0]&&ny===G.s[1]))continue;prog.push(a);x=nx;y=ny}
  const marks={};marks[x+','+y]=fr[0];const cells=[];for(let yy=0;yy<H;yy++)for(let xx=0;xx<W;xx++){const k=xx+','+yy;if(k!==x+','+y&&!(xx===G.s[0]&&yy===G.s[1]))cells.push(k)}
  shuffle(cells).slice(0,fr.length-1).forEach((k,i)=>marks[k]=fr[i+1]);const q=t('where_q',{a:G.a});
  return Q(q,fr[0],fr.slice(1),{vis:rbDraw(G,marks)+'<br><br>'+prog.join(''),visc:'emo',say:q})},
 rmiss(c){for(let tr=0;tr<40;tr++){const G=rbGrid(Math.max(c,2),3);if(G.path.length<3)continue;const i=R(0,G.path.length-1);const ok=RB_A.filter(a=>{const p=G.path.slice();p[i]=a;return rbRun(G,p).ok});
   if(ok.length!==1)continue;const shown=G.path.map((a,j)=>j===i?'❓':a).join('');const q=t('miss_q',{a:G.a,b:G.b});
   return Q(q,ok[0],RB_A.filter(a=>a!==ok[0]),{vis:rbDraw(G)+'<br><br>'+shown,visc:'emo',say:q})}return INF_X.robot(c)},
 order(c){const o=pick(INF_ORD);const ans=o.join(' ');const w=[];for(let k=0;k<30&&w.length<3;k++){const x=shuffle(o.slice()).join(' ');if(x!==ans&&!w.includes(x))w.push(x)}
  return Q(t('order_q'),ans,w,{visc:'emo',say:t('order_q')})},
 pattern(c){const kinds=c<=1?[[0,1],[0,0,1],[0,1,2]]:[[0,1,2],[0,0,1],[0,1,1],[0,1,2,1],[0,0,1,1]];const k=pick(kinds);const em=shuffle(INF_PAT.slice()).slice(0,4);
  const len=k.length*2+R(0,k.length-1);const seq=Array.from({length:len},(_,i)=>em[k[i%k.length]]);const ans=em[k[len%k.length]];
  return Q(t('next_q'),ans,em.filter(e=>e!==ans),{vis:seq.join('')+'❓',visc:'emo',say:t('next_q')})},
 draw(c){const n=R(2,c<=1?3:4);const a=pick(INF_PAT);let b=pick(INF_PAT.filter(x=>x!==a));const two=c>=2&&Math.random()<.6;const body=two?[a,b]:[a];
  const code=`${t('kw_repeat',{n})}:\n   ${body.join(' ')}`;const mk=(m,bd)=>Array(m).fill(bd.join('')).join('');const ans=mk(n,body);
  const w=[mk(n+1,body),mk(Math.max(1,n-1),body),two?mk(n,[b,a]):mk(n,[a,b]),two?mk(n,[a]):mk(n,[b])];
  return Q(t('draw_q'),ans,w,{vis:esc(code),visc:'code',say:t('draw_q')})},
 ifs(c){const f=pick(INF_IF);const yes=Math.random()<.5;const x=yes?f[1]:f[2];
  const code=`${t('kw_if')} ${f[0]} == ${f[1]}:\n   ${f[3]}\n${t('kw_else')}:\n   ${f[4]}`;const ans=yes?f[3]:f[4];
  const others=shuffle(INF_IF.filter(z=>z!==f).flatMap(z=>[z[3],z[4]])).slice(0,2);
  const q=t('if_q',{v:f[0],x});return Q(q,ans,[yes?f[4]:f[3]].concat(others),{vis:esc(code),visc:'code',say:q})}
};
const INF_UI={
it:{robot_q2:'Quali frecce portano {a} fino a {b}?',rb_wall:'Attenzione ai muri 🧱!',steps_q:'Quanti passi servono, al minimo, per portare {a} fino a {b}?',where_q:'Dove arriva {a} con questo programma?',miss_q:'Quale freccia manca per portare {a} fino a {b}?',order_q:"Qual è l'ordine giusto?",next_q:'Che cosa viene dopo?',draw_q:'Che cosa disegna questo programma?',if_q:'Che cosa fa il programma se {v} è {x}?',kw_if:'se',kw_else:'altrimenti'},
ro:{robot_q2:'Ce săgeți duc {a} până la {b}?',rb_wall:'Atenție la ziduri 🧱!',steps_q:'Câți pași trebuie, cel puțin, ca {a} să ajungă la {b}?',where_q:'Unde ajunge {a} cu acest program?',miss_q:'Ce săgeată lipsește ca {a} să ajungă la {b}?',order_q:'Care este ordinea corectă?',next_q:'Ce urmează?',draw_q:'Ce desenează acest program?',if_q:'Ce face programul dacă {v} este {x}?',kw_if:'dacă',kw_else:'altfel'},
en:{robot_q2:'Which arrows take {a} to {b}?',rb_wall:'Watch out for the walls 🧱!',steps_q:'What is the smallest number of steps to take {a} to {b}?',where_q:'Where does {a} end up with this program?',miss_q:'Which arrow is missing to take {a} to {b}?',order_q:'What is the right order?',next_q:'What comes next?',draw_q:'What does this program draw?',if_q:'What does the program do if {v} is {x}?',kw_if:'if',kw_else:'else'},
es:{robot_q2:'¿Qué flechas llevan a {a} hasta {b}?',rb_wall:'¡Cuidado con las paredes 🧱!',steps_q:'¿Cuántos pasos hacen falta, como mínimo, para llevar a {a} hasta {b}?',where_q:'¿Adónde llega {a} con este programa?',miss_q:'¿Qué flecha falta para llevar a {a} hasta {b}?',order_q:'¿Cuál es el orden correcto?',next_q:'¿Qué viene después?',draw_q:'¿Qué dibuja este programa?',if_q:'¿Qué hace el programa si {v} es {x}?',kw_if:'si',kw_else:'si no'},
fr:{robot_q2:"Quelles flèches mènent {a} jusqu'à {b} ?",rb_wall:'Attention aux murs 🧱 !',steps_q:"Combien de pas faut-il, au minimum, pour mener {a} jusqu'à {b} ?",where_q:'Où arrive {a} avec ce programme ?',miss_q:"Quelle flèche manque pour mener {a} jusqu'à {b} ?",order_q:'Quel est le bon ordre ?',next_q:"Qu'est-ce qui vient ensuite ?",draw_q:'Que dessine ce programme ?',if_q:'Que fait le programme si {v} est {x} ?',kw_if:'si',kw_else:'sinon'},
de:{robot_q2:'Welche Pfeile bringen {a} zu {b}?',rb_wall:'Achtung, Mauern 🧱!',steps_q:'Wie viele Schritte braucht {a} mindestens bis zu {b}?',where_q:'Wo landet {a} mit diesem Programm?',miss_q:'Welcher Pfeil fehlt, damit {a} zu {b} kommt?',order_q:'Was ist die richtige Reihenfolge?',next_q:'Was kommt als Nächstes?',draw_q:'Was zeichnet dieses Programm?',if_q:'Was macht das Programm, wenn {v} {x} ist?',kw_if:'wenn',kw_else:'sonst'},
nb:{robot_q2:'Hvilke piler fører {a} til {b}?',rb_wall:'Pass på veggene 🧱!',steps_q:'Hvor mange skritt trenger {a} minst for å komme til {b}?',where_q:'Hvor havner {a} med dette programmet?',miss_q:'Hvilken pil mangler for at {a} skal komme til {b}?',order_q:'Hva er riktig rekkefølge?',next_q:'Hva kommer etterpå?',draw_q:'Hva tegner dette programmet?',if_q:'Hva gjør programmet hvis {v} er {x}?',kw_if:'hvis',kw_else:'ellers'},
pl:{robot_q2:'Które strzałki prowadzą {a} do {b}?',rb_wall:'Uważaj na mury 🧱!',steps_q:'Ile najmniej kroków potrzeba, aby {a} dotarł do {b}?',where_q:'Gdzie dotrze {a} z tym programem?',miss_q:'Której strzałki brakuje, aby {a} dotarł do {b}?',order_q:'Jaka jest prawidłowa kolejność?',next_q:'Co będzie dalej?',draw_q:'Co rysuje ten program?',if_q:'Co zrobi program, jeśli {v} to {x}?',kw_if:'jeśli',kw_else:'w przeciwnym razie'}};
for(const k in INF_UI)if(LP[k]&&LP[k].ui)Object.assign(LP[k].ui,INF_UI[k]);
"""

# ---------- 2. Muzică ----------
OLD_M=s[s.index("let MUS={on:false,timer:null,step:0};"):s.index("function musicStop(){clearInterval(MUS.timer);MUS.on=false}")]
NEW_M=r"""let MUS={on:false,timer:null,step:0,m:0};
const MELS=[
 {n:[0,2,4,7,4,2,0,-1, 4,7,9,7,4,2,4,-1, 0,2,4,2,0,-3,0,-1, 7,9,7,4,2,4,0,-1],ms:280,w:'sine',b:523.25},
 {n:[0,4,7,4,7,4, 2,5,9,5,9,5, 0,4,7,12,7,4, 2,7,11,7,2,-1],ms:250,w:'triangle',b:523.25},
 {n:[7,7,9,7,4,-1,2,4, 5,5,7,5,2,-1,0,2, 4,4,5,4,0,-1,-3,0, 2,4,2,0,-1,-1,-1,-1],ms:230,w:'triangle',b:587.33},
 {n:[0,-1,4,-1,7,-1,9,7, 4,-1,2,-1,0,-1,-1,-1, 2,-1,4,-1,7,-1,4,2, 0,-1,-3,-1,0,-1,-1,-1],ms:320,w:'sine',b:493.88},
 {n:[0,0,4,4,7,7,4,-1, 5,5,9,9,7,7,4,-1, 2,2,5,5,4,4,0,-1, 2,4,2,-3,0,-1,0,-1],ms:210,w:'triangle',b:523.25},
 {n:[9,-1,12,9,7,-1,4,-1, 5,7,9,-1,7,-1,-1,-1, 9,-1,12,14,12,-1,9,7, 4,7,9,-1,9,-1,-1,-1],ms:260,w:'sine',b:440}];
function musPlay(){clearInterval(MUS.timer);const M=MELS[MUS.m%MELS.length];MUS.step=0;
 MUS.timer=setInterval(()=>{if(document.hidden||S.music===false)return;if(MUS.step>=M.n.length*2){MUS.m=(MUS.m+1)%MELS.length;musPlay();return}
  const n=M.n[MUS.step%M.n.length];MUS.step++;if(n<0)return;try{const tt=AC.currentTime;const f=M.b*Math.pow(2,n/12);const o=AC.createOscillator(),g=AC.createGain();o.type=M.w;o.frequency.value=f;g.gain.setValueAtTime(M.w==='sine'?.035:.03,tt);g.gain.exponentialRampToValueAtTime(.001,tt+.32);o.connect(g);g.connect(AC.destination);o.start(tt);o.stop(tt+.34);
  if(MUS.step%2===1){const o2=AC.createOscillator(),g2=AC.createGain();o2.type='triangle';o2.frequency.value=f/4;g2.gain.setValueAtTime(.03,tt);g2.gain.exponentialRampToValueAtTime(.001,tt+.4);o2.connect(g2);g2.connect(AC.destination);o2.start(tt);o2.stop(tt+.42)}}catch(e){}},M.ms)}
function musicStart(){if(MUS.on||S.music===false)return;try{AC=AC||new (window.AudioContext||window.webkitAudioContext)();if(AC.state==='suspended')AC.resume()}catch(e){return}MUS.on=true;
 MUS.m=((S.mel|0)+1)%MELS.length;S.mel=MUS.m;try{save()}catch(e){}musPlay()}
"""
rep(OLD_M,NEW_M)
rep("/* ---------- Musica ---------- */",JS+"\n/* ---------- Musica ---------- */")
open(p,'w',encoding='utf-8').write(s);print('ok')

# ---------- 3. Fără repetări între sesiuni (toate materiile) ----------
s=open(p,encoding='utf-8').read()
OLD_G="function genLocal(sid){let q,tries=0;do{const l=sess&&sess.fl!=null?sess.fl:Math.round(getLvl(sid));try{q=SM[sid].g(S.cls,l)}catch(e){q=null}tries++}while((!q||!q.opts||q.opts.length<2||(sess&&sess.used.has(q.q+(q.vis||''))))&&tries<25);if(!q)q=gMat(S.cls,1);q.sid=sid;return q}"
NEW_G="""const qKey=q=>String(q.q)+(q.vis||'');let QSEEN=null;
function qSeen(){if(!QSEEN)QSEEN=new Set(S.qSeen||[]);return QSEEN}
function qMark(q){const k=qKey(q).slice(0,80);const a=S.qSeen||(S.qSeen=[]);a.push(k);if(a.length>900)a.splice(0,a.length-900);QSEEN=null}
function genLocal(sid){let q,tries=0,best=null;const rs=qSeen();do{const l=sess&&sess.fl!=null?sess.fl:Math.round(getLvl(sid));try{q=SM[sid].g(S.cls,l)}catch(e){q=null}tries++;
 if(q&&q.opts&&q.opts.length>=2&&!(sess&&sess.used.has(qKey(q)))){if(!best)best=q;if(!rs.has(qKey(q).slice(0,80)))break}q=null}while(tries<40);
 q=q||best;if(!q)q=gMat(S.cls,1);q.sid=sid;qMark(q);return q}"""
assert s.count(OLD_G)==1;s=s.replace(OLD_G,NEW_G)
OLD_B="function fromBank(B,c,l){const tg=c+(l-1)*0.7;const sc=B.map(x=>({x,d:Math.abs(x.g-tg)+Math.random()*0.35})).sort((a,b)=>a.d-b.d);\n const it=pick(sc.slice(0,Math.min(16,sc.length))).x;"
NEW_B="""function fromBank(B,c,l){const tg=c+(l-1)*0.7;const sc=B.map(x=>({x,d:Math.abs(x.g-tg)+Math.random()*0.35})).sort((a,b)=>a.d-b.d);
 const rs=(typeof qSeen==='function')?qSeen():new Set();const near=sc.filter(o=>Math.abs(o.x.g-c)<=1.5);const win=near.length>=8?near:sc.slice(0,Math.min(30,sc.length));
 const un=o=>!rs.has((o.x.q+(o.x.vis||'')).slice(0,80));let fresh=win.filter(un);if(!fresh.length)fresh=sc.slice(0,40).filter(o=>un(o)&&Math.abs(o.x.g-c)<=2.5);const it=pick((fresh.length?fresh:win).slice(0,40)).x;"""
assert s.count(OLD_B)==1;s=s.replace(OLD_B,NEW_B)
open(p,'w',encoding='utf-8').write(s);print('ok anti-repetare')
s=open(p,encoding='utf-8').read()
a="function svMake(){const o=Object.assign({},S);delete o.duSeen;";assert s.count(a)==1
s=s.replace(a,"function svMake(){const o=Object.assign({},S);delete o.duSeen;delete o.qSeen;")
open(p,'w',encoding='utf-8').write(s);print('ok cod salvare')
