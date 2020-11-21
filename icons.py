from PIL import ImageTk, Image, ImageEnhance
class Icon():
    """
    Provides Icon class that represent single menu icon 
    """
    def __init__(self,val, onPath, offPath = "", resize = False, onAlpha = 1, offAlpha = 1, state = False):
        self.onPath = "textures/icons/" + onPath + ".png"
        if not offPath:
            offPath = onPath
        self.offPath = "textures/icons/" + offPath + ".png"
        self.onResize = resize
        self.offResize = resize
        self.onAlpha = onAlpha
        self.offAlpha = offAlpha
        self.state = state
        self.on = 0
        self.off = 0
        self.val = val
        self.tag = 0
        self.open()
        
    def open(self):
        # Open and config active (on) image
        on = Image.open(self.onPath).convert("RGBA")
        if self.onResize:
            on = on.resize(self.onResize, Image.ANTIALIAS)
        if self.onAlpha != 1:
            self.on = ImageTk.PhotoImage(
               self.reduce_opacity(on, opacity=self.onAlpha))
        else:
            self.on = ImageTk.PhotoImage(on)

        # Open and config hovered (off) image
        if self.offPath:
            im = Image.open(self.offPath).convert("RGBA")
            if self.offResize:
                im = im.resize(self.offResize, Image.ANTIALIAS)
            if self.offAlpha != 1:
                self.off = ImageTk.PhotoImage(self.reduce_opacity(im, opacity = self.offAlpha))
            else:
                self.off = ImageTk.PhotoImage(im)

    def get(self):
        if self.state:
            return self.on
        else:
            return self.off 
    
    def toggle(self):
        self.state = not self.state

    def turnOff(self):
        self.state = False
    def getState(self):
        return self.state
    def getVal(self):
        return self.val
    def getTag(self):
        return self.tag
    def setTag(self, tag):
        self.tag = tag
        

    @staticmethod
    def reduce_opacity(im, opacity):
        """Returns an image with reduced opacity."""
        # from https://stackoverflow.com/questions/61271072/how-can-i-solve-python-3-pil-putalpha-problem
        assert opacity >= 0 and opacity <= 1
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        else:
            im = im.copy()
        alpha = im.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        im.putalpha(alpha)
        return im
