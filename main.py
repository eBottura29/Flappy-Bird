from pg_extensions import *


class Settings:
    GRAVITY = Vector2(0, -2000)
    MAX_VEL = 1000
    PIPE_VEL = 1000
    JUMP_HEIGHT = 900 // 0.72
    POPULATION = 10


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
        # Move pipe left
        self.position.x -= Settings.PIPE_VEL * window.delta_time

        # Reset pipe position
        if self.position.x + self.width < -window.WIDTH // 2:
            self.position = Vector2(window.WIDTH // 2, random.randint(-self.variation // 2, self.variation // 2))

        # Update pipe objects
        self.top = Pipe(Vector2(self.position.x, self.position.y + window.HEIGHT + self.separation // 2), Vector2(self.width, window.HEIGHT), self.color)
        self.bottom = Pipe(Vector2(self.position.x, self.position.y - self.separation // 2), Vector2(self.width, window.HEIGHT), self.color)


class Player:
    def __init__(self, position, radius, color):
        self.position = position
        self.velocity = Vector2(0, 0)
        self.radius = radius
        self.color = color
        self.alive = True

    def jump(self):
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
                self.handle_collisions()

    def check_collisions(self, pipe, is_top):
        # Ground and ceiling check
        if self.position.y + self.radius >= window.HEIGHT // 2 or self.position.y - self.radius <= -window.HEIGHT // 2:
            return True

        # Clamp xy to pipe bounds
        closest = Vector2(
            clamp(self.position.x, pipe.position.x, pipe.position.x + pipe.size.x),  # Clamp X within pipe's width
            clamp(self.position.y, pipe.position.y, pipe.position.y - pipe.size.y),  # Clamp Y within pipe's height
        )

        # Calculate squared distance from the circle to the closest point on the pipe
        dst_sqr = (self.position.x - closest.x) ** 2 + (self.position.y - closest.y) ** 2

        # Check for collision using the squared distance
        if dst_sqr <= self.radius**2:
            return True

        return False

    def handle_collisions(self):
        # Kill the player
        # self.alive = False
        # Change player color
        self.color = GRAY

        self.position.y = clamp(self.position.y, -window.HEIGHT // 2 + self.radius, window.HEIGHT // 2 - self.radius)

    def render(self):
        if self.alive:
            draw_circle(window.SURFACE, self.color, self.position, self.radius)


def game():
    pipes.update()
    player.update(pipes)

    if input_manager.get_key_down(pygame.K_SPACE):
        player.jump()

    pipes.top.render()
    pipes.bottom.render()
    player.render()


def start():
    global player, pipes, window
    window = get_window()

    player = Player(Vector2(-window.WIDTH // 4, 0), window.WIDTH // 50, WHITE)

    variation = window.HEIGHT // 2
    pipes = Pipes(Vector2(window.WIDTH // 2, random.randint(-variation // 2, variation // 2)), variation, window.HEIGHT // 4, window.WIDTH // 50, WHITE)


def update():
    global window
    window = get_window()
    window.SURFACE.fill(BLACK.tup())

    if input_manager.get_key_down(pygame.K_ESCAPE):
        window.running = False

    game()

    set_window(window)


if __name__ == "__main__":
    run(start, update, 2560, 1440, False, "AI Flappy Bird", 999)
