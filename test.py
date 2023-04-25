"""
import pygame
import sys
import random


pygame.init()
screen_width = 1000
screen_height = 700
screen = pygame.display.set_mode((screen_width,screen_height))

clock = pygame.time.Clock()

test_surface = pygame.Surface((45,45))
test_surface.fill('Red')

char_surface = pygame.image.load('guts(1).png')
s1_surf = pygame.image.load('swingRightStart.png')
s2_surf = pygame.image.load('midSwingRight.png')
s3_surf = pygame.image.load('swingRightUp.png')
s4_surf = pygame.image.load('swingRightFinish.png')
s5_surf = pygame.image.load('swingRightFinal.png')
eSwing = 0
facing_right = True
swing = False
charX_pos = 100
charY_pos = 100
char_speed = 2

background_surf = pygame.image.load('startBackground.jpeg')
# Load slime image and create 3 instances at random positions
slime_surf = pygame.image.load('slime.png')
slime_width, slime_height = slime_surf.get_size()
slimes = []
for i in range(3):
    x = random.randint(0, screen_width - slime_width)
    y = random.randint(0, screen_height - slime_height)
    slime_rect = slime_surf.get_rect(topleft=(x, y))
    slimes.append({'rect': slime_rect, 'dx': 0, 'dy': 0, 'health': 3})

# Define a timer variable to control slime movement interval
slime_timer = 0


keys = {}

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif event.type == pygame.KEYDOWN:
            keys[event.key] = True
            if event.key == pygame.K_SPACE:
                swing = True
                eSwing = 0
            elif event.key == pygame.K_a:
                facing_right = False
            elif event.key == pygame.K_d:
                facing_right = True
        elif event.type == pygame.KEYUP:
            keys[event.key] = False

    screen.blit(background_surf,(0,0))
    for slime in slimes:
        screen.blit(slime_surf, slime['rect'])
    for slime in slimes:
        if swing:
            if s5_surf.get_rect(center=(charX_pos,charY_pos)).colliderect(slime['rect']):
                slime['health'] -= 1
                if slime['health'] <= 0:
                    slimes.remove(slime)
    
       # update character position based on which keys are pressed
    dx = 0
    dy = 0
    if keys.get(pygame.K_w):
        dy -= char_speed
    if keys.get(pygame.K_s):
        dy += char_speed
    if keys.get(pygame.K_a):
        dx -= char_speed
    if keys.get(pygame.K_d):
        dx += char_speed
    charX_pos += dx
    charY_pos += dy
    
    # update slime positions
    slime_timer += 1
    if slime_timer >= 10:  # change this value to adjust slime movement interval
        for slime in slimes:
            dx = charX_pos - slime['rect'].centerx
            dy = charY_pos - slime['rect'].centery
            length = max(abs(dx), abs(dy))
            if length > 0:
                slime['dx'] = dx / length * 5
                slime['dy'] = dy / length * 5
            else:
                slime['dx'] = 0
                slime['dy'] = 0
            slime['rect'].move_ip(slime['dx'], slime['dy'])
        slime_timer = 0
                
    if swing:
        if facing_right:
            swing_pos = (charX_pos, charY_pos)
            swing_surf = s1_surf
        else:
            # adjust x-coordinate value for left-facing character
            swing_pos = (charX_pos - s5_surf.get_width(), charY_pos)
            swing_surf = pygame.transform.flip(s5_surf, True, False)
        if eSwing < 4:
            screen.blit(swing_surf, swing_pos)
        elif eSwing < 8:
            if facing_right:
                screen.blit(s2_surf, (charX_pos, charY_pos))
            else:
                screen.blit(s2_surf, swing_pos)
        elif eSwing < 12:
            if facing_right:
                screen.blit(s3_surf, (charX_pos, charY_pos))
            else:
                screen.blit(s3_surf, swing_pos)
        elif eSwing < 16:
            if facing_right:
                screen.blit(s4_surf, (charX_pos, charY_pos))
            else:
                screen.blit(s4_surf, swing_pos)
        elif eSwing < 20:
            if facing_right:
                screen.blit(s5_surf, (charX_pos, charY_pos))
            else:
                screen.blit(s5_surf, swing_pos)
        else:
            if facing_right:
                screen.blit(char_surface, (charX_pos,charY_pos))
            else:
                screen.blit(pygame.transform.flip(char_surface, True, False), (charX_pos - char_surface.get_width(), charY_pos))
            swing = False
        eSwing += 1
    else:
        if facing_right:
            screen.blit(char_surface, (charX_pos, charY_pos))
        else:
            screen.blit(pygame.transform.flip(char_surface, True, False), (charX_pos - char_surface.get_width(), charY_pos))


    pygame.display.update()
    clock.tick(60)




"""
import pygame
import pygame.font
import sys
import random

