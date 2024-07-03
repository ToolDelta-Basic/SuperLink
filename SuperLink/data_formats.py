import json
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .client_classes import Client

@dataclass
class Data:
    sender: "Client"
    type: str
    content: dict

    def marshal(self):
        return json.dumps({
            "Sender": self.sender.name if self.sender else "System",
            "Type": self.type,
            "Content": self.content
        })

@dataclass
class SystemData:
    type: str
    content: dict

    def marshal(self):
        return json.dumps({
            "Type": self.type,
            "Content": self.content
        })

def format_data(sender: "Client", type: str, content: dict):
    return Data(sender, type, content)

def format_sys_data(type: str, content: dict):
    return SystemData(type, content)

def unmarshal_data(data_json, sender: "Client") -> Data:
    dat = json.loads(data_json)
    if sender is not None:
        return Data(sender, dat["Type"], dat["Content"])