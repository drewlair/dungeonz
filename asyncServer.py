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
gameClock = -1
clientClock = {}
swingTime = 0.5
hurtTime = 0.3
globalGame = {}
MAX_THREADS = 4
SLIME_SPEED = 5
wave_slimes = {1: 3, 2: 5, 3: 8, 4: 12, 5: 15}
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SLIME_WIDTH = 100
SLIME_HEIGHT = 100
SLIME_HP = 50
executor = ThreadPoolExecutor(MAX_THREADS)

threadLock = Lock()

def playerHandler(sock, host, port, lock):

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
    while True:
        print("inwhile")
        if timeoutStreak > 100:
            print("player disconnected")
            return True
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

    globalGame[playerKey] = {}
    globalGame[playerKey]["background"] = "background_surf"
    globalGame[playerKey]["characterStats"] = {"hp": 100, "gold": 0, "xp": 0, "lvl": 0, "XY": (100, 100)}
    globalGame[playerKey]["character"] = "stanceRightMain"
    globalGame[playerKey]["isSwinging"] = False
    globalGame["monsters"] = {}
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
    print("PAST")
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

    global threadLock
    args = [threadSock, threadHost, threadPort, threadLock]
    future = executor.submit(playerHandler, *args)
    


    return future

def updateSwing(swingData):
    currTime = time.time_ns() / 10**9
    startTime = swingData[1] / 10**9
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
"""
def damaged(hurtData, userState):
    currTime = time.time_ns() / 10**9
    startTime = time.time_ns() / 10**9
    elapsedState = currTime - startTime
    if elapsedState < (hurtTime / 3):
        xy = userState["characterStats"]["XY"]
        return (True, (xy[0] - 10, xy[1] - 10))
"""

def findDir(x1,y1,x2,y2):
    if x2 == x1 and y2 == y1:
        return None
    elif x1 == x2:
        if (y2-y1) < 0:
            return math.pi/2
        else:
            return -1*math.pi/2
    elif y1 == y2:
        if (x2 - x1) > 0:
            return 0
        else:
            return math.pi
    return math.atan( (y2 - y1) / (x2 - x1) )

    


