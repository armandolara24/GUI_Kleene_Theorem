import node
Node = node.Node

class LeafNode(Node):

    def __init__(self, symb, leaf_id):
        super().__init__(symb)
        self.follow_pos = set()
        self.leaf_id = leaf_id        