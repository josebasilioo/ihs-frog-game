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

    def get_SW(self, pos):
        ioctl(self.fd, SW)
        sw_pos = (0x1 << pos)
        os.read(self.fd, 4)
        ret_sw = os.read(self.fd, 4)
        return 1 if (sw_pos & int.from_bytes(ret_sw, 'little')) > 0 else 0

    def get_PB(self, pos):
        ioctl(self.fd, PB)
        pb_pos = (1 << pos)
        os.read(self.fd, 4)
        ret_pb = os.read(self.fd, 4)
        data_ret = 1 if (pb_pos & int.from_bytes(ret_pb, 'little')) > 0 else 0
        return data_ret

    def put_LD(self, val):
        ioctl(self.fd, LED_R)
        os.write(self.fd, val.to_bytes(4, 'little'))

    def put_ar_LD(self, list_pos):
        ioctl(self.fd, LED_R)
        data = 0
        for num in list_pos:
            data = (1 << num) | data
        os.write(self.fd, data.to_bytes(4, 'little'))

    def put_DP(self, pos, ar_num):
        if pos == 0:
            ioctl(self.fd, DIS_R)
        else:
            ioctl(self.fd, DIS_L)

        data = 0
        for num in ar_num:
            data = self.__aux_DP(data, num, 8)
        os.write(self.fd, data.to_bytes(4, 'little'))

    def __aux_DP(self, data, num, ind):
        data = data << ind
        if num == '0':
            data = data | HEX_0
        elif num == '1':
            data = data | HEX_1
        elif num == '2':
            data = data | HEX_2
        elif num == '3':
            data = data | HEX_3
        elif num == '4':
            data = data | HEX_4
        elif num == '5':
            data = data | HEX_5
        elif num == '6':
            data = data | HEX_6
        elif num == '7':
            data = data | HEX_7
        elif num == '8':
            data = data | HEX_8
        elif num == '9':
            data = data | HEX_9
        elif num == 'A':
            data = data | HEX_A
        elif num == 'B':
            data = data | HEX_B
        elif num == 'C':
            data = data | HEX_C
        elif num == 'D':
            data = data | HEX_D
        elif num == 'E':
            data = data | HEX_E
        elif num == 'F':
            data = data | HEX_F
        return data


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


def main():
    clock = pygame.time.Clock()
    frog = Frog()
    cars = [Car(random.randint(100, SCREEN_HEIGHT - 100)) for _ in range(5)]
    score = 0
    high_scores = [0, 0, 0]
    font = pygame.font.Font(None, 36)
    button_font = pygame.font.Font(None, 28)
    io = IO()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Controle pelos botões físicos
        if io.get_PB(0):  # Esquerda
            frog.move(-5, 0)
        if io.get_PB(1):  # Direita
            frog.move(5, 0)
        if io.get_PB(2):  # Cima
            frog.move(0, -5)
        if io.get_PB(3):  # Baixo
            frog.move(0, 5)

        for car in cars:
            car.move()

        for car in cars:
            if frog.rect.colliderect(car.rect):
                got_top_1 = score > max(high_scores)

                high_scores.append(score)
                high_scores = sorted(high_scores, reverse=True)[:3]

                # LED vermelho por 5s (colisão)
                io.put_LD(1)
                time.sleep(5)
                io.put_LD(0)

                # LED verde por 5s se for top 1
                if got_top_1:
                    io.put_LD(2)
                    time.sleep(5)
                    io.put_LD(0)

                score = 0
                frog.rect.y = SCREEN_HEIGHT - FROG_HEIGHT - 10
                frog.rect.x = GAME_WIDTH // 2
                frog.has_scored = False

        screen.fill(GRAY)
        pygame.draw.rect(screen, DARK_GREEN,
                         (0, 0, GAME_WIDTH, SAFE_ZONE_HEIGHT))
        pygame.draw.rect(screen, DARK_GREEN, (0, SCREEN_HEIGHT -
                         SAFE_ZONE_HEIGHT, GAME_WIDTH, SAFE_ZONE_HEIGHT))
        pygame.draw.rect(screen, LIGHT_GRAY, (GAME_WIDTH,
                         0, PANEL_WIDTH, SCREEN_HEIGHT))

        frog.draw()
        for car in cars:
            car.draw()

        if frog.rect.y < SAFE_ZONE_HEIGHT and not frog.has_scored:
            score += 1
            frog.has_scored = True
        if frog.rect.y >= SCREEN_HEIGHT - FROG_HEIGHT:
            frog.has_scored = False

        # Interface gráfica
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

        # Atualiza o display de 7 segmentos
        score_str = str(score).zfill(4)
        io.put_DP(0, score_str[2:])
        io.put_DP(1, score_str[:2])

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
