from typing import Optional

from .colour import Colour

class BasePresence:
    def __init__(self, name: str, colour: Optional[Colour]):
        self.name = name
        self.colour = colour
    
    def __eq__(self, other):
        if type(other) != BasePresence:
            return False
        else:
            return self.name == other.name
    
    def __str__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)

class Presence:
    online = BasePresence('Online', Colour.green())
    offline = BasePresence('Offline', Colour.grey())
    idle = BasePresence('Idle', Colour.from_rgb(255, 198, 41))
    invisible = BasePresence('Invisible', Colour.grey())
    do_not_disturb = BasePresence('Do Not Disturb', Colour.red())
    dnd = do_not_disturb

    @classmethod
    def from_value(cls, value: str):
        return getattr(cls, value.lower(), None)