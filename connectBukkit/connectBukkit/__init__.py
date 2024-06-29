"""
插件基本信息
"""
__extension_data__ = {
    "name": "消息互通1",
    "id": "basic-msg-link1",
    "version": (0, 0, 1),
    "author": "SuperScript1"
}

import threading
from multiprocessing import cpu_count
from gevent.pywsgi import WSGIServer

from SuperLink import on_load
from 扩展组件.connectBukkit.server import server

@on_load
async def main():
    print(1)
    obj = server()
    multiverse = WSGIServer(("0.0.0.0", 8080), obj.app, log=None)
    multiverse.max_accept = int(500)
    multiverse = multiverse
    multiverse.start()

    # noinspection PyProtectedMember
    def server_forever():
        multiverse.start_accepting()
        multiverse._stop_event.wait()

    for i in range(cpu_count() * 2 + 1):
        threading.Thread(target=server_forever).start()


main()
