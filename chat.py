#    15-112: Principles of Programming and Computer Science
#    HW07 Programming: Implementing a Chat Client
#    Name      : Ulan Seitkaliyev
#    AndrewID  : useitkal

#    File Created: 10/20/2020
#    Modification History: 10/26/2020
import socket
import math
BLCK_SIZE = 512
CHNK_SIZE = 16
CHNK_ITEM_SIZE = 32
SZ_BLOCK_SZ = 6
RECV_SIZE = 1024

# generates block from given password and challenge


def getBlock(p, c):
    md = ""
    n, m = len(p), len(c)
    l = n+m   # length of string p..pc..c1
    times = BLCK_SIZE // l
    # multiply strs pc1 available time and ljust 0 and add l-1
    notFullBlock = p+c+"1"
    notFullBlock += (p+c)*(times-1)
    digitLen = len(str(n+m))
    block = notFullBlock.ljust(BLCK_SIZE-digitLen, "0") + str(n+m)
    return block

# gets sum of ord's in each chunck


def getChuncks(block):
    m = [0] * CHNK_SIZE
    for i in range(CHNK_SIZE):
        # count sum of first 32 bits
        m[i] = sum([ord(c) for c in block[0:CHNK_ITEM_SIZE]])
        block = block[CHNK_ITEM_SIZE:]   # slice up the first 32 bits
    return m

# Implements the given md5 helper function


def leftrotate(x, c):
    return (x << c) & 0xFFFFFFFF | (x >> (32-c) & 0x7FFFFFFF >> (32-c))


# Implements the given md5 functionality
def processChuncks(m):
    s = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
         5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20,
         4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
         6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21]
    k = [0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf,
         0x4787c62a, 0xa8304613, 0xfd469501, 0x698098d8, 0x8b44f7af,
         0xffff5bb1, 0x895cd7be, 0x6b901122, 0xfd987193, 0xa679438e,
         0x49b40821, 0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
         0xd62f105d, 0x2441453, 0xd8a1e681, 0xe7d3fbc8, 0x21e1cde6,
         0xc33707d6, 0xf4d50d87, 0x455a14ed, 0xa9e3e905, 0xfcefa3f8,
         0x676f02d9, 0x8d2a4c8a, 0xfffa3942, 0x8771f681, 0x6d9d6122,
         0xfde5380c, 0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
         0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x4881d05, 0xd9d4d039,
         0xe6db99e5, 0x1fa27cf8, 0xc4ac5665, 0xf4292244, 0x432aff97,
         0xab9423a7, 0xfc93a039, 0x655b59c3, 0x8f0ccc92, 0xffeff47d,
         0x85845dd1, 0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
         0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391]
    # add precalc later

    A = 0x67452301
    B = 0xefcdab89
    C = 0x98badcfe
    D = 0x10325476

    a0 = A
    b0 = B
    c0 = C
    d0 = D

    for i in range(64):
        if 0 <= i <= 15:
            F = (B & C) | ((~B) & D)
            F = F & 0xFFFFFFFF
            g = i
        elif 16 <= i <= 31:
            F = (D & B) | ((~D) & C)
            F = F & 0xFFFFFFFF
            g = (5*i + 1) % 16
        elif 32 <= i <= 47:
            F = B ^ C ^ D
            F = F & 0xFFFFFFFF
            g = (3*i + 5) % 16
        elif 48 <= i <= 63:
            F = C ^ (B | (~D))
            F = F & 0xFFFFFFFF
            g = (7*i) % 16
        dTemp = D
        newB = (B + leftrotate(A + F + k[i] + m[g], s[i])) & 0xFFFFFFFF
        D, C, B = C, B, newB
        A = dTemp
    a0 = (a0 + A) & 0xFFFFFFFF
    b0 = (b0 + B) & 0xFFFFFFFF
    c0 = (c0 + C) & 0xFFFFFFFF
    d0 = (d0 + D) & 0xFFFFFFFF
    # in ten base
    res = str(a0)+str(b0)+str(c0)+str(d0)
    return res


