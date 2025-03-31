import pygame
import random
import time
from fcntl import ioctl
import os

# Constantes para a placa física
HEX_0 = 0xC0
HEX_1 = 0xF9
HEX_2 = 0xA4
HEX_3 = 0xB0
HEX_4 = 0x99
HEX_5 = 0x92
HEX_6 = 0x82
HEX_7 = 0xF8
HEX_8 = 0x80
HEX_9 = 0x90
HEX_A = 0x88
HEX_B = 0x83
HEX_C = 0xC6
HEX_D = 0xA1
HEX_E = 0x86
HEX_F = 0x8E
LED_ALL_RED = 0x3FFFF
LED_ALL_GREEN = 0x1FF

PB = 24930
SW = 24929
DIS_L = 24931
DIS_R = 24932
LED_R = 24933
LED_G = 24934

# Inicializa o Pygame
pygame.init()

# Constantes do jogo
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
GAME_WIDTH = 800
PANEL_WIDTH = 200
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

class IO:
    def __init__(self) -> None:
        self.fd = os.open('/dev/mydev', os.O_RDWR)
        self.dev = SW

    def __del__(self):
        os.close(self.fd)

    def get_PB(self, pos):
        ioctl(self.fd, PB)
        pb_pos = (1 << pos)
        os.read(self.fd, 4)
        ret_pb = os.read(self.fd, 4)
        return 1 if (pb_pos & int.from_bytes(ret_pb, 'little')) > 0 else 0

    def put_LD_G(self, val):
        ioctl(self.fd, LED_G)
        os.write(self.fd, val.to_bytes(4, 'little'))

    def put_LD(self, val):
        ioctl(self.fd, LED_R)
        os.write(self.fd, val.to_bytes(4, 'little'))

    def put_DP(self, pos, ar_num):
         ioctl(self.fd, DIS_L if pos else DIS_R)
         data = 0
         for num in ar_num:
             data = (data << 8) | globals()[f'HEX_{num}']
         os.write(self.fd, data.to_bytes(4, 'little'))
 
    def reset_displays(self):
         for _ in range(8):
             self.put_DP(0, "00")
             self.put_DP(1, "00")

class Frog:
    def __init__(self):
        # Posição inicial centralizada na zona segura inferior
        start_x = GAME_WIDTH // 2 - FROG_WIDTH // 2
        start_y = SCREEN_HEIGHT - SAFE_ZONE_HEIGHT + (SAFE_ZONE_HEIGHT - FROG_HEIGHT) // 2
        self.rect = pygame.Rect(start_x, start_y, FROG_WIDTH, FROG_HEIGHT)
        self.has_scored = False

    def move(self, dx, dy):
        self.rect.x = max(0, min(self.rect.x + dx, GAME_WIDTH - FROG_WIDTH))
        self.rect.y = max(0, min(self.rect.y + dy, SCREEN_HEIGHT - FROG_HEIGHT))

    def draw(self):
        pygame.draw.rect(screen, GREEN, self.rect)

class Car:
    def __init__(self, y):
        self.rect = pygame.Rect(GAME_WIDTH, y, CAR_WIDTH, CAR_HEIGHT)
        self.speed = random.randint(3, 10)

    def move(self):
        self.rect.x -= self.speed
        if self.rect.x < -CAR_WIDTH:
            self.rect.x = GAME_WIDTH
            self.rect.y = random.randint(SAFE_ZONE_HEIGHT, SCREEN_HEIGHT - SAFE_ZONE_HEIGHT - CAR_HEIGHT)
            self.speed = random.randint(3, 10)

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)

def main():
    clock = pygame.time.Clock()
    frog = Frog()
    cars = [Car(random.randint(SAFE_ZONE_HEIGHT, SCREEN_HEIGHT - SAFE_ZONE_HEIGHT - CAR_HEIGHT)) for _ in range(5)]
    score = 0
    high_scores = [0, 0, 0]
    font = pygame.font.Font(None, 36)
    button_font = pygame.font.Font(None, 28)
    io = IO()

    io.reset_displays()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if io.get_PB(0):
            frog.move(-5, 0)
        if io.get_PB(1):
            frog.move(5, 0)
        if io.get_PB(2):
            frog.move(0, -5)
        if io.get_PB(3):
            frog.move(0, 5)

        for car in cars:
            car.move()

        for car in cars:
            if frog.rect.colliderect(car.rect):
                is_new_record = score > high_scores[0]
        
                if is_new_record:
                    io.put_LD_G(LED_ALL_GREEN)  # Acende os 9 LEDs verdes

                high_scores.append(score)
                high_scores = sorted(high_scores, reverse=True)[:3]
                io.put_LD(LED_ALL_RED)
                time.sleep(2)
                io.put_LD(0)
                io.put_LD_G(0)
                score = 0
                frog = Frog()  # Reseta a posição do sapo corretamente

        # Verifica se o sapo chegou na zona segura superior
        if frog.rect.y < SAFE_ZONE_HEIGHT and not frog.has_scored:
            score += 1
            frog.has_scored = True
        # Reseta o has_scored quando o sapo volta para a base
        if frog.rect.y >= SCREEN_HEIGHT - SAFE_ZONE_HEIGHT:
            frog.has_scored = False

        screen.fill(GRAY)
        pygame.draw.rect(screen, DARK_GREEN, (0, 0, GAME_WIDTH, SAFE_ZONE_HEIGHT))
        pygame.draw.rect(screen, DARK_GREEN, (0, SCREEN_HEIGHT - SAFE_ZONE_HEIGHT, GAME_WIDTH, SAFE_ZONE_HEIGHT))
        pygame.draw.rect(screen, LIGHT_GRAY, (GAME_WIDTH, 0, PANEL_WIDTH, SCREEN_HEIGHT))

        title_text = font.render("Scoreboard", True, DARK_BLUE)
        screen.blit(title_text, (GAME_WIDTH + 50, 20))

        score_text = font.render(f"Score: {score}", True, BLUE)
        screen.blit(score_text, (GAME_WIDTH + 50, 60))

        for i, high_score in enumerate(high_scores):
            high_score_text = font.render(f"Top {i+1}: {high_score}", True, BLACK)
            screen.blit(high_score_text, (GAME_WIDTH + 50, 100 + i * 30))

        frog.draw()
        for car in cars:
            car.draw()

        io.put_DP(0, str(score).zfill(2))
        io.put_DP(1, str(high_scores[0]).zfill(2))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()