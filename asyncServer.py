import socket
import asyncio
import platform
import time
import sys
import select
import json
import math
import random
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from threading import Lock



MOVESPEED = 30
ATTACK_DAMAGE = 50
gameClock = -1
clientClock = {}
swingTime = 0.5
hurtTime = 0.3
globalGame = {}
MAX_THREADS = 4
SLIME_SPEED = 3
wave_slimes = {1: 3, 2: 5, 3: 8, 4: 12, 5: 15}
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SLIME_WIDTH = 100
SLIME_HEIGHT = 100
SLIME_HP = 50
SLIME_DAMAGE = 10
BAT_DAMAGE = 20
executor = ThreadPoolExecutor(MAX_THREADS)
numclients = 0
threadData = {}
serverPort = None


threadLock = Lock()

def playerHandler(sock, host, port, lock, playerKey):

    friends = []
    exit = False

    ############################
    #Establishing server connection

    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    global serverPort 
    serverSock.settimeout(5)
    try:
        serverSock.connect((socket.gethostname(), serverPort))
    except:
        print("Couldn't connect to server")
        return False
    
    msg = {}
    msg["newThread"] = (host, port)
    msg["playerKey"] = playerKey
    msg = json.dumps(msg)
    length = msgLength(msg)

    try:
        serverSock.sendall(length.encode("utf-8"))

        serverSock.sendall(msg.encode("utf-8"))
    except:
        print("Error sending thread data to server")
        return False
    
    try:
        length = serverSock.recv(8)

    except:
        print("Error recieving msg length from server")
        return False
    
    if length.decode() == '':
        print("Bad length msg from server")
        return False
    
    length = int(length.decode())

    try:
        msg = serverSock.recv(length)

    except:
        print("Error recieving msg from server")
        return False
    
    if msg.decode("utf-8") != "SUCCESS":
        print("Server Error, stopping thread")
        return False
    
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
    inputs = [sock, conn]

    ############################


    ############################
    #Select loop for client updates and server interrupts

    while True:
        
        if timeoutStreak > 100:
            print("player disconnected")
            return True
        try:
            readable, _, _ = select.select(inputs, [], [], 30)
        except TimeoutError:
            print("threadwaiting")
            exit = True

        if exit:
            msg = "DEADCLIENT"
            length = msgLength(msg)
            try:
                serverSock.sendall(length.encode("utf-8"))

                serverSock.sendall(msg.encode("utf-8"))
            except:
                print("Error sending deadclient to server")
                return False

        for s in readable:
            if s is sock:
                conn, addr = s.accept()
                
                if addr is not (socket.gethostname(), serverPort):
                    s.close()
                    continue

                try:
                    length = s.recv(8)
                except:
                    print("Error for thread receving msg length from server 1")
                    continue
                length = length.decode()
                if length == '':
                    print("Error for thread receving msg length from server 2")
                    continue
                try:
                    msg = s.recv(int(length))
                except:
                    print("Error for thread receving msg from server")
                    continue
                
                msg = json.loads(msg)
                if msg["status"] == "NEWCLIENT":
                    friends.append(msg["playerKey"])

                elif msg["status"] == "DEADCLIENT":
                    friends.remove(msg["playerKey"])


            else:
                try:
                    length = conn.recv(8)
                except TimeoutError:
                    print("threadWaiting")
                    continue
                if length.decode() == '':
                    print("conn error")
                    timeoutStreak += 1
                    continue
                length = int(length.decode("utf-8"))
                try:
                    msg = conn.recv(length)
                except TimeoutError:
                    print("Length received but not msg")
                    continue
                if msg.decode() == '':
                    print("conn error")
                    timeoutStreak += 1
                    continue
                timeoutStreak = 0

                msg = json.loads(msg.decode())
                localGame = gameStateUpdate(msg, conn, playerClock, lock)

    



    pass
def gameInit(connection, playerKey):

    global globalGame
    global executor
    global numclients

    globalGame[playerKey] = {}
    globalGame[playerKey]["background"] = "background_surf"
    globalGame[playerKey]["characterStats"] = {"hp": 100, "gold": 0, "xp": 0, "lvl": 0, "XY": (100, 100)}
    globalGame[playerKey]["character"] = "stanceRightMain"
    globalGame[playerKey]["isSwinging"] = False
    globalGame[playerKey]["isHurt"] = False
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
    args = [threadSock, threadHost, threadPort, threadLock, playerKey]
    future = executor.submit(playerHandler, *args)

    global threadData
    threadData[playerKey] = (threadHost, threadPort)

    


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

    


