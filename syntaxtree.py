import binarytree, leafnode
BinaryTree = binarytree.BinaryTree
LeafNode = leafnode.LeafNode

class SyntaxTree:
    def __init__(self, reg_exp):
        self.reg_exp = reg_exp
        # create binary tree from RE
        bt = BinaryTree(self.reg_exp)
        self.root = bt.generate_tree()
        #bt.print_node(self.root)
        #print()
        self.calc_nullables(self.root)
        #bt.print_node_attr(self.root)
        self.calc_first_last_pos(self.root)
        #bt.print_node_attr(self.root)
        self.leafs = bt.leafs
        self.calc_follow_pos(self.root)
        #self.print_follow_pos()

    # calculate nullable nodes in tree
    def calc_nullables(self, node):
        if node is None:
            return
        self.calc_nullables(node.left_child)
        self.calc_nullables(node.right_child)
        if isinstance(node, LeafNode):
            if node.symb == '$':
                node.nullable = True
        else:
            if node.symb == '*':
                node.nullable = True
            elif node.symb == '+':
                node.nullable = node.left_child.nullable or node.right_child.nullable
            elif node.symb == '.':
                node.nullable = node.left_child.nullable and node.right_child.nullable

    # calculate first and last positions for nodes in tree
    def calc_first_last_pos(self, node):
        if node is None:
            return
        if isinstance(node, LeafNode):
            if not node.symb == '$':
                node.first_pos.add(node.leaf_id)
                node.last_pos.add(node.leaf_id)
        else:
            left = node.left_child
            right = node.right_child
            self.calc_first_last_pos(left)
            self.calc_first_last_pos(right)
            if node.symb == '+':
                node.first_pos.update(left.first_pos)
                node.first_pos.update(right.first_pos)
                node.last_pos.update(left.last_pos)
                node.last_pos.update(right.last_pos)
            elif node.symb == '.':
                if left.nullable:
                    node.first_pos.update(left.first_pos)
                    node.first_pos.update(right.first_pos)
                else:
                    node.first_pos.update(left.first_pos)
                if right.nullable:
                    node.last_pos.update(left.last_pos)
                    node.last_pos.update(right.last_pos)
                else:
                    node.last_pos.update(right.last_pos)
            else:
                node.first_pos.update(left.first_pos)
                node.last_pos.update(left.last_pos)

    # calculate first and last positions for leafs in tree
    def calc_follow_pos(self, node):
        if node is None:
            return
        left = node.left_child
        right = node.right_child
        if node.symb == '.':
            for leaf_id in left.last_pos:
                self.leafs[leaf_id].follow_pos.update(right.first_pos)
        elif node.symb == '*':
            for leaf_id in node.last_pos:
                self.leafs[leaf_id].follow_pos.update(node.first_pos)
        self.calc_follow_pos(left)
        self.calc_follow_pos(right)

    # print leaf's follow positions in console
    def print_follow_pos(self):
        for leaf_id, leaf in self.leafs.items():
            print('leaf_id = {}, follow_pos = {}'.format(leaf_id, leaf.follow_pos))