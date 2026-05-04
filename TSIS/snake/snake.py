import random
import pygame
import sys
import json
import os

try:
    import psycopg2
except ImportError:
    psycopg2 = None

from pygame.locals import *


# SETTINGS
BASE_FPS = 10
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20

assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."

CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

SETTINGS_FILE = "settings.json"

DB_CONFIG = {
    "host": "localhost",
    "dbname": "pygame_db",
    "user": "postgres",
    "password": "98v898v8A@", 
    "port": 5432
}

PLAYER_NAME = "Player"
PLAYER_ID = None
DB_CONN = None
DB_CUR = None


# COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 155, 0)
DARKGRAY = (40, 40, 40)
YELLOW = (255, 215, 0)
BLUE = (0, 100, 255)
LIGHT_GREEN = (50, 255, 50)
PURPLE = (170, 80, 255)
ORANGE = (255, 140, 0)
GRAY = (120, 120, 120)
BROWN = (120, 75, 40)
BGCOLOR = BLACK

SNAKE_COLORS = [
    ("Green", GREEN),
    ("Blue", BLUE),
    ("Yellow", YELLOW),
    ("Purple", PURPLE),
    ("Orange", ORANGE)
]


# DIRECTIONS
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0


# MAIN
def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    global PLAYER_NAME, PLAYER_ID, DB_CONN, DB_CUR

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 48)
    pygame.display.set_caption('Snake Advanced')

    settings = loadSettings()

    DB_CONN, DB_CUR = connectDB()

    PLAYER_NAME = showUsernameScreen()

    if PLAYER_NAME.strip() == "":
        PLAYER_NAME = "Player"

    PLAYER_ID = getOrCreatePlayer(PLAYER_NAME)

    while True:
        choice = showMainMenu()

        if choice == "start":
            personal_best = getPersonalBest(PLAYER_NAME)
            score, level, foods_eaten = runGame(settings, personal_best)

            saveGameSession(PLAYER_ID, score, level)

            top_scores = getTopScores()
            showGameOverScreen(score, level, top_scores)

        elif choice == "leaderboard":
            top_scores = getTopScores()
            showLeaderboardScreen(top_scores)

        elif choice == "settings":
            settings = showSettingsScreen(settings)
            saveSettings(settings)

        elif choice == "quit":
            terminate()


# SETTINGS JSON
def loadSettings():
    default_settings = {
        "snake_color": "Green",
        "grid": True,
        "sound": False
    }

    if not os.path.exists(SETTINGS_FILE):
        saveSettings(default_settings)
        return default_settings

    try:
        with open(SETTINGS_FILE, "r") as file:
            settings = json.load(file)

        for key in default_settings:
            if key not in settings:
                settings[key] = default_settings[key]

        return settings

    except Exception:
        saveSettings(default_settings)
        return default_settings


def saveSettings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)


def getSnakeColor(settings):
    for name, color in SNAKE_COLORS:
        if settings["snake_color"] == name:
            return color

    return GREEN


def getNextSnakeColor(current_name):
    names = []

    for name, color in SNAKE_COLORS:
        names.append(name)

    if current_name not in names:
        return names[0]

    index = names.index(current_name)
    next_index = (index + 1) % len(names)

    return names[next_index]


