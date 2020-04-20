import os

import trio
from quart_trio import QuartTrio
from quart import request, redirect, url_for, websocket, jsonify
from dotenv import load_dotenv

from distribution import request_smsc, Methods

load_dotenv()

app = QuartTrio(__name__)


LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
PHONE = os.getenv("PHONE")
MESSAGE = "Привет"


@app.route('/')
async def index():
    with open('templates/index.html') as f:
        a = f.read()
    return a  # await render_template('index.html')


@app.route('/send/', methods=['POST'])
async def get_message():
    form = await request.form
    await send_notification(form['text'])
    return jsonify({
        "errorMessage": "Потеряно соединение с SMSC.ru"
    })
    #return redirect(url_for('index'))

import json
@app.websocket('/ws')
async def ws():
    data = {
        "msgType": "SMSMailingStatus",
        "SMSMailings": [
            {
                "timestamp": 1123131392.734,
                "SMSText": "Сегодня гроза! Будьте осторожны!",
                "mailingId": "1",
                "totalSMSAmount": 345,
                "deliveredSMSAmount": 0,
                "failedSMSAmount": 20,
            },
            {
                "timestamp": 1323141112.924422,
                "SMSText": "Новогодняя акция!!! Приходи в магазин и получи скидку!!!",
                "mailingId": "new-year",
                "totalSMSAmount": 3993,
                "deliveredSMSAmount": 0,
                "failedSMSAmount": 0,
            },
        ]
    }
    for i in range(1, 101):
        for mail in data['SMSMailings']:
            mail['deliveredSMSAmount'] += int(mail['totalSMSAmount'] / 100)
        await websocket.send(json.dumps(data))
        await trio.sleep(1)


async def send_notification(message):
    status_payload = {
        "id": 76,
        "fmt": 3,
        "phone": PHONE
    }
    send_payload = {
        "phones": PHONE,
        "fmt": 3,
        "mes": message
    }
    res = await request_smsc(Methods.SEND, LOGIN, PASSWORD, send_payload)
    print("GGGGGGGG")
    print(res)
    print("GGGGGGGG")


if __name__ == '__main__':
    app.run()
