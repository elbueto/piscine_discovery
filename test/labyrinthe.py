import pygame
import random
import sys
import math
import time

pygame.init()

# Config
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎮 Survivor Square")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (0, 100, 255)
ENEMY_COLOR = (255, 50, 50)
BG_COLOR = (30, 30, 30)

# Joueur
player_size = 30
player = pygame.Rect(WIDTH//2, HEIGHT//2, player_size, player_size)
player_speed = 5

# Ennemis
enemies = []
spawn_delay = 1000  # ms
last_spawn = pygame.time.get_ticks()

# Score
start_time = time.time()
font = pygame.font.SysFont("Arial", 28)
game_over = False

def draw_text(text, x, y, color=WHITE, center=True):
    render = font.render(text, True, color)
    rect = render.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    WIN.blit(render, rect)

def spawn_enemy():
    side = random.choice(["top", "bottom", "left", "right"])
    size = 25
    if side == "top":
        x, y = random.randint(0, WIDTH - size), -size
    elif side == "bottom":
        x, y = random.randint(0, WIDTH - size), HEIGHT
    elif side == "left":
        x, y = -size, random.randint(0, HEIGHT - size)
    else:
        x, y = WIDTH, random.randint(0, HEIGHT - size)

    speed = random.uniform(1.5, 2.5)
    enemies.append({"rect": pygame.Rect(x, y, size, size), "speed": speed})

def move_enemies():
    for enemy in enemies:
        dx = player.centerx - enemy["rect"].centerx
        dy = player.centery - enemy["rect"].centery
        dist = math.hypot(dx, dy)
        if dist == 0: continue
        dx, dy = dx / dist, dy / dist
        enemy["rect"].x += int(dx * enemy["speed"])
        enemy["rect"].y += int(dy * enemy["speed"])

def reset_game():
    global enemies, player, start_time, game_over
    enemies = []
    player.topleft = (WIDTH//2, HEIGHT//2)
    start_time = time.time()
    game_over = False

def main():
    global last_spawn, game_over

    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)
        WIN.fill(BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if not game_over:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: player.x -= player_speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player.x += player_speed
            if keys[pygame.K_UP] or keys[pygame.K_w]: player.y -= player_speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: player.y += player_speed

            # Garder le joueur dans la fenêtre
            player.clamp_ip(WIN.get_rect())

            # Ennemis
            move_enemies()
            now = pygame.time.get_ticks()
            if now - last_spawn > spawn_delay:
                spawn_enemy()
                last_spawn = now

            # Collision
            for enemy in enemies:
                if player.colliderect(enemy["rect"]):
                    game_over = True
                    break

            # Score
            survival_time = round(time.time() - start_time, 1)
            draw_text(f"Temps de survie : {survival_time} s", WIDTH//2, 30)

        else:
            draw_text("💀 GAME OVER 💀", WIDTH//2, HEIGHT//2 - 50)
            draw_text("Appuie sur R pour rejouer", WIDTH//2, HEIGHT//2 + 10)
            if keys[pygame.K_r]:
                reset_game()

        # Dessin
        pygame.draw.rect(WIN, PLAYER_COLOR, player)
        for enemy in enemies:
            pygame.draw.rect(WIN, ENEMY_COLOR, enemy["rect"])

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
