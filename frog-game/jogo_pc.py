import pygame
import random

# Inicializa o Pygame
pygame.init()

# Constantes
SCREEN_WIDTH = 1000  # Aumentei a largura da área do jogo
SCREEN_HEIGHT = 700  # Aumentei a altura da área do jogo
GAME_WIDTH = 800  # Área do jogo
PANEL_WIDTH = 200  # Área da seção lateral
FROG_WIDTH = 50
FROG_HEIGHT = 50
CAR_WIDTH = 50
CAR_HEIGHT = 50
FPS = 60

# Cores
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
DARK_GREEN = (0, 200, 0)
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
DARK_BLUE = (0, 0, 139)

# Configuração das faixas
SAFE_ZONE_HEIGHT = 50

# Cria a tela
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Frogger Game")

# Classe do Sapo


class Frog:
    def __init__(self):
        self.rect = pygame.Rect(
            GAME_WIDTH // 2, SCREEN_HEIGHT - FROG_HEIGHT - 10, FROG_WIDTH, FROG_HEIGHT)
        self.has_scored = False

    def move(self, dx, dy):
        self.rect.x = max(0, min(self.rect.x + dx, GAME_WIDTH - FROG_WIDTH))
        self.rect.y = max(
            0, min(self.rect.y + dy, SCREEN_HEIGHT - FROG_HEIGHT))

    def draw(self):
        pygame.draw.rect(screen, GREEN, self.rect)

# Classe do Carro


class Car:
    def __init__(self, y):
        self.rect = pygame.Rect(GAME_WIDTH, y, CAR_WIDTH, CAR_HEIGHT)
        self.speed = random.randint(3, 10)

    def move(self):
        self.rect.x -= self.speed
        if self.rect.x < -CAR_WIDTH:
            self.rect.x = GAME_WIDTH
            self.rect.y = random.randint(100, SCREEN_HEIGHT - 100)
            self.speed = random.randint(3, 10)

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)

# Loop principal do jogo


def main():
    clock = pygame.time.Clock()
    frog = Frog()
    cars = [Car(random.randint(100, SCREEN_HEIGHT - 100)) for _ in range(5)]
    score = 0
    high_scores = [0, 0, 0]
    font = pygame.font.Font(None, 36)
    button_font = pygame.font.Font(None, 28)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if GAME_WIDTH + 50 <= x <= GAME_WIDTH + 150 and SCREEN_HEIGHT - 80 <= y <= SCREEN_HEIGHT - 50:
                    running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            frog.move(-5, 0)
        if keys[pygame.K_RIGHT]:
            frog.move(5, 0)
        if keys[pygame.K_UP]:
            frog.move(0, -5)
        if keys[pygame.K_DOWN]:
            frog.move(0, 5)

        for car in cars:
            car.move()

        for car in cars:
            if frog.rect.colliderect(car.rect):
                high_scores.append(score)
                high_scores = sorted(high_scores, reverse=True)[:3]
                score = 0
                frog.rect.y = SCREEN_HEIGHT - FROG_HEIGHT - 10
                frog.rect.x = GAME_WIDTH // 2
                frog.has_scored = False

        screen.fill(GRAY)
        pygame.draw.rect(screen, DARK_GREEN,
                         (0, 0, GAME_WIDTH, SAFE_ZONE_HEIGHT))
        pygame.draw.rect(screen, DARK_GREEN, (0, SCREEN_HEIGHT -
                         SAFE_ZONE_HEIGHT, GAME_WIDTH, SAFE_ZONE_HEIGHT))
        pygame.draw.rect(screen, LIGHT_GRAY, (GAME_WIDTH, 0,
                         PANEL_WIDTH, SCREEN_HEIGHT))  # Painel lateral

        frog.draw()
        for car in cars:
            car.draw()

        if frog.rect.y < SAFE_ZONE_HEIGHT and not frog.has_scored:
            score += 1
            frog.has_scored = True
        if frog.rect.y >= SCREEN_HEIGHT - FROG_HEIGHT:
            frog.has_scored = False

        title_text = font.render("Scoreboard", True, DARK_BLUE)
        screen.blit(title_text, (GAME_WIDTH + 50, 20))

        score_text = font.render(f"Score: {score}", True, BLUE)
        screen.blit(score_text, (GAME_WIDTH + 50, 60))

        for i, high_score in enumerate(high_scores):
            high_score_text = font.render(
                f"Top {i+1}: {high_score}", True, BLACK)
            screen.blit(high_score_text, (GAME_WIDTH + 50, 100 + i * 30))

        pygame.draw.rect(screen, WHITE, (GAME_WIDTH + 50,
                         SCREEN_HEIGHT - 80, 100, 30))
        exit_text = button_font.render("Sair", True, BLACK)
        screen.blit(exit_text, (GAME_WIDTH + 80, SCREEN_HEIGHT - 75))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
