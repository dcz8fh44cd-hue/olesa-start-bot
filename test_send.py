import os, json, urllib.request, urllib.parse
T = os.environ['TG_TOKEN']
A = 'https://api.telegram.org/bot' + T + '/'
p = {'chat_id': 7447975152, 'text': 'Test: bot works. Write /start in the bot chat.'}
r = urllib.request.Request(A + 'sendMessage', data=urllib.parse.urlencode(p).encode())
print(urllib.request.urlopen(r, timeout=60).read().decode())
