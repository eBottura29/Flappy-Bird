from pg_extensions import *
from network import *


class Settings:
    GRAVITY = Vector2(0, -2000)
    MAX_VEL = 1000
    PIPE_VEL = 1000
    JUMP_HEIGHT = 900 // 0.72
    POPULATION = 25


class Pipe:
    def __init__(self, position, size, color):
        self.position = position
        self.size = size
        self.color = color

    def render(self):
        draw_rectangle(window.SURFACE, self.color, self.position, self.size)


class Pipes:
    def __init__(self, position, variation, separation, width, color):
        self.position = position
        self.variation = variation
        self.separation = separation
        self.width = width
        self.color = color

        # Initialize pipe objects
        self.top = Pipe(Vector2(self.position.x, self.position.y + window.HEIGHT + self.separation // 2), Vector2(self.width, window.HEIGHT), self.color)
        self.bottom = Pipe(Vector2(self.position.x, self.position.y - self.separation // 2), Vector2(self.width, window.HEIGHT), self.color)

    def update(self):
        global score

        # Move pipe left
        self.position.x -= Settings.PIPE_VEL * window.delta_time

        # Reset pipe position
        if self.position.x + self.width < -window.WIDTH // 2:
            self.position = Vector2(window.WIDTH // 2, random.randint(-self.variation // 2, self.variation // 2))
            score += 1

        # Update pipe objects
        self.top = Pipe(Vector2(self.position.x, self.position.y + window.HEIGHT + self.separation // 2), Vector2(self.width, window.HEIGHT), self.color)
        self.bottom = Pipe(Vector2(self.position.x, self.position.y - self.separation // 2), Vector2(self.width, window.HEIGHT), self.color)

    def reset(self):
        self.position = Vector2(window.WIDTH // 2, random.randint(-self.variation // 2, self.variation // 2))


class Player:
    def __init__(self, position, radius, color):
        self.position = position
        self.initial_position = position
        self.velocity = Vector2(0, 0)
        self.radius = radius
        self.color = color
        self.initial_color = color
        self.alive = True

        self.neurons = [
            Neuron(0, Types.INPUT, 0.0),
            Neuron(1, Types.INPUT, 0.0),
            Neuron(2, Types.INPUT, 0.0),
            Neuron(3, Types.INPUT, 0.0),
            Neuron(4, Types.OUTPUT, 0.0),
        ]

        self.connections = [
            Connection(0, self.neurons[0], self.neurons[4], random_float(-1, 1), True),
            Connection(1, self.neurons[1], self.neurons[4], random_float(-1, 1), True),
            Connection(2, self.neurons[2], self.neurons[4], random_float(-1, 1), True),
            Connection(3, self.neurons[3], self.neurons[4], random_float(-1, 1), True),
        ]

        self.time_survived = time.time()
        self.fitness = 0

    def compute(self, distance_to_pipe, distance_to_top_pipe, distance_to_bottom_pipe):
        # Update Inputs
        self.neurons[0].value = distance_to_pipe
        self.neurons[1].value = self.velocity.y
        self.neurons[2].value = distance_to_top_pipe
        self.neurons[3].value = distance_to_bottom_pipe

        # Compute
        for neuron in self.neurons:
            neuron.get_connections(self.connections)
            neuron.compute_value()

        # Decision
        if self.neurons[4].value >= 0.5:
            self.velocity.y = Settings.JUMP_HEIGHT

    def update(self, pipes):
        if self.alive:
            # Update player position & velocity
            self.velocity += Settings.GRAVITY * window.delta_time
            self.position += self.velocity * window.delta_time

            # Clamp Velocity
            mag = self.velocity.magnitude()
            if mag > Settings.MAX_VEL:
                self.velocity = self.velocity * Settings.MAX_VEL / mag

            # Check collisions and handle if present
            if self.check_collisions(pipes.top, True) or self.check_collisions(pipes.bottom, False):
                self.handle_collisions(GRAY)

    def check_collisions(self, pipe, is_top):
        # Ground and ceiling check
        if self.position.y + self.radius >= window.HEIGHT // 2 or self.position.y - self.radius <= -window.HEIGHT // 2:
            return True

        # Clamp xy to pipe bounds
        closest = Vector2(
            clamp(self.position.x, pipe.position.x, pipe.position.x + pipe.size.x),  # Clamp X within pipe's width
            clamp(self.position.y, pipe.position.y - pipe.size.y, pipe.position.y),  # Clamp Y within pipe's height
        )

        # DEBUG
        # print(f"Is Top: {is_top}")
        # print(f"Pipe Top: {pipe.position.y}")
        # print(f"Pipe Bottom: {pipe.position.y-pipe.size.y}")
        # print(f"Player Position: {player.position.y}")
        # print(f"Player Clamped Position: {clamp(self.position.y, pipe.position.y, pipe.position.y - pipe.size.y)}")
        # print(f"Closest Position: {closest.y}")
        # print(f"######################################################################")
        # draw_circle(window.SURFACE, GREEN, closest, self.radius, 2)

        # Calculate squared distance from the circle to the closest point on the pipe
        dst_sqr = (self.position.x - closest.x) ** 2 + (self.position.y - closest.y) ** 2

        # Check for collision using the squared distance
        if dst_sqr <= self.radius**2:
            return True

        return False

    def handle_collisions(self, color):
        self.alive = False

        # DEBUG
        # self.color = color

        self.time_survived -= time.time()
        self.time_survived = abs(self.time_survived)

        self.fitness = (score + 1) * self.time_survived

        self.position.y = clamp(self.position.y, -window.HEIGHT // 2 + self.radius, window.HEIGHT // 2 - self.radius)

    def rebirth(self):
        self.position = self.initial_position
        self.alive = True
        self.color = self.initial_color

        self.fitness = 0

    def render(self):
        if self.alive:
            draw_circle(window.SURFACE, self.color, self.position, self.radius)


def save():
    global winner

    file_name = f"{time.localtime().tm_mon:02}{time.localtime().tm_mday:02}{time.localtime().tm_year:04}-{time.localtime().tm_hour * 3600 + time.localtime().tm_min * 60 + time.localtime().tm_sec}.neat"
    print(f"Saving to: {file_name}")

    # Get values
    neuron_ids = []
    neuron_types = []
    biases = []

    enabled = []
    from_neurons_id = []
    to_neurons_id = []
    weights = []

    for n in winner.neurons:
        neuron_ids.append(n.id)
        neuron_types.append(n.type.name)
        biases.append(n.bias)

    for c in winner.connections:
        enabled.append(c.enabled)
        from_neurons_id.append(c.from_neuron.id)
        to_neurons_id.append(c.to_neuron.id)
        weights.append(c.weight)

    with open(file_name, "w") as f:
        f.write(f"neuron ids: {neuron_ids}\n")
        f.write(f"neuron types: {neuron_types}\n")
        f.write(f"biases: {biases}\n")
        f.write(f"enabled: {enabled}\n")
        f.write(f"from neurons: {from_neurons_id}\n")
        f.write(f"to neurons: {to_neurons_id}\n")
        f.write(f"weights: {weights}")


def game():
    global score, generation, winner

    winner = players[0]

    pipes.update()

    current_population = 0

    for player in players:
        player.update(pipes)
        player.compute(
            player.position.x - pipes.position.x, abs(player.position.y - pipes.top.position.y - window.HEIGHT), abs(player.position.y - pipes.bottom.position.y - window.HEIGHT)
        )

        if player.alive:
            current_population += 1

    # If generation dies
    if current_population == 0:
        # Determine agent with highest fitness
        winner = players[0]

        for player in players:
            if winner.fitness < player.fitness:
                winner = player

        # Inherit and mutate
        for player in players:
            player.rebirth()

            for n in player.neurons:
                n.mutate_bias(winner.neurons, 0.1)

            for c in player.connections:
                c.mutate_weight(winner.connections, 0.1)

        # Reset game
        pipes.reset()
        score = 0
        generation += 1

    pipes.top.render()
    pipes.bottom.render()

    for player in players:
        player.render()

    score_text = Text(f"Score: {score}", Text.arial_32, Vector2(0, window.HEIGHT // 3), Text.center, WHITE, BLACK)
    score_text.render()

    gen_text = Text(f"Generation: {generation}", Text.arial_32, Vector2(0, window.HEIGHT // 3 - 32), Text.center, WHITE, BLACK)
    gen_text.render()

    pop_text = Text(f"Population: {current_population}", Text.arial_32, Vector2(0, window.HEIGHT // 3 - 64), Text.center, WHITE, BLACK)
    pop_text.render()


def start():
    global players, pipes, window, score, generation, current_population
    window = get_window()

    score = 0
    generation = 1
    current_population = Settings.POPULATION

    players = []

    for _ in range(Settings.POPULATION):
        players.append(Player(Vector2(-window.WIDTH // 3, 0), window.WIDTH // 50, WHITE))

    variation = window.HEIGHT // 2
    pipes = Pipes(Vector2(window.WIDTH // 2, random.randint(-variation // 2, variation // 2)), variation, window.HEIGHT // 4, window.WIDTH // 25, WHITE)


def update():
    global window
    window = get_window()
    window.SURFACE.fill(BLACK.tup())

    if input_manager.get_key_down(pygame.K_ESCAPE):
        save()
        window.running = False

    game()

    set_window(window)


if __name__ == "__main__":
    run(start, update, 2560, 1440, False, "AI Flappy Bird", 999)
