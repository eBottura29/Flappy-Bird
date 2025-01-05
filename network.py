from enum import Enum, auto


class Types(Enum):
    INPUT = auto()
    HIDDEN = auto()
    OUTPUT = auto()


class Neuron:
    def __init__(self, id, type, bias=0.0):
        self.id = id
        self.type = type
        self.bias = bias
        self.value = 0.0

        self.incoming_connections = []
        self.outgoing_connections = []


class Connection:
    def __init__(self, innovation_number, from_neuron, to_neuron, weight, enabled=True):
        self.innovation_number = innovation_number
        self.from_neuron = from_neuron
        self.to_neuron = to_neuron
        self.weight = weight
        self.enabled = enabled
