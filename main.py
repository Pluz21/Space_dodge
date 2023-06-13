import pygame
import random # Generate random numbers for the stars and bonuses
import math # Needed for the log function for bonus scaling
import os
pygame.init()

# Set up the window
WIDTH, HEIGHT = 1000, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Dodge")  

# Load and play the background music
pygame.mixer.music.load('sounds/music2.WAV')

pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)  # Set -1 to loop the music indefinitely


# Define the actual width and height of the boss star image
BOSS_STAR_WIDTH = 400
BOSS_STAR_HEIGHT = 300
SPACESHIP_HEIGHT = 135
SPACESHIP_WIDTH = 150
scroll = - HEIGHT // 0.15
scroll_speed = 1  # Adjust the scroll speed as needed

# Load images and fonts
BG = pygame.image.load("media/full_background.png").convert_alpha()

SpaceShip = pygame.image.load('media/spaceshipmain.png')
SpaceShip_scaled = pygame.transform.scale(SpaceShip, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))
FONT = pygame.font.SysFont("Orbitron", 35)
Bossstar = pygame.image.load("media/bossstar3.png")
Bossstar_scaled = pygame.transform.scale(Bossstar, (BOSS_STAR_WIDTH, BOSS_STAR_HEIGHT))

# Player settings
PLAYER_WIDTH = SPACESHIP_WIDTH
PLAYER_HEIGHT = SPACESHIP_HEIGHT
PLAYER_VEL = 10

# Bonus Settings
BONUS_RADIUS = 15
BONUS_COLOR = (255, 0, 0)
BONUS_TEXT_COLOR = (255, 255, 255)
BONUS_FONT = pygame.font.SysFont("Quantico", 20)
BONUS_VEL = 8
SPAWN_BONUS_INTERVAL = 200 # in milliseconds

# Star settings
STAR_WIDTH = 10
STAR_HEIGHT = 20
STAR_VEL = 7.5

# Projectile settings
PROJECTILE_WIDTH = 3.5
PROJECTILE_HEIGHT = 10
PROJECTILE_VEL = 15
SPAWN_PROJECTILE_INTERVAL = 1000  # in milliseconds

# Define font variables
TIMER_FONT = pygame.font.SysFont("Orbitron", 30)

class Player:
    def __init__(self, x, y):
        player_hitbox_width = 104  # Define the width of the hitbox
        player_hitbox_height = 120  # Define the height of the hitbox
        self.rect = pygame.Rect(x, y, player_hitbox_width, player_hitbox_height)
        self.side_shooting_enabled = False
    
    # Checking that movement is within window boundaries
    def move(self, dx, dy): 
        if self.rect.x + dx > 0 and self.rect.x + dx + PLAYER_WIDTH < WIDTH:      
            self.rect.x += dx
        if self.rect.y + dy > 0 and self.rect.y + dy + PLAYER_HEIGHT < HEIGHT:
            self.rect.y += dy

    def shoot(self):
        """ Angles for side shooting, you can add as many as you want to increase 
        the amount of projectiles once side shooting is enabled"""
        projectiles = []
        if bonus_score >= 3 and self.side_shooting_enabled:
            angles = [0, -15, 15]  
            for angle in angles:
                # Use negative sine for y-axis velocity
                projectile = Projectile(
                    self.rect.x + self.rect.width // 2 - PROJECTILE_WIDTH // 2,
                    self.rect.y,
                    PROJECTILE_WIDTH,
                    PROJECTILE_HEIGHT,
                    angle
                )
                projectiles.append(projectile)
        else:
            projectile = Projectile(
                self.rect.x + self.rect.width // 2 - PROJECTILE_WIDTH // 2,
                self.rect.y,
                PROJECTILE_WIDTH,
                PROJECTILE_HEIGHT,
            )
            projectiles.append(projectile)
        
        # Play shoot sound effect
        shoot_sound.play()
        
        return projectiles
    
    def enable_side_shooting(self):
        self.side_shooting_enabled = True

    def draw(self):
        WIN.blit(SpaceShip_scaled, self.rect)
        
    def reduce_projectile_spawn_interval(self):
        global SPAWN_PROJECTILE_INTERVAL
        scaling_factor = 0.1  
        #Higher values will make the reduction more 
        #powerful initially, while lower values will make it less powerful.
        reduction_amount = int(150 * math.log10(1 + bonus_score) * scaling_factor)
        SPAWN_PROJECTILE_INTERVAL -= reduction_amount

    def increase_projectile_width(self):
        global PROJECTILE_WIDTH
        PROJECTILE_WIDTH += 2 # Adjust the amount as needed to tweak difficulty


