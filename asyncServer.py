import socket
import asyncio
import platform
import time
import sys
import select
import json
import math
import random
import traceback
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from threading import Lock



#MOVESPEED = 30

MOVESPEED = 3
ATTACK_DAMAGE = 50

gameClock = -1
clientClock = {}
swingTime = 0.5
hurtTime = 0.3
globalGame = {}
MAX_THREADS = 4
SLIME_SPEED = 2
wave_monsters = {1: (3,0), 2: (5,0), 3: (8,2), 4: (12,5), 5: (15,10)}
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SLIME_WIDTH = 100
SLIME_HEIGHT = 100
SLIME_HP = 50
SLIME_DAMAGE = 10
BAT_WIDTH = 50
BAT_HEIGHT = 50
BAT_HP = 50
BAT_DAMAGE = 20


numclients = 0
threadData = {}
serverPort = None


threadLock = Lock()


class ThreadPoolExecutorStackTraced(ThreadPoolExecutor):

    def submit(self, fn, *args, **kwargs):
        """Submits the wrapped function instead of `fn`"""

        return super(ThreadPoolExecutorStackTraced, self).submit(
            self._function_wrapper, fn, *args, **kwargs)

    def _function_wrapper(self, fn, *args, **kwargs):
        """Wraps `fn` in order to preserve the traceback of any kind of
        raised exception
        """
        try:
            return fn(*args, **kwargs)
        except Exception:
            raise sys.exc_info()[0](traceback.format_exc())
        
executor = ThreadPoolExecutorStackTraced(max_workers=MAX_THREADS)

