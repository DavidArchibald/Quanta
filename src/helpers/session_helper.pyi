import aiohttp

from typing import Optional

session: Optional[aiohttp.ClientSession] = ...

async def get_session() -> aiohttp.ClientSession: ...
