import socket
import time
import platform

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



sock.settimeout(5)

sock.sendto(bytes("Hello World", "utf-8"), (platform.node(), 8080))

print("finished send")

sock.sendto(bytes("Hello World", "utf-8"), (platform.node(), 8080))

sock.sendto(bytes("Hello World", "utf-8"), (platform.node(), 8080))

sock.sendto(bytes("Hello World", "utf-8"), (platform.node(), 8080))

