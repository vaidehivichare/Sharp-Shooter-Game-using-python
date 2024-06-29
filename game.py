import pygame
pygame.init()

w_width = 500
w_height = 500
screen = pygame.display.set_mode((w_width, w_height))
pygame.display.set_caption("Sharp Shooter")

clock = pygame.time.Clock()
bg_img = pygame.image.load("bg_img.jpeg")
bg_img = pygame.transform.scale(bg_img, (w_width, w_height))
walkRight = [pygame.image.load(f'soldier/{i}.png') for i in range(1, 10)]
walkLeft = [pygame.image.load(f'soldier/L{i}.png') for i in range(1, 10)]
moveLeft = [pygame.image.load(f'enemy/L{i}.png') for i in range(1, 10)]
moveRight = [pygame.image.load(f'enemy/R{i}.png') for i in range(1, 10)]
font = pygame.font.SysFont("helvetica", 30, 1, 1)
score = 0
bulletsound = pygame.mixer.Sound("sounds/Bulletsound.mp3")
hitsound = pygame.mixer.Sound("sounds/Hit.mp3")
music = pygame.mixer.music.load("sounds/music.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.2)

class Player():
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel = 5
        self.is_jump = False
        self.jump_count = 10
        self.left = False
        self.right = False
        self.walkCount = 0
        self.standing = True
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.walkCount + 1 >= 27:
            self.walkCount = 0

        if not self.standing:
            if self.left:
                screen.blit(walkLeft[self.walkCount // 3], (self.x, self.y))
                self.walkCount += 1
            elif self.right:
                screen.blit(walkRight[self.walkCount // 3], (self.x, self.y))
                self.walkCount += 1
        else:
            if self.right:
                screen.blit(walkRight[0], (self.x, self.y))
            else:
                screen.blit(walkLeft[0], (self.x, self.y))

        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

    def touch(self):
        self.x = 0
        self.y = w_height - self.height
        self.is_jump = False
        self.jump_count = 10

class Projectile():
    def __init__(self, x, y, radius, color, direction):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.direction = direction
        self.vel = 8 * direction

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

class Enemy():
    def __init__(self, x, y, width, height, end, speed, health):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.walkCount = 0
        self.vel = speed
        self.path = [x, end]
        self.hitbox = pygame.Rect(self.x + 20, self.y, self.width - 40, self.height - 4)
        self.health = health
        self.visible = True

    def draw(self, screen):
        self.move()
        if self.visible:
            if self.walkCount + 1 >= 27:
                self.walkCount = 0

            if self.vel > 0:
                screen.blit(moveRight[self.walkCount // 3], (self.x, self.y))
                self.walkCount += 1
            else:
                screen.blit(moveLeft[self.walkCount // 3], (self.x, self.y))
                self.walkCount += 1

            pygame.draw.rect(screen, "grey", (self.hitbox[0], self.hitbox[1] - 20, 50, 10))
            pygame.draw.rect(screen, "green", (self.hitbox[0], self.hitbox[1] - 20, 50 - (5 * (9 - self.health)), 10))

        self.hitbox = pygame.Rect(self.x + 20, self.y, self.width - 40, self.height - 4)

    def move(self):
        if self.vel > 0:
            if self.x < self.path[1] - self.width + 20:
                self.x += self.vel
            else:
                self.vel = self.vel * -1
                self.x += self.vel
                self.walkCount = 0
        else:
            if self.x > self.path[0] - 20:
                self.x += self.vel
            else:
                self.vel = self.vel * -1
                self.x += self.vel
                self.walkCount = 0

    def respawn(self):
        self.visible = True
        self.health = 9

    def touch(self):
        hitsound.play()
        if self.health > 0:
            self.health -= 1
        else:
            self.visible = False

def DrawInGameLoop():
    screen.blit(bg_img, (0, 0))
    clock.tick(25)
    soldier.draw(screen)
    text = font.render("Score : " + str(score), 1, "red")
    screen.blit(text, (0, 10))
    enemy_instance.draw(screen)
    for bullet in bullets:
        bullet.draw(screen)
    pygame.display.flip()

soldier = Player(210, 435, 64, 64)
enemy_instance = Enemy(0, w_height - 64, 64, 64, w_width, 3, 9)
bullets = []
shoot = 0
done = True

while done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = False

    if enemy_instance.visible:
        if soldier.hitbox.colliderect(enemy_instance.hitbox):
            enemy_instance.vel = enemy_instance.vel * -1
            soldier.touch()

    if shoot > 0:
        shoot += 1
    if shoot > 3:
        shoot = 0

    for bullet in bullets:
        if enemy_instance.visible:
            if bullet.y - bullet.radius < enemy_instance.hitbox.y + enemy_instance.hitbox.height and bullet.y + bullet.radius > enemy_instance.hitbox.y:
                if bullet.x + bullet.radius > enemy_instance.hitbox.x and bullet.x - bullet.radius < enemy_instance.hitbox.x + enemy_instance.hitbox.width:
                    bullets.remove(bullet)
                    score += 1
                    enemy_instance.touch()

        if 0 < bullet.x < w_width:
            bullet.x += bullet.vel
        else:
            bullets.remove(bullet)

    if not enemy_instance.visible:
        enemy_instance.respawn()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE] and shoot == 0:
        bulletsound.play()
        direction = 1 if soldier.right else -1
        if len(bullets) < 5:
            bullets.append(Projectile((soldier.x + soldier.width // 2), (soldier.y + soldier.height // 2), 6, "black", direction))
        shoot = 1

    if keys[pygame.K_LEFT] and soldier.x > 0:
        soldier.x -= soldier.vel
        soldier.left = True
        soldier.right = False
        soldier.standing = False
    elif keys[pygame.K_RIGHT] and soldier.x < w_width - soldier.width:
        soldier.x += soldier.vel
        soldier.right = True
        soldier.left = False
        soldier.standing = False
    else:
        soldier.standing = True
        soldier.walkCount = 0

    if not soldier.is_jump:
        if keys[pygame.K_UP]:
            soldier.is_jump = True
            soldier.right = False
            soldier.left = False
    else:
        if soldier.jump_count >= -10:
            neg = 1
            if soldier.jump_count < 0:
                neg = -1
            soldier.y -= (soldier.jump_count ** 2) * neg * 0.5
            soldier.jump_count -= 1
        else:
            soldier.jump_count = 10
            soldier.is_jump = False

    DrawInGameLoop()

pygame.quit()
