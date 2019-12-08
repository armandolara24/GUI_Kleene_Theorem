"""
State elimination algorithm implementation for converting a Transition Graph into a Regular Expression.
"""
import os
import sys
import shutil
#from drawing import Drawing


# Input Transition Graph
filepath = 'tg_to_re_input.txt'
# symbol for the null string
null_string = '$'
# states is a dictionary that will contain instances of the state class, it stores the current states and
# its connections and it its used and modified along the entire algorithm.
states = {}
# alphabet to be used, it is only symbolic this is not a constraint for the algorithm to work.
alphabet = ''
# output directory to store the generated graphs and .txt transition graphs.
out_dir = r'.\tables'
# global counter to store the number of plots that were saved to the moment.
drawing_counter = 1


def main():
    states.clear()
    alphabet = ''
    global drawing_counter
    drawing_counter = 1

    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    # get the transition graph from a txt and save it into the states global variable
    read_file()
    dump_st_table('initial_tg.txt')
    # draw the initial transition graph
    #Drawing(states, out_dir + '\\' + str(drawing_counter) + '_initial_tg.txt')
    drawing_counter += 1
    # if initial and final states are the same state this function will separate them
    separate_start_final_st()
    # algorithm for creating a unique initial state
    make_uniq_start_st()
    # algorithm for creating a unique final state
    make_uniq_final_st()
    # draw the transition graph with separated initial and final states
    #Drawing(states, out_dir + '\\' + str(drawing_counter) + '_initial_final.txt')
    drawing_counter += 1
    # simplify 'or' connections
    simplify_transitions()
    # dump_st_table('simplified_transitions.txt') for debugging purposes
    #Drawing(states, out_dir + '\\' + str(drawing_counter) + '_simplified_transitions.txt')
    drawing_counter += 1
    # eliminate states
    elimination_algorithm()
    print_states()
    # simplify double null strings
    simplify_symbols()
    #Drawing(states, out_dir + '\\' + str(drawing_counter) + '_final.txt')
    drawing_counter += 1
    print("Output:")
    print_states()
    write_to_output_file()

def write_to_output_file():
    with open('tg_to_re_output.txt', 'w') as file:
        reg_exp=states[0]._edges_out[0][1]
        file.write(reg_exp)    

def separate_start_final_st():
    """
    Separates the initial and final states if they are in the same state
    :return:
    """
    start_final_st = {}
    max_st = 0
    for key, value in states.items():
        if value.get_pos() == '-+':
            start_final_st[key] = value
        if key > max_st:
            max_st = key
    if len(start_final_st) > 0:
        for key, value in start_final_st.items():
            id_start = max_st + 1
            id_final = max_st + 2
            start_st = State(id_start)
            final_st = State(id_final)
            start_st.set_pos('-')
            final_st.set_pos('+')
            states[id_start] = start_st
            states[id_final] = final_st
            value.set_pos('')
            value.add_edge_in((id_start, null_string))
            value.add_edge_out((id_final, null_string))
            start_st.add_edge_out((key, null_string))
            final_st.add_edge_in((key, null_string))


def make_uniq_start_st():
    """
    Makes a unique initial state connected with null strings to the other previous initial states
    :return:
    """
    start_st = {}
    max_st = 0
    for key, value in states.items():
        if value.get_pos() == '-':
            start_st[key] = value
            if key > max_st:
                max_st = key
    if len(start_st) == 0:
        print('TG accepts only empty language')
        #sys.exit()
    elif len(start_st) >= 1:
        id = 0
        if states.get(id):
            id = max_st + 1
        uniq_st = State(id)
        uniq_st.set_pos('-')
        states[id] = uniq_st
        for key, value in start_st.items():
            value.set_pos('')
            value.add_edge_in((id, null_string))
            uniq_st.add_edge_out((key, null_string))


def make_uniq_final_st():
    """
    Makes a unique final state connecting with null strings the previous final states
    :return:
    """
    final_st = {}
    max_st = 0
    for key, value in states.items():
        if value.get_pos() == '+':
            final_st[key] = value
        if key > max_st:
            max_st = key
    if len(final_st) == 0:
        print('TG accepts only empty language')
        sys.exit()
    elif len(final_st) >= 1:
        id = max_st + 1
        uniq_st = State(id)
        uniq_st.set_pos('+')
        states[id] = uniq_st
        for key, value in final_st.items():
            value.set_pos('')
            value.add_edge_out((id, null_string))
            uniq_st.add_edge_in((key, null_string))


