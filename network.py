import math, random


class Neuron:
    def __init__(self, value, weights: list, bias):
        self.weights = weights
        self.bias = bias
        self.value = value

    def compute(self, inputs: list):
        self.value = 0

        for i in range(len(inputs)):
            self.value += inputs[i] * self.weights[i]  # Sum all inputs * weights

        self.value += self.bias  # Add Bias

        # self.value = max(0, self.value)  # ReLU Activation Function
        self.value = 1 / (1 + math.e ** (-self.value))  # Sigmoid Activation Function

        return self.value


class Layer:
    def __init__(self, size, size_l):
        self.size = size
        self.neurons = []
        self.outputs = [0 for _ in range(self.size)]

        for _ in range(self.size):
            self.neurons.append(Neuron(0, [random.uniform(-1, 1) for _ in range(size_l)], random.uniform(-1, 1)))

    def compute(self, inputs: list):
        for i in range(self.size):
            # Compute each neuron's value and store it in self.outputs[i]
            self.neurons[i].compute(inputs)
            self.outputs[i] = self.neurons[i].value

        return self.outputs


class Network:
    def __init__(self, dimensions: list):
        self.dimensions = dimensions
        self.layers = []  # Initialize layers
        for i in range(1, len(self.dimensions)):
            self.layers.append(Layer(self.dimensions[i], self.dimensions[i - 1]))

    def compute(self, inputs: list):
        for i, layer in enumerate(self.layers):
            if i == 0:
                layer.compute(inputs)
            else:
                layer.compute(self.layers[i - 1].outputs)

        return self.layers[-1].outputs
