import pygame
import random
import copy

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_SIZE = 40
FPS = 60
MOVE_DELAY = 250  # Milliseconds


class Apple:
    def __init__(self, screen, grid_size=40):
        self.screen = screen
        self.grid_size = grid_size
        self.rect = None
        self.spawn_new()

    def spawn_new(self, snakes=None):
        valid_position = False
        while not valid_position:
            new_x = random.randint(0, (self.screen.get_width() - self.grid_size) // self.grid_size) * self.grid_size
            new_y = random.randint(0, (self.screen.get_height() - self.grid_size) // self.grid_size) * self.grid_size
            self.rect = pygame.Rect(new_x, new_y, self.grid_size, self.grid_size)

            if not snakes or all(not segment.colliderect(self.rect) for snake in snakes for segment in snake.body):
                valid_position = True  # Found a valid position, exit loop

    def render(self):
        pygame.draw.rect(self.screen, "red", self.rect)


class Snake:
    def __init__(self, location, controls, move_event, screen, grid_size=40):
        self.grid_size = grid_size
        self.move_event = move_event
        self.screen = screen
        self.starting_location = copy.copy(location)

        self.is_dead = None
        self.body = [pygame.Rect((location[0] + grid_size, location[1]), (grid_size, grid_size))]
        self.controls = controls

        self.current_direction = "right"
        self.next_direction = "right"

    def handle_event(self, event, snakes, apples):
        if self.is_dead:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == self.controls["right"]:
                if not self.current_direction == 'left':
                    self.next_direction = "right"
            if event.key == self.controls["left"]:
                if not self.current_direction == 'right':
                    self.next_direction = "left"
            if event.key == self.controls["up"]:
                if not self.current_direction == 'down':
                    self.next_direction = "up"
            if event.key == self.controls["down"]:
                if not self.current_direction == 'up':
                    self.next_direction = "down"

        if event.type == self.move_event:
            direction_offsets = {
                "right": (self.grid_size, 0),
                "left": (-self.grid_size, 0),
                "up": (0, -self.grid_size),
                "down": (0, self.grid_size),
            }

            self.body.insert(0, self.body[0].copy())
            offset_x, offset_y = direction_offsets[self.next_direction]
            self.body[0].move_ip(offset_x, offset_y)
            self.current_direction = self.next_direction

            # Check apple collision
            for apple in apples:
                if self.body[0].colliderect(apple.rect):
                    apple.spawn_new(snakes)
                    self.body.insert(-1, pygame.Rect(self.body[-1].x, self.body[-1].y, self.grid_size, self.grid_size))

            # Check snake collision with walls
            if self.body[0].right > (self.screen.get_width()) or self.body[0].left < 0 or self.body[0].top < 0 or self.body[0].bottom > (self.screen.get_height()):
                # Switch to the dead state
                self.body.pop(0)
                self.is_dead = True
                return

            # Check snake collision with other snakes
            for snake in snakes:
                if any(self.body[0].colliderect(segment) for segment in snake.body if snake != self):
                    self.is_dead = True
                    return

            if len(self.body) > 1:
                self.body.pop()

            # Check snake collision with itself
            for i in range(1, len(self.body)):
                if self.body[0].colliderect(self.body[i]):
                    self.is_dead = True
                    return

    def reset(self):
        self.body = [pygame.Rect((self.starting_location[0] + self.grid_size, self.starting_location[1]), (self.grid_size, self.grid_size))]
        self.current_direction = "right"
        self.next_direction = "right"
        self.is_dead = False

    def render(self):
        if not self.is_dead:
            for segment in self.body:
                pygame.draw.rect(self.screen, "blue", segment)
            pygame.draw.rect(self.screen, "green", self.body[0])
        else:
            for segment in self.body:
                pygame.draw.rect(self.screen, "orange", segment)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Segoe UI", 35)
        self.fps = FPS
        grid_size = GRID_SIZE

        move_event = pygame.USEREVENT + 1
        pygame.time.set_timer(move_event, MOVE_DELAY)

        self.is_over = False
        self.snakes = [
            Snake(
                (2 * grid_size, 2 * grid_size),
                {
                    "left": pygame.K_LEFT,
                    "right": pygame.K_RIGHT,
                    "up": pygame.K_UP,
                    "down": pygame.K_DOWN
                }, move_event, self.screen, grid_size
            ),
            Snake(
                (5 * grid_size, 5 * grid_size),
                {
                    "left": pygame.K_a,
                    "right": pygame.K_d,
                    "up": pygame.K_w,
                    "down": pygame.K_s
                }, move_event, self.screen, grid_size
            ),
        ]
        self.apples = []
        for i in range(2):
            self.apples.append(Apple(self.screen, grid_size))

    def render(self):
        self.screen.fill("dark gray")
        for apple in self.apples:
            apple.render()
        for snake in self.snakes:
            snake.render()
        if self.is_over:
            text = self.font.render("Game Over", True, "white")
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(text, text_rect)

        pygame.display.update()
        self.clock.tick(self.fps)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        for snake in self.snakes:
            snake.handle_event(event, self.snakes, self.apples)

        if all(snake.is_dead for snake in self.snakes):
            self.is_over = True

        if self.is_over and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            for snake in self.snakes:
                snake.reset()
            self.is_over = False
            for apple in self.apples:
                apple.spawn_new(self.snakes)

    def run(self):
        while True:
            # Event handling
            for event in pygame.event.get():
                self.handle_event(event)
            self.render()


Game().run()
