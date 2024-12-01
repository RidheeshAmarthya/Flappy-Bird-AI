import pygame
import random
import os
import neat

pygame.font.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 600, 800
GROUND_LEVEL = 730
GAME_FONT = pygame.font.SysFont("arial", 20)
END_FONT = pygame.font.SysFont("arial", 50)
SHOW_PATH = False

# Initialize game window
GAME_WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Load and scale images
def load_image(name, scale=1):
    img = pygame.image.load(os.path.join("imgs", name)).convert_alpha()
    return pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))

pipe_image = load_image("pipe.png", 2)
background_image = pygame.transform.scale(load_image("bg.png"), (600, 900))
bird_frames = [load_image(f"bird{x}.png", 2) for x in range(1, 4)]
base_image = load_image("base.png", 2)

generation = 0

class GameObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, window):
        pass

class Bird(GameObject):
    MAX_ROTATION = 25
    ROTATION_VELOCITY = 20
    ANIMATION_DURATION = 5

    def __init__(self, x, y):
        super().__init__(x, y)
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.frame_count = 0
        self.current_image = bird_frames[0]

    def flap(self):
        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        displacement = self.velocity * self.tick_count + 0.5 * 3 * self.tick_count**2
        displacement = min(16, max(-16, displacement))
        self.y += displacement

        if displacement < 0 or self.y < self.height + 50:
            self.tilt = min(self.tilt + self.ROTATION_VELOCITY, self.MAX_ROTATION)
        else:
            self.tilt = max(self.tilt - self.ROTATION_VELOCITY, -90)

    def draw(self, window):
        self.frame_count = (self.frame_count + 1) % (self.ANIMATION_DURATION * 4)
        frame_index = self.frame_count // self.ANIMATION_DURATION
        self.current_image = bird_frames[min(frame_index, 2)]

        if self.tilt <= -80:
            self.current_image = bird_frames[1]
            self.frame_count = self.ANIMATION_DURATION * 2

        rotated_image = pygame.transform.rotate(self.current_image, self.tilt)
        new_rect = rotated_image.get_rect(center=self.current_image.get_rect(topleft=(self.x, self.y)).center)
        window.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.current_image)

class Obstacle(GameObject):
    GAP = 200
    VELOCITY = 5

    def __init__(self, x):
        super().__init__(x, 0)
        self.OBSTACLE_TOP = pygame.transform.flip(pipe_image, False, True)
        self.OBSTACLE_BOTTOM = pipe_image
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.OBSTACLE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, window):
        window.blit(self.OBSTACLE_TOP, (self.x, self.top))
        window.blit(self.OBSTACLE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.OBSTACLE_TOP)
        bottom_mask = pygame.mask.from_surface(self.OBSTACLE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        return bird_mask.overlap(top_mask, top_offset) or bird_mask.overlap(bottom_mask, bottom_offset)

class Ground(GameObject):
    VELOCITY = 5
    WIDTH = base_image.get_width()

    def __init__(self, y):
        super().__init__(0, y)
        self.x2 = self.WIDTH

    def move(self):
        self.x -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x + self.WIDTH < 0:
            self.x = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x + self.WIDTH

    def draw(self, window):
        window.blit(base_image, (self.x, self.y))
        window.blit(base_image, (self.x2, self.y))

def draw_game_window(window, birds, obstacles, ground, score, gen, obstacle_index):
    window.blit(background_image, (0, 0))
    for obstacle in obstacles:
        obstacle.draw(window)
    ground.draw(window)

    for bird in birds:
        if SHOW_PATH:
            try:
                pygame.draw.line(window, (255, 0, 0),
                                 (bird.x + bird.current_image.get_width() / 2, bird.y + bird.current_image.get_height() / 2),
                                 (obstacles[obstacle_index].x + obstacles[obstacle_index].OBSTACLE_TOP.get_width() / 2,
                                  obstacles[obstacle_index].height), 5)
                pygame.draw.line(window, (255, 0, 0),
                                 (bird.x + bird.current_image.get_width() / 2, bird.y + bird.current_image.get_height() / 2),
                                 (obstacles[obstacle_index].x + obstacles[obstacle_index].OBSTACLE_BOTTOM.get_width() / 2,
                                  obstacles[obstacle_index].bottom), 5)
            except IndexError:
                pass
        bird.draw(window)

    # Info labels
    for i, (text, pos) in enumerate([
        (f"Score: {score}", (WINDOW_WIDTH - 15, 10)),
        (f"Gen: {gen}", (10, 10)),
        (f"Alive: {len(birds)}", (10, 50))
    ]):
        label = GAME_FONT.render(text, 1, (255, 255, 255))
        window.blit(label, (pos[0] - label.get_width() * (i == 0), pos[1]))

    pygame.display.update()

def evaluate_genomes(genomes, config):
    global GAME_WINDOW, generation
    generation += 1

    neural_networks = []
    birds = []
    ge = []

    for _, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        neural_networks.append(net)
        birds.append(Bird(230, 350))
        ge.append(genome)

    ground = Ground(GROUND_LEVEL)
    obstacles = [Obstacle(700)]
    score = 0

    clock = pygame.time.Clock()
    run = True

    while run and birds:
        clock.tick(50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        obstacle_index = 1 if len(obstacles) > 1 and birds[0].x > obstacles[0].x + obstacles[0].OBSTACLE_TOP.get_width() else 0

        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            bird.move()

            output = neural_networks[x].activate((bird.y,
                                                  abs(bird.y - obstacles[obstacle_index].height),
                                                  abs(bird.y - obstacles[obstacle_index].bottom)))

            if output[0] > 0.5:
                bird.flap()

        ground.move()

        rem = []
        add_obstacle = False
        for obstacle in obstacles:
            obstacle.move()

            for bird in birds[:]:
                if obstacle.collide(bird):
                    ge[birds.index(bird)].fitness -= 1
                    neural_networks.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.remove(bird)

            if obstacle.x + obstacle.OBSTACLE_TOP.get_width() < 0:
                rem.append(obstacle)

            if not obstacle.passed and obstacle.x < bird.x:
                obstacle.passed = True
                add_obstacle = True

        if add_obstacle:
            score += 1
            for genome in ge:
                genome.fitness += 5
            obstacles.append(Obstacle(WINDOW_WIDTH))

        for r in rem:
            obstacles.remove(r)

        for bird in birds[:]:
            if bird.y + bird.current_image.get_height() - 10 >= GROUND_LEVEL or bird.y < -50:
                neural_networks.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.remove(bird)

        draw_game_window(GAME_WINDOW, birds, obstacles, ground, score, generation, obstacle_index)

def run_neat(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(evaluate_genomes, 50)
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run_neat(config_path)
