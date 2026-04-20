import pygame
import os
import time

WIDTH, HEIGHT = 700, 300
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
INFO_COLOR = (180, 180, 180)
BAR_COLOR = (70, 130, 180)
BAR_BG_COLOR = (80, 80, 80)

MUSIC_FOLDER = "music"
TRACKS = ["track1.mp3", "track2.mp3", "track3.mp3"]


def load_tracks():
    playlist = []
    for track in TRACKS:
        path = os.path.join(MUSIC_FOLDER, track)
        if os.path.exists(path):
            playlist.append(path)
    return playlist


def format_time(seconds):
    seconds = max(0, int(seconds))
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02}:{secs:02}"


def draw_text(screen, font, text, x, y, color):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def get_track_length(track_path):
    sound = pygame.mixer.Sound(track_path)
    return sound.get_length()


def run_player():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Music Player")
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont(None, 40)
    text_font = pygame.font.SysFont(None, 30)

    playlist = load_tracks()
    if not playlist:
        running = True
        while running:
            screen.fill(BG_COLOR)
            draw_text(screen, title_font, "No tracks found", 240, 110, TEXT_COLOR)
            draw_text(screen, text_font, "Put track1.mp3, track2.mp3, track3.mp3 into music folder", 60, 160, INFO_COLOR)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            pygame.display.flip()
            clock.tick(30)
        return

    current_index = 0
    is_playing = False
    start_time = 0
    current_length = get_track_length(playlist[current_index])

    def play_current_track():
        nonlocal is_playing, start_time, current_length
        pygame.mixer.music.load(playlist[current_index])
        pygame.mixer.music.play()
        is_playing = True
        start_time = time.time()
        current_length = get_track_length(playlist[current_index])

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    play_current_track()

                elif event.key == pygame.K_s:
                    pygame.mixer.music.stop()
                    is_playing = False

                elif event.key == pygame.K_n:
                    current_index = (current_index + 1) % len(playlist)
                    play_current_track()

                elif event.key == pygame.K_b:
                    current_index = (current_index - 1) % len(playlist)
                    play_current_track()

                elif event.key == pygame.K_q:
                    running = False

        if is_playing and not pygame.mixer.music.get_busy():
            current_index = (current_index + 1) % len(playlist)
            play_current_track()

        screen.fill(BG_COLOR)

        current_track_name = os.path.basename(playlist[current_index])
        draw_text(screen, title_font, "Music Player", 250, 20, TEXT_COLOR)
        draw_text(screen, text_font, f"Current Track: {current_track_name}", 50, 80, TEXT_COLOR)
        draw_text(screen, text_font, f"Playlist Position: {current_index + 1}/{len(playlist)}", 50, 120, TEXT_COLOR)
        draw_text(screen, text_font, "P=Play  S=Stop  N=Next  B=Previous  Q=Quit", 50, 240, INFO_COLOR)

        elapsed = 0
        if is_playing:
            elapsed = time.time() - start_time
            if elapsed > current_length:
                elapsed = current_length

        draw_text(
            screen,
            text_font,
            f"Track Position: {format_time(elapsed)} / {format_time(current_length)}",
            50,
            160,
            TEXT_COLOR
        )

        bar_x = 50
        bar_y = 200
        bar_width = 600
        bar_height = 20

        pygame.draw.rect(screen, BAR_BG_COLOR, (bar_x, bar_y, bar_width, bar_height))

        progress = 0
        if current_length > 0:
            progress = elapsed / current_length

        progress_width = int(progress * bar_width)
        pygame.draw.rect(screen, BAR_COLOR, (bar_x, bar_y, progress_width, bar_height))

        pygame.display.flip()
        clock.tick(30)