########## Implementation of chat client class ##########
class chatComm:
    def __init__(self, ipaddress, portnum):
    	# initialize the class
        self.ipaddress = ipaddress
        self.portnum = portnum

    def startConnection(self):
        # starts the connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ipaddress, self.portnum))
        self.s = s
        return

    def getChallenge(self, username):
        # recieves challenge from the server
        cmd = "LOGIN " + username + "\n"
        self.s.send(cmd.encode())
        msg = self.s.recv(BLCK_SIZE*2)
        msg = str(msg, 'utf-8')
        c = msg.split()[2]
        return c

    def sendMD(self, username, md):
        # send messege digest to the server as a last step of authentifincaion
        cmd = "LOGIN " + username + " "+md + "\n"
        self.s.send(cmd.encode())
        msg = self.s.recv(BLCK_SIZE*2)
        msg = str(msg, 'utf-8')
        return msg.startswith("Login Successful")

    def login(self, username, p):
        # logins to the chat client
        c = self.getChallenge(username)
        block = getBlock(p, c)
        chuncks = getChuncks(block)
        md = processChuncks(chuncks)
        return self.sendMD(username, md)

    # makes serrver a request and returns content of the response
    def makeRequest(self, req):
        # return server response knowing the size
        s = self.s
        s.send(req.encode())
        size = s.recv(SZ_BLOCK_SZ)  # recieve only first 6 chars
        msgSize = int(size.decode()[1:]) - SZ_BLOCK_SZ
        msg = ""
        while len(msg) != msgSize:
            msg += s.recv(RECV_SIZE).decode()
        # assert(len(msg) + len(size) == msgSize + SZ_BLOCK_SZ )
        return msg

    def getUsers(self):
    	# returns the list of users
        res = self.makeRequest("@users")
        # split ignoring first '@' to handle no error case
        resList = res[1:].split("@")
        # resList is ["users", "n", "u1", "u2", ... "un"]
        users = resList[2:]
        return users

    def getFriends(self):
    	# return list of firends
        res = self.makeRequest("@friends")
        # split ignoring first '@' to handle no error case
        resList = res[1:].split("@")

        # resList is ["friends", "n", "f1", "f2", ... "fn"]
        friends = resList[2:]
        return friends

    def prependSize(self, msg):
        """Prepends size block into a msg"""
        size = len(msg) + SZ_BLOCK_SZ  # final size of msg
        # pad size number with zero up to 5 symbols + adds @
        sizeString = "@" + "{0:0>5}".format(str(size))
        return sizeString + msg

    def sendFriendRequest(self, friend):
    	# sends friend request
        preMsg = "@request@friend@" + friend  # content of message
        msg = self.prependSize(preMsg)
        res = self.makeRequest(msg)
        return res.startswith("@ok")

    def acceptFriendRequest(self, friend):
    	# accept friend request
        preMsg = "@accept@friend@" + friend  # content of message
        msg = self.prependSize(preMsg)
        res = self.makeRequest(msg)
        return res.startswith("@ok")

    def sendMessage(self, friend, message):
    	# send message
        # @size@sendmsg@[username]@[messageText]
        preMsg = "@sendmsg@" + friend + "@" + message
        # create a request prepending msg's size
        req = self.prependSize(preMsg)
        res = self.makeRequest(req)
        return res.startswith("@ok")

    def sendFile(self, friend, filename):
    	# sends file
        # open and read whole file
        with open(filename, 'r') as fd:
            content = fd.read()
        preMsg = "@sendfile@" + friend + "@"+filename+"@" + content
        req = self.prependSize(preMsg)
        res = self.makeRequest(req)
        return res.startswith("@ok")

    def getRequests(self):
    	# list of friend requests
        res = self.makeRequest("@rxrqst")
        # split ignoring first '@' to handle no error case
        resList = res[1:].split("@")
        # resList is ["n", "u1", "f2", ... "un"]
        reqs = resList[2:]
        return reqs

    def saveFile(self, filename, content):
    	# saves files with given content
        with open(filename, 'w') as fd:
            fd.write(content)
        return

    def getMail(self):
    	# recieve the whole mail
        res = self.makeRequest("@rxmsg")
        # splites to string to ["n", "remainingstring"]
        splited = res[1:].split('@', 1)
        n = int(splited[0])
        msgBox = []
        fileBox = []
        if len(splited) < 2:
            return [msgBox, fileBox]
        remainingStr = splited[1]

        for _ in range(n):
            # in each iteration get first three parts(one message) and update remaining
            if remainingStr.startswith("msg"):
                splited = remainingStr.split('@', 3)
                msgType, username, content = splited[:3]
                msgBox.append((username, content))
                if len(splited) > 3:
                    remainingStr = splited[3]
            elif remainingStr.startswith("file"):
                # File has 4 entries
                splited = remainingStr.split('@', 4)
                msgType, username, filename, content = splited[:4]
                fileBox.append((username, filename))
                self.saveFile(filename, content)
                if len(splited) > 4:
                    remainingStr = splited[4]
        return [msgBox, fileBox]
