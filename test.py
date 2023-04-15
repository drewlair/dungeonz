import pygame
import sys


pygame.init()

screen = pygame.display.set_mode((1000,700))

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
swing = False
charX_pos = 100
charY_pos = 100













background_surf = pygame.image.load('startBackground.jpeg')

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                swing = True
                eSwing = 0
            elif event.key == pygame.K_w:
                charY_pos -= 30
            elif event.key == pygame.K_a:
                charX_pos -= 30
            elif event.key == pygame.K_s:
                charY_pos += 30
            elif event.key == pygame.K_d:
                charX_pos += 30

                  

    screen.blit(background_surf,(0,0))
    if swing:
        if eSwing < 4:
            screen.blit(s1_surf,(charX_pos,charY_pos))
        elif eSwing < 8:
            screen.blit(s2_surf,(charX_pos,charY_pos))
        elif eSwing < 12:
            screen.blit(s3_surf,(charX_pos,charY_pos))
        elif eSwing < 16:
            screen.blit(s4_surf,(charX_pos,charY_pos))
        elif eSwing < 20:
            screen.blit(s5_surf,(charX_pos,charY_pos))
        else:
            screen.blit(char_surface, (charX_pos,charY_pos))
            swing = False
        eSwing += 1
    else:
        screen.blit(char_surface, (charX_pos, charY_pos))

    pygame.display.update()
    clock.tick(60)






