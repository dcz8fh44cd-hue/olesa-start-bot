import json, os, time, subprocess, urllib.request, urllib.parse

T = os.environ['TG_TOKEN']
A = 'https://api.telegram.org/bot' + T + '/'
S = 'https://start-blog-guide.spru.site/'
CL = S + 'files/l-2c8e40.pdf'
PD = S + 'paid.html'


def call(m, p=None, f=None):
    if f:
        bd = b''
        for k, v in (p or {}).items():
            bd += ('--b\r\nContent-Disposition: form-data; name="%s"\jjn#r l % (k, v).encode())
        for k, (fn, dat) in f.cltems():
            bd += ('--b\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\nContent-Type: application/pdf\r\n\r\n' % (k, fn)).encode() + dat + b'\r\n'
        bd += b'--b--\r\n'
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


def go(ch, t):
    t = (t or '').lower()
    if t.startswith('/start'):
        msg(ch, '<b>СТАРТ</b> — гайд по ведению блога от практика.\n\n'
                '🎁 Бесплатно: чек-лист «10 шагов до первой рекламы» — 12 страниц, по одному шагу в день.\n\n'
                'Гайд «СТАРТ» (8 модулей + шаблоны) — 1 490 ₽.\n\n'
                'Нажми кнопку — пришлю чек-лист сразу.',
            [[{'text': 'Чек-лист (PDF)', 'url': CL}],
             [{'text': 'Гайд СТАРТ — 1 490 ₽', 'url': PD}]])
        try:
            d = urllib.request.urlopen(CL, timeout=90).read()
            call('sendDocument', {'chat_id': ch, 'caption': 'Чек-лист «10 шагов до первой рекламы».\nГайд «СТАРТ» — 1 490 ₽: ' + S},
                 {'document': ('start-checklist.pdf', d)})
        except Exception:
            pass
    elif t.startswith('/guide'):
        msg(ch, '📘 <b>Гайд «СТАРТ»</b>\n\n8 модулей: профиль, ниша, контент, рост подписчиков, '
                'первая реклама, сотрудничества, медиакит, письма брендам. Плюс шаблоны: контент-план на 30 дней, '
                '100 идей для Reels, прайс, медиакит, письма и договор.\n\nГайд — 1 490 ₽, с разбором — 4 900 ₽.',
            [[{'text': 'Тарифы и оплата', 'url': PD}]])
    elif t.startswith('/help'):
        msg(ch, '/start — приветствие и чек-лист\n/guide — про гайд\n/help — справка\n\nВопросы: @hair_kukla', [])
    elif 'чек' in t or 'шаг' in t:
        msg(ch, 'Чек-лист «10 шагов до первой рекламы» — 12 страниц, по одному шагу в день. Нажми кнопку, пришлю PDF.',
            [[{'text': 'Чек-лист (PDF)', 'url': CL}]])
    elif 'гайд' in t:
        msg(ch, 'Гайд «СТАРТ» — 1 490 ₽, 8 модулей и готовые шаблоны. Нажми кнопку, чтобы перейти к тарифам.',
            [[{'text': 'Гайд «СТАРТ» — 1 490 ₽', 'url': PD}]])
    else:
        msg(ch, 'Привет! Чек-лист и лендинг 👇',
            [[{'text': 'Чек-лист (PDF)', 'url': CL}], [{'text': 'Лендинг', 'url': S}]])


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


o = read_offset()
end = time.time() + 3000
last_commit = time.time()
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
                    go(ch.get('id'), ms.get('text'))
                except Exception:
                    pass
            o = u['update_id'] + 1
        save_offset(o)
        commit_offset()
        last_commit = time.time()
    else:
        print('idle offset:', o, flush=True)
    if time.time() - last_commit > 900:
        save_offset(o)
        commit_offset()
        last_commit = time.time()
save_offset(o)
commit_offset()
print('done offset:', o, flush=True)