def playerHandler(sock, host, port, lock, playerKey, friends):
    
    threadFriends = friends
    exit = False
    numClients = 0
    clientIndex = -1
    
    if len(threadFriends) > 0:
       
        numClients = len(threadFriends)
    dx = 0
    dy = 0
    ############################
    #Establishing server connection

    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    global serverPort 
    serverSock.settimeout(5)
    try:
        serverSock.connect((socket.gethostname(), serverPort))
    except:
        print("Couldn't connect to server")
        return playerKey
    
    msg = {}
    msg["newThread"] = [host, port]
    msg["playerKey"] = playerKey
    msg = json.dumps(msg)
    length = msgLength(msg)

    try:
        serverSock.sendall(length.encode("utf-8"))

        serverSock.sendall(msg.encode("utf-8"))
    except:
        print("Error sending thread data to server")
        return playerKey
    
    try:
        length = serverSock.recv(8)

    except:
        print("Error recieving msg length from server")
        return playerKey
    
    if length.decode() == '':
        print("Bad length msg from server")
        return playerKey
    
    length = int(length.decode())

    try:
        msg = serverSock.recv(length)

    except:
        print("Error recieving msg from server")
        return playerKey
    
    if msg.decode("utf-8") != "SUCCESS":
        print("Server Error, stopping thread")
        return playerKey
    
    print("thread starting client")
    ####################################


    ####################################
    #Establishing client connection

    try:
        conn, addr = sock.accept()
    except:
        print("Didn't get player req in time")
        sys.exit()

    try:
        length = conn.recv(8)
        length = int(length.decode())
        msg = conn.recv(length)

    except:
        print("Error receiving init message from player")
        sys.exit()
    msg = msg.decode("utf-8")

    if msg != "INIT":
        print("did not receive INIT message")
        sys.exit()

    msg = "START"
    
    length = msgLength(msg)
    try:
        conn.sendall(length.encode("utf-8"))
        conn.sendall(msg.encode("utf-8"))
    except:
        print("Error sending start message to player")
        sys.exit()
    playerClock = time.time_ns()
    localGame = {}
    sock.settimeout(1)
    timeoutStreak = 0
    inputs = [sock, conn, serverSock]
    addClient = (False, None)

    ############################


    ############################
    #Select loop for client updates and server interrupts
    
    while True:
        
       
        if timeoutStreak > 100:
            print("player disconnected")
            msg = {"status": "DEADCONN", "playerKey": playerKey}
            msg = json.dumps(msg)
            length = msgLength(msg)
            try:
                serverSock.sendall(length.encode())

                serverSock.sendall(msg.encode())
                
            except:
                print("Error sending deadclient to server")
                return playerKey
            for s in inputs:
                s.close()
            return playerKey

            
        elif numClients > 0 and not addClient[0]:
            clientIndex += 1
            addClient = (True, friends[clientIndex])

        
        try:
            readable, _, _ = select.select(inputs, [], [], 30)
        except TimeoutError:
            print("thread is waiting")
            exit = True
            

        if exit:
            msg = {"status": "DEADCONN", "playerKey": playerKey}
            msg = json.dumps(msg)
            length = msgLength(msg)
            try:
                serverSock.sendall(length.encode())

                serverSock.sendall(msg.encode())
                
            except:
                print("Error sending deadclient to server")

            return playerKey
        

        for s in readable:
            if s is sock:
                
                conn, addr = s.accept()
                
                if addr[0] is not socket.gethostname() and addr[1] is not serverPort:
                    conn.close()
                    continue

                try:
                    length = conn.recv(8)
                except:
                    print("Error for thread receving msg length from server 1")
                    continue
                length = length.decode()
                if length == '':
                    print("Error for thread receving msg length from server 2")
                    continue
                try:
                    msg = conn.recv(int(length))
                except:
                    print("Error for thread receving msg from server")
                    continue
                
                msg = json.loads(msg)
                if msg["status"] == "NEWCLIENT":
                    
                    threadFriends.append(msg["playerKey"])
                    addClient = (True, msg["playerKey"])

                elif msg["status"] == "DEADCLIENT":
                    
                    if msg["playerKey"] in threadFriends:
                        threadFriends.remove(msg["playerKey"])

            elif s is serverSock:
            
                
                try:
                    length = serverSock.recv(8)
                    
                    length = int(length.decode())
                    if length == '':
                        print("error receiving data from server")
                        continue
                    msg = serverSock.recv(length)
                except Exception as e:
                    print(e)
                    print("error receiving new client msg from server")
                
                msg = json.loads(msg.decode())

                if msg["status"] == "NEWCLIENT":
                    
                    threadFriends.append(msg["playerKey"])
                    addClient = (True, msg["playerKey"])
                    numClients += 1





                
            else:
                try:
                    length = conn.recv(8)
                except TimeoutError:
                    print("threadWaiting")
                    continue
                if length.decode() == '':
                    
                    timeoutStreak += 1
                    continue
                length = int(length.decode("utf-8"))
                try:
                    msg = conn.recv(length)
                except TimeoutError:
                    print("Length received but not msg")
                    continue
                
                if msg.decode() == '':
                    
                    timeoutStreak += 1
                    continue
                timeoutStreak = 0

                msg = json.loads(msg.decode())
                
                if addClient[0] and numClients > 0:
                    
                    dx, dy = gameStateUpdate(msg, conn, playerClock, lock, addClient[1], threadFriends, dx, dy)
                    addClient = (False, None)
                    numClients -= 1
                else:
                    dx, dy = gameStateUpdate(msg, conn, playerClock, lock, None, threadFriends, dx, dy)

def gameInit(connection, playerKey, friends):

    global globalGame
    global executor
    global numclients

    globalGame[playerKey] = {}
    globalGame[playerKey]["background"] = "background_surf"
    globalGame[playerKey]["characterStats"] = {"hp": 100, "gold": 0, "xp": 0, "lvl": 1, "XY": (100, 100)}
    globalGame[playerKey]["character"] = "stanceRightMain"
    globalGame[playerKey]["isSwinging"] = False
    globalGame[playerKey]["isHurt"] = False
    #globalGame[playerKey]["isCooldown"] = False
    
    if len(friends) == 0:
        
        globalGame["isWin"] = False
        globalGame["monsters"] = {"slimes": [], "bats": []}
        globalGame["wave"] = 0
    clientClock[playerKey] = time.time_ns()

    


    threadSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    threadSock.settimeout(10)
    threadHost = platform.node()
    threadPort = 0
    Found = True

    while Found:
        for port in range(80,11000,1):
            try:
                threadSock.bind((threadHost, port))
                print(f"binded to {threadHost}, {port}")
               
                threadPort = port
                Found = False
                break
            except OSError:
                continue

    threadSock.listen(1)
    msg = {"host": threadHost, "port": threadPort}
    print(f"sending {threadHost} and {threadPort}")
    
    msg = json.dumps(msg)
    length = msgLength(msg)
    try:
        connection.sendall(length.encode("utf-8"))
        connection.sendall(msg.encode("utf-8"))
    except:
        print("error sending thread addr to player")
        return False
    if numclients == 0:
        numclients += 1
    
    

    global threadLock
    args = [threadSock, threadHost, threadPort, threadLock, playerKey, friends]
    future = executor.submit(playerHandler, *args)

    

    return future

