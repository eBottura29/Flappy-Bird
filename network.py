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

    def mutate_bias(self, best_neurons, perturb_amount=0.1):
        """
        Mutate the bias by inheriting the bias from the best agent's neuron and slightly perturbing it.

        :param best_neurons: A list of neurons from the best agent.
        :param perturb_amount: Maximum amount to perturb the bias.
        """
        # Find the matching neuron in the best agent's neurons
        for best_neuron in best_neurons:
            if best_neuron.id == self.id:
                # Inherit the bias from the best neuron
                self.bias = best_neuron.bias

                # Slightly perturb the bias
                self.bias += random.uniform(-perturb_amount, perturb_amount)
                return  # Stop after finding the match

        # If no matching neuron is found, leave the bias unchanged or initialize it (optional)
        print(f"Warning: No matching neuron found for id {self.id}")


class Connection:
    def __init__(self, innovation_number, from_neuron, to_neuron, weight, enabled=True):
        self.innovation_number = innovation_number
        self.from_neuron = from_neuron
        self.to_neuron = to_neuron
        self.weight = weight
        self.enabled = enabled

    def mutate_weight(self, best_connections, perturb_amount=0.1):
        """
        Mutate the weight of this connection by inheriting the weight
        from the highest-scoring agent and slightly perturbing it.

        :param best_connections: A list of connections from the best agent.
        :param perturb_amount: Maximum amount to perturb the weight.
        """
        # Find the matching connection in the best agent's connections
        for best_connection in best_connections:
            if best_connection.innovation_number == self.innovation_number:
                # Inherit the weight from the best connection
                self.weight = best_connection.weight

                # Slightly perturb the weight
                self.weight += random.uniform(-perturb_amount, perturb_amount)
                return  # Stop after finding the match

        # If no matching connection is found, leave the weight unchanged or initialize it with a random value (optional).
        print(f"Warning: No matching connection found for innovation {self.innovation_number}")
