import pygame
import math
from datetime import datetime

WIDTH, HEIGHT = 800, 800
CENTER = (WIDTH // 2, HEIGHT // 2)

IMAGE_PATH = "images/mickeyclock.jpeg"


def get_hand_end(center, length, angle_degrees):
    angle_radians = math.radians(angle_degrees - 90)
    x = center[0] + length * math.cos(angle_radians)
    y = center[1] + length * math.sin(angle_radians)
    return int(x), int(y)


def run_clock():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mickey Clock")
    timer = pygame.time.Clock()

    background = pygame.image.load(IMAGE_PATH)
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        now = datetime.now()
        minutes = now.minute
        seconds = now.second

        minute_angle = minutes * 6
        second_angle = seconds * 6

        minute_end = get_hand_end(CENTER, 180, minute_angle)
        second_end = get_hand_end(CENTER, 240, second_angle)

        screen.blit(background, (0, 0))

        # right hand = minutes hand
        pygame.draw.line(screen, (210, 0, 50), CENTER, minute_end, 6)

        # left hand = seconds hand
        pygame.draw.line(screen, (210, 0, 50), CENTER, second_end, 3)

        pygame.draw.circle(screen, (0, 0, 0), CENTER, 8)

        pygame.display.flip()
        timer.tick(1)