# Battleship Game Instructions

### Both the server and client are started using provided shell scripts:

    startServer.sh  launches the server

    startClient.sh  launches the client

These scripts must be run from the directory containing the Python source code.

### Requirements
- Python 3 installed
- numpy library installed (pip install numpy)


### Start the Server

Open a terminal window, navigate to the project directory, and run:

    ./startServer.sh

By default, the server listens on port 5050. You can pass a different port as a command-line argument, for example <code>./startServer.sh 5051</code>

### Start the Client

Open another terminal window, navigate to the same project directory, and run:

    ./startClient.sh

By default, the client connects to localhost on port 5050. You can pass a different host and port as command-line arguments, for example <code>./startClient.sh localhost 5051</code>

### Optional: Auto Mode (Testing Only)
To make the client automatically fire random shots (useful for testing), run:

    ./startClient.sh --auto

In auto mode, the client does not require manual input.