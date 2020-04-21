import os
import random

from dotenv import load_dotenv
from unittest.mock import AsyncMock

from distribution import request_smsc, Methods

load_dotenv()


def _side_effect(*args, **kwargs):
    if args[0] == 'send':
        return {'id': random.randint(1, 1000), 'cnt': 1}
    elif args[0] == 'status':
        raise NotImplementedError


request_smsc = AsyncMock(side_effect=_side_effect)
async def send_notification(message, phones):
    send_payload = {
        "phones": phones,
        "mes": message
    }
    res = await request_smsc(
        Methods.SEND, os.getenv('LOGIN'), os.getenv('PASSWORD'), send_payload
    )
    return res
