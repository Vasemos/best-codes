import pygame
import math
import datetime
from collections import deque

pygame.init()

# SETTINGS
WIDTH, HEIGHT = 1200, 800
TOOLBAR_HEIGHT = 110
CANVAS_WIDTH = WIDTH
CANVAS_HEIGHT = HEIGHT - TOOLBAR_HEIGHT

FPS = 60
WINDOW_TITLE = "Paint Extended"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)
clock = pygame.time.Clock()

canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
canvas.fill((255, 255, 255))

# COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (230, 230, 230)
DARK_GRAY = (80, 80, 80)
RED = (220, 50, 50)
GREEN = (40, 170, 90)
BLUE = (50, 100, 220)
YELLOW = (240, 200, 40)
PURPLE = (150, 80, 200)
ORANGE = (255, 140, 0)

COLOR_LIST = [
    ("Black", BLACK),
    ("Red", RED),
    ("Green", GREEN),
    ("Blue", BLUE),
    ("Yellow", YELLOW),
    ("Purple", PURPLE),
    ("Orange", ORANGE)
]

PALETTE_RECTS = []

# FONTS
font = pygame.font.SysFont("arial", 20)
small_font = pygame.font.SysFont("arial", 15)
title_font = pygame.font.SysFont("arial", 24, bold=True)
text_font = pygame.font.SysFont("arial", 28)

# TOOLS
TOOLS = {
    pygame.K_b: "brush",
    pygame.K_e: "eraser",
    pygame.K_l: "line",
    pygame.K_r: "rectangle",
    pygame.K_o: "circle",
    pygame.K_s: "square",
    pygame.K_t: "right_triangle",
    pygame.K_u: "equilateral_triangle",
    pygame.K_h: "rhombus",
    pygame.K_f: "fill",
    pygame.K_x: "text",
}

TOOL_LABELS = {
    "brush": "Pencil [B]",
    "eraser": "Eraser [E]",
    "line": "Line [L]",
    "rectangle": "Rectangle [R]",
    "circle": "Circle [O]",
    "square": "Square [S]",
    "right_triangle": "Right Triangle [T]",
    "equilateral_triangle": "Equilateral Triangle [U]",
    "rhombus": "Rhombus [H]",
    "fill": "Fill [F]",
    "text": "Text [X]",
}

# BRUSH SIZE LEVELS
SIZE_LEVELS = {
    pygame.K_1: 2,
    pygame.K_2: 5,
    pygame.K_3: 10
}

# STATE
current_tool = "brush"
current_color = BLACK
brush_size = 2

drawing = False
start_pos = None
current_pos = None
prev_pos = None

message = "Ready"
message_timer = 0

text_mode = False
text_pos = None
text_buffer = ""


# HELPERS
def set_message(text, duration=120):
    global message, message_timer
    message = text
    message_timer = duration


def clamp(value, low, high):
    return max(low, min(value, high))


def to_canvas_pos(screen_pos):
    x = clamp(screen_pos[0], 0, CANVAS_WIDTH - 1)
    y = clamp(screen_pos[1] - TOOLBAR_HEIGHT, 0, CANVAS_HEIGHT - 1)
    return (x, y)


