import pygame
import time
import random
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 700
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

# We will no longer need the static background image
# BG = pygame.transform.scale(pygame.image.load("assets/bg.png"), (WIDTH, HEIGHT))
FONT = pygame.font.SysFont("Times New Roman", 30)

class Particle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        # Give particles different speeds for a parallax effect
        self.speed = random.uniform(0.5, 2.5) 
        # Give particles different sizes
        self.size = random.randint(1, 3)
        # Give particles slightly different shades of grey/white
        self.color = (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))


def draw(player, time_passed, obstacles, bullets, particles):
    # Fill the screen with black instead of blitting a static image
    WIN.fill((0, 0, 0))

    # Draw the star particles
    for particle in particles:
        pygame.draw.circle(WIN, particle.color, (int(particle.x), int(particle.y)), particle.size)

    time_text = FONT.render(f"{round(time_passed)}", 1, "yellow")
    WIN.blit(time_text, (10, 10))
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

    obstacle_increment = 310
    obstacle_timing = 0
    obstacles = []

    bullets = []

    # Create a list to hold the star particles
    particles = []
    for _ in range(250):  # You can adjust this number for more or fewer stars
        particles.append(Particle())
        
    run = True
    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)

    pygame.mixer.music.load('assets/bg_music.mp3')
    pygame.mixer.music.play(-1)
    
    while run:
        obstacle_timing += clock.tick(FPS)
        time_passed = (pygame.time.get_ticks() - started_time) / 1000

        if obstacle_timing > obstacle_increment:
            for i in range(3):
                obstacle_x = random.randint(0, WIDTH - OBSTACLE_WIDTH)
                obstacle = pygame.Rect(obstacle_x, -OBSTACLE_HEIGHT, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
                obstacles.append(obstacle)
            obstacle_timing = 0
        
        # Update and wrap the star particles
        for particle in particles:
            particle.y += particle.speed
            if particle.y > HEIGHT:
                particle.y = 0
                particle.x = random.randint(0, WIDTH)

        for bullet in bullets:
            bullet.y -= BULLET_VELOCITY
            if bullet.y < 0:
                bullets.remove(bullet)

            for obstacle in obstacles[:]:
                if bullet.colliderect(obstacle):
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

        for obstacle in obstacles[:]:
            obstacle.y += OBSTACLE_VELOCITY
            if obstacle.y > HEIGHT:
                obstacles.remove(obstacle)
            
            elif obstacle.y >= player.y and obstacle.colliderect(player):
                #Game Over
                obstacles.remove(obstacle)
                break

        # Pass the particle list to the draw function
        draw(player, time_passed, obstacles, bullets, particles)


    pygame.quit()


if __name__ == "__main__":
    main()