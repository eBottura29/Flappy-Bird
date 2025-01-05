from enum import Enum, auto
import math, random
from pg_extensions import clamp


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

    def get_connections(self, connections):
        self.incoming_connections = []
        self.outgoing_connections = []

        for c in connections:
            if c.to_neuron == self:
                self.incoming_connections.append(c)

            if c.from_neuron == self:
                self.outgoing_connections.append(c)

    def compute_value(self):
        # Input neurons don't compute their value; their value is set externally
        if self.type == Types.INPUT:
            return self.value

        # Sum the weighted inputs from all active incoming connections
        total = 0.0
        for connection in self.incoming_connections:
            if connection.enabled:  # Use only active connections
                total += connection.weight * connection.from_neuron.value

        # Add the bias and apply an activation function (e.g., sigmoid)
        self.value = self.sigmoid(total + self.bias)
        return self.value

    def sigmoid(self, x):
        # Sigmoid activation function: maps the value to a range between 0 and 1
        x = clamp(x, -100, 100)
        return 1 / (1 + math.exp(-x))


class Connection:
    def __init__(self, innovation_number, from_neuron, to_neuron, weight, enabled=True):
        self.innovation_number = innovation_number
        self.from_neuron = from_neuron
        self.to_neuron = to_neuron
        self.weight = weight
        self.enabled = enabled

    def mutate_weight(self, perturb_probability=0.9, perturb_amount=0.1):
        # With `perturb_probability`, slightly adjust the weight
        if random.random() < perturb_probability:
            # Perturb the weight by a small random amount
            self.weight += random.uniform(-perturb_amount, perturb_amount)
        else:
            # Replace the weight with a completely random value
            self.weight = random.uniform(-1.0, 1.0)  # Random weight between -1 and 1
