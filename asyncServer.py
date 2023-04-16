import socket
import asyncio
import platform
import time
import sys
import select
import json
from concurrent.futures import ThreadPoolExecutor

globalGame = {}
localGames = {}
MOVESPEED = 30
gameClock = -1


def gameInit(client, clientKey):
    pass


def gameStateUpdate(client, updates, serverSock):

    updateRes = {}
    clientKey = msg["clientKey"]
    for key in updates.keys():

        if key == "type":

            if msg[key] == "moveUp":
                
                xy = globalGame[clientKey]["characterStats"]["XY"]
                globalGame[clientKey]["characterStats"]["XY"] = (xy[0], (xy[1] -  MOVESPEED))
                updateRes["characterStats"]["XY"] = (xy[0], (xy[1] -  MOVESPEED))
                

            elif msg[key] == "moveRight":
                
                xy = globalGame[msg["clientKey"]]["characterStats"]["XY"]
                globalGame[clientKey]["characterStats"]["XY"] = ((xy[0] + MOVESPEED), xy[1])
                updateRes["characterStats"]["XY"] = ((xy[0] + MOVESPEED), xy[1])
                

            elif msg[key] == "moveDown":
                xy = globalGame[clientKey]["characterStats"]["XY"]
                globalGame[clientKey]["characterStats"]["XY"] = (xy[0], (xy[1] +  MOVESPEED))
                updateRes["characterStats"]["XY"] = (xy[0], (xy[1] +  MOVESPEED))
                

            elif msg[key] == "moveLeft":
                xy = globalGame[clientKey]["characterStats"]["XY"]
                globalGame[clientKey]["characterStats"]["XY"] = ((xy[0] - MOVESPEED), xy[1])
                updateRes["characterStats"]["XY"] = ((xy[0] - MOVESPEED), xy[1])

                
            elif msg["swing"]:
                globalGame[msg["clientKey"]] = ("swingRightStart", 0)
                updateRes["character"] = "swingRightStart"


        localGames[clientKey] = globalGame

    
    try:
        msg = json.dumps(updateRes)

        serverSock.sendto(msgLength(msg), client)

        serverSock.sendto(msg, client)
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
                
                print("hello")
                print(sock)
                print(serverSock)
                print(evt)
                print(select.POLLIN)
                
                if sock == serverSock.fileno():

                #client, address = sock.accept()
                
                    # if the socket that generated the event is the server socket, recv message from client
                    try:
                        length, client = serverSock.recvfrom(8)
                        clients.append(client)
                    except:
                        print("Error receiving req from client")
                        continue
                    
                    
                    print("client is:")
                    print(client)

                    # decode message to get the length
                    length = int(length.decode())
                    print(length)
                    
                    # try to receive full message
                    # TODO
                    try:
                        msg_data, client = serverSock.recvfrom(length)
                        msg = msg_data.decode('utf-8')
                    except Exception as e:
                        print("Issue receiving initialized state")
                        continue
                    
                    msg = json.loads(msg)
                    print(msg)
                    if client in clients:
                        print("gotmessage")
                        

                        players[msg["playerKey"]] = msg

                        res = "OK"

                        try:
                            length = msgLength(msg)
                            print(length)
                            serverSock.sendto(length.encode(), client)

                            serverSock.sendto(res.encode(), client)

                        
                        except:
                            print("Error sending initialize OK")
                            continue

                    else:
                        print("in correct spot")
                        try:
                            length, client = sock.recvfrom(8)
                            length = int(length.decode())
                            msg, client = sock.recvfrom(length)
                            msg = json.loads(msg.decode())
                            
                        except:
                            print("Issue receiving initialized state")
                            continue
                    
                        gameStateUpdate(msg, client, serverSock)


def msgLength(msg):
    length = str(len(msg))
    for i in range(8 - len(str(length))):
        length = "0" + length
    return length


if __name__ == "__main__":
    main()
        
        
