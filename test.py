import pygame
import random
import time

pygame.init()

# === Asset paths ===
IMG_ROCKET = "assets/images/player/PlayerBlue.png"
IMG_ENEMY = "assets/images/enemy/enemy01.png"
IMG_ASTEROID = "assets/images/asteroid/asteroid.png"
IMG_BULLET = "assets/images/bullet/laser.png"
IMG_BACKGROUND = "assets/images/background/galaxy05.jpg"
SOUND_SHOOT = "assets/sounds/laser.wav"
MUSIC_BACKGROUND = "assets/sounds/space.ogg"
EXPLOSION_SOUND = "assets/sounds/explosion01.mp3"

# === Game loop variables ===
game = True
pause = False
score = 0
missed = 0
goal = 100
clock = pygame.time.Clock()
FPS = 60

# === Explosion animation ===
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []
        for num in range(1, 8):
            img = pygame.image.load(f"assets/images/explosion/regularExplosion0{num}.png")
            img = pygame.transform.scale(img, (100, 100))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.counter = 0

    def update(self):
        explosion_speed = 5  # Adjust speed as needed
        self.counter += 1
        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()

# === GameSprite class ===
class GameSprite(pygame.sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, player_width, player_height, player_speed):
        super().__init__()
        self.image = pygame.transform.scale(
            pygame.image.load(player_image),
            (player_width, player_height)
        )
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# === Player class ===
class Player(GameSprite):
    def __init__(self, *kwargs):
        super().__init__(*kwargs)
        self.last_shot_time = 0
        self.cooldown = 250

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.x < win_width - 70:
            self.rect.x += self.speed
        if keys[pygame.K_s] and self.rect.y < win_height -70:
            self.rect.y += self.speed
        if keys[pygame.K_w] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[pygame.K_SPACE]:
            curent_time = pygame.time.get_ticks()
            if curent_time - self.last_shot_time >= self.cooldown:
                self.fire()
                self.last_shot_time = curent_time
            
    def fire(self):
        bullet = Bullet(IMG_BULLET, self.rect.centerx, self.rect.y, 15, 50, 40)
        bullets.add(bullet)
        shoot_sound.play()

# === Enemy class ===
class Enemy(GameSprite):
    def update(self):
        global missed
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.y = -50
            self.rect.x = random.randint(5, 715)
            missed += 1

# === Bullet class ===
class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()

# === Asteroid class ===
class Asteroid(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.y = -50
            self.rect.x = random.randint(5, 715)

# === Window and UI setup ===
win_width = 800
win_height = 600

background = pygame.transform.scale(
    pygame.image.load(IMG_BACKGROUND),
    (win_width, win_height)
)

pygame.mixer.music.load(MUSIC_BACKGROUND)
pygame.mixer.music.play()

shoot_sound = pygame.mixer.Sound(SOUND_SHOOT)
explode_sound = pygame.mixer.Sound(EXPLOSION_SOUND)

window = pygame.display.set_mode((win_width, win_height))

rocket = Player(IMG_ROCKET, 5, win_height - 105, 80, 100, 4)

enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
explosions = pygame.sprite.Group()

for i in range(6):
    enemies.add(Enemy(IMG_ENEMY, random.randint(5, 715), -50, 80, 50, random.randint(1, 3)))

for i in range(6):
    asteroids.add(Enemy(IMG_ASTEROID, random.randint(5, 715), -50, 80, 50, random.randint(1, 3)))

# === Fonts and texts ===
font = pygame.font.Font(None, 70)
lose = font.render("YOU LOSE!", True, "red")
win = font.render("YOU WIN!", True, "green")
font2 = pygame.font.Font(None, 40)


# === Main loop ===
while game:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            game = False

    if not pause:
        rocket.update()
        enemies.update()
        bullets.update()
        explosions.update()

        window.blit(background, (0, 0))
        rocket.reset()
        bullets.draw(window)
        enemies.draw(window)
        asteroids.draw(window)
        explosions.draw(window)

        collides = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for enemy in collides:
            enemies.add(Enemy(IMG_ENEMY, random.randint(5, 715), -50, 80, 50, random.randint(1, 3)))
            score += 1
            explosion = Explosion(enemy.rect.centerx,enemy.rect.centery)
            explosions.add(explosion)
            explode_sound.play()

        if pygame.sprite.spritecollide(rocket, enemies, False, pygame.sprite.collide_mask):
            pause = True
            lose_rect = lose.get_rect(center=(win_width / 2, win_height / 2))
            window.blit(lose, lose_rect)
        score_text = font2.render(f"Score: {score}", True, "white")
        miss_text = font2.render(f"Missed: {missed}", True, "white")

        window.blit(score_text, (10, 20))
        window.blit(miss_text, (10, 50))
        if score >= goal:
            pause = True
            win_rect = win.get_rect(center=(win_width / 2, win_height / 2))
            window.blit(win, win_rect)
        if  missed >= 5:
            pause = True
            lose_rect = lose.get_rect(center=(win_width / 2, win_height / 2))
            window.blit(lose, lose_rect)
        pygame.display.update()

    else:
        pause = False
        score = 0
        missed = 0
        lost = 0
        num_fire = 0
        life = 3

        bullets.empty()
        enemies.empty()

        time.sleep(3)

        for _ in range(5):
            enemies.add(Enemy(IMG_ENEMY, random.randint(5, 715), -50, 80, 50, random.randint(1, 3)))

    clock.tick(FPS)
    ádasd
    áda
    sda
    sda
    sd