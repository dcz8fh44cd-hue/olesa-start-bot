import json, os, time, subprocess
import urllib.request, urllib.parse
T = os.environ['TG_TOKEN']
A = 'https://api.telegram.org/bot' + T + '/'
S = 'https://start-blog-guide.spru.site/'
CL = S + 'files/l-2c8e40.pdf'
PD = S + 'paid.html'
TX = S + 'bottexts.json'
CRLF = bytes([13, 10])


def get(url):
    try:
        return urllib.request.urlopen(url, timeout=60).read()
    except Exception:
        return b''


def texts():
    try:
        return json.loads(get(TX).decode('utf-8'))
    except Exception:
        return {}


def call(m, p=None, f=None):
    if f:
        bd = b''
        for k, v in (p or {}).items():
            bd += b'--b' + CRLF + b'Content-Disposition: form-data; name="' + k.encode() + b'"' + CRLF + CRLF + v.encode() + CRLF
        for k, (fn, dat) in f.items():
            bd += b'--b' + CRLF + b'Content-Disposition: form-data; name="' + k.encode() + b'"; filename="' + fn.encode() + b'"' + CRLF + CRLF + dat + CRLF
        bd += b'--b--' + CRLF
        r = urllib.request.Request(A + m, data=bd, headers={'Content-Type': 'multipart/form-data; boundary=--b'})
    else:
        r = urllib.request.Request(A + m, data=urllib.parse.urlencode(p or {}).encode())
    try:
        return json.loads(urllib.request.urlopen(r, timeout=90).read().decode())
    except Exception:
        return {'ok': False}


def msg(ch, t, kb):
    p = {'chat_id': ch, 'text': t, 'parse_mode': 'HTML'}
    if kb:
        p['reply_markup'] = json.dumps({'inline_keyboard': kb})
    return call('sendMessage', p)


def go(ch, t, tx):
    t = (t or '').lower()
    kb_ch = [[{'text': 'Checklist (PDF)', 'url': CL}]]
    kb_g = [[{'text': 'Guide 1490 RUB', 'url': PD}]]
    if t.startswith('/start'):
        msg(ch, tx.get('start', ''), kb_ch + kb_g)
        try:
            d = get(CL)
            if d:
                call('sendDocument', {'chat_id': ch, 'caption': tx.get('caption', '')}, {'document': ('start-checklist.pdf', d)})
        except Exception:
            pass
    elif t.startswith('/guide'):
        msg(ch, tx.get('guide', ''), [[{'text': 'Taries', 'url': PD}]])
    elif t.startswith('/help'):
        msg(ch, tx.get('help', ''), [])
    else:
        msg(ch, tx.get('hello', ''), kb_ch + [[{'text': 'Landing', 'url': S}]])


def read_offset():
    try:
        return int(open('offset.txt').read().strip())
    except Exception:
        return -1


def save_offset(o):
    open('offset.txt', 'w').write(str(o))


def commit_offset():
    try:
        subprocess.run(['bash', 'commit_offset.sh'], timeout=120)
    except Exception:
        pass


tx = texts()
o = read_offset()
end = time.time() + 240
last = time.time()
while time.time() < end:
    try:
        r = call('getUpdates', {'timeout': 45, 'offset': o})
    except Exception:
        r = {}
    res = r.get('result', [])
    if res:
        print('updates:', len(res), 'offset:', o, flush=True)
        for u in res:
            ms = u.get('message') or {}
            ch = ms.get('chat') or {}
            if ch.get('type') == 'private':
                try:
                    go(ch.get('id'), ms.get('text'), tx)
                except Exception:
                    pass
            o = u['update_id'] + 1
        save_offset(o)
        commit_offset()
        last = time.time()
    else:
        print('idle offset:', o, flush=True)
    if time.time() - last > 120:
        save_offset(o)
        commit_offset()
        last = time.time()
save_offset(o)
commit_offset()
print('done offset:', o, flush=True)
