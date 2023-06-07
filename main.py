import pygame
import os     # necessary for interaction with the OS. Get information and control processes to a limit
import time   # used to create clock object that helps keep track of time
import random    # helps to generate float numbers between 0.0 and 1.0
pygame.font.init()    # intializes the font


# Game Window
WIDTH, HEIGHT = 750, 750
WIND = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Hitters")
#pygame.display.set_icon(pygame.image.load("myicon.png"))

#load images
B_CORONA = pygame.image.load(os.path.join("resources", "browncorona.png"))
R_CORONA = pygame.image.load(os.path.join("resources", "redcorona.png"))
RED_DEADLY = pygame.image.load(os.path.join("resources", "reddeadly.png"))
GREEN_DEADLY = pygame.image.load(os.path.join("resources", "greendeadly.png"))

# Players
BLACK_SHOOTER = pygame.image.load(os.path.join("resources", "black_shooter.png"))
RED_SHOOTER = pygame.image.load(os.path.join("resources", "red_shooter.png"))

# Lasers
BLUE_LASER = pygame.image.load(os.path.join("resources", "bluelaser.png"))
GREEN_LASER = pygame.image.load(os.path.join("resources", "greenlaser.png"))
BROWN_LASER = pygame.image.load(os.path.join("resources", "brownlaser.png"))
RED_LASER = pygame.image.load(os.path.join("resources", "redlaser.png"))

# Bullets
RED_BULLET = pygame.image.load(os.path.join("resources", "redbullet.png"))
BLACK_BULLET =pygame.image.load(os.path.join("resources", "blackbullet.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("resources", "background.jpg")), (WIDTH, HEIGHT))

# Create parent class for movement of enemy and player objects

class Laser:   ## lasers must be independent not following player
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y -= vel

    def off_screen(self, height):  # tells if lasers are off the screen
        return not self.y <= height and self.y >= 0

    def collision(self, obj):   # checks if laser collides with object
        return collide(obj, self)    # returns the value of the collide function, "self is passed because it gives access to this specific instance"


class Objects:
    CALMDOWN = 30
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.objects_image = None  # allows to draw objects
        self.laser_image = None    # allows drawing of laser
        self.lasers = []
        self.less_down_counter = 0  # allows a wait period between shooting of lasers

    def draws(self, window):    # window tells us where to draw the objects
        #pygame.draw.rect(window, (255, 0, 0), (self.x, self.y, 50, 50))
        window.blit(self.objects_image, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj): # obj is there because when the laser moves you want to check if theres collision with any object (player)
        self.lessdown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)


    def lessdown(self):    # serves as counter regulator
        if self.less_down_counter >= self.CALMDOWN:
            self.less_down_counter = 0
        elif self.less_down_counter > 0:
            self.less_down_counter += 1

    def shoot(self):   #checks if laser counter is = 0, if yes, it creates another and append it to Laser list, setting the counter back to 1
        if self.less_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_image)
            self.lasers.append(laser)
            self.less_down_counter = 1


    def get_width(self):          # methods to get width and height of objects
        return self.objects_image.get_width()

    def get_height(self):
        return self.objects_image.get_height()

class Player(Objects):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.objects_image = RED_SHOOTER
        self.laser_image = RED_BULLET
        self.mask = pygame.mask.from_surface(self.objects_image)   # mask helps to know where pixels are and where they are'nt in this image, so you can know if you actually hit a pixel during collision
        self.maximum_health = health

    def move_lasers(self, vel, objs): # obj is there because when the laser moves you want to check if theres collision with any object (enemy)
        self.lessdown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draws(self, window):
        super().draws(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.objects_image.get_height() + 10, self.objects_image.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0),
                         (self.x, self.y + self.objects_image.get_height() + 10, self.objects_image.get_width() * (self.health / self.maximum_health), 10))

class Enemy(Objects):
    TYPES_ENEMY = {
        "red": (RED_DEADLY, RED_LASER),
        "green": (GREEN_DEADLY, GREEN_LASER),
        "brown": (B_CORONA, BROWN_LASER),
        "blue": (R_CORONA, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.objects_image, self.laser_image = self.TYPES_ENEMY[color]
        self.mask = pygame.mask.from_surface(self.objects_image)

       #  method allows movement of the enemies
    def move(self, vel):
        self.y += vel

    def shoot(self):   #checks if laser counter is = 0, if yes, it creates another and append it to Laser list, setting the counter back to 1
        if self.less_down_counter == 0:
            laser = Laser(self.x - 40, self.y, self.laser_image)
            self.lasers.append(laser)
            self.less_down_counter = 1

def collide(obj1, obj2):      # checks for collission of pixels alone
    offset_x = obj2.x - obj1.x       # checks the distance between top left corner of both objects
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None    # checks if the mask of object1 overlaps with that of object 2 with the offset of offset x, offset y

# Main loop (handle all event)
def main():
    run = True
    FPS = 60
    level = 0
    laser_velocity = 4
    lives = 7
    game_font = pygame.font.SysFont("budmo jiggler", 35)
    lost_font = pygame.font.SysFont("budmo jiggler", 40)
    enemies = []
    wave_length = 5
    enemy_velocity = 1
    lost = False
    lost_count = 0

    player_velocity = 5

    player = Player(300, 450)



    clock = pygame.time.Clock()

    def draw_window():
        WIND.blit(BG, (0, 0))
        lives_label = game_font.render(f"Lives: {lives}", True, (0, 255, 0))
        levels_label = game_font.render(f"Levels: {level}", True, (0, 255, 0))

        WIND.blit(lives_label, (20, 20))
        WIND.blit(levels_label, (WIDTH - levels_label.get_width() -10, 10))

        for enemy in enemies:
            enemy.draws(WIND)

        player.draws(WIND)

        if lost:
            lost_label = lost_font.render("You Lost!!! Try again.", True, (255, 255, 255))
            WIND.blit(lost_label,(WIDTH/2 - lost_label.get_width()/2, 350))


        pygame.display.update()   # refreshes the display

    while run:
        clock.tick(FPS)
        draw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 5:  # makes lost message stay for 5 seconds
                run = False
            else:
                continue


        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "green", "brown", "blue"]))    # gives a range within which the enemies will appear
                enemies.append(enemy)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()    # returns a dictionary of all keys and tells if any of them is pressed at a time
        if keys[pygame.K_a] and player.x - player_velocity > 0:  # left
            player.x -= player_velocity
        if keys[pygame.K_d] and player.x + player_velocity + player.get_width() < WIDTH:   # right
            player.x += player_velocity
        if keys[pygame.K_w] and player.y - player_velocity > 0:   # up
            player.y -= player_velocity
        if keys[pygame.K_s] and player.y + player_velocity + player.get_height() + 20 < HEIGHT:   # down
            player.y += player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:      # '[:]' creates a shallow copy of the list so that modification won't affect the oringinal list
            enemy.move(enemy_velocity)
            enemy.move_lasers(-laser_velocity, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)


        player.move_lasers(laser_velocity, enemies)



def main_menu(): # if any of the mouse button is pressed function will activate the main loop
    title_font = pygame.font.SysFont("comicsans", 60)
    run = True
    while run:
        WIND.blit(BG, (0,0))
        title_label = title_font.render("Press Mouse To Begin...", True, (255, 255, 255))
        WIND.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()

main_menu()
