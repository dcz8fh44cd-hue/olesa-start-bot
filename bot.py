import json,os,time,urllib.request,urllib.parse
T=os.environ['TG_TOKEN'];A='https://api.telegram.org/bot'+T+'/'
S='https://start-blog-guide.spru.site/';CL=S+'files/l-2c8e40.pdf';PD=S+'paid.html'
def call(m,p=None,f=None):
    if f:
        bd=b''
        for k,v in (p or {}).items():
            bd+=('--b\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n'%(k,v)).encode()
        for k,(fn,dat) in f.items():
            bd+=('--b\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\nContent-Type: application/pdf\r\n\r\n'%(k,fn)).encode()+dat+b'\r\n'
        bd+=b'--b--\r\n'
        r=urllib.request.Request(A+m,data=bd,headers={'Content-Type':'multipart/form-data; boundary=--b'})
    else:
        r=urllib.request.Request(A+m,data=urllib.parse.urlencode(p or {}).encode())
    try: return json.loads(urllib.request.urlopen(r,timeout=90).read().decode())
    except Exception: return {'ok':False}
def msg(ch,t,kb):
    p={'chat_id':ch,'text':t,'parse_mode':'HTML'}
    if kb: p['reply_markup']=json.dumps({'inline_keyboard':kb})
    return call('sendMessage',p)
def go(ch,t):
    t=(t or '').lower()
    if t.startswith('/start'):
        msg(ch,'<b>СТАРТ</b> — гайд по ведению блога.\n\n🎁 Бесплатный чек-лист «10 шагов до первой рекламы».\n\nГайд — 1 490 ₽.',[[{'text':'Чек-лист (PDF)','url':CL}],[{'text':'Гайд 1 490 ₽','url':PD}]])
        try:
            d=urllib.request.urlopen(CL,timeout=90).read()
            call('sendDocument',{'chat_id':ch,'caption':'Чек-лист «10 шагов до первой рекламы».\nГайд «СТАРТ» — 1 490 ₽: '+S},{'document':('start-checklist.pdf',d)})
        except Exception: pass
    elif t.startswith('/guide'):
        msg(ch,'📘 <b>Гайд «СТАРТ»</b>\n\n8 модулей + шаблоны.\n\nГайд — 1 490 ₽, с разбором — 4 900 ₽.',[[{'text':'Тарифы','url':PD}]])
    elif t.startswith('/help'):
        msg(ch,'/start — чек-лист\n/guide — про гайд\n/help — справка\n\n@hair_kukla',[])
    else:
        msg(ch,'Привет! Чек-лист и лендинг 👇',[[{'text':'Чек-лист','url':CL}],[{'text':'Лендинг','url':S}]])
o=-1
try: o=int(open('offset.txt').read().strip())
except Exception: pass
end=time.time()+220
while time.time()<end:
    r=call('getUpdates',{'timeout':30,'offset':o})
    for u in r.get('result',[]):
        ms=u.get('message') or {};ch=ms.get('chat') or {}
        if ch.get('type')=='private':
            try: go(ch.get('id'),ms.get('text'))
            except Exception: pass
        o=u['update_id']+1
    open('offset.txt','w').write(str(o))
