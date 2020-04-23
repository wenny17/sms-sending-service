import asyncio
import os
import json
import warnings

import aioredis
import trio
import trio_asyncio
from quart import request, websocket, jsonify
from quart_trio import QuartTrio
from dotenv import load_dotenv
from hypercorn.trio import serve
from hypercorn.config import Config as HyperConfig

from db import Database
from helpers import send_notification, get_quantity_of_completed_sms

warnings.filterwarnings("ignore")

load_dotenv()

app = QuartTrio(__name__)


LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
REDIS_URI = os.getenv("REDIS_URI")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
PHONES = os.getenv("PHONES").split(';') or '+389999999;+3877777777'


@app.before_serving
async def connect_db():
    asyncio._set_running_loop(asyncio.get_event_loop())
    redis = await trio_asyncio.run_asyncio(
        aioredis.create_redis_pool(
            REDIS_URI,
            password=REDIS_PASSWORD,
            encoding='utf-8',
        )
    )
    app.db = Database(redis)


@app.after_serving
async def close_db():
    app.db.redis.close()
    await trio_asyncio.run_asyncio(app.db.redis.wait_closed())


@app.route('/')
async def index():
    return await app.send_static_file("index.html")


@app.route('/send/', methods=['POST'])
async def get_message():
    form = await request.form
    message = form['text']
    res = await send_notification(message, PHONES)
    await trio_asyncio.run_asyncio(app.db.add_sms_mailing(
        res['id'], PHONES, message
    ))
    return jsonify({})


@app.websocket('/ws')
async def ws():
    while True:
        ids = await trio_asyncio.run_asyncio(app.db.list_sms_mailings())
        sms_mailings = await trio_asyncio.run_asyncio(
            app.db.get_sms_mailings(*ids)
        )
        response = {
            "msgType": "SMSMailingStatus",
            "SMSMailings": [
            ]
        }
        for sms in sms_mailings:
            delivered, failed = get_quantity_of_completed_sms(sms['phones'])
            response["SMSMailings"].append(
                {
                    "timestamp": sms['created_at'],
                    "SMSText": sms['text'],
                    "mailingId": str(sms['sms_id']),
                    "totalSMSAmount": sms['phones_count'],
                    "deliveredSMSAmount": delivered,
                    "failedSMSAmount": failed,
                }
            )
        await websocket.send(json.dumps(response))
        await trio.sleep(1)


async def run_server():
    async with trio_asyncio.open_loop() as loop:
        config = HyperConfig()
        config.bind = [f"127.0.0.1:5000"]
        config.use_reloader = True
        await serve(app, config)


if __name__ == '__main__':
    trio.run(run_server)
