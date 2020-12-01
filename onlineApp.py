# Implements the online version of the Fifteen Game
from tkinter import *
from tkinter import messagebox
from onlineGameInterface import *
from chat import *
from config import *

class LoginScreen():
    # Class implements the login window of GUI
    def __init__(self, master):
        self.master = master
        self.connect()
        self.display()
        self.closed = 0

    def connect(self):
        # Connect to the server
        self.comm = chatComm("86.36.46.10", 15112)
        self.comm.startConnection()

    def display(self):
        # Display the window and its widgets (elements)
        self.master.geometry("200x150")
        self.master.title("Login")
        #Username Label
        self.uLabel = Label(self.master, text="Username: ")
        self.uLabel.pack()
        #Username Entry Box
        self.uEntry = Entry(self.master)
        self.uEntry.pack()
        #Username Label
        self.pLabel = Label(self.master, text="Password: ")
        self.pLabel.pack()
        #Username Entry Box
        self.pEntry = Entry(self.master, show="*")
        self.pEntry.pack()
        #Sign In Button
        self.ok = Button(
            self.master, text="OK", command=self.submit)
        self.ok.pack()

    def submit(self):
        # Submits login form
        self.username = self.uEntry.get()
        password = self.pEntry.get()
        self.pEntry.delete(0, END)
        # send login request to the server
        if self.comm.login(self.username, password):
            # successfully logged in, hide login screen and open home window
            self.master.withdraw()
            self.openHome()
        else:
            # if password is wrong exit ----- but it is too easy
            messagebox.showerror(
                title="Error", message="Your username/passport is incorrect. Try again")

    def openHome(self):
        # opens Home (main) window
        home = HomeWindow(self.master, self.comm, self.username)

    def close(self, event=0):
        # A method for exiting
        self.closed += 1
        if self.closed < 2:
            self.master.destroy()


