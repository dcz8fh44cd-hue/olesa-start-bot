// Telegram webhook for @olesa_start_guide_bot — Cloudflare Workers
// Secret binding: TG_TOKEN (bot token from BotFather)
// Secret binding: YK_SHOP_ID, YK_SECRET_KEY (опционально, для автовыдачи после оплаты ЮKassa)

const LEAD = "https://start-blog-guide.spru.site/files/l-2c8e40.pdf";
const GUIDE = "https://start-blog-guide.spru.site/files/g-7f3a91.pdf";
const SITE = "https://start-blog-guide.spru.site/";

let TOKEN = "";

const BTN = [
  [{ text: "Чек-лист «10 шагов» (PDF)", callback_data: "lead" }],
  [{ text: "Гайд «СТАРТ» — 1 490 ₽", callback_data: "buy" }],
  [{ text: "Открыть лендинг", url: SITE }],
];

const SITE_BTN = [[{ text: "Открыть лендинг", url: SITE }]];

const WELCOME =
  "<b>СТАРТ</b> — гайд по ведению блога от практика.\n\n" +
  "Бесплатно: чек-лист «10 шагов до первой рекламы» — 12 страниц, по одному шагу в день.\n\n" +
  "Нажми кнопку — пришлю PDF. Полный гайд (8 модулей + шаблоны) — 1 490 ₽, вопросы: @hair_kukla";

async function api(method, payload) {
  const res = await fetch(`https://api.telegram.org/bot${TOKEN}/${method}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

async function send(chatId, text, buttons) {
  const payload = { chat_id: chatId, text, parse_mode: "HTML", disable_web_page_preview: true };
  if (buttons) payload.reply_markup = { inline_keyboard: buttons };
  return api("sendMessage", payload);
}

async function sendDoc(chatId, caption, url) {
  return api("sendDocument", { chat_id: chatId, caption, document: url });
}

export default {
  async fetch(request, env) {
    TOKEN = env.TG_TOKEN || "";
    const url = new URL(request.url);

    if (url.pathname === "/health") {
      return new Response(TOKEN ? "ok" : "no-token");
    }

    if (url.pathname === "/setwebhook") {
      const r = await api("setWebhook", {
        url: url.origin + "/tg",
        allowed_updates: JSON.stringify(["message", "callback_query"]),
      });
      return new Response(JSON.stringify(r));
    }

    if (url.pathname === "/delwebhook") {
      return new Response(JSON.stringify(await api("deleteWebhook", { drop_pending_updates: true })));
    }

    if (url.pathname === "/setcommands") {
      const r = await api("setMyCommands", {
        commands: [
          { command: "start", description: "Чек-лист и гайд" },
          { command: "guide", description: "Гайд «СТАРТ»" },
          { command: "help", description: "Что умеет бот" },
        ],
      });
      return new Response(JSON.stringify(r));
    }

    if (url.pathname !== "/tg") return new Response("not found", { status: 404 });

    let body = {};
    try {
      body = await request.json();
    } catch (e) {}

    const msg = body.message || {};
    const chatId = msg.chat && msg.chat.id;
    const text = (msg.text || "").toLowerCase();
    if (chatId !== undefined) {
      if (text.startsWith("/start")) {
        await send(chatId, WELCOME, BTN);
      } else if (text.startsWith("/guide") || text.includes("гайд")) {
        await send(
          chatId,
          "Гайд «СТАРТ» — 8 модулей: от профиля до первой рекламы, контент-план на 30 дней, 100 идей для Reels, шаблон медиакита, письма брендам и договор.\n\nЦена — 1 490 ₽. Нажми кнопку ниже, оплата и файлы на лендинге.",
          BTN
        );
      } else if (text.startsWith("/help") || text.includes("помощ") || text.includes("как")) {
        await send(
          chatId,
          "Я бот СТАРТ. Команды:\n/start — приветствие и чек-лист\n/guide — про гайд\n/help — эта справка\n\nЕщё есть бесплатный чек-лист «10 шагов до первой рекламы» и гай� «СТАРТ» за 1 490 ₽.",
          BTN
        );
      } else if (text.includes("чек") || text.includes("шаг")) {
        await send(chatId, "Чек-лист «10 шагов до первой рекламы» — 12 страниц, по одному шагу в день. Нажми кнопку, пришлю PDF.", BTN);
      } else {
        await send(chatId, "Нажми кнопку ниже — пришлю чек-лист. По гай�у и разбору — @hair_kukla.", BTN);
      }
    }

    const cb = body.callback_query || {};
    if (cb && cb.from) {
      const id = cb.from.id;
      if (cb.data === "lead") {
        await sendDoc(id, "Чек-лист «10 шагов до первой рекламы». Один шаг в день. Гай� «СТАРТ» — @hair_kukla.", LEAD);
      } else if (cb.data === "buy") {
        await send(
          id,
          "Гайд «СТАРТ» — 1 490 ₽: 8 модулей, контент-план на 30 дней, 100 идей для Reels, шаблон медиакита, письма брендам, договор.\n\nОплата — по ссылке на лендинге, файԻы пришлю сразу.",
          BTN
        );
      }
    }
    return new Response(JSON.stringify({ ok: true }));
  },
};
