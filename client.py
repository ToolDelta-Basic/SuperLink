import websockets
import asyncio

async def a():
    async with websockets.connect("ws://localhost:24013", extra_headers={"b":"2"}) as super_link: # type: ignore
        await super_link.send("lala")

asyncio.get_event_loop().run_until_complete(a())