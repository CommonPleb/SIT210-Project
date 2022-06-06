from socket import *

ServerPort = 9999

# Creates initial variables
weightThreshold = 0
hour = 0
currentMode = 0
night = 0
nightStart = 0
nightEnd = 0

# Creates the UDP socket required
ServerSocket = socket(AF_INET, SOCK_DGRAM)

# Assigns the port number of ServerPort to this program
ServerSocket.bind(("", ServerPort))

while True:
    print("Waiting for client to request")
    ClientQuery, ClientAddress = ServerSocket.recvfrom(2048)
    try:
        ClientQuery = ClientQuery.decode()
        ReceivedFields = ClientQuery.split(";")
        if len(ReceivedFields) == 4:
            currentMode, hour, weightThreshold, night = ReceivedFields[0], ReceivedFields[1], ReceivedFields[2], ReceivedFields[3]
        elif len(ReceivedFields) == 6:
            currentMode, hour, weightThreshold, night, nightStart, nightEnd = ReceivedFields[0], ReceivedFields[1], ReceivedFields[2], ReceivedFields[3], ReceivedFields[4], ReceivedFields[5]
        else:
            response = "{};{};{};{};{};{}".format(currentMode, hour, weightThreshold, night, nightStart, nightEnd)
            ServerSocket.sendto(response.encode(), ClientAddress)
    except:
        print("Invalid request")
