import pygame
import random
from PyNeuro.PyNeuro import PyNeuro
from time import sleep

# Initialize PyNeuro
pn = PyNeuro()
blink_strength = pn.delta

pn.connect()
pn.start()
sleep(200)
print(pn.delta)
sleep(5)
pygame.init()

# Get the display info
display_info = pygame.display.Info()
SCREEN_WIDTH = display_info.current_w
SCREEN_HEIGHT = display_info.current_h

# Scale factors (based on original 800x400 design)
SCALE_X = SCREEN_WIDTH / 800
SCALE_Y = SCREEN_HEIGHT / 400

# Dino variables
DINO_WIDTH = int(50 * SCALE_X)
DINO_HEIGHT = int(50 * SCALE_Y)
DINO_COLOR = (255, 255, 0)
DINO_JUMP_VELOCITY = int(-20 * SCALE_Y)
GRAVITY = SCALE_Y

# Obstacle variables
OBSTACLE_WIDTH = int(50 * SCALE_X)
OBSTACLE_HEIGHT = int(50 * SCALE_Y)
OBSTACLE_COLOR = (0, 0, 255)
OBSTACLE_VELOCITY = int(-5 * SCALE_X)

# Game settings
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
FPS = 30

# Scale font size based on screen height
FONT_SIZE = int(25 * min(SCALE_X, SCALE_Y))
FONT = pygame.font.SysFont('Arial', FONT_SIZE)

# Button settings
BUTTON_WIDTH = int(100 * min(SCALE_X, SCALE_Y))
BUTTON_HEIGHT = int(40 * min(SCALE_X, SCALE_Y))
BUTTON_MARGIN = int(10 * min(SCALE_X, SCALE_Y))

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.is_hovered = False

    def draw(self, screen):
        color = (min(self.color[0] + 30, 255), 
                min(self.color[1] + 30, 255), 
                min(self.color[2] + 30, 255)) if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        text_surface = FONT.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Dino:
    def __init__(self):
        self.x = int(50 * SCALE_X)
        self.y = SCREEN_HEIGHT - DINO_HEIGHT
        self.velocity = 0
        self.is_jumping = False
        self.rect = pygame.Rect(self.x, self.y, DINO_WIDTH, DINO_HEIGHT)
        self.last = 0
    
    def update(self):
        bs = pn.blinkStrength
    
        print(bs, self.last)

        if (bs > 55 and not self.is_jumping and bs != self.last):
            self.last = bs
            self.velocity = DINO_JUMP_VELOCITY
            self.is_jumping = True
            bs = 0

        self.velocity += GRAVITY
        self.y += self.velocity

        if self.y >= SCREEN_HEIGHT - DINO_HEIGHT:
            self.y = SCREEN_HEIGHT - DINO_HEIGHT
            self.is_jumping = False

        self.rect.y = self.y

    def draw(self, screen):
        pygame.draw.rect(screen, DINO_COLOR, self.rect)

class Obstacle:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.y = SCREEN_HEIGHT - OBSTACLE_HEIGHT
        self.rect = pygame.Rect(self.x, self.y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)

    def update(self, speed):
        self.x += speed
        self.rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, OBSTACLE_COLOR, self.rect)

class DinoGame:
    def __init__(self):
        # Initialize fullscreen display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Dino Game with NeuroSky Control")
        self.clock = pygame.time.Clock()
        self.dino = Dino()
        self.obstacles = [Obstacle()]
        self.score = 0
        self.running = True
        self.game_started = False
        self.paused = False
        self.speed = OBSTACLE_VELOCITY
        
        # Create buttons in top-right corner
        button_x = SCREEN_WIDTH - (BUTTON_WIDTH + BUTTON_MARGIN)
        self.resume_button = Button(button_x, BUTTON_MARGIN, 
                                  BUTTON_WIDTH, BUTTON_HEIGHT, "Resume", (0, 255, 255))
        
        button_x -= (BUTTON_WIDTH + BUTTON_MARGIN)
        self.pause_button = Button(button_x, BUTTON_MARGIN,
                                 BUTTON_WIDTH, BUTTON_HEIGHT, "Pause", (255, 255, 0))
        
        button_x -= (BUTTON_WIDTH + BUTTON_MARGIN)
        self.stop_button = Button(button_x, BUTTON_MARGIN,
                                BUTTON_WIDTH, BUTTON_HEIGHT, "Stop", (255, 0, 0))
        
        button_x -= (BUTTON_WIDTH + BUTTON_MARGIN)
        self.start_button = Button(button_x, BUTTON_MARGIN,
                                 BUTTON_WIDTH, BUTTON_HEIGHT, "Start", (0, 255, 0))

    def run(self):
        while self.running:
            blink_strength = pn.blinkStrength
            self.clock.tick(FPS)
            self.screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:  # Add ESC to quit
                        self.running = False
                    if event.key == pygame.K_r:
                        self.reset_game()
                    if event.key == pygame.K_UP:
                        self.speed -= SCALE_X
                    if event.key == pygame.K_DOWN:
                        self.speed += SCALE_X
                    if event.key == pygame.K_f:  # Toggle fullscreen
                        pygame.display.toggle_fullscreen()

                # Handle button events
                if self.start_button.handle_event(event):
                    self.game_started = True
                    self.paused = False
                elif self.stop_button.handle_event(event):
                    self.reset_game()
                    self.game_started = False
                elif self.pause_button.handle_event(event):
                    self.paused = True
                elif self.resume_button.handle_event(event):
                    self.paused = False

            # Draw buttons
            self.start_button.draw(self.screen)
            self.stop_button.draw(self.screen)
            self.pause_button.draw(self.screen)
            self.resume_button.draw(self.screen)

            if self.game_started and not self.paused:
                self.dino.update()
                for obstacle in self.obstacles:
                    obstacle.update(self.speed)

                if self.obstacles[-1].x < SCREEN_WIDTH // 2:
                    self.obstacles.append(Obstacle())

                if self.check_collisions():
                    print(f"Game Over! Final Score: {self.score}")
                    self.game_started = False

                self.obstacles = [obstacle for obstacle in self.obstacles if obstacle.x + OBSTACLE_WIDTH > 0]
                self.score += 1

            self.dino.draw(self.screen)
            for obstacle in self.obstacles:
                obstacle.draw(self.screen)

            # Display score in top-left corner
            score_text = FONT.render(f"Score: {self.score}", True, BLACK)
            self.screen.blit(score_text, (BUTTON_MARGIN, BUTTON_MARGIN))

            pygame.display.update()

        pygame.quit()

    def reset_game(self):
        self.dino = Dino()
        self.obstacles = [Obstacle()]
        self.score = 0
        self.paused = False

    def check_collisions(self):
        for obstacle in self.obstacles:
            if self.dino.rect.colliderect(obstacle.rect):
                return True
        return False

def main():
    sleep(2)
    game = DinoGame()
    game.run()

if __name__ == "__main__":
    main()