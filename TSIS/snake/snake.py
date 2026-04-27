import random, pygame, sys

try:
    import psycopg2
except ImportError:
    psycopg2 = None

from pygame.locals import *


#SETTINGS
BASE_FPS = 10
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20

assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."

CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

DB_CONFIG = {
    "host": "localhost",
    "dbname": "pygame_db",
    "user": "postgres",
    "password": "98v898v8A@",
    "port": 5432
}

PLAYER_NAME = "Player"
DB_CONN = None
DB_CUR = None


#COLORS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 155, 0)
DARKGRAY = (40, 40, 40)
YELLOW = (255, 215, 0)
BLUE = (0, 100, 255)
LIGHT_GREEN = (50, 255, 50)
BGCOLOR = BLACK


#DIRECTIONS

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0


#MAIN

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT
    global PLAYER_NAME, DB_CONN, DB_CUR

    PLAYER_NAME = input("Enter player name: ")

    if PLAYER_NAME.strip() == "":
        PLAYER_NAME = "Player"

    DB_CONN, DB_CUR = connectDB()

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Snake')


    while True:
        score, level, foods_eaten = runGame()

        saveScore(PLAYER_NAME, score, level, foods_eaten)
        top_scores = getTopScores()

        showGameOverScreen(score, level, top_scores)


#DATABASE
def connectDB():
    if psycopg2 is None:
        print("psycopg2 is not installed. Database is disabled.")
        return None, None

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS snake_scores (
                id SERIAL PRIMARY KEY,
                player_name VARCHAR(50),
                score INT,
                level INT,
                foods_eaten INT,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        print("Database connected.")
        return conn, cur

    except Exception as error:
        print("Database error:", error)
        return None, None


def saveScore(player_name, score, level, foods_eaten):
    if DB_CONN is None or DB_CUR is None:
        return

    try:
        DB_CUR.execute(
            """
            INSERT INTO snake_scores (player_name, score, level, foods_eaten)
            VALUES (%s, %s, %s, %s)
            """,
            (player_name, score, level, foods_eaten)
        )
        DB_CONN.commit()

    except Exception as error:
        print("Save score error:", error)


def getTopScores():
    if DB_CUR is None:
        return []

    try:
        DB_CUR.execute("""
            SELECT player_name, score, level
            FROM snake_scores
            ORDER BY score DESC
            LIMIT 5
        """)
        return DB_CUR.fetchall()

    except Exception as error:
        print("Get top scores error:", error)
        return []


#GAME

def runGame():
    # Random start position for snake
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)

    wormCoords = [
        {'x': startx, 'y': starty},
        {'x': startx - 1, 'y': starty},
        {'x': startx - 2, 'y': starty}
    ]

    direction = RIGHT
    score = 0
    foods_eaten = 0
    level = 1
    fps = BASE_FPS

    # Food appears in a random free cell
    apple = getRandomFood(wormCoords)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        # If food disappeared, create new food
        if foodExpired(apple):
            apple = getRandomFood(wormCoords)

        # Create new head
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}

        # Check wall collision
        if (
            newHead['x'] < 0 or
            newHead['x'] >= CELLWIDTH or
            newHead['y'] < 0 or
            newHead['y'] >= CELLHEIGHT
        ):
            return score, level, foods_eaten

        # Check if snake eats food
        eating_food = newHead['x'] == apple['x'] and newHead['y'] == apple['y']

        # Check collision with itself
        # If snake is not eating, tail will move away, so we do not check last part
        if eating_food:
            body_to_check = wormCoords
        else:
            body_to_check = wormCoords[:-1]

        for wormBody in body_to_check:
            if wormBody['x'] == newHead['x'] and wormBody['y'] == newHead['y']:
                return score, level, foods_eaten

        # Move snake
        wormCoords.insert(0, newHead)

        if eating_food:
            score += apple['weight']
            foods_eaten += 1

            # New level every 3 eaten foods
            level = foods_eaten // 3 + 1
            fps = BASE_FPS + (level - 1) * 2

            apple = getRandomFood(wormCoords)
        else:
            del wormCoords[-1]

        # Draw everything
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)
        drawApple(apple)
        drawScore(score)
        drawLevel(level)
        drawFoodsEaten(foods_eaten)
        drawFoodTimer(apple)

        pygame.display.update()
        FPSCLOCK.tick(fps)