pygame.init()
pygame.font.init()
pygame.mixer.init()

# Basic Parameters
font = pygame.font.Font(None, 36)
upgrade_font = pygame.font.Font(None, 24)
game_over_font = pygame.font.Font(None, 72) 
win_font = pygame.font.Font(None, 72)
level_up_sound = pygame.mixer.Sound('level_up.mp3')
game_over_sound = pygame.mixer.Sound('game_over.mp3')
victory_sound = pygame.mixer.Sound('victory.mp3')

screen_width = 1000
screen_height = 700
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
test_surface = pygame.Surface((45, 45))
test_surface.fill('Red')

# Load Sprites 
char_surface = pygame.image.load('guts(1).png')
char_hurt_surface = pygame.image.load('guts_hurt.png')
s1_surf = pygame.image.load('swingRightStart.png')
s2_surf = pygame.image.load('midSwingRight.png')
s3_surf = pygame.image.load('swingRightUp.png')
s4_surf = pygame.image.load('swingRightFinish.png')
s5_surf = pygame.image.load('swingRightFinal.png')
background_surf = pygame.image.load('startBackground.jpeg')

# Character State
charX_pos = 100
charY_pos = 100
char_speed = 2
char_health = 1000
max_health = 1000
char_exp = 0
char_invuln = False
char_invuln_timer = 0
eSwing = 0
facing_right = True
swing = False
swing_cooldown_timer = 0
attack_speed = 50

# Slime Variables
slime_surf = pygame.image.load('slime.jpg')
slime_width, slime_height = slime_surf.get_size()
slimes = []
wave = 1
wave_slimes = {1: 3, 2: 5, 3: 8, 4: 12, 5: 15, 6: 15, 7: 15, 8 : 20}

# Bat Variables
bat_surf = pygame.image.load('bat.png')
bat_width, bat_height = bat_surf.get_size()
bats = []
wave_bats = {5: 2, 6: 3, 7: 5, 8: 5}


# Define a timer variable to control mob movement interval
slime_timer = 0
bat_timer = 0

# Adjust hitbox size for accuracy
def create_custom_hitbox(rect, x_offset, y_offset):
    return pygame.Rect(
        rect.x + x_offset, rect.y + y_offset,
        rect.width - 2 * x_offset, rect.height - 2 * y_offset
    )
    
# Spawn mobs in depending on wave number and type
def spawn_mobs(wave, type):
    if type == "slime":
        num_mobs = wave_slimes.get(wave, 0)
        mob_surf = slime_surf
        mob_width = slime_width
        mob_height = slime_height
        mob_health = 1
        mob_exp = 3
    elif type == "bat":
        num_mobs = wave_bats.get(wave, 0)
        mob_surf = bat_surf
        mob_width = bat_width
        mob_height = bat_height
        mob_health = 2
        mob_exp = 5
    else:
        # Invalid enemy type
        return []

    mobs = []
    for _ in range(num_mobs):
        x = random.randint(0, screen_width - mob_width)
        y = random.randint(0, screen_height - mob_height)
        mob_rect = mob_surf.get_rect(topleft=(x, y))
        custom_hitbox = create_custom_hitbox(mob_rect, 5, 5)
        mobs.append({'rect': mob_rect, 'hitbox': custom_hitbox, 'dx': 0, 'dy': 0, 'health': mob_health, 'exp' : mob_exp})
    
    return mobs

# Wave 1
slimes = spawn_mobs(wave, "slime")
keys = {}

