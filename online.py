from testToplevel import *

# from tkinter import tkinter
from tkinter import messagebox
from chat import *


class LoginScreen():
    # Class implements the login window of GUI
    def __init__(self, master):
        self.master = master
        self.connect()
        self.display()

    def connect(self):
        # Connect to the server
        self.comm = chatComm("86.36.46.10", 15112)
        self.comm.startConnection()

    def display(self):
        # Display the window and its widgets (elements)
        self.master.geometry("200x150")
        self.master.title("Login")
        #Username Label
        self.uLabel = tk.Label(self.master, text="Username: ")
        self.uLabel.pack()
        #Username Entry Box
        self.uEntry = tk.Entry(self.master)
        self.uEntry.pack()
        #Username Label
        self.pLabel = tk.Label(self.master, text="Password: ")
        self.pLabel.pack()
        #Username Entry Box
        self.pEntry = tk.Entry(self.master, show="*")
        self.pEntry.pack()
        #Sign In Button
        self.ok = tk.Button(
            self.master, text="OK", command=self.submit)
        self.ok.pack()

    def submit(self):
        # Submits login form
        self.username = self.uEntry.get()
        password = self.pEntry.get()
        self.pEntry.delete(0, tk.END)
        # send login request to the server
        if self.comm.login(self.username, password):
            # successfully logged in, hide login screen and open home window
            self.master.withdraw()
            self.openHome()
        else:
            messagebox.showerror(
                title="Error", message="Your username/passport is incorrect. Try again")

    def openHome(self):
        # opens Home (main) window
        game = Online(self.master, self.comm, self.username)


    def close(self, event=0):
        # A method for exiting
        self.master.destroy()

class  Online(App):
    def __init__(self, master, comm, username):
        self.master = master
        self.comm = comm
        self.username = username
        t = tk.Toplevel()
        self.g = App(t)
        self.c = self.g.getCanvas()
        self.pLabel.pack()
        


root = tk.Tk()
master = LoginScreen(root)
root.mainloop()
# root = tk.Tk()
# app = App(root)
# root.mainloop()