#FOOD

def getRandomLocation(wormCoords):
    # Keep generating food until it is not on the snake
    while True:
        location = {
            'x': random.randint(0, CELLWIDTH - 1),
            'y': random.randint(0, CELLHEIGHT - 1)
        }

        if location not in wormCoords:
            return location


def getRandomFood(wormCoords):
    location = getRandomLocation(wormCoords)

    # different chances for different food weights
    weight = random.choices(
        [1, 2, 3],
        weights=[70, 20, 10]
    )[0]

    if weight == 1:
        color = LIGHT_GREEN
        ttl = 10000      # 10 seconds
    elif weight == 2:
        color = YELLOW
        ttl = 7000       # 7 seconds
    else:
        color = RED
        ttl = 5000       # 5 seconds

    food = {
        'x': location['x'],
        'y': location['y'],
        'weight': weight,
        'color': color,
        'spawn_time': pygame.time.get_ticks(),
        'ttl': ttl
    }

    return food


def foodExpired(food):
    current_time = pygame.time.get_ticks()
    return current_time - food['spawn_time'] > food['ttl']


def getFoodTimeLeft(food):
    current_time = pygame.time.get_ticks()
    time_left = food['ttl'] - (current_time - food['spawn_time'])

    if time_left < 0:
        time_left = 0

    return time_left // 1000


#SCREENS

def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)

    if len(keyUpEvents) == 0:
        return None

    if keyUpEvents[0].key == K_ESCAPE:
        terminate()

    return keyUpEvents[0].key

def showGameOverScreen(score, level, top_scores):
    gameOverFont = pygame.font.Font('freesansbold.ttf', 90)

    while True:
        DISPLAYSURF.fill(BGCOLOR)

        gameSurf = gameOverFont.render('Game Over', True, WHITE)
        gameRect = gameSurf.get_rect()
        gameRect.midtop = (WINDOWWIDTH / 2, 20)
        DISPLAYSURF.blit(gameSurf, gameRect)

        drawText(f'Player: {PLAYER_NAME}', 200, 130, WHITE)
        drawText(f'Final Score: {score}', 200, 160, WHITE)
        drawText(f'Level: {level}', 200, 190, WHITE)

        drawText('Top Scores:', 200, 240, YELLOW)

        y = 270

        if len(top_scores) == 0:
            drawText('No database results', 200, y, DARKGRAY)
        else:
            for i, row in enumerate(top_scores, start=1):
                name, top_score, top_level = row
                drawText(f'{i}. {name} - {top_score} pts, level {top_level}', 200, y, WHITE)
                y += 25

        drawPressKeyMsg()

        pygame.display.update()
        pygame.time.wait(200)

        if checkForKeyPress():
            pygame.event.get()
            return


#DRAWING

def drawText(text, x, y, color):
    textSurf = BASICFONT.render(text, True, color)
    textRect = textSurf.get_rect()
    textRect.topleft = (x, y)
    DISPLAYSURF.blit(textSurf, textRect)


def drawScore(score):
    scoreSurf = BASICFONT.render(f'Score: {score}', True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 160, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawLevel(level):
    levelSurf = BASICFONT.render(f'Level: {level}', True, WHITE)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 160, 30)
    DISPLAYSURF.blit(levelSurf, levelRect)


def drawFoodsEaten(foods_eaten):
    foodsSurf = BASICFONT.render(f'Foods: {foods_eaten}', True, WHITE)
    foodsRect = foodsSurf.get_rect()
    foodsRect.topleft = (WINDOWWIDTH - 160, 50)
    DISPLAYSURF.blit(foodsSurf, foodsRect)


def drawFoodTimer(food):
    time_left = getFoodTimeLeft(food)

    timerSurf = BASICFONT.render(f'Food time: {time_left}s', True, WHITE)
    timerRect = timerSurf.get_rect()
    timerRect.topleft = (10, 10)
    DISPLAYSURF.blit(timerSurf, timerRect)


def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE

        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)

        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE

    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, coord['color'], appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))

    for y in range(0, WINDOWHEIGHT, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


# EXIT

def terminate():
    global DB_CONN, DB_CUR

    if DB_CUR is not None:
        DB_CUR.close()

    if DB_CONN is not None:
        DB_CONN.close()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()