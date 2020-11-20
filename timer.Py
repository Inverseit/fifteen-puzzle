import time
class Timer(object):
    def __init__(self, master, canvas):
        self.master = master
        self.canvas = canvas
        self.total = 0
        self.stoped = False
        self.tag = ""
        print("started")
    def run(self):
        print("here")
        self.start = time.time()
        self.draw()
    def draw(self):
        if not self.stoped:
            self.delete()
            self.passed = round(time.time() - self.start + self.total,3)
            self.s = self.getString()
            self.tag = self.canvas.create_text(350, 350, text=self.s, font = "Helvetica 16")
            self.master.after(5, self.draw)
    def getString(self):
        t = self.passed
        return t
    def delete(self):
        if self.tag:
            self.canvas.delete(self.tag)
    def resume(self):
        self.stoped = False
        self.total += self.passed
        self.start = time.time()
        self.draw() 

    def stop(self):
        self.stoped = True
    

