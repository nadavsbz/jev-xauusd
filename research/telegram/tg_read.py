"""Read-only access to the developer's Telegram group with the user's session (telegram/*.session, git-ignored).
API_ID / API_HASH are read from the user's existing local .env (outside this repo) and never printed or saved.
Nothing is sent: only get_dialogs / iter_messages / download of documents.
Usage: python research/telegram/tg_read.py dialogs
       python research/telegram/tg_read.py dump <dialog_id> OUT_DIR"""
import asyncio, json, os, sys
from telethon import TelegramClient

ENV = r"D:\Claude\money\telegram\read messages\.env"
SESSION = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "telegram", "delta_session")


def env():
    e = {}
    for line in open(ENV, encoding="utf-8").read().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1); e[k.strip()] = v.strip().strip('"').strip("'")
    return e


async def main():
    e = env()
    async with TelegramClient(SESSION, int(e["API_ID"]), e["API_HASH"]) as c:
        if sys.argv[1] == "dialogs":
            async for d in c.iter_dialogs():
                if d.is_group or d.is_channel:
                    print(d.id, "|", d.name, "|", getattr(d.entity, "participants_count", ""), flush=True)
        elif sys.argv[1] == "dump":
            did, out = int(sys.argv[2]), sys.argv[3]; os.makedirs(out, exist_ok=True)
            rows = []
            async for m in c.iter_messages(did, limit=None):
                r = {"id": m.id, "date": m.date.isoformat(), "from": m.sender_id, "reply_to": m.reply_to_msg_id,
                     "text": m.message or "", "file": None}
                if m.document and m.file and m.file.name and m.file.name.lower().endswith((".set", ".pdf", ".txt", ".docx", ".ini", ".zip")):
                    p = await m.download_media(file=os.path.join(out, "files", f"{m.id}_{m.file.name}"))
                    r["file"] = os.path.basename(p) if p else None
                rows.append(r)
            json.dump(rows, open(os.path.join(out, "messages.json"), "w", encoding="utf-8"), ensure_ascii=False)
            print("messages:", len(rows), "files:", sum(1 for r in rows if r["file"]))

asyncio.run(main())
