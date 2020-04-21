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
from helpers import send_notification

warnings.filterwarnings("ignore")

load_dotenv()

app = QuartTrio(__name__)


LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
PHONES = os.getenv("PHONES").split(';')
MESSAGE = "Привет"


@app.before_serving
async def connect_db():
    asyncio._set_running_loop(asyncio.get_event_loop())
    redis = await trio_asyncio.run_asyncio(
        aioredis.create_redis_pool(
            "redis://localhost",
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
    with open('templates/index.html') as f:
        a = f.read()
    return a  # await render_template('index.html')


@app.route('/send/', methods=['POST'])
async def get_message():
    form = await request.form
    message = form['text']
    res = await send_notification(message, PHONES)
    await trio_asyncio.run_asyncio(app.db.add_sms_mailing(
        res['id'], PHONES, message
    ))
    # TODO check errors in res and send to frontend
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
            d = f = 0
            for sms_status in sms['phones'].values():
                if sms_status == 'delivered':
                    d += 1
                elif sms_status == 'failed':
                    f += 1
            response["SMSMailings"].append(
                {
                    "timestamp": sms['created_at'],
                    "SMSText": sms['text'],
                    "mailingId": str(sms['sms_id']),
                    "totalSMSAmount": sms['phones_count'],
                    "deliveredSMSAmount": d,
                    "failedSMSAmount": f,
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
