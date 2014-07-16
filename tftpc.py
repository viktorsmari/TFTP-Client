#Usage : 'python tftpc.py localhost read(write) file.txt 69'
import sys
import socket
import os
import time
 
total = len(sys.argv)
 
try:    #make sure we get required arguments
    hostname = sys.argv[1]
    myCommand = sys.argv[2]
    myFile = sys.argv[3]
 
    if total > 4: # Check if port number is given as argument
        myPort = int(sys.argv[4])
    else:
        myPort = 69
except:
    print "-- Error, expected at least 4 arguments, got: ",total
    sys.exit()

########################## Functions ###########################
def sendFirstPacket(myOpcode,myFile):
    MESSAGE = bytearray()
    MESSAGE.append(0)
    MESSAGE.append(myOpcode)
    MESSAGE += myFile
    MESSAGE.append(0)
    MESSAGE += 'octet'
    MESSAGE.append(0)
    s.sendto(MESSAGE,(hostname,myPort)) #original send
    
def sendAckPacket(blockNumber):
    MESSAGE = bytearray()
    MESSAGE.append(0)
    MESSAGE.append(4) # Ack
    MESSAGE.append(0)
    MESSAGE.append(blockNumber)
    s.sendto(MESSAGE,(hostname,newPort))
    
def sendDataPacket(blockNumber,dataSend):
    MESSAGE = bytearray()
    MESSAGE.append(0)
    MESSAGE.append(3) # Data
    MESSAGE.append(0)
    MESSAGE.append(blockNumber)
    MESSAGE += dataSend
    s.sendto(MESSAGE,(hostname,newPort))

#def sendErrorPacket()
###############################################################

if myCommand == "skrifa" :
    if not os.path.exists(myFile):  # File not found client side
        print "File not found on client: %s" % (myFile)
        sys.exit()
    myOpcode = 2
 
elif myCommand == "lesa" :
    myOpcode = 1

else:
    print "-- Wrong command. Expected 'skrifa' or 'lesa' "
    sys.exit()
 
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # SOCK_DGRAM = UDP socket

sendFirstPacket(myOpcode,myFile)    # Initial packet sent!

blockNumber = 0     # debug

while 1:
    allData = s.recvfrom(516)
    data = allData[0][4:]
    newPort = allData[1][1]
    opcode = repr(allData[0])[8:9]

    if opcode == '3':   # If first received package is 3 DATA, write localfile
        if file.closed:
            file = open(myFile,'w+')
            #file = open(myFile,'a')
        file.write(data)
  
        blockNumber = ord((allData[0])[3:4])
        sendAckPacket(blockNumber)

        if len(data) < 512:
            file.close()
            break


    elif opcode == '4': # Server is ready to receive our file!

        file = open(myFile, 'r')

        extraPakki = False
        if len(myFile) % 512 == 0:
            extraPakki = True

        dataSend = file.read(512)

# ERROR --> Allows us only to receive files of size 51 kb. blockNumber 123?
#        blockNumber = int(repr(allData[0])[15:17]) + 1   # Old version
        blockNumber = ord((allData[0])[3:4]) + 1

        ##############################################
        while len(dataSend) > 0 or extraPakki:
            sendDataPacket(blockNumber,dataSend)

            if len(dataSend) == 0 and extraPakki:
                extraPakki = False

            ackData = s.recvfrom(516)

            if blockNumber == ord((ackData[0])[3:4]):
                blockNumber +=1
                dataSend = file.read(512)
        ##############################################

        file.close()
        time.sleep(.3)  # wait a little bit for the last ack packet.
        break

    elif opcode == "5":
        errorCode = repr(allData[0])[16:17]
        print "Error code %s, %s" % (errorCode, data)
        break

print "---- Closing ----"
s.close()







