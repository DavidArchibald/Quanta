import aiohttp

session = None


async def get_session() -> aiohttp.ClientSession:
    global session
    if session is None:
        session = aiohttp.ClientSession()

    return session


async def close_session():
    global session

    if session is not None:
        await session.close()
        session = None
