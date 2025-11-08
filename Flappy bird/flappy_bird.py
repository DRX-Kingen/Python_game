import pygame, sys, random, os
from pygame.locals import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#os.chdir(r"D:\Python\Game")  


pygame.init()
WINDOWWIDTH = 400
WINDOWHEIGHT = 600
FPS = 60
fpsClock = pygame.time.Clock()

DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Flappy Bird')


BACKGROUND = pygame.image.load(os.path.join(BASE_DIR, "background.png"))
BIRDIMG = pygame.image.load(os.path.join(BASE_DIR, "bird.png"))
COLUMNIMG = pygame.image.load(os.path.join(BASE_DIR, "column.png"))


BIRDWIDTH = 60
BIRDHEIGHT = 45
G = 0.5
SPEEDFLY = -8
COLUMNWIDTH = 60
COLUMNHEIGHT = 500
BLANK = 160
DISTANCE = 200
COLUMNSPEED = 2
class BIRD():
    def __init__(self):
        self.width = BIRDWIDTH
        self.height = BIRDHEIGHT
        self.x = (WINDOWWIDTH - self.width) / 2
        self.y = (WINDOWHEIGHT - self.height) / 2
        self.speed = 0
        self.surface = BIRDIMG

    def draw(self):
        DISPLAYSURF.blit(self.surface, (int(self.x), int(self.y)))

    def update(self, mouseClick):
        self.y += self.speed + 0.5 * G
        self.speed += G
        if mouseClick:
            self.speed = SPEEDFLY
class COLUMN():
    def __init__(self, x):
        self.width = COLUMNWIDTH
        self.height = COLUMNHEIGHT
        self.blank = BLANK
        self.distance = DISTANCE
        self.speed = COLUMNSPEED
        self.surface = COLUMNIMG
        self.ls = []
        for i in range(3):
            _x = WINDOWWIDTH + i * self.distance + x
            y = random.randrange(60, WINDOWHEIGHT - self.blank - 60, 20)
            self.ls.append([_x, y])

    def draw(self):
        for i in range(3):
            DISPLAYSURF.blit(self.surface, (self.ls[i][0], self.ls[i][1] - self.height))
            DISPLAYSURF.blit(self.surface, (self.ls[i][0], self.ls[i][1] + self.blank))

    def update(self):
        for i in range(3):
            self.ls[i][0] -= self.speed
            if self.ls[i][0] < -self.width:
                self.ls[i][0] = self.ls[(i - 1) % 3][0] + self.distance
                self.ls[i][1] = random.randrange(60, WINDOWHEIGHT - self.blank - 60, 20)
class SCORE():
    def __init__(self):
        self.score = 0
        self.addScore = True

    def draw(self):
        font = pygame.font.SysFont('Arial', 30)
        scoresurface = font.render(str(self.score), True, (255, 255, 255))
        textsize = scoresurface.get_size()
        DISPLAYSURF.blit(scoresurface, ((WINDOWWIDTH - textsize[0]) / 2, 10))

    def update(self, bird, column):
        collision = False
        for i in range(3):
            rectScore = (column.ls[i][0] + column.width, column.ls[i][1], 1, column.blank)
            rectBird = (bird.x, bird.y, bird.width, bird.height)
            if rectCollision(rectBird, rectScore):
                collision = True
                break
        if collision and self.addScore:
            self.score += 1
            self.addScore = False
        if not collision:
            self.addScore = True
def rectCollision(rect1, rect2):
    if (rect1[0] + rect1[2] > rect2[0] and rect1[0] < rect2[0] + rect2[2] and
            rect1[1] + rect1[3] > rect2[1] and rect1[1] < rect2[1] + rect2[3]):
        return True
    return False
def isGameOver(bird, column):
    for i in range(3):
        rectBird = (bird.x, bird.y, bird.width, bird.height)
        rectColumn1 = (column.ls[i][0], column.ls[i][1] - column.height, column.width, column.height)
        rectColumn2 = (column.ls[i][0], column.ls[i][1] + column.blank, column.width, column.height)
        if rectCollision(rectBird, rectColumn1) or rectCollision(rectBird, rectColumn2):
            return True
    if bird.y < 0 or bird.y > WINDOWHEIGHT - bird.height:
        return True
    return False
def gameplay(bird, column, score):
    bird.__init__()
    column.__init__(0)
    score.__init__()

    while True:
        mouseClick = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                mouseClick = True

        DISPLAYSURF.blit(BACKGROUND, (0, 0))
        bird.update(mouseClick)
        bird.draw()
        column.draw()
        column.update()
        score.draw()
        score.update(bird, column)
        pygame.display.update()
        fpsClock.tick(FPS)

        if isGameOver(bird, column):
            return
def gamestart():
    fontBig = pygame.font.SysFont('Arial', 60)
    heading = fontBig.render('Flappy Bird', True, (255, 0, 0))
    fontSmall = pygame.font.SysFont('Arial', 25)
    comment = fontSmall.render('Click mouse to start', True, (255, 0, 0))

    while True:
        DISPLAYSURF.blit(BACKGROUND, (0, 0))
        DISPLAYSURF.blit(heading, ((WINDOWWIDTH - heading.get_width()) // 2, 200))
        DISPLAYSURF.blit(comment, ((WINDOWWIDTH - comment.get_width()) // 2, 350))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                return
def gameOver(score):
    fontBig = pygame.font.SysFont('Arial', 60)
    heading = fontBig.render('Game Over', True, (255, 100, 0))
    fontSmall = pygame.font.SysFont('Arial', 25)
    comment = fontSmall.render('Click to play again', True, (255, 100, 0))
    fontScore = pygame.font.SysFont('Arial', 30)
    scoreText = fontScore.render('Your Score: ' + str(score.score), True, (255, 100, 0))

    while True:
        DISPLAYSURF.blit(BACKGROUND, (0, 0))
        DISPLAYSURF.blit(heading, ((WINDOWWIDTH - heading.get_width()) // 2, 200))
        DISPLAYSURF.blit(scoreText, ((WINDOWWIDTH - scoreText.get_width()) // 2, 300))
        DISPLAYSURF.blit(comment, ((WINDOWWIDTH - comment.get_width()) // 2, 400))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                return
def main():
    bird = BIRD()
    column = COLUMN(0)
    score = SCORE()
    while True:
        gamestart()
        gameplay(bird, column, score)
        gameOver(score)


if __name__ == '__main__':
    main()