def simplify_transitions():
    """
    If there are two or more out edges to the same state add them to make one single edge.
    :return: None
    """
    for key, value in states.items():
        edges_out = value.get_edges_out()
        new_edges_out = []
        marked = []
        for i in range(len(edges_out)):
            repeated_flag = False
            for j in range(i + 1, len(edges_out)):
                if edges_out[i][0] == edges_out[j][0]:
                    repeated_flag = True
                    new_edges_out.append(
                        (edges_out[i][0], '({0}+{1})'.format(edges_out[i][1], edges_out[j][1])))
                    marked.append(edges_out[i])
                    marked.append(edges_out[j])
            if not repeated_flag:
                if edges_out[i] not in marked:
                    new_edges_out.append(edges_out[i])

        if new_edges_out:
            states[key].set_edges_out(new_edges_out)
    sync_in_out_edges()


def sync_in_out_edges():
    """
    As our architecture stores in and out edges they should match all the time, after the sum of two or more out edges
    we should re-sync the in edges too, this method performs that task
    :return: None
    """
    for key, value in states.items():
        edges_in = value.get_edges_in()
        new_edge_in = []
        for edge_in in edges_in:
            associated_state = states[edge_in[0]]
            associated_state_edges_out = associated_state.get_edges_out()
            # compare each associated string
            for edge_out in associated_state_edges_out:
                if edge_out[0] == key:
                    edge_out_string = edge_out[1]
                    edge_in_string = edge_in[1]
                    if edge_out_string != edge_in_string:
                        # Sync up is needed here
                        new_edge_in.append((edge_in[0], edge_out_string))
                    else:
                        # No update is needed
                        new_edge_in.append(edge_in)

        # Remove duplicates
        final_edges_in = []
        for edge_in in new_edge_in:
            if edge_in not in final_edges_in:
                final_edges_in.append(edge_in)
        value.set_edges_in(final_edges_in)


def elimination_algorithm():
    """ Decides the order of the node elimination """
    global drawing_counter
    # Should we eliminate close loops first ¿?
    initial_states = []
    for key, value in states.items():
        edges_in = states[key].get_edges_in()
        edges_out = states[key].get_edges_out()
        edges_in_counter = 0
        for edge_in in edges_in:
            if edge_in[0] != key:
                edges_in_counter += 1
        edges_out_counter = 0
        for edge_out in edges_out:
            if edge_out[0] != key:
                edges_out_counter += 1
        if edges_in_counter == 1 and edges_out_counter == 1:
            initial_states.append((key, value))

    # first eliminate states that generate closed loops
    for i in range(len(initial_states)):
        eliminate_states(initial_states[i][0], initial_states[i][1])
        dump_st_table('state_' + str(initial_states[i][0]) + '.txt')
        #Drawing(states, out_dir + '\\' + str(drawing_counter) +  '_state_' + str(initial_states[i][0]) + '.txt')
        drawing_counter += 1

    # Then eliminates in order (state 1, state 2, ..., state n)
    for key, value in states.items():
        eliminate_states(key, value)
        dump_st_table('state_' + str(key) + '.txt')
        #Drawing(states, out_dir + '\\' + str(drawing_counter) + '_state_' + str(key) + '.txt')
        drawing_counter += 1


def eliminate_states(key, value):
    """ Eliminates one state bypassing its corresponding in and out edges. """
    if value.get_pos() != '+' and value.get_pos() != '-':
        # map each input to each output
        edges_in = list(value.get_edges_in())
        edges_out = list(value.get_edges_out())
        state_id = value.get_id()
        kleen_closure = ''
        # look up for Kleene's closure
        for k in range(len(edges_out)):
            if state_id == edges_out[k][0]:
                kleen_closure = '(' + edges_out[k][1] + ')*'

        for i in range(len(edges_in)):
            # connect the input node to the output node
            states[edges_in[i][0]].delete_edge_out((key, edges_in[i][1]))
            states[key].delete_edge_in(edges_in[i])
            if key != edges_in[i][0]:
                for o in range(len(edges_out)):
                    if key != edges_out[o][0]:
                        try:
                            states[key].delete_edge_out(edges_out[o])
                            states[edges_out[o][0]].delete_edge_in(
                                (key, edges_out[o][1]))
                        except:
                            pass

                        states[edges_in[i][0]].add_edge_out(
                            (edges_out[o][0], edges_in[i][1] + kleen_closure + edges_out[o][1]))
                        states[edges_out[o][0]].add_edge_in(
                            (edges_in[i][0], edges_in[i][1] + kleen_closure + edges_out[o][1]))

                        # call simplification algorithm
                        simplify_transitions()


