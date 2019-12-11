class Asset():
    js=[]
    css=[]
    depends=[]
    def __init__(self):
        pass
        
    def isDepend(self):
        if not self.depends:
            return False
        else:
            return self.depends

    def register(self):
        return self.js,self.css