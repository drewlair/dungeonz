import socket
import asyncio
import platform
import time
import sys
import select
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

globalGame = {}
localGames = {}
MOVESPEED = 30
gameClock = -1
clientClock = {}
swingTime = 0.5


def gameInit(client, playerKey):

    globalGame[playerKey] = {}
    globalGame[playerKey]["background"] = "background_surf"
    globalGame[playerKey]["characterStats"] = {"hp": 100, "gold": 0, "xp": 0, "lvl": 0, "XY": (100, 100)}
    globalGame[playerKey]["character"] = "stanceRightMain"
    globalGame[playerKey]["isSwinging"] = False
    globalGame[playerKey]["monsters"] = {}
    clientClock[playerKey] = time.time_ns()


    return

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


    


def gameStateUpdate(updates, client, serverSock):
    print("in game state update")
    updateRes = defaultdict(dict)
    
    clientKey = updates["playerKey"]
    if updates["status"] == "CHECK":
        
        print("check update")
        if globalGame[clientKey]["isSwinging"]:
            swing = updateSwing(globalGame[clientKey]["character"])
            if not swing:
                globalGame[clientKey]["isSwinging"] = False
                globalGame[clientKey]["character"] = "stanceRightMain"
                updateRes["character"] = "swingRightStart"
            else:
                globalGame[clientKey]["character"] = (swing, globalGame[clientKey]["character"][1])
                updateRes["character"] = globalGame[clientKey]["character"][0]
    elif updates["status"] == "INPUT":
        for key in updates.keys():

            if key == "type":

                if updates[key] == "moveUp":
                    
                    xy = globalGame[clientKey]["characterStats"]["XY"]
                    globalGame[clientKey]["characterStats"]["XY"] = (xy[0], (xy[1] -  MOVESPEED))
                    updateRes["characterStats"]["XY"] = (xy[0], (xy[1] -  MOVESPEED))
                    

                elif updates[key] == "moveRight":
                    print(globalGame)
                    xy = globalGame[clientKey]["characterStats"]["XY"]
                    globalGame[clientKey]["characterStats"]["XY"] = ((xy[0] + MOVESPEED), xy[1])
                    updateRes["characterStats"]["XY"] = ((xy[0] + MOVESPEED), xy[1])
                    

                elif updates[key] == "moveDown":
                    xy = globalGame[clientKey]["characterStats"]["XY"]
                    globalGame[clientKey]["characterStats"]["XY"] = (xy[0], (xy[1] +  MOVESPEED))
                    updateRes["characterStats"]["XY"] = (xy[0], (xy[1] +  MOVESPEED))
                    

                elif updates[key] == "moveLeft":
                    xy = globalGame[clientKey]["characterStats"]["XY"]
                    globalGame[clientKey]["characterStats"]["XY"] = ((xy[0] - MOVESPEED), xy[1])
                    updateRes["characterStats"]["XY"] = ((xy[0] - MOVESPEED), xy[1])

                    
                elif updates[key] == "swing":
                    if globalGame[clientKey]["isSwinging"]:
                        swing = updateSwing(globalGame[clientKey]["character"])
                        if not swing:
                            globalGame[clientKey]["isSwinging"] = False
                            globalGame[clientKey]["character"] = "stanceRightMain"
                            updateRes["character"] = "swingRightStart"
                        else:
                            globalGame[clientKey]["character"] = (swing, globalGame[clientKey]["character"][1])
                            updateRes["character"] = globalGame[clientKey]["character"][0]
                    else:
                        globalGame[clientKey]["isSwinging"] = True
                        globalGame[clientKey]["character"] = ("swingRightStart", time.time_ns())
                        updateRes["character"] = globalGame[clientKey]["character"][0]


        

    
    try:
        msg = json.dumps(updateRes)

        serverSock.sendto((msgLength(msg)).encode("utf-8"), client)

        serverSock.sendto(msg.encode("utf-8"), client)
    except:
        print("problem sending data from thread to client")

    pass

def main():

    players = {}

    MOVESPEED = 30
    SWINGFRAMES = 6
    MAX_THREADS = 4
    NUM_THREADS = 0

    try:
        port = int(sys.argv[1])
    except:
        print("Must enter port listening on")
        sys.exit()

    # create UDP socket with timeout of 1 second 
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSock.settimeout(1)

    # tries to bind the socket to the port with a 5 second delay if errors
    while True:
        try:
            serverSock.bind( (socket.gethostname(), port) )
            break
        except:
            print("Binding Error")
            time.sleep(5)

        print(f"connected to {socket.gethostname()} at port {str(port)}")

    
    # list of clients
    clients = []
    
    clientHandler = ThreadPoolExecutor(MAX_THREADS)

    # register server socket for input events
    poller = select.poll()
    poller.register(serverSock, select.POLLIN)


    while True:
        try:
            
            #readable, _, _ = select.select( inputs, [],  [], 1 )
            
            # polls for events
            events = poller.poll(5000)
            

        except TimeoutError:
            print("waiting")

        for sock, evt in events:
            if evt and select.POLLIN:
                
                
                
                if sock == serverSock.fileno():

                
                
                    # if the socket that generated the event is the server socket, recv message from client
                    try:
                        length, client = serverSock.recvfrom(8)
                    
                        
                    except:
                        print("Error receiving req from client")
                        continue
                    
                    
                   

                    # decode message to get the length
                    length = int(length.decode())
                    
                    
                    # try to receive full message
                    
                    try:
                        msg_data, client = serverSock.recvfrom(length)
                      
                        msg = msg_data.decode('utf-8')
                    except Exception as e:
                        print("Issue receiving initialized state")
                        continue
                    if msg != "CHECK":
                        msg = json.loads(msg)
                    
                    if client not in clients:
                        
                        clients.append(client)

                        players[msg["playerKey"]] = msg

                        res = "GOOD"

                        gameInit(client, msg["playerKey"])

                        try:
                            
                            length = msgLength(msg)
                         
                            serverSock.sendto(length.encode(), client)
                      
                            serverSock.sendto(res.encode(), client)
                   

                        
                        except:
                            print("Error sending initialize OK")
                            continue

                    else:
                      
                    
                        gameStateUpdate(msg, client, serverSock)


def msgLength(msg):
    length = str(len(msg))
    for i in range(8 - len(str(length))):
        length = "0" + length
    return length


if __name__ == "__main__":
    main()
        
        
