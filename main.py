import websockets
import asyncio
from SuperLink.handler import client_hander
from SuperLink.color_print import Print
from SuperLink.cfg import read_server_config

cfgs = read_server_config()

Print.print_suc(f"服务端将在端口: §f{cfgs['开放端口']} §a开启")

main_server = websockets.serve(client_hander, "localhost", cfgs['开放端口'])
asyncio.get_event_loop().run_until_complete(main_server)
asyncio.get_event_loop().run_forever()