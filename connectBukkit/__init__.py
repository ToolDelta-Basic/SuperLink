"""
插件基本信息
"""
__extension_data__ = {
    "name": "消息互通1",
    "id": "basic-msg-link1",
    "version": (0, 0, 1),
    "author": "SuperScript1"
}

from SuperLink import on_load
from .server import ServerSide

@on_load
async def bukkit_con_main():
    print(1)
    #server = ServerSide()
    #server.run()

