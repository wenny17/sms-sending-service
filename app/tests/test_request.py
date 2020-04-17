from unittest import IsolatedAsyncioTestCase, main
from exceptions import SmscApiError
from distribution import request_smsc


class RequestApiTests(IsolatedAsyncioTestCase):

    async def test_using_wrong_api_method(self):
        payload = {
            "id": 76,
            "fmt": 3,
            "phone": '+389999999999'
        }
        with self.assertRaises(SmscApiError):
            await request_smsc("wrong_method", "login", "password", payload)


if __name__ == '__main__':
    main()