def updateSwing(swingData):
    currTime = time.time_ns() / 10**9
    startTime = int(swingData[1]) / 10**9
    elapsedSwing = currTime - startTime
    if elapsedSwing  < (swingTime / 5):
        return "swingRightStart"
    elif elapsedSwing < (swingTime / 5)*2:
        return "swingRightMid"
    elif elapsedSwing < (swingTime / 5)*3:
        return "swingRightUp"
    elif elapsedSwing < (swingTime / 5)*4:
        return "swingRightFinish"
    elif elapsedSwing <= swingTime:
        return "swingRightFinal"
    else:
        return None


def findDir(x1,y1,x2,y2):
    if x2 == x1 and y2 == y1:
        return None
    elif x1 == x2:
        if (y2-y1) < 0:
            return -1*math.pi/2
        else:
            return math.pi/2
    elif y1 == y2:
        if (x2 - x1) > 0:
            return 0
        else:
            return math.pi
    if (x2-x1) < 0 and (y2-y1) < 0:
        return math.atan((y2-y1)/(x2-x1)) + math.pi
    
    elif (x2-x1) > 0 and (y2-y1) < 0:
        return math.atan((y2-y1)/(x2-x1))
    
    elif (x2-x1) > 0 and (y2-y1) > 0:
        return math.atan((y2-y1)/(x2-x1))
    
    else:
        return math.atan((y2-y1)/(x2-x1)) + math.pi
    

def updateHurt(startTime):
    tempTime = startTime / 10**9
    currTime = time.time_ns() / 10**9

    if currTime - tempTime < 0.5:
        return "hurtRight"
    else:
        return None

    


