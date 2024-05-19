import json, os
from SuperLink import *

__extension_data__ = {
    "name": "跨服银行",
    "id": "bank-link",
    "version": (0, 0, 1)
}

def get_jsdata(c: str, p: str):
    try:
        with open(os.path.join(extensions.DATA_DIR, "跨服银行", p + ".json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def set_jsdata(p: str, o):
    with open(os.path.join(extensions.DATA_DIR, "跨服银行", p + ".json"), "w", encoding="utf-8") as f:
        json.dump(o, f)

# def on_init_chan_path(c: str):
#     os.makedirs(os.path.join(extensions.DATA_DIR, "跨服银行", c), exist_ok=True)

@on_load
async def load():
    os.makedirs(os.path.join(extensions.DATA_DIR, "跨服银行"), exist_ok=True)

@on_data("scoreboard.upload.add")
async def scb_recv(data: Data):
    target = data.content["Target"]
    scb_name = data.content["ScbName"]
    add_sc = data.content["AdScore"]
    old = get_jsdata(target)
    old[scb_name] = old.get(scb_name, 0) + add_sc
    set_jsdata(target, old)

@on_data("scoreboard.upload.set")
async def scb_recv2(data: Data):
    target = data.content["Target"]
    scb_name = data.content["ScbName"]
    set_sc = data.content["AdScore"]
    old = get_jsdata(target)
    old[scb_name] = set_sc
    set_jsdata(target, old)

@on_data("scoreboard.get")
async def scb_get(data: Data):
    target = data.content["Target"]
    scb_name = data.content["ScbName"]
    dat = get_jsdata(target)
    data.sender.send(format_data(
        data.sender,
        "scoreboard.get.result",
        {
            "UUID": data.content["UUID"],
            "Score": dat.get(scb_name)
        }
    )) # type: ignore