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
MOVESPEED = 30
gameClock = -1
clientClock = {}
swingTime = 0.5
NUM_THREADS = 0
MAX_THREADS = 4
threads = []
executor = ThreadPoolExecutor(MAX_THREADS)

def playerHandler(sock, host, port):

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
    
    localGame = {}
    sock.settimeout(1)
    while True:
        print("inwhile")
        
        try:
            length = conn.recv(8)
        except TimeoutError:
            print("threadWaiting")
            continue
        length = int(length.decode("utf-8"))
        try:
            msg = conn.recv(length)
        except TimeoutError:
            print("Lenght received but not msg")
            continue

        msg = json.loads(msg.decode())

        localGame = gameStateUpdate(msg, conn)

    



    pass
def gameInit(connection, playerKey):

    globalGame[playerKey] = {}
    globalGame[playerKey]["background"] = "background_surf"
    globalGame[playerKey]["characterStats"] = {"hp": 100, "gold": 0, "xp": 0, "lvl": 0, "XY": (100, 100)}
    globalGame[playerKey]["character"] = "stanceRightMain"
    globalGame[playerKey]["isSwinging"] = False
    globalGame[playerKey]["monsters"] = {}
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

    args = [threadSock, threadHost, threadPort]
    executor.submit(playerHandler, *args)
    NUM_THREADS += 1


    return True

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


    


def gameStateUpdate(updates, connection):
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
   

    try:
        port = int(sys.argv[1])
    except:
        print("Must enter port listening on")
        sys.exit()

    # create UDP socket with timeout of 1 second 
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSock.settimeout(5)

    # tries to bind the socket to the port with a 5 second delay if errors
    host = platform.node()
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

                players[msg["playerKey"]] = msg

                res = "GOOD"

                gameInit(conn, msg["playerKey"])
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
        
        
