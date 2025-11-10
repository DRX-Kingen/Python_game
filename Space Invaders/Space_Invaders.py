import pygame, os, time, random, sys


pygame.init()
pygame.font.init()

try:
    pygame.mixer.init()
except Exception as e:
    print("Warning: pygame.mixer.init() failed:", e)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")


def load_image_safe(name, convert_alpha=True):
    path = os.path.join(ASSET_DIR, name)
    if not os.path.exists(path):
        print(f"ERROR: missing image: {path}")
        pygame.quit(); sys.exit()
    img = pygame.image.load(path)
    return img.convert_alpha() if convert_alpha else img.convert()

def load_sound_safe(name):
    path = os.path.join(ASSET_DIR, name)
    if not os.path.exists(path):
        print(f"Warning: missing sound: {path} (continuing without it)")
        return None
    try:
        return pygame.mixer.Sound(path)
    except Exception as e:
        print(f"Warning: failed to load sound {path}: {e}")
        return None


WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")


ICON = load_image_safe("pixel_ship_red_small.png")
pygame.display.set_icon(ICON)

RED_SPACE_SHIP = load_image_safe("pixel_ship_red_small.png")
GREEN_SPACE_SHIP = load_image_safe("pixel_ship_green_small.png")
BLUE_SPACE_SHIP = load_image_safe("pixel_ship_blue_small.png")
YELLOW_SPACE_SHIP = load_image_safe("pixel_ship_yellow.png")

RED_LASER = load_image_safe("pixel_laser_red.png")
GREEN_LASER = load_image_safe("pixel_laser_green.png")
BLUE_LASER = load_image_safe("pixel_laser_blue.png")
YELLOW_LASER = load_image_safe("pixel_laser_yellow.png")

BG = pygame.transform.scale(load_image_safe("space.png", convert_alpha=False), (WIDTH, HEIGHT))


FONT_FILE = os.path.join(ASSET_DIR, "RobotoMono-Regular.ttf")
if not os.path.exists(FONT_FILE):
    print(f"Warning: font not found at {FONT_FILE}. Will try default system font.")
    

SHOOT_SOUND = load_sound_safe("shoot.flac")
EXPLOSION_SOUND = load_sound_safe("explosion.flac")

if SHOOT_SOUND:
    SHOOT_SOUND.set_volume(0.25)
if EXPLOSION_SOUND:
    EXPLOSION_SOUND.set_volume(0.35)


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
        if self.ship_img:
            window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                try:
                    self.lasers.remove(laser)
                except ValueError:
                    pass
            elif laser.collision(obj):
                obj.health -= 10
                try:
                    self.lasers.remove(laser)
                except ValueError:
                    pass

    def cooldown(self):
        
        if self.cool_down_counter > 0:
            self.cool_down_counter += 1
            if self.cool_down_counter >= self.COOLDOWN:
                self.cool_down_counter = 0

    def shoot(self):
        if self.cool_down_counter == 0:
           
            laser_x = self.x + (self.get_width() // 2) - (self.laser_img.get_width() // 2)
            laser = Laser(laser_x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            if SHOOT_SOUND:
                try:
                    SHOOT_SOUND.play()
                except Exception:
                    pass

    def get_width(self):
        return self.ship_img.get_width() if self.ship_img else 0

    def get_height(self):
        return self.ship_img.get_height() if self.ship_img else 0


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
                try:
                    self.lasers.remove(laser)
                except ValueError:
                    pass
            else:
                for obj in objs[:]:
                    if laser.collision(obj):
                        self.score += self.point
                        try:
                            objs.remove(obj)
                        except ValueError:
                            pass
                        try:
                            if laser in self.lasers:
                                self.lasers.remove(laser)
                        except ValueError:
                            pass
                        if EXPLOSION_SOUND:
                            try:
                                EXPLOSION_SOUND.play()
                            except Exception:
                                pass
                        break  

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        health_width = int(self.ship_img.get_width() * (self.health / self.max_health))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, health_width, 10))


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            
            laser_x = self.x + (self.get_width() // 2) - (self.laser_img.get_width() // 2)
            laser = Laser(laser_x, self.y + self.get_height(), self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            if SHOOT_SOUND:
                try:
                    SHOOT_SOUND.play()
                except Exception:
                    pass



def collide(obj1, obj2):
    offset_x = int(obj2.x - obj1.x)
    offset_y = int(obj2.y - obj1.y)
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None



def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    point = 100

   
    if os.path.exists(FONT_FILE):
        main_font = pygame.font.Font(FONT_FILE, 40)
        lost_font = pygame.font.Font(FONT_FILE, 50)
    else:
        main_font = pygame.font.SysFont("Roboto", 40)
        lost_font = pygame.font.SysFont("Roboto", 50)

    enemies = []
    wave_length = 5
    enemy_vel = 1
    player_vel = 7
    laser_vel = 10

    player = Player(300, 630, point)
    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

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
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 275))
            final_score_label = lost_font.render(f"Điểm đạt được: {player.score}", 1, (0, 255, 255))
            WIN.blit(final_score_label, (WIDTH/2 - final_score_label.get_width()/2, 325))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            if level > 1:
                
                wave_length = int(wave_length * 1.25)
                enemy_vel += 0.1
                player.point = int(player.point * 1.5)
            print("wv len: ", wave_length, "enemy vel: ", enemy_vel, "point: ", player.point)
            for i in range(int(wave_length)):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player.x - player_vel > 0:
            player.x -= player_vel
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and player.y - player_vel > 0:
            player.y -= player_vel
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player.y + player_vel + player.get_height() + 15 < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                try:
                    enemies.remove(enemy)
                except ValueError:
                    pass
                if EXPLOSION_SOUND:
                    try:
                        EXPLOSION_SOUND.play()
                    except Exception:
                        pass
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                try:
                    enemies.remove(enemy)
                except ValueError:
                    pass

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    
    if os.path.exists(FONT_FILE):
        title_font = pygame.font.Font(FONT_FILE, 70)
    else:
        title_font = pygame.font.SysFont("Roboto", 70)

    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title = title_font.render("START GAME...", 1, (255, 255, 255))
        WIN.blit(title, (WIDTH/2 - title.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main_menu()