class HomeWindow(Toplevel):

    def __init__(self, master, comm, username):
        # It is a subclass of Toplevel window
        tk.Toplevel.__init__(self, master)
        self.master = master
        self.comm = comm
        self.username = username
        self.onlineUsers = []
        self.closed = 0
        # if we close this window we want to close the root
        self.bind("<Destroy>", self.close)
        self.display()
        # self.activeChats = {}  # dictionary that stores active chat windows
        self.playing = False
        self.moves = 0
        self.waiting = False
        self.loop = 0
        self.routine()  # runs routine services (checking new messages) and updating screens

        # self.playingFriend  = "user"
        # self.playing = True
        # self.startGame("user")

    def display(self):
        # Display the window and its widgets (elements)
        self.title("Home menu for " + self.username)
        # Labels
        userLabel = Label(self, text="All users")
        userLabel.grid(row=0, column=0)
        friendLabel = Label(self, text="Online Users")
        friendLabel.grid(row=0, column=1)
        requestLabel = Label(self, text="Pending requests")
        requestLabel.grid(row=0, column=2)
        # Buttons
        self.addFriendBtn = Button(
            self, text="Add friend", command=self.addFriend)
        self.addFriendBtn.grid(row=2, column=0)
        self.acptReqBtn = Button(
            self, text="Accept Request", command=self.acceptRequest)
        self.acptReqBtn.grid(row=2, column=2)
        self.openGameBtn = Button(
            self, text="Invite for a game", command=self.validateGameBtnPress)
        self.openGameBtn.grid(row=2, column=1)

    def close(self, ev):
        # Destroy root, so destroy itself
        self.closed += 1
        if self.closed < 2:
            self.master.destroy()

    ## LIST DISPLAYING

    def updateLists(self):
        # Loads the list boxes and since runs periodically updates them
        # Each part is for each boxes
        self.userPart()

    def userPart(self):
        # Uploades the users list and displays it
        self.userBox = Listbox(self)
        self.users = self.comm.getUsers()
        self.fillListBox(self.userBox, self.users)
        self.userBox.grid(row=1, column=0)

    def onlinePart(self):
        # Uploades the friend box and displays it
        self.onlineBox = Listbox(self)
        if self.onlineUsers:
            # self.onlineBox = Listbox(self)
            self.fillListBox(self.onlineBox, self.onlineUsers)
            # self.onlineBox.grid(row=1, column=1)
        self.onlineBox.grid(row=1, column=1)
        self.sendOnlineReq()

    def sendOnlineReq(self):
        # returns array of currently online friends
        # by first sending message and waiting for response
        friends = self.comm.getFriends()
        # print(friends)
        online = []
        for u in friends:
            self.comm.sendMessage(u, REQUEST_CHAR)

    # def sendOnlineReq(self, username):
    #     # returns True is this user is online
    #     self.comm.sendMessage(username, "?")

    def requestPart(self):
        # Uploades the requests list and displays it
        self.requestBox = Listbox(self)
        self.reqs = self.comm.getRequests()
        self.fillListBox(self.requestBox, self.reqs)
        self.requestBox.grid(row=1, column=2)

    def fillListBox(self, listbox, items):
        # Fill given listbox with given list
        for i, item in enumerate(items, start=1):
            listbox.insert(i, item)

    ## BUTTON HANDLERS

    def addFriend(self):
        # Send request to add user to friends
        selected = self.userBox.curselection()
        if not selected:
            # if button is selected before chosing anyone
            messagebox.showerror(
                title="Error", message="Choose username from above list first!")
        else:
            username = self.userBox.get(selected)
            if self.comm.sendFriendRequest(username):
                messagebox.showinfo(
                    title="Success!", message="Your friend request to %s has been sent successfully!" % username)
            else:
                messagebox.showerror(
                    title="Error", message="Server error, sorry")

    def validateGameBtnPress(self):
        # Checks if user chosen the user to open chat
        selected = self.onlineBox.curselection()
        if not selected:
            # if button is selected before chosing anyone
            messagebox.showerror(
                title="Error", message="Choose friend from above list first!")
        else:
            friend = self.onlineBox.get(selected)
            if not self.playing:
                self.inviteGame(friend)

    def inviteGame(self, friend):
        # sends invite for a game
        print("inviting" + friend)
        self.waiting = True
        self.comm.sendFile(friend, PLAY)

    def acceptRequest(self):
        # Accepts the pending requests
        selected = self.requestBox.curselection()
        if not selected:
            # if button is selected before chosing anyone
            messagebox.showerror(
                title="Error", message="Choose username from above list first!")
        else:
            username = self.requestBox.get(selected)
            if self.comm.acceptFriendRequest(username):
                messagebox.showinfo(
                    title="Success!", message="Your accepted request from %s successfully!" % username)
                self.onlinePart()
                self.requestPart()
            else:
                messagebox.showerror(
                    title="Error", message="Server error, sorry")

    ## ROUTINE TASKS

    def manageGame(self):
        if not self.app.gameOver:
            self.comm.sendMessage(self.playingFriend,
                                  "M" + str(self.app.getMoves()))
            msgBox, fileBox = self.comm.getMail()
            if msgBox:
                for freind, content in msgBox:
                    print(content)
                    if content[0] == MOVE:
                        self.moves = content[1:]
                    if content[0] == WIN:
                        print("You lost", content[1:])
                        tk.messagebox.showwarning(
                            title="You lost", message="Your opponent finished the game " + content[1:] + " seconds")
                        self.playing = False
                        self.playingFriend = ""
                        self.app.destroy()
                        return
            self.master.after(500, self.manageGame)
        else:
            print("You won!")
            print("Stop everything")
            self.playing = False
            self.playingFriend = ""
            return

    def recieveMessages(self):
        # Recieves the responses from the server
        if self.playing:
            return
        print('recieving')
        msgBox, fileBox = self.comm.getMail()
        if msgBox:
            # for every message open chats and append messages
            for friend, content in msgBox:
                # If this is online response then add to the online list
                if content[0] == ONLINE_CHAR:
                    if friend not in self.onlineUsers and friend != self.username:
                        self.onlineUsers.append(friend)
                elif content[0] == OFFLINE_CHAR:
                    # filter out this user who closed an app
                    self.onlineUsers = list(
                        filter(lambda x: x != friend, self.onlineUsers))
                elif content[0] == REQUEST_CHAR:
                    # send I am online response
                    self.comm.sendMessage(friend, ONLINE_CHAR)
                else:
                    # DEBUFGGGGGGGGGGGGGGGGGGGGGGGGGGGGG
                    print(friend, content)
        if fileBox:
            # for every file consider it as a game requests
            for friend, filename in fileBox:
                if filename == PLAY:
                    if self.playing:
                        self.comm.sendFile(friend, BUSY)
                    else:
                        # message box to choose
                        if messagebox.askquestion(title="Request", message=friend+" wants to play game with you. Do you want to play?"):
                            self.playing = True
                            self.comm.sendFile(friend, ACC)
                            print("accepted")
                            self.playingFriend = friend
                            self.startGame(friend)
                        else:
                            # decline
                            self.comm.sendFile(friend, REJ)
                elif filename == REJ and self.waiting:
                    print(friend + " Rejected your request")
                    self.waiting = False
                elif filename == BUSY and self.waiting:
                    print(friend + " is playing other game right now")
                    self.waiting = False
                elif filename == ACC and self.waiting:
                    print("You started game with " + friend)
                    self.playing = True
                    self.playingFriend = friend
                    self.waiting = False
                    self.startGame(friend)

    def updateStat(self):
        if self.playing:
            s = str(self.moves)
            self.app.setFriendStat(s)
            self.master.after(500, self.updateStat)
        return

    def startGame(self, f):
        print("play!!!!!!")
        # launches a game with friend f
        seed = "DDULDRUUDLLRLDDDLLURDDLURDLDURLDUDLRUD"
        self.app = App(self.master, seed, f, self.comm)
        self.updateStat()
        self.manageGame()

    def routine(self):
        # Routine tasks that will run peridically
        # update lists only 15 seconds once
        if self.loop % 15 == 0:
            self.updateLists()
        self.loop += 1
        self.onlinePart()
        self.requestPart()
        # load lists
        self.recieveMessages()                  # check recieved message
        # self.clean()                            # keep track of closed windows
        # run the function again after 3 secs
        self.master.after(3000, self.routine)


