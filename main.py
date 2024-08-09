import pygame
import random

pygame.init()

screen = pygame.display.set_mode((600, 600))
grid_size = 30

# Create a "timer_event" which will be triggered evey "time_delay" milliseconds. This will act as an event which will be processed in the event loop.
time_delay = 200
timer_event = pygame.USEREVENT + 1
pygame.time.set_timer(timer_event, time_delay)


# Create the main "Snake" class, this will house the repeated logic for each snake.
class Snake:
    # __init__ is the constructor for any class. It is always required. This one has "location" and "controls" set as inputs.
    def __init__(self, location, controls):
        # self.variable will create an attribute (which is a variable) generic to this class, meaning any objects made with this class will have these attributes.

        # Store the head as a separate Rect object and the body as a list of Rect objects.
        self.head = pygame.Rect(location, (grid_size, grid_size))
        self.body = [pygame.Rect((location[0] + grid_size, location[1]), (grid_size, grid_size))]

        # Controls is set as its input
        self.controls = controls

        # These booleans are hardcoded as the default state of the snake.
        self.isAlive = True
        self.direction = None

    # Instead of handling each event separately in the event loop, we will pass them to this "handle_event" method.
    # This way we can separate our code (so that everything to do with the Snake class is in one place) making it easier to understand.
    def handle_event(self, event):
        # If the snake is dead, we will not process any events and instead return nothing.
        if not self.isAlive:
            return

        # Process a KEYDOWN event
        if event.type == pygame.KEYDOWN:
            if event.key == self.controls[0]:
                self.direction = 'left'
            elif event.key == self.controls[1]:
                self.direction = 'right'
            elif event.key == self.controls[2]:
                self.direction = 'up'
            elif event.key == self.controls[3]:
                self.direction = 'down'

        # Process a timer_event, this will move our snake forward at a constant speed.
        # Notice, if the snake does not have a direction. This entire move code will not run including collision calculations.
        elif event.type == timer_event and self.direction:

            # Moving the snake forward is a 3-step process. This ensures when the snake dies it dies in the correct position.
            # 1. Add head copy to body
            # 2. Move the head
            # 3. Check for collisions on head


            # Add a copy of head to the body
            self.body.insert(0, self.head.copy())

            # Move the head forward
            if self.direction == 'left':
                self.head.x -= grid_size
            elif self.direction == 'right':
                self.head.x += grid_size
            elif self.direction == 'up':
                self.head.y -= grid_size
            elif self.direction == 'down':
                self.head.y += grid_size

            # Check if new head has made collisions with walls, if not delete end tail
            if (self.head.centerx > (screen.get_width()) or
                    self.head.centerx < 0 or
                    self.head.centery < 0 or
                    self.head.centery > (screen.get_height())):
                self.isAlive = False
            else:
                # Deleting the tail if there is no collision assures the tail doesn't disappear on death despite movement being invalid.
                self.body.pop()

            # Loop through the apple Rects in the apples list
            for apple in apples:
                # check if the head collides with the apple
                if self.head.colliderect(apple):
                    apple.x = random.randint(0, (screen.get_width() - grid_size) // grid_size) * grid_size
                    apple.y = random.randint(0, (screen.get_height() - grid_size) // grid_size) * grid_size
                    self.body.insert(-1, pygame.Rect(self.body[-1].x, self.body[-1].y, grid_size, grid_size))

            for segment in self.body:
                # Check for Collisions with the body
                if self.head.colliderect(segment):
                    self.isAlive = False

    # A separated draw method is used for a similar reason to the handle_event method.
    # This allows us to keep the snake logic contained to the class. This is more important later when objects become more complex.
    def draw(self):
        if self.isAlive:
            colour = "green"
        else:
            colour = "red"

        pygame.draw.rect(screen, colour, self.head)
        for rect in self.body:
            pygame.draw.rect(screen, colour, rect)


# The game can be changed my modifying the objects below without having to change the logic above!

# We have created the class, now we need to create objects. This creates instances (in this case 2) of the Snake class allowing us to make as many as we want without having to repeat the snake's logic.
snake1 = Snake((5 * grid_size, 5 * grid_size), (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN))
snake2 = Snake((15 * grid_size, 15 * grid_size), (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s))
# We add the snakes to a list for easy looping.
snakes = [snake1, snake2]

# Similar deal with the apples, but they do not need a custom class. A simple Rect object can be used.
apple1 = pygame.Rect(grid_size * 3, grid_size * 3, grid_size, grid_size)
apple2 = pygame.Rect(grid_size * 3, grid_size * 3, grid_size, grid_size)
apples = [apple1, apple2]

# This is the entire game loop. Look how much smaller and easier it is to read now that we are using objects!
while True:
    # Event Loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        for snake in snakes:
            snake.handle_event(event)

    # Rendering
    for snake in snakes:
        snake.draw()
    for apple in apples:
        pygame.draw.rect(screen, "red", apple)

    # Don't forget to update the screen after rendering
    pygame.display.update()
    screen.fill("gray")
