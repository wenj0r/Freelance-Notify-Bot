from aiohttp import ClientSession
from fake_useragent import FakeUserAgent


ua = FakeUserAgent()

async def _get(session: ClientSession, url: str, params = None):
    session.headers.update({'User-Agent': ua.random})
    try:

        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                return resp

            elif resp.status == 403:
                print('Need Proxy')
                return

            else:
                print(resp.status)

    except Exception as e:
        print(e)
        return


