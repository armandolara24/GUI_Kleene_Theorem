class Node:
    def __init__(self, symb):
        self.symb = symb
        self.first_pos = set()
        self.last_pos = set()
        self.nullable = False
        self.parent = None
        self.left_child = None
        self.right_child = None