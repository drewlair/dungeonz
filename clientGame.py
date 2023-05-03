import pygame
import sys
import socket
import time
import json
import random
from collections import defaultdict

def display_hp_exp(screen, hp, exp, lvl):
    font = pygame.font.Font(None, 32)
    hp_text = font.render(f"HP: {hp}", True, (255, 255, 255))
    exp_text = font.render(f"EXP: {exp}", True, (255, 255, 255))
    level_text = font.render(f"LEVEL: {lvl}", True,(255,255,255))
    
    screen.blit(hp_text, (10, 10))
    screen.blit(exp_text, (250, 10))
    screen.blit(level_text, (500, 10))

def display_win(screen):
    font = pygame.font.Font(None, 100)
    win_text = font.render(f"YOU WIN", True, (255,255,255))
    screen.blit(win_text, (375,350))

def you_died(screen):
    font = pygame.font.Font(None, 100)
    died_text = font.render(f"YOU DIED", True, (255,255,255))
    screen.blit(died_text, (375,350))


def main():
    
    try:
        port = int(sys.argv[2])
    except:
        print("Bad arguments! Must add one correct port!")
        sys.exit()
    try:
        host = sys.argv[1]
    except:
        print("Need to enter hostname")
        sys.exit()


    
    pygame.init()

    xBorderMax = 1000
    yBorderMax = 700
    
    screen = pygame.display.set_mode((xBorderMax,yBorderMax)) #pygame.FULLSCREEN
    

    clock = pygame.time.Clock()
    

    stanceRightMain = pygame.image.load('guts(1).png')
    stanceLeftMain = pygame.image.load('guts(1).png')
    swingRightStart = pygame.image.load('swingRightStart.png')
    swingRightMid = pygame.image.load('midSwingRight.png')
    swingRightUp = pygame.image.load('swingRightUp.png')
    swingRightFinish = pygame.image.load('swingRightFinish.png')
    swingRightFinal = pygame.image.load('swingRightFinal.png')
    hurtRight = pygame.image.load('guts_hurt.png')
    background_surf = pygame.image.load('startBackground.jpeg')
    slime_surf = pygame.image.load('slime.png')
    slime_width, slime_height = slime_surf.get_size()
    bat_surf = pygame.image.load('bat.png')
    bat_width, bat_height = slime_surf.get_size()
    
    
    
    charX_pos = 100
    charY_pos = 100
    
    gameState = defaultdict(dict)
    
    # init default gameState

    characterImages = {}
    characterImages["stanceRightMain"] = stanceRightMain
    characterImages["stanceLeftMain"] = stanceLeftMain
    characterImages["swingRightStart"] = swingRightStart
    characterImages["swingRightMid"] = swingRightMid
    characterImages["swingRightUp"] = swingRightUp
    characterImages["swingRightFinish"] = swingRightFinish
    characterImages["swingRightFinal"] = swingRightFinal
    characterImages["hurtRight"] = hurtRight

    #Monster stuff
    monsterImages = {}
    monsterImages["slime"] = slime_surf
    operations = 0
    

    #Music
    muzic = pygame.mixer.Sound('mainMusic.mp3')

    slimes = []

    # init default gameState
    
    # each player gets own key 
    gameState["playerKey"] = str(random.randint(0,100000000000000))
    gameState["background"] = "background_surf"
    gameState["borders"] = (xBorderMax, yBorderMax)
    gameState["character"] = "stanceRightMain"
    gameState["characterStats"] = {"hp": 100, "gold": 0, "xp": 0, "lvl": 1, "XY": (charX_pos, charY_pos)}
    gameState["status"] = "INIT"
    gameState["round"] = 0
    gameState["monsters"] = {}
    gameState["isSwinging"] = False
    gameState["isHurt"] = False
    gameState["isWin"] = False
    gameState["isDied"] = False

    


    # establish server connection
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSock.settimeout(120)
    breakMainWhile = False
    while True:
        
        if not breakMainWhile:
            

            try:
                clientSock.connect((host, port))
            except Exception as e:
                print("Error connecting to server")
                sys.exit()
                continue

            print(f"Successfully connected to {host} at port {str(port)}")

        breakMainWhile = False
        msg = defaultdict(dict)
        msg["dimensions"]["slime"] = (slime_width, slime_height)
        msg["playerKey"] = gameState["playerKey"]
        msg = json.dumps(msg)
        try:
            
            #print(f"about to send {msg}")
            print(f"with length {msgLength(msg)}")
            length = msgLength(msg)
            clientSock.sendall(length.encode("utf-8"))
            
            clientSock.sendall(msg.encode("utf-8"))
            

        except:
            print("Failed to send initialized state to server")
            continue
        
        try:
            length = clientSock.recv(8)
            
            length = int(length.decode())

            msg = clientSock.recv(length)
            
            msg = msg.decode()

        except Exception as e:
            print("Error receiving INIT update from server")
            continue

            
        
        msg = json.loads(msg)

        threadSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        threadSock.settimeout(5)
        host = msg["host"]
        port = msg["port"]
        try:
            print(f"host is {host}, {port}")
            threadSock.connect((msg["host"], int(msg["port"])))
        except:
            print("Error conncting to server Thread")
            continue
        msg = "INIT"
        length = msgLength(msg)
        try:
            threadSock.sendall(length.encode("utf-8"))
            threadSock.sendall(msg.encode("utf-8"))
        except:
            print("Error sending init to thread")
            continue
        
        try:
            length = threadSock.recv(8)
            length = int(length.decode())
            msg = threadSock.recv(length)
        except:
            print("Error receiving start msg from thread server")
            continue
        
        msg = msg.decode()
        if msg == "START":
            print("lets play!")
        else:
            print("msg not start!")
            continue
        
        muzic.play()
        failStreak = 0
        
        startTime = time.time_ns()
        friends = []
        while True:
            

            ######################################
            #Receive user input
            if gameState["isDied"]:
                time.sleep(3)
                TOstreak = 0
                while TOstreak < 30:
                    try:
                        msg = {}
                        msg["status"] = "CLIENTEXIT"
                        msg["playerKey"] = gameState["playerKey"]
                        msg = json.dumps(msg)
                        length = msgLength(msg)
                        clientSock.sendall(length.encode("utf-8"))
                        clientSock.sendall(msg.encode("utf-8"))
                        
                        break
                    except:
                        print("Error sending deadthread msg to server")
                        TOstreak += 1
                print("closing")
                clientSock.close()
                pygame.quit()
                sys.exit()
            
            if failStreak > 2:
                failStreak = 0
                while True:
                    try:
                        msg = {}
                        msg["status"] = "DEADCONN"
                        msg["playerKey"] = gameState["playerKey"]
                        msg = json.dumps(msg)
                        length = msgLength(msg)
                        clientSock.sendall(length.encode("utf-8"))
                        clientSock.sendall(msg.encode("utf-8"))
                        
                        
                        
                    except:
                        print("Error sending deadthread msg to server")
                        break

                    
                    
                    
                    try:
                        length = clientSock.recv(8)
                        
                        length = int(length.decode())

                        msg = clientSock.recv(length)
                        
                        msg = msg.decode()

                    except Exception as e:
                        print("Error receiving INIT update from server")
                        continue

                        
                    
                    if msg == "GOOD":
                        try:
                            length = clientSock.recv(8)
                        
                            length = int(length.decode())

                            msg = clientSock.recv(length)
                        
                            msg = msg.decode()

                        except Exception as e:
                            print("Error receiving INIT update from server")
                            continue
                    msg = json.loads(msg)

                    threadSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    threadSock.settimeout(5)
                    host = msg["host"]
                    port = msg["port"]
                    try:
                        print(f"host is {host}, {port}")
                        threadSock.connect((msg["host"], int(msg["port"])))
                    except:
                        print("Error conncting to server Thread")
                        continue
                    msg = "INIT"
                    length = msgLength(msg)
                    try:
                        threadSock.sendall(length.encode("utf-8"))
                        threadSock.sendall(msg.encode("utf-8"))
                    except:
                        print("Error sending init to thread")
                        continue
                    
                    try:
                        length = threadSock.recv(8)
                        length = int(length.decode())
                        msg = threadSock.recv(length)
                    except:
                        print("Error receiving start msg from thread server")
                        continue
                    
                    msg = msg.decode()
                    if msg == "START":
                        print("lets play!")
                    else:
                        print("Received bad START Message")
                        continue
                    break
                    


            update = {}
            update["playerKey"] = gameState["playerKey"]
            update["status"] = "INPUT"
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    endtime = time.time_ns()
                    throughput = (operations / ((endtime - startTime)/10**9))
                    print(f"system throughput was {throughput} ops/ sec")
                    latency = ((endtime - startTime) / operations) / 10**9
                    print(f"system latency was {latency} sec / ops")


                    msg = {"status": "CLIENTEXIT", "playerKey": gameState["playerKey"]}
                    msg = json.dumps(msg)
                    length = msgLength(msg)
                    TOstreak = 0
                    while TOstreak < 30:
                        try:
                            clientSock.sendall(length.encode("utf-8"))


                            clientSock.sendall(msg.encode("utf-8"))
                            break
                        except:
                            print("error sending timeout msg to server")
                            TOstreak += 1
                            time.sleep(1)

                    print("closing")
                    time.sleep(3)
                    clientSock.close()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        
                        update["type"] = "swing"
                    elif event.key == pygame.K_w:
                        
                        update["type"] = "moveUp"
                    elif event.key == pygame.K_a:
                        
                        update["type"] = "moveLeft"
                    
                    elif event.key == pygame.K_s:
                        
                        update["type"] = "moveDown"
                    elif event.key == pygame.K_d:
                        
                        update["type"] = "moveRight"
                elif event.type == pygame.KEYUP:
                    
                    if event.key == pygame.K_w:
                        
                        update["type"] = "stopUp"
                    elif event.key == pygame.K_a:
                        
                        update["type"] = "stopLeft"
                    
                    elif event.key == pygame.K_s:
                        
                        update["type"] = "stopDown"
                    elif event.key == pygame.K_d:
                        
                        update["type"] = "stopRight"
                    
                


            ####################################
            #Get collisions
         
            char_rect = characterImages[gameState["character"]].get_rect(topleft=gameState["characterStats"]["XY"])
            
            enemies = None
            monI = []
            for monster in gameState["monsters"]:
                if monster == "slimes":
                    for slimeI, slime in enumerate(gameState["monsters"]["slimes"]):
                        monst_rect = slime_surf.get_rect(topleft=(slime[0], slime[1]))
                        if monst_rect.colliderect(char_rect):
                            
                            if not gameState["isHurt"] and not gameState["isSwinging"]:
                                enemies = "slimes"
                                
                            elif gameState["isSwinging"]:
                                monI.append(("slimes", slimeI))

                            if "collisions" in update.keys():
                                
                                update["collisions"].append(("slimes", slimeI))
                            else:
                                
                                update["collisions"] = [("slimes", slimeI)]

                                
                elif monster == "bats":
                    for batI, bat in enumerate(gameState["monsters"]["bats"]):
                        monst_rect = bat_surf.get_rect(topleft=(bat[0], bat[1]))
                        if monst_rect.colliderect(char_rect):
                            

                            if not gameState["isSwinging"] and not gameState["isHurt"]:
                                enemies = "bats"
                            
                            elif gameState["isSwinging"]:
                                monI.append(("bats", batI))
                                

                            if "collisions" in update.keys():
                                update["collisions"].append(("bats", batI))
                            else:
                                update["collisions"] = [("bats", batI)]
            
            if not enemies and len(monI) > 0:
                update["attack"] = monI
            elif enemies == "slimes" or enemies == "bats":
                
                update["attack"] = enemies
            

            
            





            ####################################


                
            ####################################
            #Send update to server
            
            if len(update.keys()) == 2:
                update["status"] = "CHECK"
                update["clock"] = time.time_ns()
                msg = json.dumps(update)
                length = msgLength(msg)
                try:
                   
                    threadSock.sendall(length.encode())

                    threadSock.sendall(msg.encode())

                except:
                    print("Failed to send CHECK to state to server")
                    failStreak += 1
                    continue
                    

            else:
                msg = json.dumps(update)
                length = msgLength(msg)
                try:
                    threadSock.sendall(length.encode())

                    threadSock.sendall(msg.encode())

                except:
                    print("Failed to send updated state to server")
                    failStreak += 1
                    continue

                

            ###################################


            ###################################
            #Receive new Game State from server

            try:
                length = threadSock.recv(8)

                if length == '':
                    print("Error receiving update from server thread")
                    failStreak += 1
                    continue
               
                length = int(length.decode())
               
                update = threadSock.recv(length)
               
                update = update.decode()
             
                serverUpdate = json.loads(update)

                
            except OSError:
                print("Error receiving update from server thread")
                failStreak += 1
                continue

            failStreak = 0
            ###################################  
        

            ##############################
            #update client gamestate

            for key in serverUpdate.keys():

                if key == "character":
                    gameState["character"] = serverUpdate["character"]
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

                elif key == "monsters":
                    for monster in serverUpdate[key].keys():
                        if monster == "slimes":
                            gameState["monsters"]["slimes"] = serverUpdate["monsters"]["slimes"]
                        elif monster == "bats":
                            gameState["monsters"]["bats"] = serverUpdate["monsters"]["bats"]

                elif key == "isSwinging":
                    gameState["isSwinging"] = serverUpdate["isSwinging"]

                elif key == "isHurt":
                    gameState["isHurt"] = serverUpdate["isHurt"]
                
                elif key == "isWin":
                    gameState["isWin"] = serverUpdate["isWin"]
                
                elif key == "isDied":
                    gameState["isDied"] = serverUpdate["isDied"]

                elif key == "newClient":
                    
                    friends.append(serverUpdate["newClient"])
                    gameState[serverUpdate["newClient"]] = newPlayerInit()
                    

                
                
            ###################################


            ###################################
            #Display New Game State

            #Background
            if gameState["background"] == "background_surf":
                
                screen.blit(background_surf,(0,0))

            #Character Image
            if not gameState["isDied"]:
                screen.blit(characterImages[gameState["character"]],gameState["characterStats"]["XY"])
            
            for key in friends:
                key = str(key)
                if key not in serverUpdate:
                    friends.remove(key)
                    continue
                
                
                screen.blit(characterImages[serverUpdate[key][0]], serverUpdate[key][1])

            #Monsters

            for monster in gameState["monsters"].keys():
                if monster == "slimes":
                    for slime in gameState["monsters"]["slimes"]:
                        screen.blit(slime_surf, (slime[0], slime[1]))
                elif monster == "bats":
                    for bat in gameState["monsters"]["bats"]:
                        screen.blit(bat_surf, (bat[0],bat[1]))

            operations += 1

            display_hp_exp(screen, gameState["characterStats"]["hp"], gameState["characterStats"]["xp"], gameState["characterStats"]["lvl"])

            if gameState["isWin"]:
                display_win(screen)

            elif gameState["isDied"]:
                you_died(screen)

            pygame.display.update()
            clock.tick(60)




def msgLength(msg):
    
    length = str(len(msg))
    for i in range(8 - len(str(length))):
        length = "0" + length
    return length

def newPlayerInit():
    newRes = {}
   
    newRes["background"] = "background_surf"
    newRes["characterStats"] = {"hp": 100, "gold": 0, "xp": 0, "lvl": 1, "XY": (100, 100)}
    newRes["character"] = "stanceRightMain"
    newRes["isSwinging"] = False
    newRes["isHurt"] = False


    return newRes

if __name__ == "__main__":
    main()
