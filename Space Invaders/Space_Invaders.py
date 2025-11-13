
import pygame, os, sys, random
pygame.font.init()


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
ICON = pygame.image.load(resource_path("assets/pixel_ship_red_small.png"))
pygame.display.set_icon(ICON)
pygame.display.set_caption("Space Invaders - tàu mi ni bắn nhau")


RED_SPACE_SHIP = pygame.image.load(resource_path("assets/pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(resource_path("assets/pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(resource_path("assets/pixel_ship_blue_small.png"))

YELLOW_SPACE_SHIP = pygame.image.load(resource_path("assets/pixel_ship_yellow.png"))

RED_LASER = pygame.image.load(resource_path("assets/pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(resource_path("assets/pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(resource_path("assets/pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(resource_path("assets/pixel_laser_yellow.png"))

BG = pygame.transform.scale(
    pygame.image.load(resource_path("assets/space.png")), (WIDTH, HEIGHT)
)
pygame.mixer.init()
explosion_sound = pygame.mixer.Sound(resource_path("assets/explosion.flac"))
explosion_sound.set_volume(0.7)  


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (0 <= self.y <= height)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 2

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 0.5

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, point, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.score = 0
        self.point = point

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs[:]:
                    if laser.collision(obj):
                        self.score += self.point
                        objs.remove(obj)
                        explosion_sound.play()  
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(
            window, (255, 0, 0),
            (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10)
        )
        pygame.draw.rect(
            window, (0, 255, 0),
            (
                self.x,
                self.y + self.ship_img.get_height() + 10,
                self.ship_img.get_width() * (self.health / self.max_health),
                10,
            ),
        )

    def respawn(self, start_x, start_y):
        self.health = self.max_health
        self.x = start_x
        self.y = start_y


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER),
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 0.5


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 2
    point = 100

    main_font = pygame.font.Font(resource_path("assets/RobotoMono-Regular.ttf"), 40)
    lost_font = pygame.font.Font(resource_path("assets/RobotoMono-Regular.ttf"), 50)

    enemies = []
    wave_length = 5
    enemy_vel = 1
    player_vel = 7
    laser_vel = 10

    player = Player(300, 630, point)
    clock = pygame.time.Clock()
    lost = False
    lost_count = 0
    invincible = False
    invincible_timer = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))
        lives_label = main_font.render(f"{lives} Mạng", 1, (255, 255, 255))
        level_label = main_font.render(f"Level {level}", 1, (255, 255, 255))
        score_label = main_font.render(f"Điểm: {int(player.score)}", 1, (255, 255, 255))
        enemies_label = main_font.render(f"Còn {len(enemies)} địch", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(score_label, (10, 60))
        WIN.blit(enemies_label, (WIDTH - enemies_label.get_width() - 10, 60))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("Bạn đã thua", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 275))
            final_score_label = lost_font.render(f"Điểm đạt được: {int(player.score)}", 1, (0, 255, 255))
            WIN.blit(final_score_label, (WIDTH / 2 - final_score_label.get_width() / 2, 325))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        
        if invincible and pygame.time.get_ticks() - invincible_timer > 2000:
            invincible = False

        
        if player.health <= 0:
            lives -= 1
            if lives > 0:
                player.respawn(300, 630)
                invincible = True
                invincible_timer = pygame.time.get_ticks()
            elif lives == 0:
                lost = True
                
                while lost:
                    redraw_window()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            lost = False
                            run = False

        if lost:
            continue  
        if len(enemies) == 0:
            level += 1
            if level > 1:
                wave_length *= 1.25
                enemy_vel += 0.1
                player.point *= 1.5

            for i in range(int(wave_length)):
                enemy = Enemy(
                    random.randrange(50, WIDTH - 100),
                    random.randrange(-1500, -100),
                    random.choice(["red", "blue", "green"]),
                )
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player) and not invincible:
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.Font(resource_path("assets/RobotoMono-Regular.ttf"), 70)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title = title_font.render("Bấm để chơi...", 1, (255, 255, 255))
        WIN.blit(title, (WIDTH / 2 - title.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


if __name__ == "__main__":
    main_menu()
