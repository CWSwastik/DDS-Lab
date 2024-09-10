# **Labsheet 4: Implementing a Distributed Hash Table (Chord Protocol) using Python**

## **Objective:**

In this lab, you will implement a Chord Distributed Hash Table (DHT) with peer-to-peer communication using Python. The goal is to help you understand how the Chord DHT protocol works, including file distribution, lookups, and peer network management.

---

### **Pre-requisites:**

1. Understanding of peer-to-peer networks.
2. Basics of socket programming in Python.
3. Knowledge of threading for handling multiple connections.
4. Basic hashing techniques and consistent hashing.

---

## Background on Chord Protocol

Chord is a distributed lookup protocol that can be used for peer-to-peer (p2p) file sharing. Chord distributes objects over a dynamic network of nodes, and implements a protocol for finding these objects once they have been placed in the network. Data location is implemented on top of Chord by associating a key with each data item, and storing the key/data item pair at the node to which the key maps. Every node in this network is a server capable of looking up keys for client applications, but also participates as key store. Moreover, chord adapts efficiently as nodes join and leave the system, and can answer queries even if the system is continuously changing. Hence, Chord is a decentralized system in which no particular node is necessarily a performance bottleneck or a single point of failure.

### Keys

Every key (based on the name of a file) inserted into the DHT is hashed to fit into the keyspace supported by the particular implementation of Chord. The keyspace (the range of possible hashes), in this implementation resides between 0 and 2<sup>m</sup>-1 inclusive where m = 10 (denoted by MAX_BITS in the code). So the keyspace is between 0 and 1023.

### 'Ring' of Nodes

Just as each key that is inserted into the DHT has hash value, each node in the system also has a hash value in the keyspace of the DHT. To get this hash value, we simply use the hash of the combination of IP and port, using the same hashing algorithm we use to hash keys inserted into the DHT. Chord orders the node in a circular fashion, in which each node's successor is the node with the next highest hash. The node with the largest hash, however, has the node with the smallest hash as its successor. It is easy to imagine the nodes placed in a ring, where each node's successor is the node after it when following a clockwise rotation.

### Chord Overlay

Chord makes it possible to look up any particular key in log(n) time. Chord employs a clever overlay network that, when the topology of the network is stable, routes requests to the successor of a particular key in log(n) time, where n is the number of nodes in the network. This optimized search for successors is made possible by maintaining a finger table at each node. The number of entries in the finger table is equal to m (denoted by MAX_BITS in the code).

### Failure Resilience

The Chord supports uninformed disconnection/failure of Nodes by continously pinging its successor Node. On detecting failed Node, the Chord will self stabilize. Files in the network are also replicated to the successor Node, so in case a Node goes down while another Node is downloading from it, the latter Node will be redirected to its successor.

