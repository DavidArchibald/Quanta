import aiohttp

session = None


async def get_session():
    global session
    if session is None:
        session = aiohttp.ClientSession()

    return session