def gameStateUpdate(updates, connection, clock, lock, newClientKey, friends, dx, dy):

    
    updateRes = defaultdict(dict)
    global globalGame
    global SLIME_SPEED
    
    
    
    clientKey = updates["playerKey"]
    tempGlobal = {}

    
    with lock:
        tempGlobal = globalGame.copy()
        movableSlimes = [x for x in range(len(tempGlobal["monsters"]["slimes"]))]
        movableBats = [x for x in range(len(tempGlobal["monsters"]["bats"]))]
        aliveSlimes = tempGlobal["monsters"]["slimes"]
        aliveBats = tempGlobal["monsters"]["bats"]

        if newClientKey:
            print("LETS GO")
            updateRes["newClient"] = newClientKey

        
        if updates["status"] == "CHECK":
            
            if tempGlobal[clientKey]["isSwinging"]:
                swing = updateSwing(tempGlobal[clientKey]["character"])

                if not swing:
                    tempGlobal[clientKey]["isSwinging"] = False
                    tempGlobal[clientKey]["character"] = "stanceRightMain"
                    updateRes["character"] = "stanceRightMain"
                    updateRes["isSwinging"] = False

                else:
                    tempGlobal[clientKey]["character"] = (swing, tempGlobal[clientKey]["character"][1])
                    updateRes["character"] = tempGlobal[clientKey]["character"][0]

            elif tempGlobal[clientKey]["isHurt"]:
                temp = tempGlobal[clientKey]["character"]
                hurt = updateHurt(tempGlobal[clientKey]["character"][1])
                
                if not hurt:
                    tempGlobal[clientKey]["character"] = "stanceRightMain"
                    tempGlobal[clientKey]["isHurt"] = False
                    updateRes["character"] = "stanceRightMain"
                    updateRes["isHurt"] = False
            
            if dx != 0 or dy != 0:
                xy = tempGlobal[clientKey]["characterStats"]["XY"]
                newY = min(660,max(0,xy[1]+dy))
                newX = min(950,max(0,xy[0]+dx))
                tempGlobal[clientKey]["characterStats"]["XY"] = (newX,newY)
                updateRes["characterStats"]["XY"] = (newX, newY)

                
          
            
        
        
       
        
        elif updates["status"] == "INPUT":
            
         
            for key in updates.keys():
            
                if key == "type":
                    
                    if updates[key] == "stopUp" or updates[key] == "stopDown":
                        dy = 0

                    elif updates[key] == "stopRight" or updates[key] == "stopLeft":
                        dx = 0
                    
                    elif updates[key] == "moveUp":
                        dy = -1 * MOVESPEED
                        xy = tempGlobal[clientKey]["characterStats"]["XY"]
                        newY = min(650,max(0,xy[1]+dy))
                        tempGlobal[clientKey]["characterStats"]["XY"] = (xy[0], newY)
                        updateRes["characterStats"]["XY"] = (xy[0], newY)
                        

                    elif updates[key] == "moveRight":
                        dx = MOVESPEED
                        xy = tempGlobal[clientKey]["characterStats"]["XY"]
                        tempGlobal[clientKey]["characterStats"]["XY"] = ((xy[0] + dx), xy[1])
                        updateRes["characterStats"]["XY"] = ((xy[0] + dx), xy[1])
                        

                    elif updates[key] == "moveDown":
                        dy = MOVESPEED
                        xy = tempGlobal[clientKey]["characterStats"]["XY"]
                        newY = min(650,max(0,xy[1]+dy))
                        tempGlobal[clientKey]["characterStats"]["XY"] = (xy[0], newY)
                        updateRes["characterStats"]["XY"] = (xy[0], newY)
                        

                    elif updates[key] == "moveLeft":
                        dx = -1 * MOVESPEED
                        xy = tempGlobal[clientKey]["characterStats"]["XY"]
                        newX = min(950,max(0,xy[0]+dx))
                        tempGlobal[clientKey]["characterStats"]["XY"] = (newX, xy[1])
                        updateRes["characterStats"]["XY"] = (newX, xy[1])

                        
                    elif updates[key] == "swing":
                        if not tempGlobal[clientKey]["isHurt"]:
                            if tempGlobal[clientKey]["isSwinging"]:
                                swing = updateSwing(globalGame[clientKey]["character"])
                                if not swing:
                                    tempGlobal[clientKey]["isSwinging"] = False
                                    tempGlobal[clientKey]["character"] = "stanceRightMain"
                                    updateRes["character"] = "swingRightStart"
                                    updateRes["isSwinging"] = False
                                else:
                                    tempGlobal[clientKey]["character"] = (swing, tempGlobal[clientKey]["character"][1])
                                    updateRes["character"] = tempGlobal[clientKey]["character"][0]
                            else:
                                tempGlobal[clientKey]["isSwinging"] = True
                                tempGlobal[clientKey]["character"] = ("swingRightStart", time.time_ns())
                                updateRes["character"] = tempGlobal[clientKey]["character"][0]
                                updateRes["isSwinging"] = True
                    
                elif key == "attack":
                    
                    enemies = updates[key]
                    if enemies == "slimes" and not tempGlobal[clientKey]["isHurt"] and not tempGlobal[clientKey]["isSwinging"]:

                        tempGlobal[clientKey]["characterStats"]["hp"] -= SLIME_DAMAGE
                        if tempGlobal[clientKey]["characterStats"]["hp"] < 0:
                            tempGlobal[clientKey]["isDied"] = True
                            updateRes["isDied"] = True

                        else:
                            tempGlobal[clientKey]["character"] = ("hurtRight", time.time_ns() )
                            tempGlobal[clientKey]["isHurt"] = True
                            updateRes["character"] = "hurtRight"
                            updateRes["characterStats"]["hp"] = tempGlobal[clientKey]["characterStats"]["hp"]
                            updateRes["isHurt"] = True
                        

                    elif enemies == "bats" and not tempGlobal[clientKey]["isHurt"] and not tempGlobal[clientKey]["isSwinging"]:
  
                        tempGlobal[clientKey]["characterStats"]["hp"] -= BAT_DAMAGE
                        if tempGlobal[clientKey]["characterStats"]["hp"] < 0:
                            tempGlobal[clientKey]["isDied"] = True
                            updateRes["isDied"] = True

                        else:
                            tempGlobal[clientKey]["character"] = ( "hurtRight", time.time_ns() ) 
                            tempGlobal[clientKey]["isHurt"] = True
                            updateRes["character"] = "hurtRight"
                            updateRes["characterStats"]["hp"] = tempGlobal[clientKey]["characterStats"]["hp"]
                            updateRes["isHurt"] = True

                    elif not tempGlobal[clientKey]["isHurt"]:
                        if enemies == "slimes" or enemies == "bats":
                            
                            continue

                        for pair in enemies:
                            
                            
                            enemy = pair[0]
                            index = pair[1]

                            if enemy == "slimes":
                                
                                stats = tempGlobal["monsters"]["slimes"][index]
                                if (stats[2] - ATTACK_DAMAGE) <= 0:
                                    
                                    aliveSlimes[index] = None
                                    
                                       
                                    tempGlobal[clientKey]["characterStats"]["xp"] += 10
                                    updateRes["characterStats"]["xp"] = tempGlobal[clientKey]["characterStats"]["xp"] 
                                    if tempGlobal[clientKey]["characterStats"]["xp"] >= 100:
                                       tempGlobal[clientKey]["characterStats"]["lvl"] += 1
                                       updateRes["characterStats"]["lvl"] = tempGlobal[clientKey]["characterStats"]["lvl"] 
                                       tempGlobal[clientKey]["characterStats"]["xp"] -= 100 
                                    
                                else:
                                    
                                    aliveSlimes[index] = ( stats[0],stats[1], stats[2]-ATTACK_DAMAGE )
                                    
                            elif enemy == "bats":
                                
                                stats = tempGlobal["monsters"]["bats"][index]

                                if (stats[2] - ATTACK_DAMAGE) <= 0:
                                    
                                    aliveBats[index] = None
                                    tempGlobal[clientKey]["characterStats"]["xp"] += 10
                                    updateRes["characterStats"]["xp"] = tempGlobal[clientKey]["characterStats"]["xp"] 
                                    if tempGlobal[clientKey]["characterStats"]["xp"] >= 100:
                                       tempGlobal[clientKey]["characterStats"]["lvl"] += 1
                                       updateRes["characterStats"]["lvl"] = tempGlobal[clientKey]["characterStats"]["lvl"] 
                                       tempGlobal[clientKey]["characterStats"]["xp"] -= 100

                                else:
                                    aliveBats[index] = ( stats[0],stats[1], stats[2]-ATTACK_DAMAGE )
                
                elif key == "collisions":
                    
                    for mon, index in updates[key]:
                        if mon == "slimes":
                            if index < len(movableSlimes):
                                movableSlimes.remove(index)
                                
                            
                        elif mon == "bats":
                            if index < len(movableBats):
                                movableBats.remove(index)
                
            if dx != 0 or dy != 0:
                xy = tempGlobal[clientKey]["characterStats"]["XY"]
                newX = min(960,max(0,dx+xy[0]))
                newY = min(670,max(0,xy[1]+dy))
                tempGlobal[clientKey]["characterStats"]["XY"] = (newX, newY)
                updateRes["characterStats"]["XY"] = (newX, newY)
                
                    
    

        for friend in friends:
            if friend not in tempGlobal.keys():
                friends.remove(friend)
            elif tempGlobal[friend]["isSwinging"] or tempGlobal[friend]["isHurt"]:
                updateRes[friend] = (globalGame[friend]["character"][0], globalGame[friend]["characterStats"]["XY"])
            else:
                updateRes[friend] = (globalGame[friend]["character"], globalGame[friend]["characterStats"]["XY"])
        
        charCoords = tempGlobal[clientKey]["characterStats"]["XY"]
        ###########
        
        for slimeI in movableSlimes:
            
            if not aliveSlimes[slimeI]:
                continue
            stats = aliveSlimes[slimeI]
            dir = findDir(stats[0],stats[1],charCoords[0],charCoords[1])
            if not dir:
                continue
            
            aliveSlimes[slimeI] = (int(SLIME_SPEED*math.cos(dir)) + stats[0], int(SLIME_SPEED*math.sin(dir)) + stats[1], stats[2] )
        
        for batsI in movableBats:
            if not aliveBats[batsI]:
                continue
            stats = aliveBats[batsI]
            dir = findDir(stats[0],stats[1],charCoords[0],charCoords[1])
            if not dir:
                continue
            
            aliveBats[batsI] = (int(SLIME_SPEED*math.cos(dir)) + stats[0], int(SLIME_SPEED*math.sin(dir)) + stats[1], stats[2] )
      
        tempGlobal["monsters"]["slimes"] = [slime for slime in aliveSlimes if slime is not None]
        updateRes["monsters"]["slimes"] = tempGlobal["monsters"]["slimes"]
        tempGlobal["monsters"]["bats"] = [bat for bat in aliveBats if bat is not None]
        updateRes["monsters"]["bats"] = tempGlobal["monsters"]["bats"]
        
        if tempGlobal["wave"] == 0:

            slimes = []
            global SCREEN_WIDTH
            global SCREEN_HEIGHT
            global SLIME_HEIGHT
            global SLIME_WIDTH
            global SLIME_HP

            for i in range(wave_monsters[1][0]):
                slimes.append((random.randint(0, SCREEN_WIDTH - SLIME_WIDTH), random.randint(0, SCREEN_HEIGHT - SLIME_HEIGHT), SLIME_HP))
            tempGlobal["monsters"]["slimes"] = slimes
            tempGlobal["wave"] = 1
            updateRes["monsters"]["slimes"] = slimes
            updateRes["wave"] = 1
        
        elif len(tempGlobal["monsters"]["slimes"]) == 0 and len(tempGlobal["monsters"]["bats"]) == 0:
            
            slimes = []
            bats = []
            wave = tempGlobal["wave"] + 1
            
            if wave == 6:
                
                tempGlobal["isWin"] = True
                updateRes["isWin"] = True

            else:
                for i in range(wave_monsters[wave][0]):
                    
                    slimes.append((random.randint(0, SCREEN_WIDTH - SLIME_WIDTH), random.randint(0, SCREEN_HEIGHT - SLIME_HEIGHT), SLIME_HP))
                
                for i in range(wave_monsters[wave][1]):
                    bats.append((random.randint(0, SCREEN_WIDTH - BAT_WIDTH), random.randint(0, SCREEN_HEIGHT - BAT_HEIGHT), BAT_HP))

                tempGlobal["monsters"]["slimes"] = slimes
                tempGlobal["wave"] = wave
                tempGlobal["monsters"]["bats"] = bats
                updateRes["monsters"]["bats"] = bats
                updateRes["monsters"]["slimes"] = slimes
                updateRes["wave"] = wave
                


        
        globalGame = tempGlobal.copy()


        

    if newClientKey:
        print("about to send dollars")
    try:
        
        msg = json.dumps(updateRes)
     
        

        #serverSock.sendto((msgLength(msg)).encode("utf-8"), client)
        connection.sendall((msgLength(msg)).encode("utf-8"))

        #serverSock.sendto(msg.encode("utf-8"), client)
        connection.sendall(msg.encode("utf-8"))
    except:
        print("problem sending data from thread to client")
        sys.exit()

    return dx, dy

    pass

