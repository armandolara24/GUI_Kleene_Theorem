'''
This program generates a DFA from a RE using a direct method (not passing through NFA)
Steps:
1 create augmented RE from input RE
2 generate binary tree from augmented RE
3 calculate first and last positions in tree making it a syntax tree
4 calculate follow positions for each leaf in syntax tree
5 generate DFA states from follow positions
'''
import node, binarytree, leafnode, syntaxtree, state
from graphviz import Digraph
SyntaxTree = syntaxtree.SyntaxTree
State = state.State
Node = node.Node
LeafNode = leafnode.LeafNode

class RE_to_DFA:
    def __init__(self):
        self.file_name = 'testcases.txt'
        self.reg_exp = ''
        self.special_symbs = {'+', '.', '*', '(', ')'}  # char '#' not considered
        self.alphabet = set()
        self.root = Node('')
        self.leafs = dict()
        self.start_state = State(0)
        self.states = list()

    def set_reg_exp(self, reg_exp):
        self.reg_exp = reg_exp.rstrip()

    def main(self):
        print('---Program Started---')
        #self.read_reg_exp()        
        print('RE: {}'.format(self.reg_exp))
        self.insert_expl_concat()
        #print('Reg. Exp.: {}'.format(self.reg_exp))
        self.save_symbols()
        st = SyntaxTree(self.reg_exp)
        self.root = st.root
        self.leafs = st.leafs
        self.create_dfa()
        self.print_dfa()
        self.write_dfa_table_format()
        self.graph_dfa()
        print('---Program Ended---')

    # read input RE from txt file
    def read_reg_exp(self):
        with open(self.file_name) as f:
            # read first line and remove newline char
            self.reg_exp = f.readline().rstrip()

    # insert explicit concat operator and generate augmented RE
    def insert_expl_concat(self):
        self.reg_exp = '(' + self.reg_exp + ')'
        self.reg_exp += '#'
        output = ''
        for i in range(len(self.reg_exp)):
            char = self.reg_exp[i]
            output += char
            if char == '(' or char == '+':
                continue
            if i < len(self.reg_exp) - 1:
                lookahead = self.reg_exp[i + 1]
                if lookahead == '*' or lookahead == '+' or lookahead == ')':
                    continue
                output += '.'
        self.reg_exp = output

    # detect alphabet
    def save_symbols(self):
        i = 1
        for char in self.reg_exp:
            if char not in self.special_symbs and char != '#':
                self.alphabet.add(char)
                i += 1

    # create DFA based on syntax tree
    def create_dfa(self):
        # create initial state
        state_cnt = 1
        start_state = State(state_cnt)
        start_state.follow_pos.update(self.root.first_pos)
        if len(self.leafs) in start_state.follow_pos:
            start_state.final = True
        self.states.append(start_state)
        todo_states = list()
        todo_states.append(start_state)
        state_cnt += 1
        # process each state in the queue until empty
        while todo_states:
            curr_state = todo_states.pop()
            letters_fp = dict()
            for leaf_id in curr_state.follow_pos:
                if self.leafs[leaf_id].symb != '#':
                    letters_fp[self.leafs[leaf_id].symb] = set()
            for leaf_id in curr_state.follow_pos:
                leaf = self.leafs[leaf_id]
                if leaf.symb != '#':
                    letters_fp[leaf.symb].update(leaf.follow_pos)
            # iterating thru letters and the union of their follow pos
            for letter, follow_pos in letters_fp.items():
                #print('state_id: {} letter: {} follow_pos: {}'.format(curr_state.state_id, letter, follow_pos))
                # iterating thru already created states
                state_found = False
                for state in self.states:
                    if state.follow_pos == follow_pos:
                        curr_state.out_trans[letter] = state
                        state_found = True
                        break
                # creating new state if not found one with desired follow pos
                if not state_found:
                    new_state = State(state_cnt)
                    new_state.follow_pos.update(follow_pos)
                    curr_state.out_trans[letter] = new_state
                    if len(self.leafs) in new_state.follow_pos:
                        new_state.final = True
                    self.states.append(new_state)
                    todo_states.append(new_state)
                    state_cnt += 1

    # print generated DFA in console
    def print_dfa(self):
        print('DFA:')
        for state in self.states:
            print('State ID {}'.format(state.state_id), end='')
            if state.final:
                print(' Final')
            else:
                print()
            for letter, dest_state in state.out_trans.items():
                print('{} -- {} --> {}'.format(state.state_id, letter, dest_state.state_id))

    def write_dfa_table_format(self):
        file = open("re_to_dfa_output.txt", "w")
        # first_iter = True
        # for letter in self.alphabet:
        #     if first_iter:
        #         file.write(letter)
        #         first_iter = False
        #     else:
        #         file.write(',' + letter)
        # file.write('\n')
        for state in self.states:            
            if state.state_id == 1:
                file.write(str(state.state_id) + ',-' + '\n')
            if state.final:
                file.write(str(state.state_id) + ',+' + '\n')
            for letter, dest_state in state.out_trans.items():
                file.write(str(state.state_id) + ',' +
                           str(dest_state.state_id) + ',' + letter + '\n')

        file.close()

    # graph DFA in png using graphviz package
    def graph_dfa(self):
        f = Digraph('finite_state_machine', filename='dfa.gv')
        f.format = 'png'
        f.attr(rankdir='LR', size='8,5')
        f.attr('node', shape='doublecircle')
        for state in self.states:
            if state.final:
                f.node('S_{}'.format(state.state_id))
        f.attr('node', shape='circle')
        for state in self.states:
            for letter, dest_state in state.out_trans.items():
                f.edge('S_{}'.format(state.state_id),
                       'S_{}'.format(dest_state.state_id),
                       label='{}'.format(letter))
        f.view()

if __name__ == "__main__":
    ReToDfa().main()