def draw_brush(surface, color, start, end, size):
    pygame.draw.line(surface, color, start, end, size)
    pygame.draw.circle(surface, color, start, max(1, size // 2))
    pygame.draw.circle(surface, color, end, max(1, size // 2))


def draw_rectangle(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end

    rect = pygame.Rect(
        min(x1, x2),
        min(y1, y2),
        abs(x2 - x1),
        abs(y2 - y1)
    )

    pygame.draw.rect(surface, color, rect, width)


def draw_square(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end

    dx = x2 - x1
    dy = y2 - y1
    side = min(abs(dx), abs(dy))

    left = x1 if dx >= 0 else x1 - side
    top = y1 if dy >= 0 else y1 - side

    rect = pygame.Rect(left, top, side, side)
    pygame.draw.rect(surface, color, rect, width)


def draw_circle(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end

    left = min(x1, x2)
    top = min(y1, y2)

    w = abs(x2 - x1)
    h = abs(y2 - y1)

    side = min(w, h)

    rect = pygame.Rect(left, top, side, side)
    pygame.draw.ellipse(surface, color, rect, width)


def draw_right_triangle(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end

    points = [
        (x1, y1),
        (x1, y2),
        (x2, y2)
    ]

    pygame.draw.polygon(surface, color, points, width)


def draw_equilateral_triangle(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end

    side = max(1, abs(x2 - x1))
    direction_x = 1 if x2 >= x1 else -1
    direction_y = -1 if y2 < y1 else 1

    p1 = (x1, y1)
    p2 = (x1 + direction_x * side, y1)

    h = int(side * math.sqrt(3) / 2)

    mid_x = (p1[0] + p2[0]) // 2
    p3 = (mid_x, y1 + direction_y * h)

    pygame.draw.polygon(surface, color, [p1, p2, p3], width)


def draw_rhombus(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end

    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2

    points = [
        (cx, y1),
        (x2, cy),
        (cx, y2),
        (x1, cy)
    ]

    pygame.draw.polygon(surface, color, points, width)


def draw_shape(surface, tool, color, start, end, width):
    if tool == "line":
        pygame.draw.line(surface, color, start, end, width)

    elif tool == "rectangle":
        draw_rectangle(surface, color, start, end, width)

    elif tool == "circle":
        draw_circle(surface, color, start, end, width)

    elif tool == "square":
        draw_square(surface, color, start, end, width)

    elif tool == "right_triangle":
        draw_right_triangle(surface, color, start, end, width)

    elif tool == "equilateral_triangle":
        draw_equilateral_triangle(surface, color, start, end, width)

    elif tool == "rhombus":
        draw_rhombus(surface, color, start, end, width)


def flood_fill(surface, x, y, fill_color):
    target_color = surface.get_at((x, y))[:3]
    fill_color = tuple(fill_color[:3])

    if target_color == fill_color:
        return

    width, height = surface.get_size()

    queue = deque()
    queue.append((x, y))

    visited = set()
    visited.add((x, y))

    while queue:
        cx, cy = queue.popleft()

        if surface.get_at((cx, cy))[:3] != target_color:
            continue

        surface.set_at((cx, cy), fill_color)

        neighbors = [
            (cx - 1, cy),
            (cx + 1, cy),
            (cx, cy - 1),
            (cx, cy + 1)
        ]

        for nx, ny in neighbors:
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited:
                    if surface.get_at((nx, ny))[:3] == target_color:
                        visited.add((nx, ny))
                        queue.append((nx, ny))


def save_canvas():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"paint_{timestamp}.png"

    pygame.image.save(canvas, filename)
    set_message(f"Saved as {filename}")


def get_color_name():
    if current_tool == "eraser":
        return "White"

    for name, color in COLOR_LIST:
        if color == current_color:
            return name

    return "Custom"


def draw_toolbar():
    PALETTE_RECTS.clear()

    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, DARK_GRAY, (0, TOOLBAR_HEIGHT), (WIDTH, TOOLBAR_HEIGHT), 2)

    title = title_font.render("Paint Extended", True, BLACK)
    screen.blit(title, (15, 8))

    tool_text = font.render(f"Tool: {TOOL_LABELS[current_tool]}", True, BLACK)
    color_text = font.render(f"Color: {get_color_name()}", True, BLACK)
    size_text = font.render(f"Size: {brush_size}px", True, BLACK)

    screen.blit(tool_text, (15, 38))
    screen.blit(color_text, (300, 38))
    screen.blit(size_text, (500, 38))

    # Palette
    palette_x = 700
    palette_y = 15

    for i, (name, color) in enumerate(COLOR_LIST):
        rect = pygame.Rect(palette_x + i * 45, palette_y, 32, 32)
        PALETTE_RECTS.append((rect, name, color))

        pygame.draw.rect(screen, color, rect)

        if color == current_color:
            pygame.draw.rect(screen, ORANGE, rect, 4)
        else:
            pygame.draw.rect(screen, BLACK, rect, 2)

    # Info text, fixed so it fits
    info1 = small_font.render(
        "Tools: B Pencil | E Eraser | L Line | R Rect | O Circle | S Square | T RightTri",
        True,
        DARK_GRAY
    )

    info2 = small_font.render(
        "More: U EquiTri | H Rhombus | F Fill | X Text    Size: 1=2px  2=5px  3=10px    Ctrl+S Save | Delete Clear | Esc Quit",
        True,
        DARK_GRAY
    )

    screen.blit(info1, (15, 72))
    screen.blit(info2, (15, 92))

    msg_text = small_font.render(message, True, BLUE)
    screen.blit(msg_text, (700, 55))


# MAIN LOOP
running = True

while running:
    clock.tick(FPS)

    if message_timer > 0:
        message_timer -= 1
        if message_timer == 0:
            message = "Ready"

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # KEYBOARD EVENTS
        elif event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()

            if text_mode:
                if event.key == pygame.K_RETURN:
                    if text_buffer:
                        text_surface = text_font.render(text_buffer, True, current_color)
                        canvas.blit(text_surface, text_pos)
                        set_message("Text added")

                    text_mode = False
                    text_pos = None
                    text_buffer = ""

                elif event.key == pygame.K_ESCAPE:
                    text_mode = False
                    text_pos = None
                    text_buffer = ""
                    set_message("Text canceled")

                elif event.key == pygame.K_BACKSPACE:
                    text_buffer = text_buffer[:-1]

                else:
                    if event.unicode and event.unicode.isprintable():
                        text_buffer += event.unicode

            else:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                    save_canvas()

                elif event.key in SIZE_LEVELS:
                    brush_size = SIZE_LEVELS[event.key]
                    set_message(f"Brush size: {brush_size}px")

                elif event.key in TOOLS:
                    current_tool = TOOLS[event.key]
                    set_message(f"Selected: {TOOL_LABELS[current_tool]}")

                elif event.key == pygame.K_DELETE:
                    canvas.fill(WHITE)
                    set_message("Canvas cleared")

        # MOUSE BUTTON DOWN
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked_palette = False

                for rect, name, color in PALETTE_RECTS:
                    if rect.collidepoint(event.pos):
                        current_color = color
                        set_message(f"Color: {name}")
                        clicked_palette = True
                        break

                if clicked_palette:
                    continue

                if event.pos[1] >= TOOLBAR_HEIGHT:
                    canvas_pos = to_canvas_pos(event.pos)

                    if current_tool == "fill":
                        flood_fill(canvas, canvas_pos[0], canvas_pos[1], current_color)
                        set_message("Area filled")

                    elif current_tool == "text":
                        text_mode = True
                        text_pos = canvas_pos
                        text_buffer = ""
                        set_message("Typing text... Enter confirm, Esc cancel")

                    else:
                        drawing = True

                        if current_tool in ("brush", "eraser"):
                            prev_pos = canvas_pos

                            if current_tool == "eraser":
                                color = WHITE
                            else:
                                color = current_color

                            draw_brush(canvas, color, canvas_pos, canvas_pos, brush_size)

                        else:
                            start_pos = canvas_pos
                            current_pos = canvas_pos

        # MOUSE MOTION
        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                canvas_pos = to_canvas_pos(event.pos)

                if current_tool in ("brush", "eraser"):
                    if current_tool == "eraser":
                        color = WHITE
                    else:
                        color = current_color

                    draw_brush(canvas, color, prev_pos, canvas_pos, brush_size)
                    prev_pos = canvas_pos

                else:
                    current_pos = canvas_pos

        # MOUSE BUTTON UP
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                canvas_pos = to_canvas_pos(event.pos)

                if current_tool not in ("brush", "eraser") and start_pos is not None:
                    draw_shape(canvas, current_tool, current_color, start_pos, canvas_pos, brush_size)

                drawing = False
                start_pos = None
                current_pos = None
                prev_pos = None

    # DRAW SCREEN
    screen.fill((245, 245, 245))
    draw_toolbar()

    if drawing and current_tool not in ("brush", "eraser") and start_pos and current_pos:
        preview = canvas.copy()
        draw_shape(preview, current_tool, current_color, start_pos, current_pos, brush_size)
        screen.blit(preview, (0, TOOLBAR_HEIGHT))
    else:
        screen.blit(canvas, (0, TOOLBAR_HEIGHT))

    # Text tool preview
    if text_mode and text_pos is not None:
        preview_text = text_font.render(text_buffer + "|", True, current_color)
        screen.blit(preview_text, (text_pos[0], text_pos[1] + TOOLBAR_HEIGHT))

    pygame.draw.rect(screen, BLACK, (0, TOOLBAR_HEIGHT, CANVAS_WIDTH, CANVAS_HEIGHT), 2)

    pygame.display.flip()

pygame.quit()