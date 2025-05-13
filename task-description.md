# COSC340 Assessment 3 - Programming Assignment

## Aims
- Develop a secure networked application using TCP sockets
- Identify security/privacy/trust issues and implement solutions to mitigate them
- Develop a protocol to allow secure transfer of data

## Introduction
The game you developed in the previous assignment places a great deal of trust on the server. For example, there is nothing preventing the server from repositioning ships after the client's first "shot" to ensure that the first "shot" is never a "hit". Further, the protocol is susceptible to MITM attacks. Your task in this assignment is to identify security/privacy/trust issues in your solution to the previous assignment and implement a system that prevents such abuses.

## Protocol
You are free to base your protocol on the previous version, but are given free reign to modify the protocol in any way you choose.

## Functionality
Your system should provide as much of the following functionality as possible:

- Encrypt all communication between client and server using Transport Layer Security
- Ensure neither side can cheat
- Any other security/privacy/trust enhancements you can think of


## Details
You may use any programming language and libraries that run on turing.une.edu.au to implement your solution. Your solution should be submitted through myLearn in a single .zip or .tgz file which, along with your source code and any instructions to compile your code, should also include two shell scripts:

1. startServer.sh which takes a port number as its only command-line parameter and attempts to start a server on that port. This script should compile your server code (if required) before attempting to execute it. If the server is unable to be started (perhaps because that port is already in use), your program should exit with an appropriate error message.

2. startClient.sh which takes a host name as its first command-line parameter and a port number as its second command-line parameter and attempts to connect to the server with the given host name and port number. This script should compile your client code (if required) before attempting to execute it. If the client is unable to connect, it should exit with an appropriate error message.

Your submission should also include two documents. The first, in a PDF file named protocol.pdf, should describe the protocol used by your system in enough detail to allow another developer to be able to implement your protocol by looking only at this document. The second, in a PDF file named report.pdf, should describe the security/privacy/trust issues that were present in your previous assignment submission, your approaches to mitigating those issues (which may refer to your protocol document), and how those approaches work (including any limitations).

*Note that program specifications are not always clear. If you are uncertain about any aspect, you are typically better off asking than making assumptions. Please use the appropriate discussion forum to ask for clarification, if required.*

| Marking | Scheme |
| --- | --- |
| **Criteria** | **Weighting** |
Documented protocol (protocol.pdf)	| 20%
Report describing issues and solutions (report.pdf)	| 30%
Shell scripts	| 3%
Host and ports configurable	| 2%
Client can connect and communicate with server	| 5%
Server implements protocol correctly	| 10%
Client implements protocol correctly	| 10%
Errors handled correctly	| 5%
Client user interface	| 5%
Programming documentation and comments	| 10%