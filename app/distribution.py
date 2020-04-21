from typing import Dict, Union

import asks
from asks.errors import BadStatus

from exceptions import SmscApiError


_url = "https://smsc.ru/sys/{method}.php?login={login}&psw={password}"


def build_url(method: str,
              login: str,
              password: str,
              payload: Dict[str, Union[str, int]]) -> str:
    url = _url.format(method=method, login=login, password=password)
    if not payload.get("fmt"):
        payload["fmt"] = 3  # set json response as default
    for k, v in payload.items():
        url += f"&{k}={v}"
    return url


async def request_smsc(method: str,
                       login: str,
                       password: str,
                       payload: Dict) -> Dict:
    """Send request to SMSC.ru service.

    Args:
        method (str): API method. E.g. 'send' or 'status'.
        login (str): Login for account on SMSC.
        password (str): Password for account on SMSC.
        payload (dict): Additional request params, override default ones.
    Returns:
        dict: Response from SMSC API.
    Raises:
        SmscApiError: If SMSC API response status is not 200 or it has `"ERROR" in response.

    Examples:
        >>> request_smsc("send", "my_login", "my_password", {"phones": "+79123456789"})
        {"cnt": 1, "id": 24}
        >>> request_smsc("status", "my_login", "my_password", {"phone": "+79123456789", "id": "24"})
        {'status': 1, 'last_date': '28.12.2019 19:20:22', 'last_timestamp': 1577550022}
    """
    url = build_url(method, login, password, payload)
    res = await asks.get(url)

    try:
        res.raise_for_status()
        res = res.json()
        if res.get("error"):
            raise SmscApiError(res.get("error"))
    except BadStatus:
        raise SmscApiError(
            "Wrong status, available choices: %s" %
            [getattr(Methods, x) for x in Methods.__dict__ if not x.startswith('_')]
        )
    return res


class Methods:
    STATUS = "status"
    SEND = "send"
