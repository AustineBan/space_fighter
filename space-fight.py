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
OBSTACLE_WIDTH = 22
OBSTACLE_HEIGHT = 15
OBSTACLE_VELOCITY = 6

#Bullet
BULLET_WIDTH = 5
BULLET_HEIGHT = 10
BULLET_VELOCITY = 15

BG = pygame.transform.scale(pygame.image.load("assets/bg.png"), (WIDTH, HEIGHT))
FONT = pygame.font.SysFont("Times New Roman", 30)

class Particle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)

        if self.size == 1:
            self.speed = random.uniform(0.5, 1.5) 
            self.color = (random.randint(50, 90), random.randint(50, 90), random.randint(50, 90))
        elif self.size == 2:
            self.speed = random.uniform(1, 2) 
            self.color = (random.randint(80, 130), random.randint(80, 130), random.randint(80, 130))
        else:
            self.speed = random.uniform(1.5, 2.5) 
            self.color = (random.randint(120, 170), random.randint(120, 170), random.randint(120, 170))


def draw(player, time_passed, obstacles, bullets, particles, user_score):
    WIN.fill((0, 0, 0))
    for particle in particles:
        pygame.draw.circle(WIN, particle.color, (int(particle.x), int(particle.y)), particle.size)
    time_text = FONT.render(f"Time: {round(time_passed)}", 1, "yellow")
    WIN.blit(time_text, (10, 10))
    user_score_text = FONT.render(f"Kills {user_score}", 1, "yellow")
    WIN.blit(user_score_text, (WIDTH - user_score_text.get_width() - 10, 10))
    for bullet in bullets:
        pygame.draw.rect(WIN, 'white', bullet)
    for obstacle in obstacles:
        pygame.draw.rect(WIN, 'red', obstacle)
    pygame.draw.rect(WIN, 'orange', player)
    pygame.display.update()

def main():
    clock = pygame.time.Clock()
    started_time = pygame.time.get_ticks()
    time_passed = 0
    user_score = 0

    obstacle_increment = 310
    obstacle_timing = 0
    obstacles = []

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

    pygame.mixer.music.load('assets/bg_music.mp3')
    pygame.mixer.music.play(-1)
    while run:
        obstacle_timing += clock.tick(FPS)
        time_passed = (pygame.time.get_ticks() - started_time) / 1000

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
                    if bullet in bullets:
                        obstacles.remove(obstacle)
                        bullets.remove(bullet)
                    break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bullet = pygame.Rect(player.centerx - BULLET_WIDTH // 2, player.top, BULLET_WIDTH, BULLET_HEIGHT)
                bullets.append(bullet)


        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - PLAYER_VELOCITY >= 0:
            player.x -= PLAYER_VELOCITY
        if keys[pygame.K_RIGHT] and player.x + PLAYER_VELOCITY + player.width <= WIDTH:
            player.x += PLAYER_VELOCITY

        if keys[pygame.K_UP] and player.y - PLAYER_VELOCITY >= 0:
            player.y -= PLAYER_VELOCITY
        if keys[pygame.K_DOWN] and player.y + PLAYER_VELOCITY + player.height <= HEIGHT:
            player.y += PLAYER_VELOCITY

        for obstacle in obstacles[:]:
            obstacle.y += current_obstacle_velocity
            if obstacle.y > HEIGHT:
                obstacles.remove(obstacle)
            
            elif obstacle.y >= player.y and obstacle.colliderect(player):
                #Game Over
                obstacles.remove(obstacle)
                break

        draw(player, time_passed, obstacles, bullets, particles, user_score)


    pygame.quit()




if __name__ == "__main__":
    main()