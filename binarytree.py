import node, leafnode
Node = node.Node
LeafNode = leafnode.LeafNode

class BinaryTree:
    def __init__(self, reg_exp):
        self.reg_exp = reg_exp
        self.nodes_stack = list()
        self.ops_stack = list()
        self.num_leafs = 0
        self.leafs = dict()
        self.special_symbs = {'+', '.', '*', '(',
                              ')'}  # char '#' is removed for convenience
        self.ops_prec = {'(': 1, '+': 2, '.': 3, '*': 4}

    # generate binary tree from RE
    def generate_tree(self):
        # iterate over RE chars
        for char in self.reg_exp:
            # if char is from alphabet create leaf
            if char not in self.special_symbs:
                self.create_leaf(char)
            elif not self.ops_stack or char == '(':
                self.ops_stack.append(char)
            elif char == ')':
                # execute stack ops until finding a '('
                while self.ops_stack[-1] != '(':
                    self.do_ops()
                self.ops_stack.pop()
            else:
                # compare stacked and current operator precedence
                while self.ops_stack and self.ops_prec[
                        self.ops_stack[-1]] >= self.ops_prec[char]:
                    self.do_ops()
                self.ops_stack.append(char)
        # do ops left to do
        while self.ops_stack:
            self.do_ops()
        # return root node
        return self.nodes_stack.pop()

    # create new leaf
    def create_leaf(self, symb):
        # if empty string leaf node has no ID
        if symb == '$':
            leaf_node = LeafNode(symb, 0)
        else:
            self.num_leafs += 1
            leaf_node = LeafNode(symb, self.num_leafs)
            self.leafs[self.num_leafs] = leaf_node
        self.nodes_stack.append(leaf_node)

    # ops execution: union, concat and star
    def do_ops(self):
        if self.ops_stack:
            op = self.ops_stack.pop()
            if op == '+':
                self.union()
            elif op == '.':
                self.concat()
            elif op == '*':
                self.star()
            else:
                print('Invalid operation')

    # union operation
    def union(self):
        node_2 = self.nodes_stack.pop()
        node_1 = self.nodes_stack.pop()
        op_node = Node('+')
        op_node.left_child = node_1
        op_node.right_child = node_2
        node_1.parent = op_node
        node_2.parent = op_node
        self.nodes_stack.append(op_node)

    # concatenation operation
    def concat(self):
        node_2 = self.nodes_stack.pop()
        node_1 = self.nodes_stack.pop()
        op_node = Node('.')
        op_node.left_child = node_1
        op_node.right_child = node_2
        node_1.parent = op_node
        node_2.parent = op_node
        self.nodes_stack.append(op_node)

    # kleene star operation
    def star(self):
        node = self.nodes_stack.pop()
        op_node = Node('*')
        op_node.left_child = node
        node.parent = op_node
        self.nodes_stack.append(op_node)

    # print node and children's symbols in console
    def print_node(self, node):
        if node:
            self.print_node(node.left_child)
            print(node.symb, end='')
            self.print_node(node.right_child)

    # print node and children's attr in console
    def print_node_attr(self, node):
        if node:
            self.print_node_attr(node.left_child)
            print('symb: {}, nullable: {}, first_pos: {}, last_pos: {}'.format(node.symb, node.nullable, node.first_pos, node. last_pos))
            self.print_node_attr(node.right_child)