def main():

    players = {}

    MOVESPEED = 30
    SWINGFRAMES = 6
    global NUM_THREADS
    NUM_THREADS = 0
    global globalGame
    globalGame = {}
    threads = []
    
    global serverPort
   
    
    try:
        serverPort = int(sys.argv[1])
    except:
        print("Must enter port listening on")
        sys.exit()

    # create UDP socket with timeout of 1 second 
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSock.settimeout(60)

    # tries to bind the socket to the port with a 5 second delay if errors
    host = socket.gethostname()
    
    try:
        serverSock.bind( (host, serverPort) )
        
    except:
        print("Binding Error")
        while True:
            serverPort = 80
            try:
                serverSock.bind((host, serverPort))
                break
            except:
                serverPort += 1
                if serverPort > 11000:
                    print("Could not find open port")
                    sys.exit()
            

    print(f"connected to {socket.gethostname()} at port {str(serverPort)}")

    try:
        serverSock.listen(5)
        print("listening")
    except:
        print("Error with listen")

    
    # list of clients

    inputs = [serverSock]


    while True:
        for t in threads:
            
            try:
                exc = t.exception(0.00001)
                if not exc:
                    continue
                threads.remove(t)
                NUM_THREADS -= 1
                print(f"Thread died: {exc}")
                playerKey = t.result()

                if playerKey in inputs:
                    inputs.remove(playerKey)
                
                
                
            except:
                print("checking threads")
            
        try:
            
            readable, _, exceptions = select.select( inputs, [],  [], 10 )
            
            
        except TimeoutError:
            print("server waiting")
            continue
        global numclients
        
        for s in readable:
            if s is serverSock:
              
                
                try:
                    conn, addr = s.accept()
                    print("Accepting new player")
                except:
                    print("Error accepting connection")
                    continue
                if conn in inputs:
                    continue
                inputs.append(conn)

               
                try:
                    length = conn.recv(8)
                    
                except:
                    print("Error receiving req from client")
                    continue
               
                # decode message to get the length
             
                length = int(length.decode("utf-8"))
                
                
                # try to receive full message
                
                try:
                    msg_data = conn.recv(length)
                    
                    message = msg_data.decode('utf-8')
                   
                except Exception as e:
                    print("Issue receiving initialized state")
                    continue
                

                if message != "CHECK":
                    
                    message = json.loads(message)
                
                
                if "newThread" in message.keys():
                    res = "SUCCESS"
                    length = msgLength(res)
                    try:
                        conn.sendall(length.encode("utf-8"))

                        conn.sendall(res.encode("utf-8"))
                    except:
                        print("Error sending confirmation to thread")
                        if conn in inputs:
                            if conn in inputs:
                                inputs.remove(conn)
                        continue

                    NUM_THREADS += 1

                    if NUM_THREADS > 1:

                        msg = {"status": "NEWCLIENT", "playerKey": message["playerKey"]}
                        msg = json.dumps(msg)
                        length = msgLength(msg)

                        for key in threadData.keys():
                            connection = threadData[key][0]
                            

                            while True:
                                try:
                                    connection.sendall(length.encode())

                                    connection.sendall(msg.encode())
                                    
                                    break
                                except TimeoutError:
                                    print("error sending new player msg")
                    
                    
                    threadData[message["playerKey"]] = [conn]

                    continue

                global SLIME_WIDTH
                global SLIME_HEIGHT
                SLIME_WIDTH = message["dimensions"]["slime"][0]
                SLIME_HEIGHT = message["dimensions"]["slime"][1]
                print(message)
                res = "GOOD"
                
                fr = [x for x in threadData.keys()]
                future = gameInit(conn, message["playerKey"], fr)
                if not future:
                    print("gameInit failure")
                    return playerKey
                threads.append(future)
                
                
                try:
                    
                    length = msgLength(res)
                    
                    conn.sendall(length.encode())
                
                    conn.sendall(res.encode())
                    

                
                except:
                    print("Error sending initialize OK")
                    continue

                

            else:
                
                try:
                    length = s.recv(8)
                    length = int(length.decode("utf-8"))
                    msg = s.recv(length)
                except Exception as e:
                    print(e)
                    if s in inputs:
                        inputs.remove(s)
                    s.close()
                    continue
                
                msg = json.loads(msg.decode("utf-8"))

                

                if msg["status"] == "DEADCONN":
                    #If thread dies, server will remove thread data and close client connection so client can reconnect and use a new thread
                    
                    inputs.remove(threadData[msg["playerKey"]][0])
                    
                    del threadData[msg["playerKey"]]
                    fr = [x for x in threadData.keys()]
                    future = gameInit(s, msg["playerKey"], fr)
                    if not future:
                        print("gameInit failure")
                        return msg["playerKey"]
                    threads.append(future)
                    

                elif msg["status"] == "DEADCLIENT":
                    ##If thread tells server that client died, server will delete client from the game and the thread will kill itself
                    playerKey = msg["playerKey"]
                    del globalGame[playerKey]
                    if s in inputs:
                        inputs.remove(s)
                    s.close()

                elif msg["status"] == "CLIENTEXIT":
                    playerKey = msg["playerKey"]
                    del globalGame[playerKey]
                    if s in inputs:
                        print("client successfully exitted from game")
                        inputs.remove(s)
                    s.close()

        for s in exceptions:
            if s in inputs:
                print("got exception!!")
                inputs.remove(s)
            s.close()
                    
                

def msgLength(msg):
    length = str(len(msg))
    for i in range(8 - len(str(length))):
        length = "0" + length
    return length


if __name__ == "__main__":
    main()
