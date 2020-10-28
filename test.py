from tkinter import *
from tkinter import ttk
from tkinter.simpledialog import Dialog
from PIL import Image, ImageTk

# From very old 2012 demo code https://pyinmyeye.blogspot.com/2012/07/tkinter-demos.html

class Fifteen(Frame):

    def __init__(self, started=True, name='fifteen'):
        Frame.__init__(self, name=name)
        self.pack(expand=Y, fill=BOTH)
        self.n = 4
        self.master.title('15 Puzzle')
        self.started = started
        self.create()
        self.dificulty = 4
        print(self.dificulty)
        self.width = 500
        self.height = 500
        self.border = [3, 1, 6, 2, 5, 7, 15, 13, 4, 11, 8, 9, 14, 10, 12]

    def create(self):
        if self.started:
            self.pack(side=BOTTOM, fill=X)

        self._create_demo_panel()

    def _create_demo_panel(self):
        bgColor = 'gray80' 
        demoPanel = Frame(self, borderwidth=2, relief=SUNKEN, background=bgColor,
                          width=500, height=500)
        demoPanel.pack(side=TOP, pady=1, padx=1)

        # buttons are placed relative to the top, left corner of demoPanel
        # with relations expressed as a value between 0.0 and 1.0
        # top, left corner = (x,y) = (0,0)
        # bottom, right corner = (x,y) = (1,1)
        self.pos = {}
        self.pos['space'] = (self.unitLen()*(self.n-1),
                               self.unitLen()*(self.n-1))
        order = self.border

        for i in range(15):
            num = order[i]
            self.pos[num] = (i % self.n * self.unitLen(),
                               i//self.n * self.unitLen())
            b = ttk.Button(text=num, style='TButton')
            b['command'] = lambda b=b: self._puzzle_switch(b)
            b.place(in_=demoPanel, relx=self.pos[num][0], rely=self.pos[num][1],
                    relwidth=self.unitLen(), relheight=self.unitLen())

        # set button background to demoPanel background
        ttk.Style().configure('TButton', background=bgColor)
    
    def unitLen(self):
        # return 1 / self.dificulty
        return 0.25

    # return whether is the selected button next to the space
    def isNearSpace(self,button):
        num = button['text']
        sx = self.pos['space'][0]     # position of 'space'
        sy = self.pos['space'][1]
        x = self.pos[num][0]          # position of selected button
        y = self.pos[num][1]
        return sy-.01 <= y <= sy+.01 and sx-self.unitLen()-.01 <= x <= sx+self.unitLen()+.01 or sx-.01 <= x <= sx+.01 and sy-(self.unitLen()+.01) <= y <= sy+self.unitLen()+.01

    def _puzzle_switch(self, button):
        if(self.isNearSpace(button)):
            num = button['text']
            # swap button with space
            self.pos['space'], self.pos[num] = self.pos[num], self.pos['space']

            # re-position button
            button.place(relx=self.pos[num][0], rely=self.pos[num][1])


if __name__ == '__main__':
    Fifteen().mainloop()
