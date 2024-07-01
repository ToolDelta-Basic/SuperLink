import json
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .client_classes import Client

@dataclass
class Data:
    sender: "Client | None"
    type: str
    content: dict

    def marshal(self):
        return json.dumps({
            "Sender": self.sender.name if self.sender else "System",
            "Type": self.type,
            "Content": self.content
        })

def format_data(sender: "Client | None", type: str, content: dict):
    return Data(sender, type, content)

def unmarshal_data(data_json, sender: "Client | None"):
    dat = json.loads(data_json)
    return Data(sender, dat["Type"], dat["Content"])