def simplify_symbols():
    """ Look up for non-emtpy string edges and send them to the reduction algorithm """
    for key, value in states.items():
        edges_in = value.get_edges_in()
        edges_out = value.get_edges_out()
        new_edges_in = []
        new_edges_out = []
        for edge_in in edges_in:
            edge_string = edge_in[1]
            if edge_string != '':
                new_edges_in.append((edge_in[0], reduce(edge_string)))

        for edge_out in edges_out:
            edge_string = edge_out[1]
            if edge_string != '':
                new_edges_out.append((edge_out[0], reduce(edge_string)))
        if new_edges_in:
            value.set_edges_in(new_edges_in)
        if new_edges_out:
            value.set_edges_out(new_edges_out)


def remove_duplicates(string):
    new_string = []
    c = 0
    while c < len(string):
        if string[c] == null_string:
            if (c+1) < len(string):
                if string[c] != string[c+1]:
                    new_string.append(string[c])
        else:
            new_string.append(string[c])
        c += 1
    f_string = ''
    return f_string.join(new_string)


def reduce(string):
    """
    Traverse over each character in the input string to simplify lambda concatenation.
    If lambda is the only thing between a + + or  ( + or + ) then leave it, if not remove the lambda
    Todo: simplify nested parenthesis and improve reduction algorithm.
    :param string: Input string to be scanned
    :return: string without not needed lambdas
    """
    string = remove_duplicates(string)
    final_str = ''
    for l in range(len(string)):
        if string[l] != null_string:
            final_str += string[l]
        else:
            if l == 0:
                if string[l+1] == '+' or string[l+1] == ')':
                    final_str += string[l]
            elif l == (len(string) - 1):
                if string[l-1] == '+' or string[l-1] == '(':
                    final_str += string[l]
            else:
                if (string[l-1] == '+' or string[l-1] == '(') and (string[l+1] == '+' or string[l+1] == ')'):
                    final_str += string[l]
    return final_str


def get_state(id):
    """Creates a state if it doesn't already exist"""
    if not states.get(id):
        states[id] = State(id)
    return states.get(id)


def dump_st_table(filename):
    """
    This method dumps the states dictionary into a txt file for exporting the data. It may be deprecated in the future.
    :param filename: target name for saving the txt
    :return: None
    """
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    with open(out_dir + '\\' + filename, 'w') as f:
        f.write(alphabet)
        for key, value in states.items():
            edges_out = states[key].get_edges_out()
            pos = str(states[key].get_pos())
            state_id = str(states[key].get_id())
            if pos == '+' or pos == '-':
                f.write(state_id + ',' + pos+'\n')
            for edge_out in edges_out:
                f.write(state_id+','+str(edge_out[0])+','+edge_out[1]+'\n')


def read_file():
    global alphabet
    with open(filepath, 'r') as f:
        '''Reading transition graph input file'''
        #aphabet_line = f.readline()
        #alphabet += aphabet_line
        for line in f:
            if line == '\n':
                continue
            line = line.rstrip().split(',')
            if line[1] == '-' or line[1] == '+':
                id = int(line[0])
                state = get_state(id)
                state.set_pos(line[1])
                if len(line) == 3:
                    state.set_pos(line[2])
            else:
                id_orig = int(line[0])
                id_dest = int(line[1])
                state_orig = get_state(id_orig)
                state_dest = get_state(id_dest)
                state_orig.add_edge_out((id_dest, line[2]))
                state_dest.add_edge_in((id_orig, line[2]))

def print_states():
    for key, value in states.items():
        print(value)
    print('\n')


class State:
    def __init__(self, id):
        self._id = id
        self._pos = ''
        self._edges_in = []
        self._edges_out = []

    def __str__(self):
        return 'id: {self._id} pos: {self._pos}\n edges in: {self._edges_in}\n edges out: {self._edges_out}'.format(self=self)

    def set_pos(self, pos):
        if (not self._pos) or (not pos):
            self._pos = pos
        elif self._pos == '-' and pos == '+':
            self._pos = '-+'
        elif self._pos == '+' and pos == '-':
            self._pos = '-+'

    def get_pos(self):
        return self._pos

    def get_id(self):
        return self._id

    def add_edge_in(self, edge):
        self._edges_in.append(edge)

    def add_edge_out(self, edge):
        self._edges_out.append(edge)

    def delete_edge_in(self, edge):
        self._edges_in.remove(edge)

    def delete_edge_out(self, edge):
        self._edges_out.remove(edge)

    def get_edges_in(self):
        return self._edges_in

    def get_edges_out(self):
        return self._edges_out

    def set_edges_out(self, edges_out):
        self._edges_out = edges_out

    def set_edges_in(self, edges_in):
        self._edges_in = edges_in


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        out_dir = r'tg/tables'
        out_dir = os.getcwd() + r'\tg\tables'
        with open("log.txt", 'w') as f:
            f.write(out_dir)            
        main()
    else:
        main()
