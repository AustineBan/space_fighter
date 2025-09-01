import pygame
import time
import random
import os
import json
pygame.font.init()
pygame.mixer.init()

WIDTH ,HEIGHT = 1000, 700
PLAYER_HEIGHT = 40
PLAYER_WIDTH = 70
PLAYER_VELOCITY = 10
FPS = 60
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SPACE FIGHTER")

# High Score File Path
HIGH_SCORE_FILE = "high_scores.json"

#OBSTACLE
OBSTACLE_WIDTH = 32
OBSTACLE_HEIGHT = 45
OBSTACLE_VELOCITY = 6

#Bullet
BULLET_WIDTH = 5
BULLET_HEIGHT = 10
BULLET_VELOCITY = 15

# 
BG = pygame.transform.scale(pygame.image.load("assets/bg.png"), (WIDTH, HEIGHT))

# PLAYER_WIDTH and PLAYER_HEIGHT must match your images
PLAYER_WIDTH = 64
PLAYER_HEIGHT = 70

HEART_FONT = pygame.font.SysFont("Segoe UI Emoji", 30)

# Player Images
PLAYER_IMAGES = {
    "middle": pygame.transform.scale(pygame.image.load("assets/player/character/PlayerBlue_middle.png"), (PLAYER_WIDTH, PLAYER_HEIGHT)),
    "left": pygame.transform.scale(pygame.image.load("assets/player/character/PlayerBlue_left.png"), (PLAYER_WIDTH, PLAYER_HEIGHT)),
    "left_left": pygame.transform.scale(pygame.image.load("assets/player/character/PlayerBlue_left_left.png"), (PLAYER_WIDTH, PLAYER_HEIGHT)),
    "right": pygame.transform.scale(pygame.image.load("assets/player/character/PlayerBlue_right.png"), (PLAYER_WIDTH, PLAYER_HEIGHT)),
    "right_right": pygame.transform.scale(pygame.image.load("assets/player/character/PlayerBlue_right_right.png"), (PLAYER_WIDTH, PLAYER_HEIGHT))
}

# Exhaust Fire Animation Frames
FIRE_FRAMES = [
    pygame.transform.scale(pygame.image.load(f"assets/player/exhaust/Exhaust_0{i}.png"), (PLAYER_WIDTH, 30)) for i in range(1, 7)
]

# Explosion Images
EXPLOSION_IMAGES = [pygame.transform.scale(pygame.image.load(os.path.join("assets", "Explosion", f"Explosion0{i}.png")), (100, 100)) for i in range(1, 10)]

