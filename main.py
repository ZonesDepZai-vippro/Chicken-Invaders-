import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
CYAN = (0, 200, 255)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chicken Invaders!")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# Difficulty settings
DIFFICULTY = {
    "easy": {"hp": 3, "enemy_speed": 1, "drop_rate": 0.005, "boss_hp": 500},
    "normal": {"hp": 5, "enemy_speed": 2, "drop_rate": 0.01, "boss_hp": 1000},
    "hard": {"hp": 8, "enemy_speed": 3, "drop_rate": 0.02, "boss_hp": 1500},
}

# Player class
class Player:
    def __init__(self, hp):
        self.width = 40
        self.height = 60
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 80
        self.speed = 6
        self.bullets = []
        self.cooldown = 0
        self.hp = hp
        self.mana = 0
        self.max_mana = 100
        self.laser_active = False
        self.laser_timer = 0

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

    def shoot(self):
        if self.cooldown == 0:
            bullet = pygame.Rect(self.x + self.width // 2 - 3, self.y, 6, 15)
            self.bullets.append(bullet)
            self.cooldown = 10

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        for bullet in self.bullets[:]:
            bullet.y -= 10
            if bullet.y < 0:
                self.bullets.remove(bullet)
        if self.laser_active:
            self.laser_timer -= 1
            if self.laser_timer <= 0:
                self.laser_active = False

    def activate_laser(self):
        if self.mana >= self.max_mana and not self.laser_active:
            self.laser_active = True
            self.laser_timer = 30  # frames laser stays active
            self.mana = 0

    def draw(self, screen):
        # Placeholder rocket (triangle)
        pygame.draw.polygon(screen, BLUE, [
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height),
            (self.x + self.width // 2, self.y)
        ])
        for bullet in self.bullets:
            pygame.draw.rect(screen, YELLOW, bullet)
        # Draw laser if active
        if self.laser_active:
            pygame.draw.rect(screen, CYAN, (self.x + self.width//2 - 5, 0, 10, self.y))

# Enemy class (Chicken)
class Enemy:
    def __init__(self, x, y, speed, drop_rate):
        self.width = 40
        self.height = 40
        self.x = x
        self.y = y
        self.direction = 1
        self.speed = speed
        self.drop_rate = drop_rate
        self.eggs = []

    def update(self):
        self.x += self.direction * self.speed
        if self.x <= 0 or self.x + self.width >= SCREEN_WIDTH:
            self.direction *= -1
            self.y += 20
        if random.random() < self.drop_rate:
            egg = pygame.Rect(self.x + self.width//2 - 5, self.y + self.height, 10, 15)
            self.eggs.append(egg)
        for egg in self.eggs[:]:
            egg.y += 5
            if egg.y > SCREEN_HEIGHT:
                self.eggs.remove(egg)

    def draw(self, screen):
        # Placeholder chicken (oval + red comb)
        pygame.draw.ellipse(screen, WHITE, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(screen, RED, (self.x + self.width//2, self.y), 8)
        for egg in self.eggs:
            pygame.draw.ellipse(screen, WHITE, egg)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Boss class - giant chicken placeholder + supports
class Boss:
    def __init__(self, hp):
        self.image = None  # reserved for sprite if you add one later
        self.width = 160   # bigger size for giant chicken
        self.height = 140
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = 40
        self.hp = hp
        self.max_hp = hp
        self.eggs = []
        self.direction = 1
        self.supports = []

    def update(self):
        # eggs drop
        if random.random() < 0.05:
            egg = pygame.Rect(self.x + self.width//2 - 5, self.y + self.height, 12, 18)
            self.eggs.append(egg)
        for egg in self.eggs[:]:
            egg.y += 7
            if egg.y > SCREEN_HEIGHT:
                self.eggs.remove(egg)

        # Move left-right (boss patrol)
        self.x += self.direction * 2
        if self.x <= 0 or self.x + self.width >= SCREEN_WIDTH:
            self.direction *= -1

        # Ulti: summon support chickens occasionally
        if random.random() < 0.01:
            for i in range(random.randint(2, 4)):
                # spawn minion below boss
                chick_x = max(0, min(SCREEN_WIDTH-40, self.x + random.randint(-40, 40)))
                chick = Enemy(chick_x, self.y + self.height + 10, 1, 0.01)
                self.supports.append(chick)

        # Update supports
        for c in self.supports[:]:
            c.update()
            # remove supports that go off-screen or fall below bottom
            if c.y > SCREEN_HEIGHT + 50:
                try:
                    self.supports.remove(c)
                except ValueError:
                    pass

    def draw(self, screen):
        # Draw giant chicken body
        pygame.draw.ellipse(screen, WHITE, (self.x, self.y, self.width, self.height))          # body
        # comb
        pygame.draw.circle(screen, RED, (int(self.x + self.width*0.5), int(self.y + 10)), 20)
        # eyes
        pygame.draw.circle(screen, BLACK, (int(self.x + self.width*0.33), int(self.y + 40)), 6)
        pygame.draw.circle(screen, BLACK, (int(self.x + self.width*0.66), int(self.y + 40)), 6)
        # beak (triangle)
        pygame.draw.polygon(screen, YELLOW, [
            (int(self.x + self.width*0.5 - 8), int(self.y + 60)),
            (int(self.x + self.width*0.5 + 8), int(self.y + 60)),
            (int(self.x + self.width*0.5), int(self.y + 75))
        ])

        # Draw eggs dropped by boss
        for egg in self.eggs:
            pygame.draw.ellipse(screen, WHITE, egg)

        # HP bar
        bar_x, bar_y, bar_w, bar_h = 200, 20, 400, 20
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_w, bar_h))
        hp_w = int(bar_w * (self.hp / self.max_hp))
        hp_w = max(0, min(bar_w, hp_w))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, hp_w, bar_h))

        # Draw supports (minions)
        for c in self.supports:
            c.draw(screen)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Menu function
def menu():
    while True:
        screen.fill(BLACK)
        title = font.render("Choose Difficulty: 1-Easy  2-Normal  3-Hard", True, WHITE)
        screen.blit(title, (100, 250))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "easy"
                if event.key == pygame.K_2:
                    return "normal"
                if event.key == pygame.K_3:
                    return "hard"

# Game function
def main():
    difficulty = menu()
    settings = DIFFICULTY[difficulty]

    player = Player(settings["hp"])
    wave = 1
    total_waves = 10
    enemies = [Enemy(x*60+100, y*50+50, settings["enemy_speed"], settings["drop_rate"]) for x in range(6) for y in range(3)]
    boss = None
    score = 0
    running = True
    game_over = False
    win = False

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    player.shoot()
                if event.key == pygame.K_k and not game_over:
                    player.activate_laser()
                if event.key == pygame.K_RETURN and game_over:
                    return main()

        keys = pygame.key.get_pressed()
        if not game_over:
            player.move(keys)
            player.update()

            for enemy in enemies[:]:
                enemy.update()
                for bullet in player.bullets[:]:
                    if bullet.colliderect(enemy.get_rect()):
                        player.bullets.remove(bullet)
                        enemies.remove(enemy)
                        score += 10
                        player.mana = min(player.max_mana, player.mana + 5)
                        break
                for egg in enemy.eggs[:]:
                    if egg.colliderect(pygame.Rect(player.x, player.y, player.width, player.height)):
                        enemy.eggs.remove(egg)
                        player.hp -= 1

            # Laser effect on enemies (vertical strip)
            if player.laser_active:
                px_center = player.x + player.width // 2
                for enemy in enemies[:]:
                    if abs((enemy.x + enemy.width//2) - px_center) < 10:   # narrow beam
                        enemies.remove(enemy)
                        score += 10

            # Wave progression
            if not enemies and boss is None:
                if wave % 5 == 0:  # Boss at wave 5 and 10
                    boss = Boss(settings["boss_hp"])
                else:
                    wave += 1
                    if wave <= total_waves:
                        enemies = [Enemy(x*60+100, y*50+50, settings["enemy_speed"], settings["drop_rate"]) for x in range(6) for y in range(3)]

            if boss:
                boss.update()
                for bullet in player.bullets[:]:
                    if bullet.colliderect(boss.get_rect()):
                        player.bullets.remove(bullet)
                        boss.hp -= 5
                        score += 5
                        player.mana = min(player.max_mana, player.mana + 2)
                        boss.hp = max(boss.hp, 0)
                if player.laser_active:
                    px_center = player.x + player.width // 2
                    if abs((boss.x + boss.width//2) - px_center) < 10:
                        boss.hp -= 50
                        boss.hp = max(boss.hp, 0)
                for egg in boss.eggs[:]:
                    if egg.colliderect(pygame.Rect(player.x, player.y, player.width, player.height)):
                        boss.eggs.remove(egg)
                        player.hp -= 1
                # Collisions with supports
                for c in boss.supports[:]:
                    for bullet in player.bullets[:]:
                        if bullet.colliderect(c.get_rect()):
                            player.bullets.remove(bullet)
                            try:
                                boss.supports.remove(c)
                            except ValueError:
                                pass
                            score += 5
                            player.mana = min(player.max_mana, player.mana + 3)
                            break
                    for egg in c.eggs[:]:
                        if egg.colliderect(pygame.Rect(player.x, player.y, player.width, player.height)):
                            c.eggs.remove(egg)
                            player.hp -= 1
                if boss.hp <= 0:
                    boss = None
                    wave += 1
                    if wave > total_waves:
                        game_over = True
                        win = True
                    else:
                        enemies = [Enemy(x*60+100, y*50+50, settings["enemy_speed"], settings["drop_rate"]) for x in range(6) for y in range(3)]

            if player.hp <= 0:
                game_over = True
                win = False

        # Drawing
        screen.fill(BLACK)
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        if boss:
            boss.draw(screen)

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        hp_text = font.render(f"HP: {player.hp}", True, WHITE)
        screen.blit(hp_text, (10, 40))
        wave_text = font.render(f"Wave: {wave}/{total_waves}", True, WHITE)
        screen.blit(wave_text, (10, 70))
        mana_text = font.render(f"Mana: {player.mana}/{player.max_mana}", True, CYAN)
        screen.blit(mana_text, (10, 100))

        if game_over:
            if win:
                over_text = font.render("YOU WIN! - Press Enter to Restart", True, WHITE)
            else:
                over_text = font.render("GAME OVER - Press Enter to Restart", True, WHITE)
            screen.blit(over_text, (200, SCREEN_HEIGHT//2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