char_rect = char_surface.get_rect(topleft=(charX_pos, charY_pos))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif event.type == pygame.KEYDOWN:
            keys[event.key] = True
            if event.key == pygame.K_SPACE and swing_cooldown_timer == 0:
                swing = True
                eSwing = 0
                swing_cooldown_timer = attack_speed
            elif event.key == pygame.K_a:
                facing_right = False
            elif event.key == pygame.K_d:
                facing_right = True
        elif event.type == pygame.KEYUP:
            keys[event.key] = False

    screen.blit(background_surf,(0,0))
    
    # Display Text
    
    # health
    health_text = f"Health: {char_health}"
    health_surf = font.render(health_text, True, (255, 255, 255))
    screen.blit(health_surf, (10, 10))
    
    # exp
    exp_text = f"Exp: {char_exp}"
    exp_surf = font.render(exp_text, True, (255, 255, 255))
    screen.blit(exp_surf, (250, 10))
   
    # Blit mobs 
    mobs = slimes + bats
    for mob in mobs:
        if mob in slimes:
            mob_surf = slime_surf
        else:
            mob_surf = bat_surf
        screen.blit(mob_surf, mob['hitbox'])
    
    mobs = slimes + bats
    for mob in mobs:
        if swing and any(create_custom_hitbox(s_surf.get_rect(center=(charX_pos, charY_pos)), -5, -5).colliderect(mob['hitbox']) for s_surf in [s1_surf, s2_surf, s3_surf, s4_surf, s5_surf]):
            mob['health'] -= 1
            if mob['health'] <= 0:
                if mob in slimes:
                    slimes.remove(mob)
                else:
                    bats.remove(mob)
            char_exp += mob['exp']
                
            if char_exp >= 100:
                level_up_sound.play()
                
                # upgrade_choice = input("You have gained 100 experience points! Enter 1 to restore some health, 2 to increase speed, or 3 to upgrade weapon:")
                upgrade_text = upgrade_font.render("You have gained 100 experience points! Enter 1 to restore health, 2 to increase speed, or 3 to increase attack speed", True, (255, 255, 255))
                upgrade_rect = upgrade_text.get_rect(center=(screen_width // 2, screen_height // 2))
                
                pygame.event.clear()
                
                screen.blit(upgrade_text, upgrade_rect)
                pygame.display.update()
                # handle the upgrade choice

                flag = True
                while flag:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_1:
                                # restore up to half of the health difference between current and max health
                                health_diff = max_health - char_health
                                health_restore = min(health_diff // 2, max_health - char_health)
                                char_health += health_restore
                                flag = False
                            elif event.key == pygame.K_2:
                                char_speed += 1
                                flag = False
                            elif event.key == pygame.K_3:
                                if attack_speed >= 10:
                                    attack_speed -= 8
                                flag = False
                
                keys = {pygame.K_w: False, pygame.K_s: False, pygame.K_a: False, pygame.K_d: False}

                                
                pygame.event.clear()
            
                # reset experience counter
                char_exp -= 100
 
       # update character position based on which keys are pressed
    dx = 0
    dy = 0
    if keys.get(pygame.K_w):
        dy -= char_speed
    if keys.get(pygame.K_s):
        dy += char_speed
    if keys.get(pygame.K_a):
        dx -= char_speed
    if keys.get(pygame.K_d):
        dx += char_speed
    charX_pos += dx
    charY_pos += dy
    char_rect.topleft = (charX_pos, charY_pos)

    # update slime positions
    slime_timer += 1
    if slime_timer >= 10:  # change this value to adjust slime movement interval
        for slime in slimes:
            dx = charX_pos - slime['hitbox'].centerx
            dy = charY_pos - slime['hitbox'].centery
            length = max(abs(dx), abs(dy))
            if length > 0:
                slime['dx'] = dx / length * 5
                slime['dy'] = dy / length * 5
            else:
                slime['dx'] = 0
                slime['dy'] = 0
            slime['hitbox'].move_ip(slime['dx'], slime['dy'])
            slime['rect'].move_ip(slime['dx'], slime['dy']) 
        slime_timer = 0
        
    # update bat positions
    bat_timer += 1
    if bat_timer >= 5:  # change this value to adjust bat movement interval
        for bat in bats:
            dx = charX_pos - bat['hitbox'].centerx
            dy = charY_pos - bat['hitbox'].centery
            length = max(abs(dx), abs(dy))
            if length > 0:
                bat['dx'] = dx / length * 5
                bat['dy'] = dy / length * 5
            else:
                bat['dx'] = 0
                bat['dy'] = 0
            bat['hitbox'].move_ip(bat['dx'], bat['dy'])
            bat['rect'].move_ip(bat['dx'], bat['dy']) 
        bat_timer = 0
    
    # char collision check
    if not char_invuln and not swing:
        char_rect.topleft = (charX_pos, charY_pos)

        # detect collisions between player and mobs
        for mob in slimes + bats:
            if char_rect.colliderect(mob['hitbox']): 
                char_health -= 1
                char_invuln = True
                char_invuln_timer = 0
                
                
                # game over
                if char_health <= 0:
                    # Render the "GAME OVER!" text
                    game_over_text = game_over_font.render("GAME OVER!", True, (255, 0, 0))  # You can change the color (255, 0, 0) to your desired value
                    game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2))

                    # Display the "GAME OVER!" text
                    screen.blit(game_over_text, game_over_rect)
                    pygame.display.update()
                    game_over_sound.play()

                    # Wait for 5 seconds
                    pygame.time.delay(5000)

                    # Quit the game
                    pygame.quit()
                    sys.exit()
                    
    if swing_cooldown_timer > 0:
        swing_cooldown_timer -= 1
    
    if char_invuln:
        char_invuln_timer += 1
        # invuln for this long
        if char_invuln_timer >= 140:
            char_invuln = False
    
    
    if not slimes and not bats:
        wave += 1
        slimes = spawn_mobs(wave, "slime") 
        bats = spawn_mobs(wave, "bat")
    
        
    if swing:
        if facing_right:
            swing_pos = (charX_pos, charY_pos)
            swing_surf = s1_surf
        else:
            # adjust x-coordinate value for left-facing character
            swing_pos = (charX_pos - s5_surf.get_width(), charY_pos)
            swing_surf = pygame.transform.flip(s5_surf, True, False)
        if eSwing < 4:
            screen.blit(swing_surf, swing_pos)
        elif eSwing < 8:
            if facing_right:
                screen.blit(s2_surf, (charX_pos, charY_pos))
            else:
                screen.blit(s2_surf, swing_pos)
        elif eSwing < 12:
            if facing_right:
                screen.blit(s3_surf, (charX_pos, charY_pos))
            else:
                screen.blit(s3_surf, swing_pos)
        elif eSwing < 16:
            if facing_right:
                screen.blit(s4_surf, (charX_pos, charY_pos))
            else:
                screen.blit(s4_surf, swing_pos)
        elif eSwing < 20:
            if facing_right:
                screen.blit(s5_surf, (charX_pos, charY_pos))
            else:
                screen.blit(s5_surf, swing_pos)
        else:
            if facing_right:
                screen.blit(char_surface, (charX_pos,charY_pos))
            else:
                screen.blit(pygame.transform.flip(char_surface, True, False), (charX_pos - char_surface.get_width(), charY_pos))
            swing = False
        eSwing += 1
    else:
        if char_invuln:
            if facing_right:
                screen.blit(char_hurt_surface, (charX_pos, charY_pos))
            else:
                screen.blit(pygame.transform.flip(char_hurt_surface, True, False), (charX_pos - char_hurt_surface.get_width(), charY_pos))
        else:       
            if facing_right:
                screen.blit(char_surface, (charX_pos, charY_pos))
            else:
                screen.blit(pygame.transform.flip(char_surface, True, False), (charX_pos - char_surface.get_width(), charY_pos))
                
    # you win!
    if wave >= 9:
        you_win_text = win_font.render("YOU WIN!", True, (0, 255, 0)) 
        you_win_rect = you_win_text.get_rect(center=(screen_width // 2, screen_height // 2))

        # Display the "YOU WIN!"" text
        screen.blit(you_win_text, you_win_rect)
        pygame.display.update()
        victory_sound.play()
        # Wait for 10 seconds
        pygame.time.delay(10000)

        # Quit the game
        pygame.quit()
        sys.exit()
        
    pygame.display.update()
    clock.tick(60)
