import socket
import platform
import time
import select

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((platform.node(), 8080))

sock.settimeout(5)

msg, client = sock.recvfrom(11)

print(msg.decode())

poller = select.poll()

poller.register(sock, select.POLLIN)


while True:
    evts = poller.poll(5000)
    for s, evt in evts:
        if evt and select.POLLIN:
            if s == sock.fileno():
                msg, client = sock.recvfrom(11)
                print(msg.decode())