![image](https://github.com/user-attachments/assets/3c32f051-6ba4-497a-a2cc-8626639995b3)

## **Architecture Overview:**

Each node in our Chord DHT network will:

- Have a unique **ID** generated from its IP and port using SHA-1 hashing.
- Maintain information about its **predecessor** and **successor**.
- Keep a **finger table** to route requests efficiently within the network.
- Be able to:
  - Upload and download files.
  - Join and leave the network dynamically.
  - Update other peers about its status and successor/predecessor changes.

![image](https://github.com/user-attachments/assets/140690f7-05b8-4065-9e64-fbd206befcc2)

Refer to https://en.wikipedia.org/wiki/Chord_(peer-to-peer) for more details on the Chord protocol.

The lab will guide you through implementing these functionalities step by step.

---

## **Code Breakdown:**

### **Step 0: Setup**

##### **1. Importing Required Libraries**
```python
import socket
import threading
import pickle
import hashlib
import time
import os
from collections import OrderedDict
```
The key libraries used here are:

- `socket`: For communication between nodes.
- `threading`: To handle multiple connections simultaneously.
- `pickle`: For serializing and deserializing data between nodes.
- `hashlib`: To implement the hashing mechanism for node and file identifiers.
##### **2. Defining the Global Variables**
We define some key constants like the IP, Port, and buffer size for data transmission.

```python
IP = "127.0.0.1"
PORT = 2000
buffer = 4096

MAX_BITS = 10        # 10-bit for hash space
MAX_NODES = 2 ** MAX_BITS
```
##### **3. Hash Function**
We create a hash function that takes a string key, hashes it using SHA-1, and then compresses it into a 10-bit integer.

```python
def getHash(key):
    result = hashlib.sha1(key.encode())
    return int(result.hexdigest(), 16) % MAX_NODES
```

### **Step 1: Initializing a Node Class**

```python
class Node:
    def __init__(self, ip, port):
        self.filenameList = []    # List of filenames the node stores
        self.ip = ip              # IP address of the node
        self.port = port          # Port on which the node listens
        self.address = (ip, port) # Address tuple
        self.id = getHash(ip + ":" + str(port))  # Unique Node ID
        self.pred = (ip, port)    # Predecessor of this node
        self.predID = self.id
        self.succ = (ip, port)    # Successor of this node
        self.succID = self.id
        self.fingerTable = OrderedDict() # Finger table for routing

        # Socket for listening to connections
        try:
            self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ServerSocket.bind((IP, PORT))
            self.ServerSocket.listen()
        except socket.error:
            print("Socket error")
```

#### Explanation:

- The constructor initializes the node with its IP and port and assigns it a **unique ID**.
- The **predecessor** and **successor** are initially set to itself (in case it's the only node).
- A **server socket** is created to listen for incoming connections from other nodes and clients.

---

### **Step 2: Listening for Connections**

```python
def listenThread(self):
    while True:
        try:
            connection, address = self.ServerSocket.accept()  # Accept incoming connection
            connection.settimeout(120)  # Timeout after 120 seconds
            threading.Thread(target=self.connectionThread, args=(connection, address)).start()
        except socket.error:
            pass
```

#### Explanation:

- This method runs on a separate thread and continuously listens for new connections.
- For each connection, a new thread is started to handle the connection, allowing multiple peers to connect simultaneously.

---

### **Step 3: Handling Peer Connections**

```python
def connectionThread(self, connection, address):
    rDataList = pickle.loads(connection.recv(buffer))
    connectionType = rDataList[0]

    # Depending on the type of request, different actions are taken
    if connectionType == 0:
        self.joinNode(connection, address, rDataList)
    elif connectionType == 1:
        self.transferFile(connection, address, rDataList)
    elif connectionType == 2:
        connection.sendall(pickle.dumps(self.pred))
    elif connectionType == 3:
        self.lookupID(connection, address, rDataList)
    elif connectionType == 4:
        if rDataList[1] == 1:
            self.updateSucc(rDataList)
        else:
            self.updatePred(rDataList)
    connection.close()
```

#### Explanation:

- **connectionType 0**: A new peer wants to join the network.
- **connectionType 1**: Handles file upload/download.
- **connectionType 2**: Responds with the node's predecessor (for network stabilization).
- **connectionType 3**: Lookup request for a specific file or node.
- **connectionType 4**: Updates the successor/predecessor information.

---

### **Step 4: Handling new node joins**

```python
def joinNode(self, connection, address, rDataList):
    peerIPport = rDataList[1]
    peerID = getHash(peerIPport[0] + ":" + str(peerIPport[1]))
    oldPred = self.pred

    self.pred = peerIPport  # Updating predecessor to the new node
    self.predID = peerID

    # Sending the new node's predecessor back to it
    sDataList = [oldPred]
    connection.sendall(pickle.dumps(sDataList))

    # Update finger table after the new node joins
    self.updateFTable()
    self.updateOtherFTables()
```

#### Explanation:

- When a new node joins, the predecessor of the current node is updated to the joining node.
- The predecessor information is sent back to the new node.
- The finger table is updated to reflect the change.

---

### **Step 5: File Transfer**

```python
def transferFile(self, connection, address, rDataList):
    choice = rDataList[1]
    filename = rDataList[2]
    fileID = getHash(filename)

    if choice == 0:  # Download request
        if filename not in self.filenameList:
            connection.send("NotFound".encode('utf-8'))
        else:
            connection.send("Found".encode('utf-8'))
            self.sendFile(connection, filename)
    elif choice == 1:  # Upload request
        self.filenameList.append(filename)
        self.receiveFile(connection, filename)
```

#### Explanation:

- **Download Request**: The node checks if the file exists in its directory and either sends the file or responds with "NotFound".
- **Upload Request**: The file is received and stored locally, and the filename is added to the node's list.

---

### **Step 6: Lookup ID**

```python
def lookupID(self, connection, address, rDataList):
    keyID = rDataList[1]
    sDataList = []
    # print(self.id, keyID)
    if self.id == keyID:        # Case 0: If keyId at self
        sDataList = [0, self.address]
    elif self.succID == self.id:  # Case 1: If only one node
        sDataList = [0, self.address]
    elif self.id > keyID:       # Case 2: Node id greater than keyId, ask pred
        if self.predID < keyID:   # If pred is higher than key, then self is the node
            sDataList = [0, self.address]
        elif self.predID > self.id:
            sDataList = [0, self.address]
        else:       # Else send the pred back
            sDataList = [1, self.pred]
    else:           # Case 3: node id less than keyId USE fingertable to search
        # IF last node before chord circle completes
        if self.id > self.succID:
            sDataList = [0, self.succ]
        else:
            value = ()
            for key, value in self.fingerTable.items():
                if key >= keyID:
                    break
            value = self.succ
            sDataList = [1, value]
    connection.sendall(pickle.dumps(sDataList))
```

#### Explanation:

This method is responsible for locating the node responsible for a given key. The steps are as follows:

- First, it extracts the key to be looked up (`keyID`) from `rDataList`.
- If the node’s ID matches the keyID, the node is responsible, and the method responds with its address.
- If there’s only one node in the network, the node returns itself as the responsible one.
- If the node’s ID is greater than the keyID, it checks if its predecessor is responsible for the key. If so, it returns its own address; otherwise, it returns its predecessor's address.
- If none of the above conditions are met, the method uses the finger table to forward the lookup request to the appropriate node. It loops through the finger table to find the closest node to the keyID and forwards the lookup request.
- The result is serialized using `pickle` and sent back to the requester.

---

### **Step 7: Updating Successor and Predecessor**

```python
def updateSucc(self, rDataList):
    newSucc = rDataList[2]
    self.succ = newSucc
    self.succID = getHash(newSucc[0] + ":" + str(newSucc[1]))

def updatePred(self, rDataList):
    newPred = rDataList[2]
    self.pred = newPred
    self.predID = getHash(newPred[0] + ":" + str(newPred[1]))
```

#### Explanation:

##### Method: `updateSucc(self, rDataList)`

This method updates the successor of the current node:

- It extracts the new successor’s address from `rDataList`.
- It then calculates the new successor's ID using `getHash()` and updates both the successor address and the successor ID.

##### Method: `updatePred(self, rDataList)`

This method updates the predecessor of the current node:

- It retrieves the new predecessor’s address from `rDataList`.
- Then, it updates the predecessor address and recalculates the predecessor's ID using `getHash()`.

---

### **Step 8: Thread for Pinging**

```python
def start(self):
    # Accepting connections from other threads
    threading.Thread(target=self.listenThread, args=()).start()
    threading.Thread(target=self.pingSucc, args=()).start()
    # In case of connecting to other clients
    while True:
        print("Listening to other clients")
        self.asAClientThread()

def pingSucc(self):
    while True:
        # Ping every 5 seconds
        time.sleep(2)
        # If only one node, no need to ping
        if self.address == self.succ:
            continue
        try:
            #print("Pinging succ", self.succ)
            pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            pSocket.connect(self.succ)
            pSocket.sendall(pickle.dumps([2]))  # Send ping request
            recvPred = pickle.loads(pSocket.recv(buffer))
        except:
            print("\nOffline node dedected!\nStabilizing...")
            # Search for the next succ from the F table
            newSuccFound = False
            value = ()
            for key, value in self.fingerTable.items():
                if value[0] != self.succID:
                    newSuccFound = True
                    break
            if newSuccFound:
                # print("new succ", value[1])
                self.succ = value[1]   # Update your succ to new Succ
                self.succID = getHash(self.succ[0] + ":" + str(self.succ[1]))
                # Inform new succ to update its pred to me now
                pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                pSocket.connect(self.succ)
                pSocket.sendall(pickle.dumps([4, 0, self.address]))
                pSocket.close()
            else:       # In case Im only node left
                self.pred = self.address            # Predecessor of this node
                self.predID = self.id
                self.succ = self.address            # Successor to this node
                self.succID = self.id
            self.updateFTable()
            self.updateOtherFTables()
            self.printMenu()
```

#### Explanation:

##### Method: `start(self)`

This method starts the node by launching threads for listening and pinging:

- It spawns two threads—one for listening to incoming connections (`listenThread`) and one for pinging the successor periodically (`pingSucc`).
- The main loop waits for user input and calls `asAClientThread()` to handle outgoing connections.

##### Method: `pingSucc(self)`

This method periodically pings the successor node:

- It checks if there is more than one node in the network. If not, no ping is necessary.
- It attempts to ping the successor every 2 seconds.
- If the ping fails, it detects that the successor is offline and stabilizes the network by selecting the next available node from the finger table as the new successor. If no other nodes are available, the node becomes both the predecessor and successor to itself.
- The method then updates the finger table and notifies other nodes of the changes.

---

### **Step 9: Handling user input**

```python
    def asAClientThread(self):
        # Printing options
        self.printMenu()
        userChoice = input()
        if userChoice == "1":
            ip = input("Enter IP to connect: ")
            port = input("Enter port: ")
            self.sendJoinRequest(ip, int(port))
        elif userChoice == "2":
            self.leaveNetwork()
        elif userChoice == "3":
            filename = input("Enter filename: ")
            fileID = getHash(filename)
            recvIPport = self.getSuccessor(self.succ, fileID)
            self.uploadFile(filename, recvIPport, True)
        elif userChoice == "4":
            filename = input("Enter filename: ")
            self.downloadFile(filename)
        elif userChoice == "5":
            self.printFTable()
        elif userChoice == "6":
            print("My ID:", self.id, "Predecessor:", self.predID, "Successor:", self.succID)
```

#### Explanation:

This method handles outgoing connections based on user input:

- It prints a menu of options and waits for the user to choose an action.
- Depending on the choice, the node can either join the network, leave the network, upload/download files, or print the finger table and other status information.

---

### **Step 10: Joining and Leaving the Network**

```python
def sendJoinRequest(self, ip, port):
    try:
        recvIPPort = self.getSuccessor((ip, port), self.id)
        peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peerSocket.connect(recvIPPort)
        sDataList = [0, self.address]

        peerSocket.sendall(pickle.dumps(sDataList))     # Sending self peer address to add to network
        rDataList = pickle.loads(peerSocket.recv(buffer))   # Receiving new pred
        # Updating pred and succ
        # print('before', self.predID, self.succID)
        self.pred = rDataList[0]
        self.predID = getHash(self.pred[0] + ":" + str(self.pred[1]))
        self.succ = recvIPPort
        self.succID = getHash(recvIPPort[0] + ":" + str(recvIPPort[1]))
        # print('after', self.predID, self.succID)
        # Tell pred to update its successor which is now me
        sDataList = [4, 1, self.address]
        pSocket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pSocket2.connect(self.pred)
        pSocket2.sendall(pickle.dumps(sDataList))
        pSocket2.close()
        peerSocket.close()
    except socket.error:
        print("Socket error. Recheck IP/Port.")

def leaveNetwork(self):
    # First inform my succ to update its pred
    pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pSocket.connect(self.succ)
    pSocket.sendall(pickle.dumps([4, 0, self.pred]))
    pSocket.close()
    # Then inform my pred to update its succ
    pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pSocket.connect(self.pred)
    pSocket.sendall(pickle.dumps([4, 1, self.succ]))
    pSocket.close()
    print("I had files:", self.filenameList)
    # And also replicating its files to succ as a client
    print("Replicating files to other nodes before leaving")
    for filename in self.filenameList:
        pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pSocket.connect(self.succ)
        sDataList = [1, 1, filename]
        pSocket.sendall(pickle.dumps(sDataList))
        with open(filename, 'rb') as file:
            # Getting back confirmation
            pSocket.recv(buffer)
            self.sendFile(pSocket, filename)
            pSocket.close()
            print("File replicated")
        pSocket.close()

    self.updateOtherFTables()   # Telling others to update their f tables

    self.pred = (self.ip, self.port)    # Chaning the pointers to default
    self.predID = self.id
    self.succ = (self.ip, self.port)
    self.succID = self.id
    self.fingerTable.clear()
    print(self.address, "has left the network")
```

#### Explanation:

##### Method: `sendJoinRequest(self, ip, port)`

This method sends a request to join an existing network:

- It connects to a node at the specified IP and port and requests the successor for its own ID.
- Once the successor is found, it updates the current node’s predecessor and successor IDs.
- It then informs the predecessor to update its successor to point to this node.

##### Method: `leaveNetwork(self)`

This method handles the process of leaving the network:

- It informs both its successor and predecessor to update their links to bypass the current node.
- Before leaving, it replicates its files to the successor.
- Finally, it clears the finger table and prints a message indicating that the node has left the network.

---

### **Step 11: Uploading and Downloading Files**

```python
def uploadFile(self, filename, recvIPport, replicate):
    print("Uploading file", filename)
    # If not found send lookup request to get peer to upload file
    sDataList = [1]
    if replicate:
        sDataList.append(1)
    else:
        sDataList.append(-1)
    try:
        # Before doing anything check if you have the file or not
        file = open(filename, 'rb')
        file.close()
        sDataList = sDataList + [filename]
        cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cSocket.connect(recvIPport)
        cSocket.sendall(pickle.dumps(sDataList))
        self.sendFile(cSocket, filename)
        cSocket.close()
        print("File uploaded")
    except IOError:
        print("File not in directory")
    except socket.error:
        print("Error in uploading file")

def downloadFile(self, filename):
    print("Downloading file", filename)
    fileID = getHash(filename)
    # First finding node with the file
    recvIPport = self.getSuccessor(self.succ, fileID)
    sDataList = [1, 0, filename]
    cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cSocket.connect(recvIPport)
    cSocket.sendall(pickle.dumps(sDataList))
    # Receiving confirmation if file found or not
    fileData = cSocket.recv(buffer)
    if fileData == b"NotFound":
        print("File not found:", filename)
    else:
        print("Receiving file:", filename)
        self.receiveFile(cSocket, filename)


def getSuccessor(self, address, keyID):
    rDataList = [1, address]      # Deafult values to run while loop
    recvIPPort = rDataList[1]
    while rDataList[0] == 1:
        peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            peerSocket.connect(recvIPPort)
            # Send continous lookup requests until required peer ID
            sDataList = [3, keyID]
            peerSocket.sendall(pickle.dumps(sDataList))
            # Do continous lookup until you get your postion (0)
            rDataList = pickle.loads(peerSocket.recv(buffer))
            recvIPPort = rDataList[1]
            peerSocket.close()
        except socket.error:
            print("Connection denied while getting Successor")
    # print(rDataList)
    return recvIPPort
```

#### Explanation

##### Method: `uploadFile(self, filename, recvIPport, replicate)`

This method uploads a file to the specified node:

- It first checks if the file exists locally.
- If the file is found, it connects to the target node (successor) and sends the file data.
- If the `replicate` flag is set, the file is replicated across nodes.

##### Method: `downloadFile(self, filename)`

This method downloads a file from the network:

- It computes the file ID and searches for the node responsible for that file by querying the network.
- If the file is found, it downloads the file in chunks and saves it locally.

##### Method: `getSuccessor(self, address, keyID)`

This method recursively queries the network to find the successor for a given key:

- It repeatedly sends lookup requests to the network nodes until it finds the node responsible for the key.
- The method returns the IP and port of the successor node.

---

### **Step 12: Updating Finger Tables**

```python
def updateFTable(self):
    for i in range(MAX_BITS):
        entryId = (self.id + (2 ** i)) % MAX_NODES
        # If only one node in network
        if self.succ == self.address:
            self.fingerTable[entryId] = (self.id, self.address)
            continue
        # If multiple nodes in network, we find succ for each entryID
        recvIPPort = self.getSuccessor(self.succ, entryId)
        recvId = getHash(recvIPPort[0] + ":" + str(recvIPPort[1]))
        self.fingerTable[entryId] = (recvId, recvIPPort)
    # self.printFTable()

def updateOtherFTables(self):
    here = self.succ
    while True:
        if here == self.address:
            break
        pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            pSocket.connect(here)  # Connecting to server
            pSocket.sendall(pickle.dumps([5]))
            here = pickle.loads(pSocket.recv(buffer))
            pSocket.close()
            if here == self.succ:
                break
        except socket.error:
            print("Connection denied")
```

#### Explanation:

##### Method: `updateFTable(self)`

This method updates the finger table entries of the current node:

- For each entry in the finger table, it computes the responsible node for the corresponding ID.
- It then updates the finger table by finding and storing the successor for each entry ID.

##### Method: `updateOtherFTables(self)`

This method updates the finger tables of other nodes in the network:

- It iterates over all nodes in the network and sends a request to each node to update its finger table.
- The method stops once all nodes have been updated.

---

### **Step 13: Sending and Receiving files over the socket connection**

```python
def sendFile(self, connection, filename):
    print("Sending file:", filename)
    try:
        # Reading file data size
        with open(filename, 'rb') as file:
            data = file.read()
            print("File size:", len(data))
            fileSize = len(data)
    except FileNotFoundError:
        print("File not found")
    try:
        with open(filename, 'rb') as file:
            #connection.send(pickle.dumps(fileSize))
            while True:
                fileData = file.read(buffer)
                time.sleep(0.001)
                #print(fileData)
                if not fileData:
                    break
                connection.sendall(fileData)
    except FileNotFoundError:
        pass#print("File not found in directory")
    print("File sent")

def receiveFile(self, connection, filename):
    # Receiving file in parts
    # If file already in directory
    fileAlready = False
    try:
        with open(filename, 'rb') as file:
            data = file.read()
            size = len(data)
            if size == 0:
                print("Retransmission request sent")
                fileAlready = False
            else:
                print("File already present")
                fileAlready = True
            return
    except FileNotFoundError:
        pass
    # receiving file size
    #fileSize = pickle.loads(connection.recv(buffer))
    #print("File Size", fileSize)
    if not fileAlready:
        totalData = b''
        recvSize = 0
        try:
            with open(filename, 'wb') as file:
                while True:
                    fileData = connection.recv(buffer)
                    #print(fileData)
                    recvSize += len(fileData)
                    #print(recvSize)
                    if not fileData:
                        break
                    totalData += fileData
                file.write(totalData)
        except ConnectionResetError:
            print("Data transfer interupted\nWaiting for system to stabilize")
            print("Trying again in 10 seconds")
            time.sleep(5)
            os.remove(filename)
            time.sleep(5)
            self.downloadFile(filename)
            # connection.send(pickle.dumps(True))
```

#### Explanation

##### Method: `sendFile(self, connection, filename)`

This method handles sending a file over a socket connection:

- It reads the file from the local filesystem and sends its data to the recipient in chunks.
- Once all data is sent, it prints a confirmation message.

##### Method: `receiveFile(self, connection, filename)`

This method handles receiving a file over a socket connection:

- It first checks if the file already exists locally. If not, it starts receiving data from the sender in chunks.
- The received data is written to a file on the local filesystem.

---

### **Step 14: Printing info**

```python
    def printMenu(self):
        print("\n1. Join Network\n2. Leave Network\n3. Upload File\n4. Download File")
        print("5. Print Finger Table\n6. Print my predecessor and successor")

    def printFTable(self):
        print("Printing F Table")
        for key, value in self.fingerTable.items():
            print("KeyID:", key, "Value", value)
```

#### Explanation

##### Method: `printMenu(self)`

This method prints the menu of available options for the user to choose from.

##### Method: `printFTable(self)`

This method prints the current node's finger table, showing each keyID and its corresponding node.

---

### **Step 15: Running the Node**

The following code is responsible for initializing and running a node in the DHT:

- The IP and port are passed as command-line arguments, otherwise default values are used.

```python
if len(sys.argv) < 3:
    print("Arguments not supplied (Defaults used)")
else:
    IP = sys.argv[1]
    PORT = int(sys.argv[2])

myNode = Node(IP, PORT)
print("My ID is:", myNode.id)
myNode.start()
myNode.ServerSocket.close()
```

---

### **Lab Tasks:**

**Task 1**: Run two nodes and observe the interaction as they form a peer-to-peer network.
```bash
python node.py 127.0.0.1 [PORT]
```

> **Note:** A Node can have the same IP as another, but not the same IP **and** same Port.

**Task 2**: Upload a file from one node and download it from another node.

> **Note:** Make sure to run each node from **different directories** when uploading and downloading files. If both nodes are in the same directory, the file might already exist, preventing the download. To avoid this, duplicate the `node.py` file into separate directories and run the nodes from there.

**Task 3**: Add more nodes to the network and observe how the finger table changes.

**Task 4**: Disconnect a node and observe how the network stabilizes.
