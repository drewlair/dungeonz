<div align="center">
  
# dungeonz
### A Distributed Hack and Slash Game developed in Python
### By Drew Lair and Michael Bai
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

Game Demo
```

youtube url: https://www.youtube.com/watch?v=iKZvovviQ_o

```

## Setup

### Check if you have Python installed
```
python --version
```
### If you are not given a version number, run the command
```
pip install python
```
(or)
```
pip3 install python
```
### If you do not have pygame installed run the command
```
pip install python
```
(or)
```
pip3 install pygame
```

## Clone the repository

```
git clone git@github.com:drewlair/dungeonz.git
```

### Create two terminal windows
#### In the First window, run
```
python dungeonz_server.py <port>
```
where <port> is the number corresponding to an open port on your device
If the port you enter is not open, the server will scan for another open port to use
### You should see an output to the terminal that looks similar to this:
```
connected to <hostname> on port <port>
```
Both <hostname> and <port> are important for the next step
## Go to your second terminal window and run the following command:
```
python dungeonz_client.py <hostname> <port#>
```
Use the <hostname> and <port> tokens from the first terminal to fill in these arguments.
The command needs these arguments to tell the client where the server is to connect to.
## The game should load a new window and you can start to play!
<img width="1005" alt="Screen Shot 2023-11-01 at 12 40 20 AM" src="https://github.com/drewlair/dungeonz/assets/90236451/5bbd6158-e818-49a1-854c-10eb45a8eb60">

## Exit
### To stop the game at any time, go into the window with the client command running and do Ctrl-c
The same method will stop the server if done in the server window
### The game window will close whenever a player loses the game or wins the game, or stops the client/server, otherwise it will stay open indefinitely

## Controls
W - Up

A - Left

S - Down

D - Right

spacebar - Swing

## Multiplayer
### To play with multiple players repeat the same process on a separate computer except only open one window and run the client command with the same <hostname> and <port> as the first player.
This should allow the client to connect over wifi and play on the same game if both players are running the client scripts concurrently.

### If you have questions about the game functionality or ideas to make it better, feel free to email me at drewlair41@gmail.com

Have fun!