class Star:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, STAR_WIDTH, STAR_HEIGHT)

    def move(self):
        self.rect.y += STAR_VEL

    def draw(self):
        pygame.draw.rect(WIN, "yellow", self.rect)

class Projectile:
    def __init__(self, x, y, width, height, x_vel=0, y_vel=-PROJECTILE_VEL):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = x_vel
        self.y_vel = y_vel

    def move(self):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel

    def draw(self):
        pygame.draw.rect(WIN, "red", self.rect)

class Bonus:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x - BONUS_RADIUS, y - BONUS_RADIUS, BONUS_RADIUS * 2, BONUS_RADIUS * 2)

    def move(self):
        self.y += BONUS_VEL
        self.rect.y = self.y // 1  # You can // x to adjust speed. (< 1 to make them go faster)

    def draw(self):
        pygame.draw.circle(WIN, "green", (self.rect.x + BONUS_RADIUS, self.rect.y + BONUS_RADIUS), BONUS_RADIUS)
        bonus_text = BONUS_FONT.render("B", 1, "black")
        text_x = self.rect.x + BONUS_RADIUS - bonus_text.get_width() // 2
        text_y = self.rect.y + BONUS_RADIUS - bonus_text.get_height() // 2
        WIN.blit(bonus_text, (text_x, text_y))

class BossStar:
    def __init__(self, x, y):
        boss_star_hitbox_width = 350  # Define the width of the hitbox
        boss_star_hitbox_height = 200  # Define the height of the hitbox
        self.rect = pygame.Rect(x, y, boss_star_hitbox_width, boss_star_hitbox_height)
        self.health = boss_star_health
        self.vel = boss_star_vel

        
    def move(self):
        if self.rect.y < HEIGHT // 7:  # Check if the y-coordinate is less than half the screen height
            self.rect.y += self.vel / 10  # Move the object
        else:
           self.vel = 0  # Set the velocity to 0 to stop the movement

    def draw(self):
        WIN.blit(Bossstar_scaled, self.rect)

    def handle_collision(self):
        # Play the sound effect when hit
        boss_hit_sound.play()


