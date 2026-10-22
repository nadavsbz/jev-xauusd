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
        elif sys.argv[1] == "files":          # documents whose name matches each search word, newest first
            from telethon.tl.types import InputMessagesFilterDocument
            did, out, words = sys.argv[2], sys.argv[3], sys.argv[4:]; os.makedirs(out, exist_ok=True)
            have = set(os.listdir(out)); got = 0
            for w in words:
                async for m in c.iter_messages(did, search=w, filter=InputMessagesFilterDocument, limit=300):
                    if m.file and m.file.name and m.file.name.lower().endswith((".set", ".pdf", ".txt", ".zip")):
                        name = f"{m.id}_{m.file.name}"
                        if name not in have:
                            await m.download_media(file=os.path.join(out, name)); have.add(name); got += 1
                print(w, "done", flush=True)
            print("downloaded:", got)
        elif sys.argv[1] == "dump":
            a = sys.argv[2]; did = int(a) if a.lstrip("-").isdigit() else a; out = sys.argv[3]; os.makedirs(out, exist_ok=True)
            # written line by line (a long group can outlive any timeout); files already on disk are skipped
            fdir = os.path.join(out, "files"); os.makedirs(fdir, exist_ok=True); have = set(os.listdir(fdir))
            n = nf = 0
            with open(os.path.join(out, "messages.jsonl"), "w", encoding="utf-8") as fo:
                async for m in c.iter_messages(did, limit=None):
                    r = {"id": m.id, "date": m.date.isoformat(), "from": m.sender_id, "reply_to": m.reply_to_msg_id,
                         "text": m.message or "", "file": None}
                    if m.document and m.file and m.file.name and m.file.name.lower().endswith((".set", ".pdf", ".txt", ".docx", ".ini", ".zip")):
                        name = f"{m.id}_{m.file.name}"
                        if name not in have:
                            await m.download_media(file=os.path.join(fdir, name))
                        r["file"] = name; nf += 1
                    fo.write(json.dumps(r, ensure_ascii=False) + chr(10)); n += 1
                    if n % 2000 == 0:
                        fo.flush(); print("messages so far:", n, r["date"][:10], flush=True)
            print("messages:", n, "files:", nf, flush=True)

asyncio.run(main())
