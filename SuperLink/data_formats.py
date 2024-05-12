import json
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .client_classes import Client

@dataclass
class Data:
    sender: "Client | None"
    type: str
    content: dict | list

    def marshal(self):
        return json.dumps({
            "sender": self.sender,
            "type": self.type,
            "content": self.content
        })

def format_data(sender: "Client | None", type: str, content: dict | list):
    return Data(sender, type, content)

def unmarshal_data(data_json):
    dat = json.loads(data_json)
    return Data(dat["Sender"], dat["Type"], dat["Content"])