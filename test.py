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




