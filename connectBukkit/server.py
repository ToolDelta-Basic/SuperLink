import json
import os
import socket
from concurrent.futures import ThreadPoolExecutor
from 扩展组件.connectBukkit import craftPackage, config
from 扩展组件.connectBukkit.config import port
from 扩展组件.connectBukkit.utils.utils import utils


class ServerSide:
    def __init__(self):
        self.pool = ThreadPoolExecutor(max_workers=os.cpu_count() * 2 + 1)
        self.socket_server = socket.socket()
        self.socket_server.bind(("0.0.0.0", port))

    def run(self):
        self.socket_server.listen(500)
        while True:
            client, addr = self.socket_server.accept()

            def task(conn: socket, ip):
                if ip[0] in config.allow_IP:
                    # 读取全部数据
                    data = b''
                    while True:
                        chunk = conn.recv(4096)
                        if not chunk:  # 如果接收为空或连接关闭
                            break
                        data += chunk
                    conn.shutdown(socket.SHUT_RD)  # 关闭输入流
                    # 构造请求包
                    request = craftPackage.request(data)

                    # 正式进入处理流程
                    re = json.loads(request.body)
                    # 传递消息
                    print(1)
                    utils.broadcastMessage(re["ServerName"], re["name"], re["mess"])
                    print(2)
                    # 构造响应包
                    p = craftPackage.craftRespondPackage(200, "")
                    print(p.getPackage())
                    conn.Write(p.getPackage())
                    # 结束任务
                    conn.shutdown(socket.SHUT_WR)  # 关闭输出流
                    conn.close()
                else:
                    conn.shutdown(socket.SHUT_RDWR)
                    conn.close()

            self.pool.submit(task, client, addr)
