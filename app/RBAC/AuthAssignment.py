class AuthAssignment():
    userId = None
    roleName = None
    createdAt = None
    def __init__(self,dt=None):
        if dt is not None:
            self.populate(dt)
        pass
    
    def populate(self,dt):
        userId = dt["user_id"]
        roleName = dt["item_name"]
        createdAt = dt["created_at"]