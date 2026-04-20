import pygame


def get_color(color_mode):
    if color_mode == 'red':
        return (255, 0, 0)
    elif color_mode == 'green':
        return (0, 255, 0)
    elif color_mode == 'blue':
        return (0, 0, 255)
    elif color_mode == 'black':
        return (0, 0, 0)


def draw_line_between(screen, start, end, width, color):
    dx = start[0] - end[0]
    dy = start[1] - end[1]
    iterations = max(abs(dx), abs(dy))

    if iterations == 0:
        pygame.draw.circle(screen, color, start, width)
        return

    for i in range(iterations):
        progress = i / iterations
        aprogress = 1 - progress
        x = int(aprogress * start[0] + progress * end[0])
        y = int(aprogress * start[1] + progress * end[1])
        pygame.draw.circle(screen, color, (x, y), width)


def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Paint Program")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    radius = 15
    color_mode = 'blue'
    tool = 'brush'

    points = []
    shapes = []

    while True:
        pressed = pygame.key.get_pressed()
        alt_held = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and ctrl_held:
                    return
                if event.key == pygame.K_F4 and alt_held:
                    return
                if event.key == pygame.K_ESCAPE:
                    return

                # Color selection
                if event.key == pygame.K_r:
                    color_mode = 'red'
                elif event.key == pygame.K_g:
                    color_mode = 'green'
                elif event.key == pygame.K_b:
                    color_mode = 'blue'

                # Tool selection
                elif event.key == pygame.K_l:
                    tool = 'brush'
                elif event.key == pygame.K_c:
                    tool = 'circle'
                elif event.key == pygame.K_t:
                    tool = 'rectangle'
                elif event.key == pygame.K_e:
                    tool = 'eraser'

                # Size control
                elif event.key == pygame.K_UP:
                    radius = min(200, radius + 2)
                elif event.key == pygame.K_DOWN:
                    radius = max(1, radius - 2)

                # Clear screen
                elif event.key == pygame.K_SPACE:
                    points.clear()
                    shapes.clear()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                if event.button == 1:
                    if tool == 'circle':
                        shapes.append(('circle', pos, radius, get_color(color_mode)))
                    elif tool == 'rectangle':
                        shapes.append(('rectangle', pos, radius, get_color(color_mode)))

            if event.type == pygame.MOUSEMOTION:
                pos = event.pos

                if pygame.mouse.get_pressed()[0]:
                    if tool == 'brush':
                        points.append((pos, radius, get_color(color_mode)))
                        points = points[-300:]
                    elif tool == 'eraser':
                        points.append((pos, radius, (0, 0, 0)))
                        points = points[-300:]

        screen.fill((0, 0, 0))

        for i in range(len(points) - 1):
            start, width, color = points[i]
            end, _, _ = points[i + 1]
            draw_line_between(screen, start, end, width, color)

        for shape in shapes:
            if shape[0] == 'circle':
                _, pos, size, color = shape
                pygame.draw.circle(screen, color, pos, size)

            elif shape[0] == 'rectangle':
                _, pos, size, color = shape
                rect = pygame.Rect(pos[0] - size, pos[1] - size, size * 2, size * 2)
                pygame.draw.rect(screen, color, rect)

        info = f"Tool: {tool} | Color: {color_mode} | Size: {radius}"
        help_text = "L-line C-circle T-rectangle E-eraser R/G/B-color UP/DOWN-size SPACE-clear"

        info_surface = font.render(info, True, (255, 255, 255))
        help_surface = font.render(help_text, True, (180, 180, 180))

        screen.blit(info_surface, (10, 10))
        screen.blit(help_surface, (10, 35))

        pygame.display.flip()
        clock.tick(60)


main()