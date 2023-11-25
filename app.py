import pygame
import random
import json

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
dt = 0

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
circles = []
spawn_time = 0
circle_size = 80  # initial radius of the circles
score = 0

hit_sound = pygame.mixer.Sound('assets/hit_sound.mp3')  # Replace 'hit_sound.wav' with the actual file path

class Circle(pygame.Vector2):
    def __init__(self, x, y, radius):
        super().__init__(x, y)
        self.radius = radius

    # Function to spawn a circle
    def spawn_circle(position):
        return Circle(position[0], position[1], circle_size)

    def draw_circles(circles):
        for circle in circles:
            pygame.draw.circle(screen, "white", (int(circle.x), int(circle.y)), int(circle.radius))
        
def load_beatmap(filename):
    with open(filename, 'r') as file:
        beatmap_data = json.load(file)
    return beatmap_data


class Menu:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.menu_font = pygame.font.Font(None, 36)
        self.menu_data = self.load_menu_data('menu.json')
        self.menu_index = 0

    def load_menu_data(self, filename):
        with open(filename, 'r') as file:
            menu_data = json.load(file)
        return menu_data

    def display_menu(self):
        self.screen.fill((0, 0, 0))  # Fill the screen with black

        menu_title = self.menu_font.render("Song Menu", True, "white")
        self.screen.blit(menu_title, (500, 50))

        for i, song in enumerate(self.menu_data):
            song_text = f"{i + 1}. {song['title']} - {song['author']} - Difficulty: {song['difficulty']}"
            song_rendered = self.menu_font.render(song_text, True, "white")
            self.screen.blit(song_rendered, (100, 150 + i * 40))

        pygame.display.flip()

    def select_song(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            self.menu_index = (self.menu_index + 1) % len(self.menu_data)
        elif keys[pygame.K_UP]:
            self.menu_index = (self.menu_index - 1) % len(self.menu_data)
        elif keys[pygame.K_RETURN]:
            return self.menu_data[self.menu_index]

        return None

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.display_menu()
            selected_song = self.select_song()

            if selected_song:
                return selected_song

            self.clock.tick(60)

# Load beatmap data
beatmap_data = load_beatmap('osu_beatmap.json')

bg = beatmap_data["background_image"]
bg_img = pygame.image.load("assets/"+bg)
bg_img = pygame.transform.scale(bg_img, (1280, 720))

# Keep track of spawned positions
spawned_positions = set()

# Game states
START_SCREEN = 0
PLAYING = 1
PAUSE_SCREEN = 2
GAME_COMPLETE_SCREEN = 3
END_SCREEN = 4

game_state = START_SCREEN

# Initialize a list to track remaining positions
remaining_positions = list(map(list, beatmap_data['positions']))

# Load and play the audio file
audio_filename = beatmap_data.get('audio', '')
if audio_filename:
    pygame.mixer.music.load(audio_filename)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == PLAYING:
                    game_state = PAUSE_SCREEN
                    pygame.mixer.music.pause()
                elif game_state == PAUSE_SCREEN:
                    game_state = PLAYING
                    pygame.mixer.music.unpause()

    screen.blit(bg_img, (0, 0))

    if game_state == START_SCREEN:
        # Display start screen
        font = pygame.font.Font(None, 50)
        start_text = font.render("Click to Start", True, "white")
        screen.blit(start_text, (500, 300))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            game_state = PLAYING
            pygame.mixer.music.play()

    elif game_state == PLAYING:
        # Check for circle spawn
        current_time = pygame.time.get_ticks()

        while remaining_positions:
            if current_time - spawn_time >= beatmap_data['circle_spawn_interval']:
                position = remaining_positions.pop(0)  # Pop the first position from the list
                circles.append(spawn_circle(position))
                spawn_time = current_time
            else:
                # No need to continue checking if the time interval is not met
                break

        # Draw circles and update their radius
        for circle in circles:
            pygame.draw.circle(screen, "white", (int(circle.x), int(circle.y)), int(circle.radius))
            circle.radius -= dt * beatmap_data['shrink_rate']

            if circle.radius <= 0:
                game_state = END_SCREEN

        pygame.draw.circle(screen, "red", (int(player_pos.x), int(player_pos.y)), 20)

        keys = pygame.key.get_pressed()
        player_pos = pygame.Vector2(pygame.mouse.get_pos())

        # Check for click on circle
        if keys[pygame.K_SPACE]:
            for circle in circles:
                distance = player_pos.distance_to(circle)
                if distance < circle.radius:
                    hit_sound.play()
                    print("Clicked on circle!")
                    score += 1
                    circles.remove(circle)

        # Display score and other information
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {score}", True, "white")
        screen.blit(text, (10, 10))

        # Display additional information from the JSON file
        additional_info = f"Title: {beatmap_data.get('title', '')}  Artist: {beatmap_data.get('artist', '')}"
        text_info = font.render(additional_info, True, "white")
        screen.blit(text_info, (10, 50))

    elif game_state == PAUSE_SCREEN:
        # Display pause screen
        font = pygame.font.Font(None, 50)
        pause_text = font.render("Paused", True, "white")
        screen.blit(pause_text, (550, 300))

    elif game_state == GAME_COMPLETE_SCREEN:
        # Display game complete screen
        font = pygame.font.Font(None, 50)
        complete_text = font.render(f"Game Over. Score: {score}", True, "white")
        screen.blit(complete_text, (400, 300))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            # Reset game staten
            game_state = START_SCREEN
            score = 0
            circles.clear()
            remaining_positions = list(map(list, beatmap_data['positions']))

    elif game_state == END_SCREEN:
        # Display end screen
        font = pygame.font.Font(None, 50)
        end_text = font.render(f"Missed a circle! Score: {score}", True, "white")
        screen.blit(end_text, (400, 300))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            # Reset game state
            game_state = START_SCREEN
            score = 0
            circles.clear()
            remaining_positions = list(map(list, beatmap_data['positions']))

    pygame.display.flip()

    dt = clock.tick(60) / 1000
