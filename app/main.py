import os

import trio
from dotenv import load_dotenv

from distribution import request_smsc, Methods

load_dotenv()

LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
PHONE = os.getenv("PHONE")
MESSAGE = "Привет"


async def main():
    status_payload = {
        "id": 76,
        "fmt": 3,
        "phone": PHONE
    }
    send_payload = {
        "phones": PHONE,
        "fmt": 3,
        "mes": "Привет, Мир"
    }
    res = await request_smsc(Methods.STATUS, LOGIN, PASSWORD, status_payload)
    print(res)

if __name__ == '__main__':
    trio.run(main)
