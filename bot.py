import json,os,subprocess,time,urllib.request,urllib.parse
T=os.environ['TG_TOKEN']
A='https://api.telegram.org/bot'+T+'/'
S='https://start-blog-guide.spru.site/'
CL=S+'files/l-2c8e40.pdf'
PD=S+'paid.html'
def call(m,p=None,f=None):
 u=A+m
 if f:
  bd=b''
  for k,v in (p or {}).items():
   bd+=('--b\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n'%(k,v)).encode()
  for k,(fn,dat) in f.items():
   bd+=('--b\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\nContent-Type: application/pdf\r\n\r\n'%(k,fn)).encode()+dat+b'\r\n'
  bd+=b'--b--\r\n'
  r=urllib.request.Request(u,data=bd,headers={'Content-Type':'multipart/form-data; boundary=--b'})
 else:
  r=urllib.request.Request(u,data=urllib.parse.urlencode(p or {}).encode())
 try:
  return json.loads(urllib.request.urlopen(r,timeout=90).read().decode())
 except Exception as e:
  return {'ok':False,'err':str(e)}
def msg(c,t,kb=None):
 p={'chat_id':c,'text':t,'parse_mode':'HTML'}
 if kb: p['reply_markup']=json.dumps({'inline_keyboard':kb})
 return call('sendMessage',p)
def go(c,t):
 t=(t or '').lower()
 if t.startswith('/start'):
  msg(c,'👋 Привет! Это <b>СТАРТ</b> — гайд по ведению блога.\n\n🎁 Бесплатно — чек-лист «10 шагов до первой рекламы».\n\nГай� «СТАРТ» — 1 490 ₽.',[[{'text':'🎁 Чек-лист (PDF)','url':CL}],[{'text':'Гайд — 1 490 ₽','url':PD}]])
  d=urllib.request.urlopen(CL,timeout=90).read()
  call('sendDocument',{'chat_id':c,'caption':'Чек-лист «10 шагов до первой рекламы».\nГайд «СТАРТ» (8 модулей + шаблоны) — 1 490 ₽: '+S},{'document':('start-10-shagov.pdf',d)})
 elif t.startswith('/guide'):
  msg(c,'📘 <b>Гай� «СТАРТ»</b>\n\n8 модулей + контент-план на 30 дней, 100 идей для Reels, медиакит, письма брендам, договор.\n\nГайд — 1 490 ₽, с разбором — 4 900 ₽, полное сопровождение — 8 900 ₽.',[[{'text':'Тарифы','url':PD}]])
 elif t.startswith('/help'):
  msg(c,'/start — чек-лист\n/guide — про гайд\n/help — справка\n\nВопросы: @hair_kukla')
 elif t:
  msg(c,'Привет! Чек-лист и лендинг гайда 👇',[[{'text':'🎁 Чек-лист','url':CL}],[{'text':'Лендинг','url':S}]])
def push(o):
 open('offset.txt','w').write(str(o))
 subprocess.run(['git','config','user.email','bot@local'],check=False)
 subprocess.run(['git','config','user.name','start-bot'],check=False)
 subprocess.run(['git','add','offset.txt'],check=False)
 subprocess.run(['git','commit','-m','offset '+str(o)],check=False)
 subprocess.run(['git','push','origin','HEAD'],check=False)
o=-1
try: o=int(open('offset.txt').read().strip())
except Exception: pass
prev=None
end=time.time()+230
while time.time()<end:
 r=call('getUpdates',{'timeout':30,'offset':o})
 for u in r.get('result',[]):
  m=u.get('message') or {}
  ch=m.get('chat') or {}
  if ch.get('type')=='private':
   try: go(ch.get('id'),m.get('text'))
   except Exception as e: print('e',e)
  o=u['update_id']+1
 if o!=prev:
  try: push(o)
  except Exception as e: print('git',e)
 prev=o
