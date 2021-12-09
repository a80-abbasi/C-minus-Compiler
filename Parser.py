# A:  0---B--->1
# 0 and 1: State
# B: NTT (NonTerminal or Terminal! change it if you want)
from scanner import Scanner


class Parser:

    input_address = 'input.txt'
    error_address = 'syntax_errors.txt'
    parse_tree_address = 'parse_tree.txt'

    def __init__(self):
        NTT.read_follow_sets()
        NTT.read_first_sets()
        self.td = TransitionDiagram(self)
        self.error_file = open(file=Parser.error_address, mode='w')
        self.output_file = open(file=Parser.parse_tree_address, mode='w')
        self.scanner = Scanner(open(file=Parser.input_address, mode='r'))
        self.look_ahead = None
        self.get_next_token()

    def get_next_token(self):
        while True:
            self.look_ahead = self.scanner.get_next_token()
            token_type, _ = self.look_ahead
            if token_type != 'WHITESPACE' and token_type != 'COMMENT':
                break

    def parse(self):
        while True:
            parse_tree = self.td.do_transition(self.look_ahead)
            if parse_tree is not None:
                self.output_file.write(parse_tree.to_string())
                self.close_files()
                break

    def close_files(self):
        self.scanner.close_files()
        self.error_file.close()
        self.output_file.close()

    def report_missing(self, name):
        self.error_file.write(f'#{self.scanner.line_number} : syntax error, missing {name}\n')

    def report_illegal_lookahead(self, look_ahead):
        self.error_file.write(f'#{self.scanner.line_number} : syntax error, illegal {look_ahead}\n')


def terminal_matches(lookahead, terminal):  # todo
    type, value = lookahead
    if type == 'ID' or type == 'NUM':
        return type == terminal
    elif type == 'KEYWORD' or 'SYMBOL':
        return value == terminal
    elif terminal == '$':
        return value is None and type is None
    return False


def get_lookahead_string(look_ahead):
    type, value = look_ahead
    return f'({type}, {value})'


class TransitionDiagram:

    grammar_address = 'c-minus_001.txt'

    def __init__(self, parser):
        grammar_file = open(file=TransitionDiagram.grammar_address, mode='r')
        self.grammar = grammar_file.read().splitlines()
        self.non_terminals = self.create_non_terminals()
        self.terminals = []
        self.start_symbols = self.create_transition_diagram()
        self.state = self.start_symbols[0]
        self.parser = parser
        self.saved_states = []
        self.saved_trees = []
        self.saved_trees.append(Tree(self.state.start_non_terminal.name))
        for s in self.start_symbols.values():
            s.create_condition_on_neighbors()

    def create_transition_diagram(self):
        start_symbols = {}
        state_number = 0
        for non_terminal, rule in enumerate(self.grammar):
            start_state = StartState(state_number, self.non_terminals[non_terminal])
            state_number += 1

            final_state = State(state_number, self.non_terminals[non_terminal], True)
            state_number += 1

            start_symbols[non_terminal] = start_state  # Add start state to output
            _, right_hand_sides = rule.split('->')

            for rhs in right_hand_sides.split('|'):
                first_ntt_name, *other_ntt_name = rhs.split()
                ntt = self.find_ntt(first_ntt_name)

                if len(other_ntt_name) > 0:
                    depth_two_state = State(number=state_number, start_non_terminal=self.non_terminals[non_terminal])
                    start_state.add_neighbor(depth_two_state, ntt)  # first states after start state

                    state_number += 1

                    temporary_state = depth_two_state  # to make path neighbors

                    for other_name in other_ntt_name[0:-1]:
                        next_ntt = self.find_ntt(other_name)
                        next_state = State(state_number, self.non_terminals[non_terminal])

                        state_number += 1

                        temporary_state.add_neighbor(next_state, next_ntt)
                        temporary_state = next_state

                    # add final state to last path state neighborhood
                    temporary_state.add_neighbor(final_state, self.find_ntt(other_ntt_name[-1]))
                else:
                    start_state.add_neighbor(final_state, ntt)

        return start_symbols

    def is_non_terminal(self, name):
        for non_terminal in self.non_terminals:
            if non_terminal.name == name:
                return True, non_terminal
        return False, None

    def is_terminal(self, name):
        for terminal in self.terminals:
            if terminal.name == name:
                return True, terminal
        return False, None

    def find_ntt(self, name):
        is_non_terminal, non_terminal = self.is_non_terminal(name)
        if is_non_terminal:
            return non_terminal

        is_terminal, terminal = self.is_terminal(name)
        if is_terminal:
            return terminal

        terminal = NTT(number=-1, is_terminal=True, name=name)
        self.terminals.append(terminal)

        return terminal

    def create_non_terminals(self):
        non_terminals = []
        for num, rule in enumerate(self.grammar):
            non_terminal_name = rule.split('->')[0].strip()
            non_terminal = NTT(number=num, is_terminal=False, name=non_terminal_name)
            non_terminals.append(non_terminal)
        return non_terminals

    def add_to_saved_trees(self, subtree):
        self.saved_trees.insert(0, subtree)

    def handle_transition(self, neighbor, ntt, look_ahead):
        if ntt.is_terminal:
            if terminal_matches(look_ahead, ntt.name):
                self.parser.get_next_token()
                self.add_to_saved_trees(Tree(get_lookahead_string(self.parser.look_ahead)))
                self.goto(neighbor)
            else:
                self.parser.report_missing(ntt.name)
                self.goto(neighbor)
        else:
            new_state = self.start_symbols[ntt.number]
            self.goto(new_state)
            self.saved_states.append(neighbor)
            self.add_to_saved_trees(Tree(ntt.name))

    def find_tree(self, name):
        for idx, tree in enumerate(self.saved_trees):
            if tree.ntt == name:
                return idx, tree

    def do_transition(self, look_ahead):
        # return from non terminal
        if self.state.is_final:
            # completing tree
            # index = self.saved_trees.index(Tree(self.state.start_non_terminal.name))
            # tree = self.saved_trees[index]
            # self.find_tree(self.state.start_non_terminal.name)
            index, tree = self.find_tree(self.state.start_non_terminal.name)
            for i in range(index-1):
                tree.add_subtree(self.saved_trees.pop(0))
            # return if parsing has ended
            if self.state.start_non_terminal == self.start_symbols[0]:
                return self.saved_trees.pop(0)
            self.state = self.saved_states.pop()
            return
        if isinstance(self.state, StartState):
            for ntt, neighbor, condition in self.state.neighbors:
                if any(map(lambda x: terminal_matches(look_ahead, x), condition)):
                    self.handle_transition(neighbor, ntt, look_ahead)
                    return
            # errors:
            if self.all_arcs_terminal():
                ntt, neighbor = self.get_closest_to_final()
                self.parser.report_missing(ntt.name)
                self.goto(neighbor)
                return
            if look_ahead in self.state.start_non_terminal.follow:
                self.parser.report_missing(self.state.start_non_terminal.name)
                self.state = self.saved_states.pop(0)  # return from non terminal
            else:
                self.parser.report_illegal_lookahead(look_ahead)
                self.parser.get_next_token()
        else:
            ntt, neighbor = self.state.neighbors
            self.handle_transition(neighbor, ntt, look_ahead)

    def goto(self, neighbor):
        self.state = neighbor

    def all_arcs_terminal(self):
        for ntt, neighbor, condition in self.state.neighbors:
            if not ntt.is_terminal or ntt.name == 'EPSILON':
                return False
        return True

    def get_closest_to_final(self):
        return self.state.neighbors[0]  # todo


