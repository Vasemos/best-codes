import pygame
import math

pygame.init()

#SETTINGS
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

#COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (230, 230, 230)
DARK_GRAY = (80, 80, 80)
LIGHT_BLUE = (210, 230, 255)
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

#FONTS
font = pygame.font.SysFont("arial", 20)
small_font = pygame.font.SysFont("arial", 16)
title_font = pygame.font.SysFont("arial", 24, bold=True)

#TOOL NAMES
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
}

TOOL_LABELS = {
    "brush": "Brush [B]",
    "eraser": "Eraser [E]",
    "line": "Line [L]",
    "rectangle": "Rectangle [R]",
    "circle": "Circle [O]",
    "square": "Square [S]",
    "right_triangle": "Right triangle [T]",
    "equilateral_triangle": "Equilateral triangle [U]",
    "rhombus": "Rhombus [H]",
}

#STATE
current_tool = "brush"
current_color = BLACK
brush_size = 4

drawing = False
start_pos = None
current_pos = None
prev_pos = None

message = "Ready"
message_timer = 0
save_counter = 1

#HELPERS
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
    rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
    pygame.draw.rect(surface, color, rect, width)

def draw_square(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end

    dx = x2 - x1
    dy = y2 - y1
    side = min(abs(dx), abs(dy))

    if dx >= 0:
        left = x1
    else:
        left = x1 - side

    if dy >= 0:
        top = y1
    else:
        top = y1 - side

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
    points = [(x1, y1), (x1, y2), (x2, y2)]
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
        (cx, y1),   # top
        (x2, cy),   # right
        (cx, y2),   # bottom
        (x1, cy)    # left
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

def draw_toolbar():
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, DARK_GRAY, (0, TOOLBAR_HEIGHT), (WIDTH, TOOLBAR_HEIGHT), 2)

    title = title_font.render("Paint Extended", True, BLACK)
    screen.blit(title, (15, 10))

    tool_text = font.render(f"Tool: {TOOL_LABELS[current_tool]}", True, BLACK)
    color_name = next(name for name, value in COLOR_LIST if value == current_color) if current_tool != "eraser" else "White"
    color_text = font.render(f"Color: {color_name}", True, BLACK)
    size_text = font.render(f"Size: {brush_size}", True, BLACK)

    screen.blit(tool_text, (15, 42))
    screen.blit(color_text, (300, 42))
    screen.blit(size_text, (500, 42))

    # palette
    palette_x = 700
    palette_y = 18
    for i, (name, color) in enumerate(COLOR_LIST):
        rect = pygame.Rect(palette_x + i * 45, palette_y, 32, 32)
        pygame.draw.rect(screen, color, rect)
        border_color = BLACK if color != current_color else ORANGE
        border_width = 2 if color != current_color else 4
        pygame.draw.rect(screen, border_color, rect, border_width)

        num_text = small_font.render(str(i + 1), True, BLACK if color != BLACK else WHITE)
        screen.blit(num_text, (rect.x + 11, rect.y + 7))

    info1 = small_font.render("Keys: B brush | E eraser | L line | R rect | O circle | S square", True, DARK_GRAY)
    info2 = small_font.render("T right triangle | U equilateral | H rhombus | 1-7 colors | +/- size", True, DARK_GRAY)
    info3 = small_font.render("P save | DELETE clear | Mouse wheel = size | ESC quit", True, DARK_GRAY)

    screen.blit(info1, (15, 75))
    screen.blit(info2, (420, 75))
    screen.blit(info3, (820, 75))

    msg_text = small_font.render(message, True, BLUE)
    screen.blit(msg_text, (950, 44))

def save_canvas():
    global save_counter
    filename = f"paint_{save_counter}.png"
    pygame.image.save(canvas, filename)
    save_counter += 1
    set_message(f"Saved as {filename}")

#MAIN LOOP
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

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key in TOOLS:
                current_tool = TOOLS[event.key]
                set_message(f"Selected: {TOOL_LABELS[current_tool]}")

            elif event.key == pygame.K_1:
                current_color = COLOR_LIST[0][1]
                set_message("Color: Black")
            elif event.key == pygame.K_2:
                current_color = COLOR_LIST[1][1]
                set_message("Color: Red")
            elif event.key == pygame.K_3:
                current_color = COLOR_LIST[2][1]
                set_message("Color: Green")
            elif event.key == pygame.K_4:
                current_color = COLOR_LIST[3][1]
                set_message("Color: Blue")
            elif event.key == pygame.K_5:
                current_color = COLOR_LIST[4][1]
                set_message("Color: Yellow")
            elif event.key == pygame.K_6:
                current_color = COLOR_LIST[5][1]
                set_message("Color: Purple")
            elif event.key == pygame.K_7:
                current_color = COLOR_LIST[6][1]
                set_message("Color: Orange")

            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                brush_size = min(50, brush_size + 1)
                set_message(f"Size: {brush_size}")

            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                brush_size = max(1, brush_size - 1)
                set_message(f"Size: {brush_size}")

            elif event.key == pygame.K_DELETE:
                canvas.fill(WHITE)
                set_message("Canvas cleared")

            elif event.key == pygame.K_p:
                save_canvas()

        elif event.type == pygame.MOUSEWHEEL:
            brush_size = clamp(brush_size + event.y, 1, 50)
            set_message(f"Size: {brush_size}")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and event.pos[1] >= TOOLBAR_HEIGHT:
                drawing = True
                canvas_pos = to_canvas_pos(event.pos)

                if current_tool in ("brush", "eraser"):
                    prev_pos = canvas_pos
                    color = WHITE if current_tool == "eraser" else current_color
                    draw_brush(canvas, color, canvas_pos, canvas_pos, brush_size)
                else:
                    start_pos = canvas_pos
                    current_pos = canvas_pos

        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                canvas_pos = to_canvas_pos(event.pos)

                if current_tool in ("brush", "eraser"):
                    color = WHITE if current_tool == "eraser" else current_color
                    draw_brush(canvas, color, prev_pos, canvas_pos, brush_size)
                    prev_pos = canvas_pos
                else:
                    current_pos = canvas_pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                canvas_pos = to_canvas_pos(event.pos)

                if current_tool not in ("brush", "eraser") and start_pos is not None:
                    draw_shape(canvas, current_tool, current_color, start_pos, canvas_pos, brush_size)

                drawing = False
                start_pos = None
                current_pos = None
                prev_pos = None

    #DRAW
    screen.fill((245, 245, 245))
    draw_toolbar()

    if drawing and current_tool not in ("brush", "eraser") and start_pos and current_pos:
        preview = canvas.copy()
        draw_shape(preview, current_tool, current_color, start_pos, current_pos, brush_size)
        screen.blit(preview, (0, TOOLBAR_HEIGHT))
    else:
        screen.blit(canvas, (0, TOOLBAR_HEIGHT))

    pygame.draw.rect(screen, BLACK, (0, TOOLBAR_HEIGHT, CANVAS_WIDTH, CANVAS_HEIGHT), 2)

    pygame.display.flip()

pygame.quit()