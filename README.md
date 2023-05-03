Dungeonz

How to run:
1. Create two sperate terminals in the "dungeonz" main directory.
2. For the first terminal, run the command "python dungeonz_server.py <port#>".
  - fill in <port#> with the port you want your server.
  - ensure that you are connected to a server with no private firewall (ex: ND-guest). 
  - if there is a binding error, try using a different port (8080 or 1024 for example are usually open ports for users on many devices).
3. If the server connects successfully, it should print out a statement: "connected to <hostname> on port <port#>".
  - Make sure you are connected to a network that allows for user programs to send socket messages before running the program.
4. In the second terminal, type the command: "python dungeonz_client.py <hostname> <port#>"
  - fill in <hostname> with the name given by the server stdout message in 3.
5. If connected successfully, the client should be able to start pygame on your local device.
  - if you do not have pygame installed you will need to install pygame. 
  - You can try "pip install pygame" or "brew install pygame" if you have homebrew installed. Otherwise, the client will not run properly.
6. To exit the game, either click the red x at the top left of the pygame window or run "Ctrl-C" in the terminal running the client program.
7. To connect multiplayer, on another device on the same network, run the exact same command in step 4. 
  - It is very important that the <hostname> and <port#> are the same as given by the server, whcih must still be running. 
8. To stop the server, run "Ctrl-C" in the terminal running the program.

How to play:
W - up
A - left
S - down
D - right
Space - swing sword

If you have questions about the game functionality or ideas to make it better, feel free to email me at drewlair41@gmail.com

Have fun!