OBSTALCE_IMAGE = pygame.transform.scale(pygame.image.load("assets/obstacle/obstacle.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
OBSTACLE_FIRE_FRAMES = [
    pygame.transform.scale(pygame.image.load(f"assets/obstacle/Exhaust_0{i}.png"), (OBSTACLE_WIDTH, 30)) for i in range(1, 7)
]

# Load Laser Image
LASER_IMAGE = pygame.transform.scale(pygame.image.load("assets/player/LaserBlue.png"), (BULLET_WIDTH, BULLET_HEIGHT))

FONT = pygame.font.SysFont("Times New Roman", 30)

SHOT_FX = pygame.mixer.Sound("assets/audio/sound/shot.ogg")
SHOT_FX.set_volume(0.8)
EXPLOSION_FX = pygame.mixer.Sound("assets/audio/sound/explosion.wav")
HIT_FX = pygame.mixer.Sound("assets/audio/sound/hit.wav")
PLAYERS_LIVES = 5

class Particle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)

        if self.size == 1:
            self.speed = random.uniform(0.5, 1.5) 
            self.color = (random.randint(50, 100), random.randint(50, 100), random.randint(50, 100))
        elif self.size == 2:
            self.speed = random.uniform(1, 2) 
            self.color = (random.randint(80, 170), random.randint(80, 170), random.randint(80, 170))
        else:
            self.speed = random.uniform(1.5, 2.5) 
            self.color = (random.randint(120, 220), random.randint(120, 220), random.randint(120, 220))

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = EXPLOSION_IMAGES
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50  # milliseconds per frame
        self.done = False

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame < len(self.images):
                self.image = self.images[self.frame]
            else:
                self.done = True

def draw(player, time_passed, obstacles, bullets, particles, user_score, current_fire_frame, player_direction, player_live, explosions):
    WIN.fill((0, 0, 30))
    for particle in particles:
        pygame.draw.circle(WIN, particle.color, (int(particle.x), int(particle.y)), particle.size)
    time_text = FONT.render(f"Time: {round(time_passed)}", 1, "yellow")
    WIN.blit(time_text, (10, 10))
    user_score_text = FONT.render(f"Kills {user_score}", 1, "yellow")
    WIN.blit(user_score_text, (WIDTH - user_score_text.get_width() - 10, 10))
    for bullet in bullets:
        WIN.blit(LASER_IMAGE, bullet)
    for obstacle in obstacles:
        WIN.blit(OBSTACLE_FIRE_FRAMES[current_fire_frame], (obstacle.x, obstacle.y))
        WIN.blit(OBSTALCE_IMAGE, obstacle)
    WIN.blit(FIRE_FRAMES[current_fire_frame], (player.x, player.y + player.height-15))
    WIN.blit(PLAYER_IMAGES[player_direction], (player.x, player.y))

    # Draw all active explosions
    for explosion in explosions:
        WIN.blit(explosion.image, explosion.rect)

    lives_text = HEART_FONT.render("❤️" * player_live, True, "red")
    lives_text_rect = lives_text.get_rect(center=(WIDTH/2, 25))
    WIN.blit(lives_text, lives_text_rect)
    pygame.display.update()

def show_game_over_screen(final_score, final_time):
    """Displays the game over screen with scores, high scores, and buttons."""
    high_scores = load_high_scores()
    new_kills_record = False
    new_time_record = False

    if final_score > high_scores["kills_record"]["score"]:
        new_kills_record = True
        high_scores["kills_record"]["score"] = final_score
    
    if final_time > high_scores["time_record"]["score"]:
        new_time_record = True
        high_scores["time_record"]["score"] = final_time
    
    player_name = "N/A"
    if new_kills_record or new_time_record:
        name_prompt = FONT.render("New High Score! Enter your name:", True, "white")
        name_prompt_rect = name_prompt.get_rect(center=(WIDTH/2, HEIGHT/2 - 100))
        name_input = ""
        input_rect = pygame.Rect(WIDTH/2 - 100, HEIGHT/2 - 50, 200, 40)
        active = True

        while active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                    else:
                        name_input += event.unicode
            
            WIN.fill((0, 0, 30))
            WIN.blit(name_prompt, name_prompt_rect)
            pygame.draw.rect(WIN, "white", input_rect, 2)
            name_surface = FONT.render(name_input, True, "white")
            WIN.blit(name_surface, (input_rect.x + 5, input_rect.y + 5))
            pygame.display.update()
        
        player_name = name_input.strip() if name_input.strip() else "Anonymous"
        
        if new_kills_record:
            high_scores["kills_record"]["name"] = player_name
        if new_time_record:
            high_scores["time_record"]["name"] = player_name
        
    save_high_scores(high_scores)

    # Game Over screen loop
    game_over_loop = True
    while game_over_loop:
        WIN.fill((0, 0, 30))
        
        # Display Final Score
        game_over_text = FONT.render("GAME OVER", True, "red")
        game_over_rect = game_over_text.get_rect(center=(WIDTH/2, HEIGHT/2 - 150))
        WIN.blit(game_over_text, game_over_rect)

        final_score_text = FONT.render(f"Final Kills: {final_score} | Time Survived: {round(final_time)}s", True, "white")
        final_score_rect = final_score_text.get_rect(center=(WIDTH/2, HEIGHT/2 - 80))
        WIN.blit(final_score_text, final_score_rect)

        # Display High Scores
        high_score_title = FONT.render("High Scores", True, "gold")
        high_score_title_rect = high_score_title.get_rect(center=(WIDTH/2, HEIGHT/2 - 20))
        WIN.blit(high_score_title, high_score_title_rect)

        kills_record_text = FONT.render(
            f"Highest Kills: {high_scores['kills_record']['score']} by {high_scores['kills_record']['name']}",
            True, "white"
        )
        kills_record_rect = kills_record_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 20))
        WIN.blit(kills_record_text, kills_record_rect)

        time_record_text = FONT.render(
            f"Longest Time: {round(high_scores['time_record']['score'])}s by {high_scores['time_record']['name']}",
            True, "white"
        )
        time_record_rect = time_record_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 50))
        WIN.blit(time_record_text, time_record_rect)
        
        # Draw buttons
        restart_button = pygame.Rect(WIDTH/2 - 150, HEIGHT/2 + 120, 140, 50)
        close_button = pygame.Rect(WIDTH/2 + 10, HEIGHT/2 + 120, 140, 50)

        pygame.draw.rect(WIN, (50, 200, 50), restart_button)
        pygame.draw.rect(WIN, (200, 50, 50), close_button)

        restart_text = FONT.render("Restart", True, "white")
        close_text = FONT.render("Close", True, "white")
        
        restart_text_rect = restart_text.get_rect(center=restart_button.center)
        close_text_rect = close_text.get_rect(center=close_button.center)
        
        WIN.blit(restart_text, restart_text_rect)
        WIN.blit(close_text, close_text_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over_loop = False
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    return True
                if close_button.collidepoint(event.pos):
                    game_over_loop = False
                    return False
    return False

def load_high_scores():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as f:
            return json.load(f)
    return {
        "kills_record": {"score": 0, "name": "N/A"},
        "time_record": {"score": 0, "name": "N/A"}
    }

def save_high_scores(scores):
    with open(HIGH_SCORE_FILE, "w") as f:
        json.dump(scores, f, indent=4)

def main():
    
    while True:
        clock = pygame.time.Clock()
        started_time = pygame.time.get_ticks()
        time_passed = 0
        user_score = 0
        player_direction = "middle"
        obstacle_increment = 310
        obstacle_timing = 0
        obstacles = []
        explosions = []  # List to hold active explosions
        bullets = []
        particles = []
        shoot_cooldown = 0
        shoot_delay = 100
        player_live = PLAYERS_LIVES
        fire_animation_frames = 6
        fire_animation_speed = 1
        current_fire_frame = 0
        fire_frame_timer = 0
        current_obstacle_velocity = OBSTACLE_VELOCITY
        current_obstacle_count = 2
        difficulty_level = 0
        difficulty_level_count = 0
        
        for _ in range(250):
            particles.append(Particle())
        player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        
        pygame.mixer.music.load('assets/audio/music/bg_music.mid')
        pygame.mixer.music.play(-1)
        
        run = True
        while run:
            dt = clock.tick(FPS)
            obstacle_timing += dt
            time_passed = (pygame.time.get_ticks() - started_time) / 1000

            fire_frame_timer += 1
            if fire_frame_timer > fire_animation_speed:
                current_fire_frame = (current_fire_frame + 1) % fire_animation_frames
                fire_frame_timer = 0

            DIF_NUM = 10
            if time_passed // DIF_NUM > difficulty_level:
                difficulty_level += 1
                current_obstacle_velocity += 0.8

            if (time_passed // (DIF_NUM * 4)) > difficulty_level_count:
                difficulty_level_count += 1
                current_obstacle_count += 1

            for particle in particles:
                particle.y += particle.speed
                if particle.y > HEIGHT:
                    particle.y = 0
                    particle.x = random.randint(0, WIDTH)

            if obstacle_timing > obstacle_increment:
                for i in range(current_obstacle_count):
                    obstacle_x = random.randint(0, WIDTH - OBSTACLE_WIDTH)
                    obstacle = pygame.Rect(obstacle_x, -OBSTACLE_HEIGHT, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
                    obstacles.append(obstacle)
                obstacle_timing = 0

            for bullet in bullets:
                bullet.y -= BULLET_VELOCITY
                if bullet.y < 0:
                    bullets.remove(bullet)

                # Check for bullet-obstacle collision
                for obstacle in obstacles[:]:
                    if bullet.colliderect(obstacle):
                        user_score += 1
                        HIT_FX.play()
                        # Create explosion effect
                        explosions.append(Explosion(obstacle.centerx, obstacle.centery))
                        if bullet in bullets:
                            obstacles.remove(obstacle)
                            bullets.remove(bullet)
                        break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break
            
            # reduce cooldown
            if shoot_cooldown > 0:
                shoot_cooldown -= dt

            keys = pygame.key.get_pressed()

            # --- Continuous shooting ---
            if keys[pygame.K_SPACE] and shoot_cooldown <= 0:
                SHOT_FX.play()
                bullet = pygame.Rect(player.centerx - BULLET_WIDTH // 2, player.top, BULLET_WIDTH, BULLET_HEIGHT)
                bullets.append(bullet)
                shoot_cooldown = shoot_delay

            keys = pygame.key.get_pressed()
            player_direction = "middle"
            if keys[pygame.K_LEFT]:
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    player_direction = "left_left"
                else:
                    player_direction = "left"
                player.x -= PLAYER_VELOCITY
            elif keys[pygame.K_RIGHT]:
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    player_direction = "right_right"
                else:
                    player_direction = "right"
                player.x += PLAYER_VELOCITY

            if keys[pygame.K_UP]:
                player.y -= PLAYER_VELOCITY
            if keys[pygame.K_DOWN]:
                player.y += PLAYER_VELOCITY

            player.x = max(0, min(player.x, WIDTH - player.width))
            player.y = max(0, min(player.y, HEIGHT - player.height))

            for obstacle in obstacles[:]:
                obstacle.y += current_obstacle_velocity
                if obstacle.y > HEIGHT:
                    obstacles.remove(obstacle)
                
                # Check for player-obstacle collision
                elif obstacle.y >= player.y and obstacle.colliderect(player):
                    EXPLOSION_FX.play()
                    # Create explosion effect
                    explosions.append(Explosion(player.centerx, player.centery))
                    obstacles.remove(obstacle)
                    player_live -= 1
                    if player_live <= 0:
                        run = False
                    break
            
            # Update and clean up explosions
            for explosion in explosions[:]:
                explosion.update()
                if explosion.done:
                    explosions.remove(explosion)

            draw(player, time_passed, obstacles, bullets, particles, user_score, current_fire_frame=current_fire_frame, player_direction=player_direction, player_live=player_live, explosions=explosions)

        if not show_game_over_screen(user_score, time_passed):
            break

    pygame.quit()


if __name__ == "__main__":
    main()
