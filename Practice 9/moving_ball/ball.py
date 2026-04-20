import pygame

WIDTH, HEIGHT = 600, 400
WHITE = (255, 255, 255)
RED = (255, 0, 0)

BALL_RADIUS = 25
STEP = 20


def run_game():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Moving Ball Game")
    clock = pygame.time.Clock()

    x = WIDTH // 2
    y = HEIGHT // 2

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if x - STEP >= BALL_RADIUS:
                        x -= STEP

                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if x + STEP <= WIDTH - BALL_RADIUS:
                        x += STEP

                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    if y - STEP >= BALL_RADIUS:
                        y -= STEP

                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if y + STEP <= HEIGHT - BALL_RADIUS:
                        y += STEP

        screen.fill(WHITE)
        pygame.draw.circle(screen, RED, (x, y), BALL_RADIUS)

        pygame.display.flip()
        clock.tick(60)