def gameStateUpdate(updates, connection, clock, lock):

    
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
               
            
            #TODO  add part for "isHurt"
        
        elif updates["status"] == "INPUT":
            
            for key in updates.keys():

                if key == "type":

                    if updates[key] == "moveUp":
                        
                        xy = tempGlobal[clientKey]["characterStats"]["XY"]
                        tempGlobal[clientKey]["characterStats"]["XY"] = (xy[0], (xy[1] -  MOVESPEED))
                        updateRes["characterStats"]["XY"] = (xy[0], (xy[1] -  MOVESPEED))
                        

                    elif updates[key] == "moveRight":
                        
                        xy = tempGlobal[clientKey]["characterStats"]["XY"]
                        tempGlobal[clientKey]["characterStats"]["XY"] = ((xy[0] + MOVESPEED), xy[1])
                        updateRes["characterStats"]["XY"] = ((xy[0] + MOVESPEED), xy[1])
                        

                    elif updates[key] == "moveDown":
                        xy = tempGlobal[clientKey]["characterStats"]["XY"]
                        tempGlobal[clientKey]["characterStats"]["XY"] = (xy[0], (xy[1] +  MOVESPEED))
                        updateRes["characterStats"]["XY"] = (xy[0], (xy[1] +  MOVESPEED))
                        

                    elif updates[key] == "moveLeft":
                        xy = tempGlobal[clientKey]["characterStats"]["XY"]
                        tempGlobal[clientKey]["characterStats"]["XY"] = ((xy[0] - MOVESPEED), xy[1])
                        updateRes["characterStats"]["XY"] = ((xy[0] - MOVESPEED), xy[1])

                        
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
                        tempGlobal[clientKey]["character"] = ("hurtRight", time.time_ns() )
                        tempGlobal[clientKey]["isHurt"] = True
                        updateRes["character"] = "hurtRight"
                        updateRes["characterStats"]["hp"] = tempGlobal[clientKey]["characterStats"]["hp"]
                        updateRes["isHurt"] = True

                    elif enemies == "bats" and not globalGame[clientKey]["isHurt"] and not tempGlobal[clientKey]["isSwinging"]:
  
                        tempGlobal[clientKey]["characterStats"]["hp"] -= BAT_DAMAGE
                        tempGlobal[clientKey]["character"] = ( "hurtRight", time.time_ns() ) 
                        tempGlobal[clientKey]["isHurt"] = True
                        updateRes["character"] = "hurtRight"
                        updateRes["characterStats"]["hp"] = tempGlobal[clientKey]["characterStats"]["hp"]
                        updateRes["isHurt"] = True

                    elif not globalGame[clientKey]["isHurt"]:

                        for pair in enemies:
                            enemy = pair[0]
                            index = pair[1]

                            if enemy == "slimes":
                       
                                stats = tempGlobal["monsters"]["slimes"][index]
      
                                if (stats[2] - ATTACK_DAMAGE) <= 0:
                                    #tempGlobal["monsters"]["slimes"].remove(index)
                                    aliveSlimes[index] = None
                                    print("killed slime")
                                    print(aliveSlimes)
                                else:
                                    #tempGlobal["monsters"]["slimes"][index] = ( stats[0],stats[1], stats[2]-ATTACK_DAMAGE )
                                    aliveSlimes[index] = ( stats[0],stats[1], stats[2]-ATTACK_DAMAGE )

                            if enemy == "bats":
                                stats = tempGlobal["monsters"]["bats"][index]
                                if (stats[2] - ATTACK_DAMAGE) <= 0:
                                    #tempGlobal["monsters"]["bats"].remove(index)
                                    aliveBats[index] = None
                                else:
                                    aliveBats[index] = ( stats[0],stats[1], stats[2]-ATTACK_DAMAGE )
                
                elif key == "collisions":
                    
                    for mon, index in updates[key]:
                        if mon == "slimes":
                            
                            movableSlimes.remove(index)
                        elif mon == "bats":
                            movableBats.remove(index)
                    
                        

        
        charCoords = tempGlobal[clientKey]["characterStats"]["XY"]
        ###########
        for slimeI in movableSlimes:
            print(slimeI)
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
            
            aliveBats[batsI] = (int(SLIME_SPEED*math.cos(dir)*(-1)) + stats[0], int(SLIME_SPEED*math.sin(dir)*(-1)) + stats[1], stats[2] )
      
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

            for i in range(wave_slimes[1]):
                slimes.append((random.randint(0, SCREEN_WIDTH - SLIME_WIDTH), random.randint(0, SCREEN_HEIGHT - SLIME_HEIGHT), SLIME_HP))
            tempGlobal["monsters"]["slimes"] = slimes
            tempGlobal["wave"] = 1
            updateRes["monsters"]["slimes"] = slimes
            updateRes["wave"] = 1
        
        elif len(tempGlobal["monsters"]["slimes"]) == 0 and len(tempGlobal["monsters"]["bats"]) == 0:
            print("getting new round")
            slimes = []
            wave = tempGlobal["wave"] + 1
            for i in range(wave_slimes[wave]):
                slimes.append((random.randint(0, SCREEN_WIDTH - SLIME_WIDTH), random.randint(0, SCREEN_HEIGHT - SLIME_HEIGHT), SLIME_HP))
            tempGlobal["monsters"]["slimes"] = slimes
            tempGlobal["wave"] = wave
            updateRes["monsters"]["slimes"] = slimes
            updateRes["wave"] = wave



        globalGame = tempGlobal.copy()


        

    
    try:
        
        msg = json.dumps(updateRes)
     
        

        #serverSock.sendto((msgLength(msg)).encode("utf-8"), client)
        connection.sendall((msgLength(msg)).encode("utf-8"))

        #serverSock.sendto(msg.encode("utf-8"), client)
        connection.sendall(msg.encode("utf-8"))
    except:
        print("problem sending data from thread to client")
        sys.exit()

    return globalGame[clientKey]

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
    serverSock.settimeout(5)

    # tries to bind the socket to the port with a 5 second delay if errors
    host = socket.gethostname()
    while True:
        try:
            serverSock.bind( (host, serverPort) )
            break
        except:
            print("Binding Error")
            time.sleep(5)

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
                print(f"Thread died: {exc}")
                
                
                
            except:
                print("checked thread")
            
        try:
            
            readable, _, exceptions = select.select( inputs, [],  [], 60 )
            
            
        except TimeoutError:
            print("waiting")
        global numclients
        
        for s in readable:
            if s is serverSock:
              
           
                try:
                    conn, addr = s.accept()
                    print("Accepted new connection")
                except:
                    print("Error accepting connection")
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
                    
                    msg = msg_data.decode('utf-8')
                   
                except Exception as e:
                    print("Issue receiving initialized state")
                    continue
                

                if msg != "CHECK":
                    
                    msg = json.loads(msg)
                
                
                if "newThread" in msg.keys():

                    res = "SUCCESS"
                    length = msgLength(res)
                    try:
                        conn.sendall(length.encode("utf-8"))

                        conn.sendall(res.encode("utf-8"))
                    except:
                        print("Error sending confirmation to thread")
                        inputs.remove(conn)
                        continue
                    
                    threadData[msg["playerKey"]] = msg["newThread"]
                    
                    continue
                    

                
                #inputs.append(conn)

                #players[msg["playerKey"]] = msg
                global SLIME_WIDTH
                global SLIME_HEIGHT
                SLIME_WIDTH = msg["dimensions"]["slime"][0]
                SLIME_HEIGHT = msg["dimensions"]["slime"][1]

                res = "GOOD"

                threads.append(gameInit(conn, msg["playerKey"]))
                
                
                try:
                    
                    length = msgLength(msg)
                    
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
                except:
                    print("error getting msg from connection")
                    print(s)
                    inputs.remove(s)
                    s.close()
                    continue
                msg = json.loads(msg.decode("utf-8"))

                if msg["status"] == "DEADCONN":
                    #If thread dies, server will remove thread data and close client connection so client can reconnect and use a new thread
                    NUM_THREADS -= 1
                    inputs.remove(s)
                    del threadData[msg["playerKey"]]
                    s.close()

                elif msg["status"] == "DEADCLIENT":
                    ##If thread tells server that client died, server will delete client from the game and the thread will kill itself
                    playerKey = msg["playerKey"]
                    del globalGame[playerKey]
                    inputs.remove(s)
                    s.close()

        for s in exceptions:
            inputs.remove(s)
            s.close()
                    
                

def msgLength(msg):
    length = str(len(msg))
    for i in range(8 - len(str(length))):
        length = "0" + length
    return length


if __name__ == "__main__":
    main()
    
