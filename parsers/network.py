from aiohttp import ClientSession
from fake_useragent import FakeUserAgent
from loggers import main_logger as logger


ua = FakeUserAgent()

async def _get(session: ClientSession, url: str, params = None):
    session.headers.update({'User-Agent': ua.random})
    try:
        resp = await session.get(url, params=params)
        if resp.status == 200:
            return resp

        elif resp.status == 403:
            logger.error('Need Proxy')
            return

        else:
            logger.error(resp.status)

    except Exception as e:
        logger.exception(e)
        return


