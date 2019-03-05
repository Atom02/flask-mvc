class Auth:
    name = None
    type = None
    description = None
    group = None
    craeted = None
    updated = None
    rule = None
    data = None

    def invalidate(self):
        self.name = None
        self.type = None
        self.desc = None
        self.group = None
        self.craeted = None
        self.updated = None
        self.rule = None
        self.data = None