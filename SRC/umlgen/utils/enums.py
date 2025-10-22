from enum import Enum

class RelationType(int, Enum):
    """ Výčtový typ definující druhy vztahů.
    """
    GENERALIZATION = 1
    COMPOSITION = 2
    ASSOCIATION = 3
    CONTAINMENT = 4
    PROTOCOL = 5
    


class NodeType(int, Enum):
    """ Výčtový typ definující stereotypy diagramů.
    """
    CLASS = 1
    MODULE = 2
    ABSTRACT = 3
    PROTOCOL = 4

class Positions(Enum):
    """ Výčtový typ definující polohu uzlu vuci sobe.
    """
    ABOVE = 1
    BELOW = 2
    LEFT = 3
    RIGHT = 4
    ABOVELEFT = 5
    ABOVERIGHT = 6
    BELOWLEFT = 7
    BELOWRIGHT = 8

class WidgetType(Enum):
    """ Výčtový typ definující typy widgetu.
    """
    NONE = 1
    NODE = 2
    LINE = 3
    BREAK = 4
    CORNER = 5