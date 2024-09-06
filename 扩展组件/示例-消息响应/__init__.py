from SuperLink import *

__extension_data__ = {
    "name": "跨服银行",
    "id": "bank-link",
    "version": (0, 0, 1),
    "author": "SuperScript",
}


@on_data("测试消息响应")
async def on_recv_test_data(data: Data):
    await data.sender.send(
        format_data(
            data.sender,
            "测试消息响应返回",
            {"Returns": data.content["EchoData"], "UUID": data.content["UUID"]},
        )
    )
