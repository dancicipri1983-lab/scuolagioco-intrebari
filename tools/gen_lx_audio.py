#!/usr/bin/env python3
"""
Generează pronunția (mp3) pentru „Învață o limbă”: fiecare cuvânt și propoziție din pack.json -> lx.u,
în toate cele 8 limbi, cu vocile Piper (licențe CC0 / CC-BY, vezi CREDITE.md).
Fișiere: audio/lx/<limbă>/<hash>.mp3 ; hash = FNV-1a 32 biți (hex, 8 caractere) al textului "<limbă>|<text>" (UTF-8).
La final marchează în pack.json fiecare unitate completă cu "au": 1 (aplicația folosește atunci înregistrările).

Folosire (din rădăcina depozitului):
  pip install --break-system-packages piper-tts
  python3 tools/gen_lx_audio.py            # descarcă vocile la prima rulare (~520 MB în ~/.cache/sg-piper)
"""
import json, os, subprocess, sys, tempfile, urllib.request, wave

VOICES = {  # limbă -> cale în rhasspy/piper-voices
    'ro': 'ro/ro_RO/mihai/medium/ro_RO-mihai-medium',
    'it': 'it/it_IT/paola/medium/it_IT-paola-medium',
    'en': 'en/en_GB/cori/medium/en_GB-cori-medium',
    'es': 'es/es_ES/sharvard/medium/es_ES-sharvard-medium',
    'fr': 'fr/fr_FR/siwis/medium/fr_FR-siwis-medium',
    'de': 'de/de_DE/thorsten/medium/de_DE-thorsten-medium',
    'nb': 'no/no_NO/talesyntese/medium/no_NO-talesyntese-medium',
    'pl': 'pl/pl_PL/gosia/medium/pl_PL-gosia-medium',
}
HF = 'https://huggingface.co/rhasspy/piper-voices/resolve/main/'
CACHE = os.path.expanduser(os.environ.get('SG_PIPER', '~/.cache/sg-piper'))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fnv(s):
    h = 0x811c9dc5
    for b in s.encode('utf-8'):
        h ^= b
        h = (h * 0x01000193) & 0xffffffff
    return '%08x' % h


def model(lang):
    p = VOICES[lang]
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, os.path.basename(p) + '.onnx')
    for ext in ('.onnx', '.onnx.json'):
        if not os.path.exists(f[:-5] + ext) or os.path.getsize(f[:-5] + ext) < 100:
            print('descarc', p + ext, flush=True)
            urllib.request.urlretrieve(HF + p + ext, f[:-5] + ext)
    return f


def main():
    from piper import PiperVoice
    pack = json.load(open(os.path.join(ROOT, 'pack.json'), encoding='utf-8'))
    units = (pack.get('lx') or {}).get('u', [])
    voices = {}
    made = 0
    for u in units:
        complete = True
        texts = [(l, w[l]) for w in u.get('w', []) for l in VOICES] + [(l, s[l]) for s in u.get('s', []) for l in VOICES]
        for lang, txt in texts:
            out = os.path.join(ROOT, 'audio', 'lx', lang, fnv(lang + '|' + txt) + '.mp3')
            if os.path.exists(out):
                continue
            if lang not in voices:
                voices[lang] = PiperVoice.load(model(lang))
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                wav = tmp.name
            try:
                with wave.open(wav, 'wb') as wf:
                    voices[lang].synthesize_wav(txt, wf)
                subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav,
                                '-af', 'silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,apad=pad_dur=0.12',
                                '-ac', '1', '-ar', '22050', '-b:a', '40k', out], check=True)
                made += 1
            except Exception as e:
                print('EROARE', lang, txt, e, file=sys.stderr)
                complete = False
            finally:
                os.unlink(wav)
        if complete:
            u['au'] = 1
    json.dump(pack, open(os.path.join(ROOT, 'pack.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f'gata: {made} fișiere noi; unități cu audio: {sum(1 for u in units if u.get("au"))}/{len(units)}')


if __name__ == '__main__':
    main()