class State:
    def __init__(self, number, start_non_terminal, is_final=False, neighbors=None):
        self.number = number
        self.is_final = is_final
        self.neighbors = neighbors
        self.start_non_terminal = start_non_terminal

    def add_neighbor(self, neighbor, input):  # input is an NTT
        self.neighbors = input, neighbor


class StartState(State):

    def __init__(self, number, start_non_terminal, is_final=False, neighbors=None):
        super().__init__(number, start_non_terminal, is_final, neighbors)
        self.neighbors = neighbors if neighbors is not None else []

    def add_neighbor(self, neighbor, input):
        self.neighbors.append((input, neighbor))

    def create_condition_on_neighbors(self):
        new_neighbors = []
        for input, neighbor in self.neighbors:
            condition = []
            cur = neighbor
            ntt = input
            # first
            while True:
                if cur.is_final:
                    condition.extend(ntt.first)
                    break
                first = list(set(ntt.first).difference('epsilon'))
                condition.extend(first)
                ntt, cur = cur.neighbors
            # follow
            if 'epsilon' in condition:
                condition.extend(self.start_non_terminal.follow)
            new_neighbors.append((input, neighbor, condition))
        self.neighbors = new_neighbors


class NTT:
    first_sets_address = 'first_sets.txt'
    first_sets = {}

    follow_sets_address = 'follow_sets.txt'
    follow_sets = {}

    def __init__(self, number, is_terminal=False, name=None):
        self.is_terminal = is_terminal
        self.name = name
        self.number = number
        self.first = self.set_first()
        self.follow = self.set_follow()

    def set_first(self):
        if not self.is_terminal:
            return NTT.first_sets[self.name]
        return [self.name]

    def set_follow(self):
        if not self.is_terminal:
            return NTT.follow_sets[self.name]
        return None

    @staticmethod
    def read_first_sets():
        with open(file=NTT.first_sets_address, mode='r') as first_sets_file:
            content = first_sets_file.read()
            for line in content.splitlines():
                name, first_set = line.split('\t')
                NTT.first_sets[name] = first_set.split(', ')

    @staticmethod
    def read_follow_sets():
        with open(file=NTT.follow_sets_address, mode='r') as follow_sets_file:
            content = follow_sets_file.read()
            for line in content.splitlines():
                name, follow_set = line.split('\t')
                NTT.follow_sets[name] = follow_set.split(', ')


class Tree:
    def __init__(self, ntt):
        self.ntt = ntt
        self.subtrees = []

    def add_subtree(self, tree):
        self.subtrees.append(tree)

    def to_string(self, marker_str="|--- ", level_markers=[]):
        empty_str = " " * len(marker_str)
        connection_str = "|" + empty_str[:-1]

        level = len(level_markers)
        markers = "".join(map(lambda draw: connection_str if draw else empty_str, level_markers[:-1]))
        markers += marker_str if level > 0 else ""
        res = f"{markers}{self.ntt}\n"

        for i, child in enumerate(self.subtrees):
            is_last = i == len(self.subtrees) - 1
            res += child.to_string(marker_str, [*level_markers, not is_last])

        return res
