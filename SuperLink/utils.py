import asyncio
from typing import Iterable, Coroutine


async def gather_funcs(funcs: Iterable[Coroutine]):
    return await asyncio.gather(*(func for func in funcs))
