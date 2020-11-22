import time
class Timer(object):
    def __init__(self, master, canvas):
        self.master = master
        self.canvas = canvas
        self.total = 0     # total passed since start
        self.passed = 0    # passed after past resume or start
        self.tag = ""
        self.running = False   # is started
        self.stoped = False    # is paused
    def run(self):
        print("started running")
        self.running = True
        self.start = time.time()
        self.draw()

    def draw(self):
        if not self.stoped:
            self.delete()
            self.passed = round(time.time() - self.start,2)
            self.tag = self.canvas.create_text(
                255, 520, text=self.getTime(), font="Helvetica 16")
            self.master.after(2, self.draw)

    def getTime(self):
        t = self.total + self.passed
        return round(t, 2)
    def getTotal(self):
        return self.total

    def delete(self):
        if self.tag:
            self.canvas.delete(self.tag)

    def resume(self):
        self.stoped = False
        if not self.running:
            return
        self.start = time.time()
        self.draw() 

    def stop(self):
        self.stoped = True
        self.total += self.passed
    

