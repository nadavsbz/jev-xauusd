# read-only incremental fetch (GetHistory only). No send/react/join/read-ack. Writes only to /workspace/t298b/tg/
import asyncio, json, sys
sys.path.insert(0, '/workspace/algotrade/tools')
from tg_common import connect, cfg
from telethon.tl.types import User
recs = [json.loads(l) for l in open('/workspace/algotrade/telegram/messages.jsonl')]
mx = max(r['id'] for r in recs if r['chat'] == 'group')
def sname(s):
    if s is None: return None
    if isinstance(s, User): return ' '.join(x for x in [s.first_name, s.last_name] if x)
    return getattr(s, 'title', None)
async def main():
    c = await connect()
    g = await c.get_entity(cfg['GROUP']); n = 0
    with open('/workspace/t298b/tg/refresh_messages.jsonl', 'w') as out:
        async for m in c.iter_messages(g, min_id=mx, limit=5000, wait_time=1, reverse=True):
            s = m.sender
            out.write(json.dumps(dict(chat='group', id=m.id, date=m.date.isoformat(), sender_username=getattr(s, 'username', None), sender_name=sname(s),
                      text=m.message or '', reply_to=getattr(m.reply_to, 'reply_to_msg_id', None) if m.reply_to else None,
                      media_type=type(m.media).__name__ if m.media else None, file_name=getattr(getattr(m, 'file', None), 'name', None)), ensure_ascii=False) + '\n'); n += 1
    print('fetched', n, 'after id', mx); await c.disconnect()
asyncio.run(asyncio.wait_for(main(), 600))