# DATABASE
def connectDB():
    if psycopg2 is None:
        print("psycopg2 is not installed. Database is disabled.")
        return None, None

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id SERIAL PRIMARY KEY,
                player_id INTEGER REFERENCES players(id),
                score INTEGER NOT NULL,
                level_reached INTEGER NOT NULL,
                played_at TIMESTAMP DEFAULT NOW()
            )
        """)

        conn.commit()
        print("Database connected.")
        return conn, cur

    except Exception as error:
        print("Database error:", error)
        return None, None


def getOrCreatePlayer(username):
    if DB_CONN is None or DB_CUR is None:
        return None

    try:
        DB_CUR.execute(
            """
            INSERT INTO players (username)
            VALUES (%s)
            ON CONFLICT (username) DO NOTHING
            """,
            (username,)
        )
        DB_CONN.commit()

        DB_CUR.execute(
            "SELECT id FROM players WHERE username = %s",
            (username,)
        )

        row = DB_CUR.fetchone()

        if row:
            return row[0]

    except Exception as error:
        print("Player error:", error)

    return None


def saveGameSession(player_id, score, level):
    if DB_CONN is None or DB_CUR is None or player_id is None:
        return

    try:
        DB_CUR.execute(
            """
            INSERT INTO game_sessions (player_id, score, level_reached)
            VALUES (%s, %s, %s)
            """,
            (player_id, score, level)
        )
        DB_CONN.commit()

    except Exception as error:
        print("Save session error:", error)


def getTopScores():
    if DB_CUR is None:
        return []

    try:
        DB_CUR.execute("""
            SELECT players.username, game_sessions.score, game_sessions.level_reached, game_sessions.played_at
            FROM game_sessions
            JOIN players ON game_sessions.player_id = players.id
            ORDER BY game_sessions.score DESC
            LIMIT 10
        """)
        return DB_CUR.fetchall()

    except Exception as error:
        print("Get top scores error:", error)
        return []


def getPersonalBest(username):
    if DB_CUR is None:
        return 0

    try:
        DB_CUR.execute("""
            SELECT MAX(game_sessions.score)
            FROM game_sessions
            JOIN players ON game_sessions.player_id = players.id
            WHERE players.username = %s
        """, (username,))

        row = DB_CUR.fetchone()

        if row and row[0] is not None:
            return row[0]

    except Exception as error:
        print("Personal best error:", error)

    return 0


# GAME
def runGame(settings, personal_best):
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

    boost_end_time = 0

    obstacles = getRandomObstacles(wormCoords, 12)
    apple = getRandomFood(wormCoords, obstacles)

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
                    return score, level, foods_eaten

        if foodExpired(apple):
            apple = getRandomFood(wormCoords, obstacles)

        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}

        if (
            newHead['x'] < 0 or
            newHead['x'] >= CELLWIDTH or
            newHead['y'] < 0 or
            newHead['y'] >= CELLHEIGHT
        ):
            return score, level, foods_eaten

        if newHead in obstacles:
            return score, level, foods_eaten

        eating_food = newHead['x'] == apple['x'] and newHead['y'] == apple['y']

        if eating_food:
            body_to_check = wormCoords
        else:
            body_to_check = wormCoords[:-1]

        for wormBody in body_to_check:
            if wormBody['x'] == newHead['x'] and wormBody['y'] == newHead['y']:
                return score, level, foods_eaten

        wormCoords.insert(0, newHead)

        if eating_food:
            if apple['type'] == "normal":
                score += apple['weight']
                foods_eaten += 1

            elif apple['type'] == "poison":
                score -= 2

                if score < 0:
                    score = 0

                # poison shortens the snake
                if len(wormCoords) > 3:
                    del wormCoords[-1]
                    del wormCoords[-1]
                else:
                    return score, level, foods_eaten

            elif apple['type'] == "boost":
                score += 1
                foods_eaten += 1
                boost_end_time = pygame.time.get_ticks() + 5000

            level = foods_eaten // 3 + 1
            fps = BASE_FPS + (level - 1) * 2

            apple = getRandomFood(wormCoords, obstacles)

        else:
            del wormCoords[-1]

        current_time = pygame.time.get_ticks()

        if current_time < boost_end_time:
            current_fps = fps + 6
        else:
            current_fps = fps

        DISPLAYSURF.fill(BGCOLOR)

        if settings["grid"]:
            drawGrid()

        drawObstacles(obstacles)
        drawWorm(wormCoords, settings)
        drawApple(apple)
        drawScore(score)
        drawLevel(level)
        drawFoodsEaten(foods_eaten)
        drawFoodTimer(apple)
        drawPersonalBest(personal_best)
        drawBoostTimer(boost_end_time)

        pygame.display.update()
        FPSCLOCK.tick(current_fps)


# OBSTACLES
def getRandomObstacles(wormCoords, amount):
    obstacles = []

    while len(obstacles) < amount:
        obstacle = {
            'x': random.randint(2, CELLWIDTH - 3),
            'y': random.randint(3, CELLHEIGHT - 3)
        }

        if obstacle not in wormCoords and obstacle not in obstacles:
            obstacles.append(obstacle)

    return obstacles


# FOOD
def getRandomLocation(wormCoords, obstacles):
    while True:
        location = {
            'x': random.randint(0, CELLWIDTH - 1),
            'y': random.randint(1, CELLHEIGHT - 1)
        }

        if location not in wormCoords and location not in obstacles:
            return location


def getRandomFood(wormCoords, obstacles):
    location = getRandomLocation(wormCoords, obstacles)

    food_type = random.choices(
        ["normal", "poison", "boost"],
        weights=[75, 15, 10]
    )[0]

    if food_type == "normal":
        weight = random.choices(
            [1, 2, 3],
            weights=[70, 20, 10]
        )[0]

        if weight == 1:
            color = LIGHT_GREEN
            ttl = 10000
        elif weight == 2:
            color = YELLOW
            ttl = 7000
        else:
            color = RED
            ttl = 5000

    elif food_type == "poison":
        weight = -2
        color = PURPLE
        ttl = 6000

    else:
        weight = 0
        color = BLUE
        ttl = 5000

    food = {
        'x': location['x'],
        'y': location['y'],
        'weight': weight,
        'color': color,
        'type': food_type,
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


# SCREENS
def showUsernameScreen():
    username = ""

    while True:
        DISPLAYSURF.fill(BGCOLOR)

        titleSurf = BIGFONT.render("Enter Username", True, GREEN)
        titleRect = titleSurf.get_rect()
        titleRect.center = (WINDOWWIDTH // 2, 120)
        DISPLAYSURF.blit(titleSurf, titleRect)

        boxRect = pygame.Rect(170, 200, 300, 45)
        pygame.draw.rect(DISPLAYSURF, WHITE, boxRect, 2)

        nameSurf = BASICFONT.render(username, True, WHITE)
        DISPLAYSURF.blit(nameSurf, (boxRect.x + 10, boxRect.y + 12))

        infoSurf = BASICFONT.render("Press ENTER to continue", True, DARKGRAY)
        infoRect = infoSurf.get_rect()
        infoRect.center = (WINDOWWIDTH // 2, 280)
        DISPLAYSURF.blit(infoSurf, infoRect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if username.strip() == "":
                        return "Player"
                    return username

                elif event.key == K_BACKSPACE:
                    username = username[:-1]

                elif event.key == K_ESCAPE:
                    terminate()

                else:
                    if len(username) < 15 and event.unicode.isprintable():
                        username += event.unicode


def showMainMenu():
    selected = 0
    options = ["Start Game", "Leaderboard", "Settings", "Quit"]

    while True:
        DISPLAYSURF.fill(BGCOLOR)

        titleSurf = BIGFONT.render("SNAKE", True, GREEN)
        titleRect = titleSurf.get_rect()
        titleRect.center = (WINDOWWIDTH // 2, 90)
        DISPLAYSURF.blit(titleSurf, titleRect)

        nameSurf = BASICFONT.render(f"Player: {PLAYER_NAME}", True, WHITE)
        nameRect = nameSurf.get_rect()
        nameRect.center = (WINDOWWIDTH // 2, 145)
        DISPLAYSURF.blit(nameSurf, nameRect)

        y = 210

        for i, option in enumerate(options):
            if i == selected:
                color = YELLOW
                text = "> " + option + " <"
            else:
                color = WHITE
                text = option

            optionSurf = BASICFONT.render(text, True, color)
            optionRect = optionSurf.get_rect()
            optionRect.center = (WINDOWWIDTH // 2, y)
            DISPLAYSURF.blit(optionSurf, optionRect)
            y += 40

        pygame.display.update()
        FPSCLOCK.tick(15)

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key == K_UP or event.key == K_w:
                    selected -= 1
                    if selected < 0:
                        selected = len(options) - 1

                elif event.key == K_DOWN or event.key == K_s:
                    selected += 1
                    if selected >= len(options):
                        selected = 0

                elif event.key == K_RETURN:
                    if selected == 0:
                        return "start"
                    elif selected == 1:
                        return "leaderboard"
                    elif selected == 2:
                        return "settings"
                    elif selected == 3:
                        return "quit"

                elif event.key == K_ESCAPE:
                    terminate()


def showSettingsScreen(settings):
    while True:
        DISPLAYSURF.fill(BGCOLOR)

        titleSurf = BIGFONT.render("Settings", True, GREEN)
        titleRect = titleSurf.get_rect()
        titleRect.center = (WINDOWWIDTH // 2, 70)
        DISPLAYSURF.blit(titleSurf, titleRect)

        drawText("1. Snake color: " + settings["snake_color"], 160, 150, WHITE)
        drawText("2. Grid overlay: " + ("ON" if settings["grid"] else "OFF"), 160, 190, WHITE)
        drawText("3. Sound: " + ("ON" if settings["sound"] else "OFF"), 160, 230, WHITE)

        drawText("Press 1 / 2 / 3 to change", 160, 310, DARKGRAY)
        drawText("Press ESC to return", 160, 340, DARKGRAY)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key == K_1:
                    settings["snake_color"] = getNextSnakeColor(settings["snake_color"])
                    saveSettings(settings)

                elif event.key == K_2:
                    settings["grid"] = not settings["grid"]
                    saveSettings(settings)

                elif event.key == K_3:
                    settings["sound"] = not settings["sound"]
                    saveSettings(settings)

                elif event.key == K_ESCAPE:
                    return settings


def showLeaderboardScreen(top_scores):
    while True:
        DISPLAYSURF.fill(BGCOLOR)

        titleSurf = BIGFONT.render("Top 10 Scores", True, YELLOW)
        titleRect = titleSurf.get_rect()
        titleRect.center = (WINDOWWIDTH // 2, 50)
        DISPLAYSURF.blit(titleSurf, titleRect)

        y = 110

        if len(top_scores) == 0:
            drawText("No database results", 190, y, DARKGRAY)
        else:
            for i, row in enumerate(top_scores, start=1):
                name, score, level, played_at = row
                drawText(f"{i}. {name} - {score} pts, level {level}", 120, y, WHITE)
                y += 30

        drawText("Press ESC to return", 210, 430, DARKGRAY)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_RETURN:
                    return


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to continue.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 240, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)

    if len(keyUpEvents) == 0:
        return None

    if keyUpEvents[0].key == K_ESCAPE:
        return K_ESCAPE

    return keyUpEvents[0].key


def showGameOverScreen(score, level, top_scores):
    gameOverFont = pygame.font.Font('freesansbold.ttf', 70)

    while True:
        DISPLAYSURF.fill(BGCOLOR)

        gameSurf = gameOverFont.render('Game Over', True, WHITE)
        gameRect = gameSurf.get_rect()
        gameRect.midtop = (WINDOWWIDTH / 2, 20)
        DISPLAYSURF.blit(gameSurf, gameRect)

        drawText(f'Player: {PLAYER_NAME}', 180, 110, WHITE)
        drawText(f'Final Score: {score}', 180, 140, WHITE)
        drawText(f'Level Reached: {level}', 180, 170, WHITE)

        drawText('Top Scores:', 180, 215, YELLOW)

        y = 245

        if len(top_scores) == 0:
            drawText('No database results', 180, y, DARKGRAY)
        else:
            for i, row in enumerate(top_scores[:6], start=1):
                name, top_score, top_level, played_at = row
                drawText(f'{i}. {name} - {top_score} pts, level {top_level}', 140, y, WHITE)
                y += 25

        drawPressKeyMsg()

        pygame.display.update()
        pygame.time.wait(200)

        if checkForKeyPress():
            pygame.event.get()
            return


# DRAWING
def drawText(text, x, y, color):
    textSurf = BASICFONT.render(text, True, color)
    textRect = textSurf.get_rect()
    textRect.topleft = (x, y)
    DISPLAYSURF.blit(textSurf, textRect)


def drawScore(score):
    scoreSurf = BASICFONT.render(f'Score: {score}', True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 170, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawLevel(level):
    levelSurf = BASICFONT.render(f'Level: {level}', True, WHITE)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 170, 30)
    DISPLAYSURF.blit(levelSurf, levelRect)


def drawFoodsEaten(foods_eaten):
    foodsSurf = BASICFONT.render(f'Foods: {foods_eaten}', True, WHITE)
    foodsRect = foodsSurf.get_rect()
    foodsRect.topleft = (WINDOWWIDTH - 170, 50)
    DISPLAYSURF.blit(foodsSurf, foodsRect)


def drawFoodTimer(food):
    time_left = getFoodTimeLeft(food)

    timerSurf = BASICFONT.render(f'Food time: {time_left}s', True, WHITE)
    timerRect = timerSurf.get_rect()
    timerRect.topleft = (10, 10)
    DISPLAYSURF.blit(timerSurf, timerRect)


def drawPersonalBest(personal_best):
    bestSurf = BASICFONT.render(f'Best: {personal_best}', True, YELLOW)
    bestRect = bestSurf.get_rect()
    bestRect.topleft = (10, 30)
    DISPLAYSURF.blit(bestSurf, bestRect)


def drawBoostTimer(boost_end_time):
    current_time = pygame.time.get_ticks()

    if current_time < boost_end_time:
        time_left = (boost_end_time - current_time) // 1000
        boostSurf = BASICFONT.render(f'BOOST: {time_left}s', True, BLUE)
        boostRect = boostSurf.get_rect()
        boostRect.topleft = (10, 50)
        DISPLAYSURF.blit(boostSurf, boostRect)


def drawWorm(wormCoords, settings):
    snake_color = getSnakeColor(settings)

    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE

        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)

        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, snake_color, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE

    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, coord['color'], appleRect)


def drawObstacles(obstacles):
    for obstacle in obstacles:
        x = obstacle['x'] * CELLSIZE
        y = obstacle['y'] * CELLSIZE

        obstacleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, BROWN, obstacleRect)

        innerRect = pygame.Rect(x + 3, y + 3, CELLSIZE - 6, CELLSIZE - 6)
        pygame.draw.rect(DISPLAYSURF, GRAY, innerRect)


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