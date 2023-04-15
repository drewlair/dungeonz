import pygame
import sys
import socket
import platform
import time
import json
import random



def main():
    print("INmain")
    try:
        port = int(sys.argv[1])
    except:
        print("Bad arguments! Must add one correct port!")
        sys.exit()


    print("before init")
    pygame.init()

    xBorderMax = 1000
    yBorderMax = 700
    print("bf screen")
    screen = pygame.display.set_mode((0,0)) #pygame.FULLSCREEN
    print("past screen display")

    clock = pygame.time.Clock()
    print("past pygame inits")

    stanceRightMain = pygame.image.load('guts(1).png')
    stanceLeftMain = pygame.image.load('guts(1).png')
    swingRightStart = pygame.image.load('swingRightStart.png')
    swingRightMid = pygame.image.load('midSwingRight.png')
    swingRightUp = pygame.image.load('swingRightUp.png')
    swingRightFinish = pygame.image.load('swingRightFinish.png')
    swingRightFinal = pygame.image.load('swingRightFinal.png')
    background_surf = pygame.image.load('startBackground.jpeg')
    eSwing = 0
    swing = False
    charX_pos = 100
    charY_pos = 100
    print("past images")

    gameState = {}
    gameState["playerKey"] = str(random.randint(0,10000000000))
    gameState["background"] = "background_surf"
    gameState["borders"] = (xBorderMax, yBorderMax)
    gameState["character"] = "stanceRightMain"
    gameState["characterStats"] = {"hp": 100, "gold": 0, "xp": 0, "lvl": 0, "XY": (charX_pos, charY_pos)}
    
    print("past json inits")

    backgrounds = {}
    backgrounds[gameState["background"]] = background_surf

    characterImages = {}
    characterImages["stanceRightMain"] = stanceRightMain
    characterImages["stanceLeftMain"] = stanceLeftMain
    characterImages["swingRightStart"] = swingRightStart
    characterImages["swingRightMid"] = swingRightMid
    characterImages["swingRightUp"] = swingRightUp
    characterImages["swingRightFinish"] = swingRightFinish
    characterImages["swingRightFinal"] = swingRightFinal




    # establish server connection

    clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSock.settimeout(5)
    host = platform.node()
   
        
    print(f"Successfully connected to {host} at port {str(port)}")

    msg = json.dumps(gameState)
    
    try:
        print("in try")
        print(host)
        print(port)
        host = platform.node()
        clientSock.sendto((msgLength(msg)).encode(), (host, port))
        print("past length")
        
        clientSock.sendto(msg.encode(), (host, port))

    except:
        print("Failed to send initialized state to server")
        sys.exit()


    try:
        length, client = clientSock.recvfrom(8)
        print("got length")
        length = int(length.decode())

        msg, client = clientSock.recvfrom(length)
        msg = msg.decode()

    except:
        print("Error receiving update from server 1")
        sys.exit()
    if msg == "OK":
        print("lets play!")
    else:
        sys.exit()
    
    screen.blit(backgrounds[gameState["background"]], (0,0))
    screen.blit(characterImages[gameState["character"]], (500,350))



    

    while True:


        ######################################
        #Receive user input

        update = {}
        update["playerKey"] = gameState["playerKey"]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                clientSock.close()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    #swing = True
                    #eSwing = 0
                    update["type"] = "swing"
                elif event.key == pygame.K_w:
                    #charY_pos -= 5
                    update["type"] = "moveUp"
                elif event.key == pygame.K_a:
                    #charX_pos -= 5
                    update["type"] = "moveLeft"
                
                elif event.key == pygame.K_s:
                    #charY_pos += 5
                    update["type"] = "moveDown"
                elif event.key == pygame.K_d:
                    #charX_pos += 5
                    update["type"] = "moveRight"


        ######################################


            
        ####################################
        #Send update to server

        msg = json.dumps(update)
        length = int(len(msg))
        for i in range(8 - len(str(length))):
            length = "0" + str(length)
        try:
            clientSock.sendto(length.encode(), (host, port))

            clientSock.sendto(msg.encode(), (host, port))

        except:
            print("Failed to send initialized state to server")
            sys.exit()

        ###################################


        ###################################
        #Receive new Game State from server

        try:
            length, client = clientSock.recvfrom(8)
            print("here1")
            length = int(length.decode())
            print("length is "+str(length))
            update, client = clientSock.recvfrom(length)
            print("here2")
            update = update.decode()
            print(update)
            serverUpdate = json.loads(update)


        except OSError:
            print("Error receiving update from server 2")
            continue


        ###################################  
            """
            screen.blit(background_surf,(0,0))
            if swing:
                if eSwing < 4:
                    screen.blit(swingRightStart,(charX_pos,charY_pos))
                elif eSwing < 8:
                    screen.blit(swingRightMid,(charX_pos,charY_pos))
                elif eSwing < 12:
                    screen.blit(swingRightUp,(charX_pos,charY_pos))
                elif eSwing < 16:
                    screen.blit(swingRightFinish,(charX_pos,charY_pos))
                elif eSwing < 20:
                    screen.blit(swingRightFinal,(charX_pos,charY_pos))
                else:
                    screen.blit(stanceRightMain, (charX_pos,charY_pos))
                    swing = False
                eSwing += 1
            else:
                screen.blit(stanceRightMain, (charX_pos, charY_pos))
            """

        ##############################
        #update client gamestate

        for key in serverUpdate.keys():

            if key == "character":
                if serverUpdate["character"] == "stanceRight":
                    gameState["character"] = stanceRightMain
                elif serverUpdate["character"] == "stanceLeft":
                    gameState["character"] = stanceLeftMain
                elif serverUpdate["character"] == "swingRightStart":
                    gameState["character"] = swingRightStart
                elif serverUpdate["character"] == "swingRightMid":
                    gameState["character"] = swingRightMid
                elif serverUpdate["character"] == "swingRightUp":
                    gameState["character"] = swingRightUp
                elif serverUpdate["character"] == "swingRightFinish":
                    gameState["character"] = swingRightFinish
                elif serverUpdate["character"] == "swingRightFinal":
                    gameState["character"] = swingRightFinal
                else:
                    gameState["character"] = stanceRightMain
                
            elif key == "characterStats":
                for attribute in serverUpdate[key].keys():
                    if attribute == "hp":
                        gameState["characterStats"]["hp"] = serverUpdate[key]["hp"]
                    elif attribute == "gold":
                        gameState["characterStats"]["gold"] = serverUpdate[key]["gold"]
                    elif attribute == "xp":
                        gameState["characterStats"]["xp"] = serverUpdate[key]["xp"]
                    elif attribute == "lvl":
                        gameState["characterStats"]["lvl"] = serverUpdate[key]["lvl"]
                    elif attribute == "XY":
                        gameState["characterStats"]["XY"] = serverUpdate[key]["XY"]
            else:
                print("No updates!")
            
        ###################################


        ###################################
        #Display New Game State

        #Background
        screen.blit(gameState["background"],(0,0))

        #Character Image
        screen.blit(gameState["character"],gameState["characterStats"]["XY"])

        pygame.display.update()
        clock.tick(60)




def msgLength(msg):
    
    length = str(len(msg))
    for i in range(8 - len(str(length))):
        length = "0" + length
    return length





if __name__ == "__main__":
    main()


