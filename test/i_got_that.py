import pygame
import sys
import random

# ---------- CONFIGURATION ----------
WIDTH, HEIGHT = 800, 600
FPS = 60

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)

# Initialisation pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jeu Complet 500 lignes")
clock = pygame.time.Clock()

# Polices
FONT_SMALL = pygame.font.SysFont("arial", 24)
FONT_LARGE = pygame.font.SysFont("arial", 48)

# Sons
pygame.mixer.init()
try:
    SOUND_COLLECT = pygame.mixer.Sound("collect.wav")
    SOUND_HIT = pygame.mixer.Sound("hit.wav")
except:
    SOUND_COLLECT = None
    SOUND_HIT = None

# ---------- CLASSES ----------

class Button:
    def __init__(self, text, pos, size=(200, 50), bg_color=BLUE, fg_color=WHITE):
        self.text = text
        self.pos = pos
        self.size = size
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.rect = pygame.Rect(pos, size)
        self.font = FONT_SMALL
        self.rendered_text = self.font.render(text, True, fg_color)
        self.text_rect = self.rendered_text.get_rect(center=self.rect.center)

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        surface.blit(self.rendered_text, self.text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.images = []
        # Charge images d'animation (ici carrés simples pour l'exemple)
        for i in range(4):
            surf = pygame.Surface((40, 50))
            surf.fill((0, 0, 255 - i*50))
            self.images.append(surf)
        self.current_frame = 0
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect(center=pos)
        self.speed = 5
        self.health = 100
        self.score = 0
        self.anim_timer = 0
        self.anim_speed = 100  # ms par frame

    def update(self, dt, walls):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed

        # Déplacement et collision
        self.move(dx, dy, walls)

        # Animation
        self.anim_timer += dt
        if self.anim_timer > self.anim_speed and (dx != 0 or dy != 0):
            self.current_frame = (self.current_frame + 1) % len(self.images)
            self.image = self.images[self.current_frame]
            self.anim_timer = 0
        elif dx == 0 and dy == 0:
            self.current_frame = 0
            self.image = self.images[self.current_frame]

    def move(self, dx, dy, walls):
        # Move horizontally and check collisions
        self.rect.x += dx
        self.collide(dx, 0, walls)
        # Move vertically and check collisions
        self.rect.y += dy
        self.collide(0, dy, walls)

    def collide(self, dx, dy, walls):
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if dx > 0:  # droite
                    self.rect.right = wall.rect.left
                if dx < 0:  # gauche
                    self.rect.left = wall.rect.right
                if dy > 0:  # bas
                    self.rect.bottom = wall.rect.top
                if dy < 0:  # haut
                    self.rect.top = wall.rect.bottom

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((35, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=pos)
        self.speed = 2
        self.direction = random.choice(["horizontal", "vertical"])
        self.move_dir = 1
        self.move_distance = 0
        self.max_distance = random.randint(50, 150)

    def update(self, walls, player):
        if self.direction == "horizontal":
            self.rect.x += self.move_dir * self.speed
            self.move_distance += self.speed
            if self.collide(walls):
                self.rect.x -= self.move_dir * self.speed
                self.move_dir *= -1
                self.move_distance = 0
            if self.move_distance >= self.max_distance:
                self.move_dir *= -1
                self.move_distance = 0
        else:
            self.rect.y += self.move_dir * self.speed
            self.move_distance += self.speed
            if self.collide(walls):
                self.rect.y -= self.move_dir * self.speed
                self.move_dir *= -1
                self.move_distance = 0
            if self.move_distance >= self.max_distance:
                self.move_dir *= -1
                self.move_distance = 0

        # IA simple : si proche joueur, se dirige vers lui
        if abs(self.rect.centerx - player.rect.centerx) < 120 and abs(self.rect.centery - player.rect.centery) < 120:
            if player.rect.centerx > self.rect.centerx:
                self.rect.x += self.speed
                if self.collide(walls):
                    self.rect.x -= self.speed
            else:
                self.rect.x -= self.speed
                if self.collide(walls):
                    self.rect.x += self.speed
            if player.rect.centery > self.rect.centery:
                self.rect.y += self.speed
                if self.collide(walls):
                    self.rect.y -= self.speed
            else:
                self.rect.y -= self.speed
                if self.collide(walls):
                    self.rect.y += self.speed

    def collide(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                return True
        return False

class Wall(pygame.sprite.Sprite):
    def __init__(self, rect):
        super().__init__()
        self.image = pygame.Surface((rect.width, rect.height))
        self.image.fill(GRAY)
        self.rect = rect

class Treasure(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=pos)

# ---------- FONCTIONS ----------

def draw_text(surface, text, font, color, pos):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def draw_health_bar(surface, x, y, health, max_health):
    ratio = health / max_health
    pygame.draw.rect(surface, RED, (x, y, 200, 25))
    pygame.draw.rect(surface, GREEN, (x, y, 200 * ratio, 25))

def create_walls():
    walls = []
    # Bordures
    walls.append(Wall(pygame.Rect(0, 0, WIDTH, 10)))
    walls.append(Wall(pygame.Rect(0, HEIGHT-10, WIDTH, 10)))
    walls.append(Wall(pygame.Rect(0, 0, 10, HEIGHT)))
    walls.append(Wall(pygame.Rect(WIDTH-10, 0, 10, HEIGHT)))

    # Murs intérieurs
    walls.append(Wall(pygame.Rect(150, 100, 10, 400)))
    walls.append(Wall(pygame.Rect(300, 0, 10, 350)))
    walls.append(Wall(pygame.Rect(450, 250, 10, 350)))
    walls.append(Wall(pygame.Rect(600, 100, 10, 400)))

    walls.append(Wall(pygame.Rect(150, 100, 160, 10)))
    walls.append(Wall(pygame.Rect(300, 350, 160, 10)))
    walls.append(Wall(pygame.Rect(450, 250, 160, 10)))
    walls.append(Wall(pygame.Rect(600, 100, 160, 10)))

    return walls

def create_enemies():
    enemies = pygame.sprite.Group()
    positions = [(200, 150), (400, 400), (650, 200), (700, 500)]
    for pos in positions:
        enemies.add(Enemy(pos))
    return enemies

def create_treasures():
    treasures = pygame.sprite.Group()
    positions = [(180, 500), (350, 320), (520, 400), (680, 500), (720, 150)]
    for pos in positions:
        treasures.add(Treasure(pos))
    return treasures

def game_over_screen():
    screen.fill(BLACK)
    draw_text(screen, "GAME OVER", FONT_LARGE, RED, (WIDTH//2 - 150, HEIGHT//2 - 60))
    draw_text(screen, "Appuyez sur R pour recommencer", FONT_SMALL, WHITE, (WIDTH//2 - 130, HEIGHT//2 + 10))
    draw_text(screen, "Appuyez sur ESC pour quitter", FONT_SMALL, WHITE, (WIDTH//2 - 110, HEIGHT//2 + 40))
    pygame.display.flip()

def win_screen(score):
    screen.fill(BLACK)
    draw_text(screen, "VOUS AVEZ GAGNÉ !", FONT_LARGE, GREEN, (WIDTH//2 - 200, HEIGHT//2 - 60))
    draw_text(screen, f"Score final : {score}", FONT_SMALL, WHITE, (WIDTH//2 - 80, HEIGHT//2 + 10))
    draw_text(screen, "Appuyez sur R pour recommencer", FONT_SMALL, WHITE, (WIDTH//2 - 130, HEIGHT//2 + 40))
    pygame.display.flip()

def main_menu():
    play_button = Button("Jouer", (WIDTH//2 - 100, HEIGHT//2 - 70))
    quit_button = Button("Quitter", (WIDTH//2 - 100, HEIGHT//2 + 10))

    running = True
    while running:
        screen.fill(BLACK)
        draw_text(screen, "JEU COMPLET PYTHON", FONT_LARGE, WHITE, (WIDTH//2 - 220, HEIGHT//4))
        mouse_pos = pygame.mouse.get_pos()

        play_button.draw(screen)
        quit_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.is_clicked(mouse_pos):
                    running = False
                if quit_button.is_clicked(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

def pause_menu():
    paused = True
    pause_text = FONT_LARGE.render("PAUSE", True, WHITE)
    instr_text = FONT_SMALL.render("Appuyez sur P pour reprendre", True, WHITE)
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False

        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//3))
        screen.blit(instr_text, (WIDTH//2 - instr_text.get_width()//2, HEIGHT//3 + 70))
        pygame.display.flip()
        clock.tick(15)

# ---------- BOUCLE PRINCIPALE ----------

def main():
    main_menu()
    walls = create_walls()
    walls_group = pygame.sprite.Group(walls)
    enemies = create_enemies()
    treasures = create_treasures()
    player = Player((50, HEIGHT - 60))

    running = True
    game_over = False
    win = False

    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_p:
                    pause_menu()

                if game_over or win:
                    if event.key == pygame.K_r:
                        main()
                        return

        if not game_over and not win:
            player.update(dt, walls)

            enemies.update(walls, player)

            # Collision joueur-ennemis
            if pygame.sprite.spritecollideany(player, enemies):
                if SOUND_HIT:
                    SOUND_HIT.play()
                player.health -= 1
                if player.health <= 0:
                    game_over = True

            # Collecter trésors
            collected = pygame.sprite.spritecollide(player, treasures, True)
            if collected:
                if SOUND_COLLECT:
                    SOUND_COLLECT.play()
                player.score += 10

            # Condition de victoire
            if len(treasures) == 0:
                win = True

        # Dessin
        screen.fill(GRAY)
        walls_group.draw(screen)
        treasures.draw(screen)
        enemies.draw(screen)
        screen.blit(player.image, player.rect)

        # HUD
        draw_health_bar(screen, 10, 10, player.health, 100)
        draw_text(screen, f"Vie : {player.health}", FONT_SMALL, WHITE, (220, 10))
        draw_text(screen, f"Score : {player.score}", FONT_SMALL, WHITE, (10, 40))
        draw_text(screen, "Collectez tous les trésors !", FONT_SMALL, WHITE, (10, 70))
        draw_text(screen, "Déplacement : flèches ou WASD", FONT_SMALL, WHITE, (10, HEIGHT - 30))
        draw_text(screen, "Pause : P", FONT_SMALL, WHITE, (WIDTH - 150, 10))

        if game_over:
            game_over_screen()
        if win:
            win_screen(player.score)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