# Initialize player
player = Player(WIDTH // 2 - PLAYER_WIDTH // 2, HEIGHT - PLAYER_HEIGHT - 10)

# Initialize lists for stars, projectiles, and bonuses
stars = []
projectiles = []
bonuses = []

# Track time for spawning projectiles and bonuses
last_projectile_time = pygame.time.get_ticks()
last_bonus_time = pygame.time.get_ticks()



# Load shoot sound effect
pygame.mixer.init()
shoot_sound = pygame.mixer.Sound('sounds/shoot.wav')
hit_sound = pygame.mixer.Sound('sounds/hit.wav')
boss_hit_sound = pygame.mixer.Sound('sounds/boss_defeat.MP3')
power_up_sound = pygame.mixer.Sound('sounds/power_up.wav')




#reduce volume shoot
shoot_sound.set_volume(0.1)  # Adjust the volume level as needed
power_up_sound.set_volume(0.7) 






def update_score():
    global score
    score += 1

def redraw_window():
    WIN.blit(BG, (0, scroll))
   # Draw the player, stars, projectiles, bonuses, and score
    player.draw()
    for star in stars:
        star.draw()
    for projectile in projectiles:
        projectile.draw()
    for bonus in bonuses:
        bonus.draw()
    score_text = FONT.render(f"Score: {score}", 1, (255, 255, 255))
    WIN.blit(score_text, (10, 10))
    bonus_score_text = FONT.render("Power: " + str(bonus_score), 1, (255, 255, 255))
    WIN.blit(bonus_score_text, (10, 50))

    # Draw the timer
    elapsed_time = pygame.time.get_ticks() - start_time
    timer_text = TIMER_FONT.render(f"Time: {elapsed_time / 1000:.1f}", 1, (255, 255, 255))
    WIN.blit(timer_text, (10, 90))

    # Draw the boss star if it is active
    if boss_star_active:
        boss_star.draw()

    pygame.display.update()




def handle_collisions():
    global score, bonus_score

    # Check collision between player and bonuses
    for bonus in bonuses:
        if player.rect.colliderect(bonus.rect):
            bonuses.remove(bonus)
            bonus_score += 1
            player.reduce_projectile_spawn_interval()
            power_up_sound.play()
            player.increase_projectile_width()
            if bonus_score >= 3:
                player.enable_side_shooting()

    # Check collision between projectiles and stars
    for projectile in projectiles:
        for star in stars:
            if projectile.rect.colliderect(star.rect):
                projectiles.remove(projectile)
                stars.remove(star)
                score += 1
                hit_sound.play()
    


    # Check collision between player and enemies
    for star in stars:
        if player.rect.colliderect(star.rect):
            return True
        
    # Check collision between player and boss star
    if boss_star_active and player.rect.colliderect(boss_star.rect):
        return True

    return False 

def show_game_over_message(score, high_score):
    game_over_text = FONT.render("You Lost", True, (255, 255, 255))
    score_text = FONT.render("Total Score: " + str(score * bonus_score), True, (255, 255, 255))
    high_score_text = FONT.render("High Score: " + str(high_score), True, (255, 255, 255))
    text_x = WIDTH // 2 - game_over_text.get_width() // 2
    text_y = HEIGHT // 2 - game_over_text.get_height() // 2
    score_x = WIDTH // 2 - score_text.get_width() // 2
    score_y = text_y + game_over_text.get_height() + 20
    high_score_x = WIDTH // 2 - high_score_text.get_width() // 2
    high_score_y = score_y + score_text.get_height() + 20
    WIN.blit(game_over_text, (text_x, text_y))
    WIN.blit(score_text, (score_x, score_y))
    WIN.blit(high_score_text, (high_score_x, high_score_y))
    pygame.display.update()



if not os.path.exists("highscore.txt"):
    with open("highscore.txt", "w") as file:
        file.write("0")


# Game loop
clock = pygame.time.Clock()
game_over = False
score = 0
high_score = 0
bonus_score = 0
spawn_projectile_time = pygame.time.get_ticks()


# Handle the boss star
boss_star_active = False
boss_star_health = 10
boss_star_vel = 40
#spawn_boss_star_time = 4000
boss_star = None

start_time = pygame.time.get_ticks()  # Move this line before the game loop
boss_star_respawn_timer = 15000  # Adapts boss spawn time ( First appearance as well)
boss_star_respawn_time = 0  # Time when the boss star was defeated

# Read the highscore file and use the value as an integer to display on screen later
try:
    with open("highscore.txt", "r") as file:
        high_score = int(file.read())
except FileNotFoundError:
    pass

while not game_over:
    
    clock.tick(60)  # Limit the frame rate to 60 FPS
    scroll += scroll_speed
    if scroll >= HEIGHT:
            scroll = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
            
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move(-PLAYER_VEL, 0)
    if keys[pygame.K_RIGHT]:
        player.move(PLAYER_VEL, 0)
    if keys[pygame.K_UP]:
        player.move(0, -PLAYER_VEL)
        """scroll += 0          You can use this to add scrolling to player upward movement"""  
    if keys[pygame.K_DOWN] and scroll < 0:
        player.move(0, PLAYER_VEL)
                               # Possibility to add a scroll factor here as well, to "reduce" scrolling speed



    current_time = pygame.time.get_ticks()
    if keys[pygame.K_SPACE]:
        if pygame.time.get_ticks() - spawn_projectile_time > SPAWN_PROJECTILE_INTERVAL:
            if bonus_score >= 3:
                for projectile in player.shoot():
                    projectiles.append(projectile)
            else:
                projectile = player.shoot()[0]
                projectiles.append(projectile)
            spawn_projectile_time = pygame.time.get_ticks()
            shoot_sound.play()  # Play the shoot sound effect


    # Spawn stars randomly
    if random.randint(0, 100) < 3: # Adjust to increase difficulty (3 is easy, 8 is hardcore)
        x = random.randint(0, WIDTH - STAR_WIDTH)
        y = -STAR_HEIGHT    # Needed so the star appears off screen a bit
        star = Star(x, y)
        stars.append(star)

    # Move and remove stars that are off the screen
    for star in stars[:]:
        star.move()
        if star.rect.y > HEIGHT:
            stars.remove(star)

    # Move projectiles and remove those that are off the screen
    for projectile in projectiles[:]:
        projectile.move()
        if projectile.rect.y < 0:
            projectiles.remove(projectile)

    # Spawn bonuses randomly
    if random.randint(0, 1000) < 5 and pygame.time.get_ticks() - last_bonus_time > SPAWN_BONUS_INTERVAL:
        """ Control the spawning of bonuses
        randomly but with certain restrictions. 
        The random number check and the time interval
        check ensure that bonuses are not spawned too frequently, 
        and there is a level of randomness involved in their appearance."""
        x = random.randint(0, WIDTH)
        y = -BONUS_RADIUS
        bonus = Bonus(x, y)
        bonuses.append(bonus)
        last_bonus_time = pygame.time.get_ticks()

    # Move and remove bonuses that are off the screen
    for bonus in bonuses[:]:
        bonus.move()
        if bonus.y > HEIGHT:
            bonuses.remove(bonus)

    # Handle collisions
    if handle_collisions():
        show_game_over_message(score, high_score)
        pygame.time.delay(4000)  # Delay for x000 seconds before quitting the game 
        break


#handle boss star
    if boss_star_respawn_timer <= 0 and not boss_star_active:
    # Spawn the next boss star
        boss_star = BossStar(WIDTH // 2 - BOSS_STAR_WIDTH // 2, -BOSS_STAR_HEIGHT)
        boss_star_active = True

    # Inside the game loop, after updating the score

    total_score = bonus_score * score
    if total_score > high_score:
        high_score = total_score
    # Save the new high score to the file
    with open("highscore.txt", "w") as file:
        file.write(str(high_score))



    if boss_star_active: 
        boss_star.move()
        boss_star.draw()
    

        # Check collision between projectiles and boss star
        for projectile in projectiles:
            if projectile.rect.colliderect(boss_star.rect):
                projectiles.remove(projectile)
                boss_star.health -= 1
                if boss_star.health <= 0:
                    boss_star_active = False
                    boss_star_respawn_time = pygame.time.get_ticks() + 5000
                    boss_star_respawn_timer = 15000
                    score += 10  
                    boss_hit_sound.play()

    if boss_star_respawn_timer > 0:
        boss_star_respawn_timer -= current_time - boss_star_respawn_time
        boss_star_respawn_time = current_time
    
    if boss_star_respawn_timer <= 0 and not boss_star_active:
    # Spawn the next boss star
        boss_star = BossStar(WIDTH // 2 - BOSS_STAR_WIDTH // 2, -BOSS_STAR_HEIGHT)
        boss_star_active = True

    redraw_window()

pygame.quit()
