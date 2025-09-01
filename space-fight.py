import pygame
import time
import random
pygame.font.init()
pygame.mixer.init()

WIDTH ,HEIGHT = 1000, 700
PLAYER_HEIGHT = 40
PLAYER_WIDTH = 70
PLAYER_VELOCITY = 10
FPS = 60
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SPACE FIGHTER")

#OBSTACLE
OBSTACLE_WIDTH = 32
OBSTACLE_HEIGHT = 45
OBSTACLE_VELOCITY = 6

#Bullet
BULLET_WIDTH = 5
BULLET_HEIGHT = 10
BULLET_VELOCITY = 15

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

OBSTALCE_IMAGE = pygame.transform.scale(pygame.image.load("assets/obstacle/obstacle.png"), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
OBSTACLE_FIRE_FRAMES = [
    pygame.transform.scale(pygame.image.load(f"assets/obstacle/Exhaust_0{i}.png"), (OBSTACLE_WIDTH, 30)) for i in range(1, 7)
]

# Load Laser Image
LASER_IMAGE = pygame.transform.scale(pygame.image.load("assets/player/LaserBlue.png"), (BULLET_WIDTH, BULLET_HEIGHT))

FONT = pygame.font.SysFont("Times New Roman", 30)

# SHOT_FX = pygame.mixer.Sound("assets/audio/sound/shot.wav")
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


def draw(player, time_passed, obstacles, bullets, particles, user_score, current_fire_frame, player_direction, player_live):
    WIN.fill((0, 0, 30))
    for particle in particles:
        pygame.draw.circle(WIN, particle.color, (int(particle.x), int(particle.y)), particle.size)
    time_text = FONT.render(f"Time: {round(time_passed)}", 1, "yellow")
    WIN.blit(time_text, (10, 10))
    user_score_text = FONT.render(f"Kills {user_score}", 1, "yellow")
    WIN.blit(user_score_text, (WIDTH - user_score_text.get_width() - 10, 10))
    for bullet in bullets:
        # pygame.draw.rect(WIN, 'white', bullet)
        WIN.blit(LASER_IMAGE, bullet)
    for obstacle in obstacles:
        WIN.blit(OBSTACLE_FIRE_FRAMES[current_fire_frame], (obstacle.x, obstacle.y))
        # pygame.draw.rect(WIN, 'red', obstacle)
        WIN.blit(OBSTALCE_IMAGE, obstacle)
    # pygame.draw.rect(WIN, 'orange', player)
    WIN.blit(FIRE_FRAMES[current_fire_frame], (player.x, player.y + player.height-15))
    WIN.blit(PLAYER_IMAGES[player_direction], (player.x, player.y))

    lives_text = HEART_FONT.render("❤️" * player_live, True, "red")
    lives_text_rect = lives_text.get_rect(center=(WIDTH/2, 25))
    WIN.blit(lives_text, lives_text_rect)
    pygame.display.update()

def main():
    clock = pygame.time.Clock()
    started_time = pygame.time.get_ticks()
    time_passed = 0
    user_score = 0

    player_direction = "middle"

    obstacle_increment = 310
    obstacle_timing = 0
    obstacles = []

    shoot_cooldown = 0   
    shoot_delay = 100  
    player_live = PLAYERS_LIVES

    # Fire animation variables
    fire_animation_frames = 6
    fire_animation_speed = 1
    current_fire_frame = 0
    fire_frame_timer = 0

    # Variables for progressive difficulty
    current_obstacle_velocity = OBSTACLE_VELOCITY
    current_obstacle_count = 2
    difficulty_level = 0
    difficulty_level_count = 0

    bullets = []
    particles = []

    for _ in range(250):
        particles.append(Particle())

    run = True
    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)

    pygame.mixer.music.load('assets/audio/music/bg_music.mid')
    pygame.mixer.music.play(-1)
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

            for obstacle in obstacles[:]:
                if bullet.colliderect(obstacle):
                    user_score += 1
                    HIT_FX.play()
                    if bullet in bullets:
                        obstacles.remove(obstacle)
                        bullets.remove(bullet)
                    break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            # if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            #     bullet = pygame.Rect(player.centerx - BULLET_WIDTH // 2, player.top, BULLET_WIDTH, BULLET_HEIGHT)
            #     bullets.append(bullet)

        # reduce cooldown
        if shoot_cooldown > 0:
            shoot_cooldown -= dt

        keys = pygame.key.get_pressed()

        # --- Continuous shooting ---
        if keys[pygame.K_SPACE] and shoot_cooldown <= 0:
            SHOT_FX.play()
            bullet = pygame.Rect(player.centerx - BULLET_WIDTH // 2, player.top, BULLET_WIDTH, BULLET_HEIGHT)
            bullets.append(bullet)
            shoot_cooldown = shoot_delay   # reset cooldown


       # Inside the while run: loop
        keys = pygame.key.get_pressed()
        player_direction = "middle"  # Default to middle view if no keys are pressed

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

        # The rest of your movement code (for up and down) goes here
        if keys[pygame.K_UP]:
            player.y -= PLAYER_VELOCITY
        if keys[pygame.K_DOWN]:
            player.y += PLAYER_VELOCITY

        # Boundary checks to prevent the player from leaving the screen
        player.x = max(0, min(player.x, WIDTH - player.width))
        player.y = max(0, min(player.y, HEIGHT - player.height))

        for obstacle in obstacles[:]:
            obstacle.y += current_obstacle_velocity
            if obstacle.y > HEIGHT:
                obstacles.remove(obstacle)
            
            elif obstacle.y >= player.y and obstacle.colliderect(player):
                EXPLOSION_FX.play()
                obstacles.remove(obstacle)
                player_live -= 1
                if player_live <= 0:
                    pass #Game Over
                break

        draw(player, time_passed, obstacles, bullets, particles, user_score, current_fire_frame=current_fire_frame, player_direction=player_direction, player_live=player_live)


    pygame.quit()




if __name__ == "__main__":
    main()