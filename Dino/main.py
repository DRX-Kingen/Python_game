import pygame
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import random
pygame.init()

pygame.display.set_caption("DINO VUOT NGAN CHONG GAI")
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUNNING = [pygame.image.load(os.path.join(BASE_DIR,"Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join(BASE_DIR,"Assets/Dino", "DinoRun2.png"))]
JUMPING = pygame.image.load(os.path.join(BASE_DIR,"Assets/Dino", "DinoJump.png"))
DUCKING = [pygame.image.load(os.path.join(BASE_DIR,"Assets/Dino", "DinoDuck1.png")),
           pygame.image.load(os.path.join(BASE_DIR,"Assets/Dino", "DinoDuck2.png"))]

pygame.display.set_icon(RUNNING[0])

SMALL_CACTUS = [pygame.image.load(os.path.join(BASE_DIR,"Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join(BASE_DIR,"Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join(BASE_DIR,"Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join(BASE_DIR,"Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join(BASE_DIR,"Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join(BASE_DIR,"Assets/Cactus", "LargeCactus3.png"))]

base_cactus_img = LARGE_CACTUS[0]
new_width = base_cactus_img.get_width() * 2
new_height = base_cactus_img.get_height() * 2
GIANT_CACTUS_IMG = pygame.transform.scale(base_cactus_img, (new_width, new_height))
# -------------------------------------------------

BIRD = [pygame.image.load(os.path.join(BASE_DIR,"Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join(BASE_DIR,"Assets/Bird", "Bird2.png"))]

CLOUD = pygame.image.load(os.path.join(BASE_DIR,"Assets/Other", "Cloud.png"))
BG = pygame.image.load(os.path.join(BASE_DIR,"Assets/Other", "Track.png"))

class Dinosaur:
    X_POS_RIGHT = 80 
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.orig_duck_img = DUCKING
        self.orig_run_img = RUNNING
        self.orig_jump_img = JUMPING
        self.flipped_duck_img = [pygame.transform.flip(img, True, False) for img in DUCKING]
        self.flipped_run_img = [pygame.transform.flip(img, True, False) for img in RUNNING]
        self.flipped_jump_img = pygame.transform.flip(JUMPING, True, False)

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False
        self.facing_right = True 

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.orig_run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS_RIGHT 
        self.dino_rect.y = self.Y_POS
        
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, userInput):
        global game_direction
        
        if userInput[pygame.K_LEFT] and not self.dino_jump:
            self.facing_right = False
        elif userInput[pygame.K_RIGHT] and not self.dino_jump:
            self.facing_right = True
        game_direction = 1 if self.facing_right else -1
        
        if userInput[pygame.K_UP] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0
            
        if not self.dino_jump:
            if self.facing_right:
                self.dino_rect.x = self.X_POS_RIGHT
            else:
                current_width = self.dino_rect.width
                self.dino_rect.x = SCREEN_WIDTH - 80 - current_width

    def duck(self):
        duck_imgs = self.orig_duck_img if self.facing_right else self.flipped_duck_img
        self.image = duck_imgs[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1
        self.mask = pygame.mask.from_surface(self.image)

    def run(self):
        run_imgs = self.orig_run_img if self.facing_right else self.flipped_run_img
        self.image = run_imgs[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.y = self.Y_POS
        self.step_index += 1
        self.mask = pygame.mask.from_surface(self.image)

    def jump(self):
        self.image = self.orig_jump_img if self.facing_right else self.flipped_jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < - self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL
        self.mask = pygame.mask.from_surface(self.image) 

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self, current_speed, game_direction):
        self.x -= current_speed 
        
        if game_direction == 1 and self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)
        elif game_direction == -1 and self.x > SCREEN_WIDTH:
            self.x = -self.width - random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH
        self.mask = pygame.mask.from_surface(self.image[self.type])

    def update(self, obstacles_list, current_speed, game_direction):
        self.rect.x -= current_speed 
        
        if game_direction == 1 and self.rect.x < -self.rect.width:
            obstacles_list.remove(self)
        elif game_direction == -1 and self.rect.x > SCREEN_WIDTH:
            obstacles_list.remove(self) 

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 250
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        
        current_image = self.image[self.index//5]
        self.mask = pygame.mask.from_surface(current_image)
        
        SCREEN.blit(current_image, self.rect)
        self.index += 1


class GiantCactus(Obstacle):
    def __init__(self):
        self.image = {0: GIANT_CACTUS_IMG}
        self.type = 0
        super().__init__(self.image, self.type)
        self.rect.y = 380 - self.rect.height

def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, game_direction
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font('freesansbold.ttf', 20)
    obstacles = []
    death_count = 0    
    game_direction = 1
    last_game_direction = 1 
    
    obstacle_timer = 0
    SPAWN_TIME_MIN = 70
    SPAWN_TIME_MAX = 150
    obstacle_timer = SPAWN_TIME_MIN

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1

        text = font.render("Points: " + str(points), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (1000, 40)
        SCREEN.blit(text, textRect)

    def background(current_speed):
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        
        x_pos_bg -= current_speed
        
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (x_pos_bg - image_width, y_pos_bg))

        if x_pos_bg <= -image_width:
            x_pos_bg += image_width
        elif x_pos_bg >= image_width:
            x_pos_bg -= image_width

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        SCREEN.fill((255, 255, 255))
        userInput = pygame.key.get_pressed()

        current_speed = game_speed * game_direction

        player.draw(SCREEN)
        player.update(userInput)

        if game_direction != last_game_direction:
            obstacles.clear()
            last_game_direction = game_direction
        
        if obstacle_timer <= 0:
            rand_num = random.randint(0, 10)
            new_obstacle = None
            
            if rand_num < 4:
                new_obstacle = SmallCactus(SMALL_CACTUS)
            elif rand_num < 7:
                new_obstacle = LargeCactus(LARGE_CACTUS)
            elif rand_num < 9:
                new_obstacle = Bird(BIRD)
            elif rand_num == 9 and points > 500: 
                new_obstacle = GiantCactus()
            
            if new_obstacle:
                if game_direction == -1:
                    new_obstacle.rect.x = -new_obstacle.rect.width - random.randint(0, 300)
                else:
                    new_obstacle.rect.x = SCREEN_WIDTH + random.randint(0, 300)
                obstacles.append(new_obstacle)
            
            obstacle_timer = random.randint(SPAWN_TIME_MIN, SPAWN_TIME_MAX) - (game_speed // 2)

        else:
            obstacle_timer -= 1

        for obstacle in obstacles[:]:
            obstacle.draw(SCREEN)
            obstacle.update(obstacles, current_speed, game_direction)

            offset = (obstacle.rect.x - player.dino_rect.x, obstacle.rect.y - player.dino_rect.y)
            if player.mask.overlap(obstacle.mask, offset):
                pygame.time.delay(2000)
                death_count += 1
                menu(death_count)
                
        background(current_speed)

        cloud.draw(SCREEN)
        cloud.update(current_speed, game_direction)

        score()

        clock.tick(30)
        pygame.display.update()

def menu(death_count):
    global points, game_direction
    run = True
    
    points_at_death = 0 
    if death_count > 0:
        points_at_death = points 
    
    points = 0 
    game_direction = 1 
    # ---------------------
    
    while run:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font('freesansbold.ttf', 30)

        if death_count == 0:
            text = font.render("Press any Key to Start", True, (0, 0, 0))
        elif death_count > 0:
            text = font.render("Press any Key to Restart", True, (0, 0, 0))
            score_text = font.render("Your Score: " + str(points_at_death), True, (0, 0, 0))
            scoreRect = score_text.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score_text, scoreRect)
            
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
                exit()
            if event.type == pygame.KEYDOWN:
                main()

   


menu(death_count=0)