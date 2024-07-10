import json, os
from SuperLink import *

__extension_data__ = {
    "name": "跨服银行",
    "id": "bank-link",
    "version": (0, 0, 1),
    "author": "SuperScript",
}


def get_jsdata(channel: str, player: str):
    os.makedirs(os.path.join(extensions.DATA_DIR, "跨服银行", channel), exist_ok=True)
    try:
        with open(
            os.path.join(extensions.DATA_DIR, "跨服银行", channel, player + ".json"),
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def set_jsdata(channel: str, player: str, o):
    os.makedirs(os.path.join(extensions.DATA_DIR, "跨服银行", channel), exist_ok=True)
    with open(
        os.path.join(extensions.DATA_DIR, "跨服银行", channel, player + ".json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(o, f)


@on_load
async def load():
    os.makedirs(os.path.join(extensions.DATA_DIR, "跨服银行"), exist_ok=True)


@on_data("scoreboard.upload.add")
async def scb_recv(data: Data):
    target = data.content["Target"]
    scb_name = data.content["ScbName"]
    add_sc = data.content["AdScore"]
    Print.print_inf(f"客户端 §e{data.sender.name}§r 对计分板 §b{scb_name}§r 上传 §b{target}§r 的分数 §e{add_sc}")
    old = get_jsdata(data.sender.channel.name, target)
    old[scb_name] = old.get(scb_name, 0) + add_sc
    set_jsdata(data.sender.channel.name, target, old)
    await data.sender.send(
        format_data(
            data.sender,
            "scoreboard.get.result",
            {"UUID": data.content.get("UUID"), "Score": old.get(scb_name)},
        )
    )


@on_data("scoreboard.upload.set")
async def scb_recv2(data: Data):
    target = data.content["Target"]
    scb_name = data.content["ScbName"]
    set_sc = data.content["AdScore"]
    old = get_jsdata(data.sender.channel.name, target)
    old[scb_name] = set_sc
    set_jsdata(data.sender.channel.name, target, old)


@on_data("scoreboard.get")
async def scb_get(data: Data):
    target = data.content["Target"]
    scb_name = data.content["ScbName"]
    dat = get_jsdata(data.sender.channel.name, target)
    await data.sender.send(
        format_data(
            data.sender,
            "scoreboard.get.result",
            {"UUID": data.content.get("UUID"), "Score": dat.get(scb_name)},
        )
    )