class ChatWindow(Toplevel):

    def __init__(self, master, comm, me, friend):
        Toplevel.__init__(self, master)
        self.master = master
        self.comm = comm
        self.me = me
        self.friend = friend
        self.title("Chat with %s" % self.friend)
        self.display()
        # redefine destoy behaviour
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.toBeDestroyed = False

    def close(self):
        # instead of destroying itself, hide it and wait for home to destroy
        if self.toBeDestroyed:
            self.destroy()
        else:
            self.toBeDestroyed = True
            self.withdraw()

    def getDestroyState(self):
        # return if home should destroy the window or not
        return self.toBeDestroyed

    def display(self):
        # display the window
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        # create read only text area for messages
        self.chatArea = Text(self, state="disabled")
        self.chatArea.grid(row=0, column=0, columnspan=2)
        self.entry = Text(self, height=3)
        self.entry.grid(row=2, column=0, sticky='w')
        Button(self, text="Send", command=self.sendMessage,
               width=20, height=3).grid(row=2, column=2, sticky='e')

    def sendMessage(self):
        # Send button behavior, send and append messages
        message = self.entry.get(1.0, END)
        self.comm.sendMessage(self.friend, message)
        txt = self.me + ": " + message
        # make text are editable and disable it after we append our text
        self.chatArea.configure(state='normal')
        self.chatArea.insert(END, txt)
        self.chatArea.configure(state='disabled')
        self.entry.delete("1.0", "end")

    def appendMessage(self, message):
        # Add friend messsages (called from recieve messages behavior)
        txt = self.friend + ": " + message + "\n"
        self.chatArea.configure(state='normal')
        self.chatArea.insert(END, txt)
        self.chatArea.configure(state='disabled')


root = Tk()
main_window = LoginScreen(root)
root.mainloop()
