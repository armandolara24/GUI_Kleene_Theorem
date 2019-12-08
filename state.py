class State:
    def __init__(self, state_id):
        self.state_id = state_id
        self.follow_pos = set()
        self.out_trans = dict()
        self.final = False