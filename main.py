import os, json, urllib.request, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = os.environ.get("TG_TOKEN", "")
LEAD = "https://start-blog-guide.spru.site/files/l-2c8e40.pdf"
GUIDE = "https://start-blog-guide.spru.site/files/g-7f3a91.pdf"
SITE = "https://start-blog-guide.spru.site/"

BTN = [[{"text": "Чек-лист «10 шагов» (PDF)", "callback_data": "lead"}],
       [{"text": "Гайд «СТАРТ» — 1 490 ₽", "callback_data": "buy"}],
       [{"text": "Открыть лендинг", "url": SITE}]]

WELCOME = ("<b>СТАРТ</b> — гайд по ведению блога от практика.\n\n"
           "Бесплатно: чек-лист «10 шагов до первой рекламы» — 12 страниц, по одному шагу в день.\n\n"
           "Нажми кнопку — пришлю PDF. Полный гайд (8 модулей + шаблоны) — 1 490 ₽, вопросы: @hair_kukla")


def api(method, payload=None):
    url = "https://api.telegram.org/bot%s/%s" % (TOKEN, method)
    data = urllib.parse.urlencode(payload).encode() if payload else None
    with urllib.request.urlopen(url, data, timeout=20) as r:
        return json.loads(r.read())


def send(chat_id, text, buttons=None):
    p = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": "true"}
    if buttons:
        p["reply_markup"] = json.dumps({"inline_keyboard": buttons}, ensure_ascii=False)
    return api("sendMessage", p)


def send_doc(chat_id, url, caption):
    return api("sendDocument", {"chat_id": str(chat_id), "caption": caption, "document": url})


def base_url(headers):
    h = {k.lower(): v for k, v in (headers or {}).items()}
    host = h.get("x-forwarded-host") or h.get("host") or ""
    proto = h.get("x-forwarded-proto") or "https"
    return "%s://%s" % (proto, host)


def on_event(body):
    body = body or {}
    msg = body.get("message") or {}
    chat_id = (msg.get("chat") or {}).get("id")
    text = (msg.get("text") or "").lower()
    if chat_id is not None:
        if text.startswith("/start") or text.startswith("/guide") or "чек" in text or "гайд" in text or "шаг" in text:
            send(chat_id, WELCOME, BTN)
        else:
            send(chat_id, "Нажми кнопку ниже — пришлю чек-лист. По гайду и разбору — @hair_kukla.", BTN)
    cb = body.get("callback_query") or {}
    if cb:
        cid = (cb.get("from") or {}).get("id")
        try:
            if cb.get("data") == "lead":
                send_doc(cid, LEAD, "Чек-лист «10 шагов до первой рекламы». Один шаг в день. Гайд «СТАРТ» — @hair_kukla.")
            elif cb.get("data") == "buy":
                send(cid, "Гайд «СТАРТ» — 1 490 ₽: 8 модулей, контент-план на 30 дней, 100 идей для Reels, шаблон медиакита, письма брендам, договор.\n\nОплата — по ссылке на лендинге, файлы пришлю сразу.", BTN)
        except Exception as e:
            send(cid, "Не получилось отправить файл — напишите @hair_kukla, пришлю лично.")


class H(BaseHTTPRequestHandler):
    def handle_req(self, raw):
        path = self.path.split("?")[0]
        if path == "/health":
            body = b"ok"
        elif path == "/setwebhook":
            url = base_url(dict(self.headers)) + "/tg"
            body = json.dumps(api("setWebhook", {"url": url, "allowed_updates": json.dumps(["message", "callback_query"])})).encode()
        else:
            try:
                on_event(json.loads(raw or "{}"))
            except Exception as e:
                body = json.dumps({"error": str(e)}).encode()
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            body = b'{"ok":true}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        self.handle_req(self.rfile.read(n).decode())

    def do_GET(self):
        self.handle_req("")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), H).serve_forever()