def gameStateUpdate(updates, connection, clock, lock):
    print("in game state update")
    updateRes = defaultdict(dict)
    global globalGame
    global SLIME_SPEED
    
    clientKey = updates["playerKey"]
    print("here")
    tempGlobal = {}
    with lock:
        tempGlobal = globalGame.copy()
        print("pasthere")
        if updates["status"] == "CHECK":
            
            print("check update")
            if tempGlobal[clientKey]["isSwinging"]:
                swing = updateSwing(tempGlobal[clientKey]["character"])
                if not swing:
                    tempGlobal[clientKey]["isSwinging"] = False
                    tempGlobal[clientKey]["character"] = "stanceRightMain"
                    updateRes["character"] = "swingRightStart"
                else:
                    tempGlobal[clientKey]["character"] = (swing, tempGlobal[clientKey]["character"][1])
                    updateRes["character"] = tempGlobal[clientKey]["character"][0]
            print("finish check")
            #TODO  add part for "isHurt"
        elif updates["status"] == "INPUT":
            print("ininput")
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
                        if tempGlobal[clientKey]["isSwinging"]:
                            swing = updateSwing(globalGame[clientKey]["character"])
                            if not swing:
                                tempGlobal[clientKey]["isSwinging"] = False
                                tempGlobal[clientKey]["character"] = "stanceRightMain"
                                updateRes["character"] = "swingRightStart"
                            else:
                                tempGlobal[clientKey]["character"] = (swing, tempGlobal[clientKey]["character"][1])
                                updateRes["character"] = tempGlobal[clientKey]["character"][0]
                        else:
                            tempGlobal[clientKey]["isSwinging"] = True
                            tempGlobal[clientKey]["character"] = ("swingRightStart", time.time_ns())
                            updateRes["character"] = tempGlobal[clientKey]["character"][0]
                    
                    elif updates[key] == "damage" and not tempGlobal[clientKey]["isHurt"]:
                        monster = updates["attacker"]
                        if monster == "slimes":
                            tempGlobal[clientKey]["characterStats"]["hp"] -= 10
                        tempGlobal[clientKey]["character"] = ("guts_hurt", time.time_ns())
                        tempGlobal[clientKey]["isHurt"] = True

        print("going into")
        for monster in tempGlobal["monsters"]:
            print("in monsters")
            charCoords = tempGlobal[clientKey]["characterStats"]["XY"]
            if monster == "slimes":
                slimes = tempGlobal["monsters"][monster]
                updateSlimes = [None]*len(slimes)
                for slimeI in range(len(slimes)):
                    print("in move updatess")
                    dir = findDir(slimes[slimeI][0],slimes[slimeI][1],charCoords[0],charCoords[1])
                    if not dir:
                        updateSlimes[slimeI] = slimes[slimeI]
                        continue
                    print(int(SLIME_SPEED*math.cos(dir)))
                    updateSlimes[slimeI] = (int(SLIME_SPEED*math.cos(dir)*(-1)) + slimes[slimeI][0], int(SLIME_SPEED*math.sin(dir)*(-1)) + slimes[slimeI][1], slimes[slimeI][2] )
                tempGlobal["monsters"][monster] = updateSlimes
                updateRes["monsters"][monster] = updateSlimes

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
        
        elif len(tempGlobal["monsters"]) == 0:
            slimes = []
            wave = tempGlobal["wave"] + 1
            for i in range(wave_slimes[wave]):
                slimes.append(random.randint(0, SCREEN_WIDTH - SLIME_WIDTH), random.randint(0, SCREEN_HEIGHT - SLIME_HEIGHT))
            tempGlobal["monsters"]["slimes"] = slimes
            tempGlobal["wave"] = wave
            updateRes["monsters"]["slimes"] = slimes
            updateRes["wave"] = tempGlobal["wave"]



        globalGame = tempGlobal.copy()


        

    
    try:
        print("in sender")
        msg = json.dumps(updateRes)
        print(f"sending: {msg}")

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
   
    
    try:
        port = int(sys.argv[1])
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
            serverSock.bind( (host, port) )
            break
        except:
            print("Binding Error")
            time.sleep(5)

    print(f"connected to {socket.gethostname()} at port {str(port)}")

    try:
        serverSock.listen(5)
        print("listening")
    except:
        print("Error with listen")

    
    # list of clients
    
    
    

    inputs = [serverSock]

    # register server socket for input events
    #poller = select.poll()
    #poller.register(serverSock, select.POLLIN)


    while True:
        for t in threads:
            exc = t.exception()
            if exc:
                print(f"Exception: {exc}")
        try:
            print("in select")
            readable, _, _ = select.select( inputs, [],  [], 1 )
            
            # polls for events
            #events = poller.poll(5000)
            

        except TimeoutError:
            print("waiting")

        #for sock, evt in events:
        for s in readable:
            if s is serverSock:      
            #if evt and select.POLLIN:
                #if sock == serverSock.fileno():
                    # if the socket that generated the event is the server socket, recv message from client
                try:
                    conn, addr = s.accept()
                    print("Accepted new connection")
                except:
                    print("Error accepting connection")
                    continue
                #conn.setblocking(0)
                try:
                    length = conn.recv(8)
                    print("got length:")
                
                    
                except:
                    print("Error receiving req from client")
                    continue
                
                
                

                # decode message to get the length
                print(length.decode("utf-8"))
                length = int(length.decode("utf-8"))
                
                
                # try to receive full message
                
                try:
                    msg_data = conn.recv(length)
                    
                    msg = msg_data.decode('utf-8')
                except Exception as e:
                    print("Issue receiving initialized state")
                    continue
                if msg != "CHECK":
                    print(msg)
                    msg = json.loads(msg)
                
                
                print("inif")
                
                #inputs.append(conn)

                #players[msg["playerKey"]] = msg
                global SLIME_WIDTH
                global SLIME_HEIGHT
                SLIME_WIDTH = msg["dimensions"]["slime"][0]
                SLIME_HEIGHT = msg["dimensions"]["slime"][1]

                res = "GOOD"

                threads.append(gameInit(conn, msg["playerKey"]))
                print("past gameInit")
                
                try:
                    print("on try") 
                    length = msgLength(msg)
                    
                    conn.sendall(length.encode())
                
                    conn.sendall(res.encode())
                    

                
                except:
                    print("Error sending initialize OK")
                    continue

            else:
                print("in correct else")
                try:
                    length = s.recv(8)
                    length = int(length.decode("utf-8"))
                    msg = s.recv(length)
                except:
                    print("error getting msg from connection")
                    continue
                msg = json.loads(msg.decode("utf-8"))
                if msg["status"] == "DEADCONN":
                    NUM_THREADS -= 1
                    
                

def msgLength(msg):
    length = str(len(msg))
    for i in range(8 - len(str(length))):
        length = "0" + length
    return length


if __name__ == "__main__":
    main()
        
        
