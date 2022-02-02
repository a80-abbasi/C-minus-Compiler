# A:  0---B--->1
# 0 and 1: State
# B: NTT (NonTerminal or Terminal! change it if you want)
from Code_Generator import CodeGenerator
from scanner import Scanner
from anytree import Node, RenderTree


class Parser:
    input_address = 'input.txt'
    error_address = 'syntax_errors.txt'
    parse_tree_address = 'parse_tree.txt'

    def __init__(self):
        NTT.read_follow_sets()
        NTT.read_first_sets()
        self.td = TransitionDiagram(self)
        self.error_file = open(file=Parser.error_address, mode='w')
        self.output_file = open(file=Parser.parse_tree_address, mode='w', encoding='utf-8')
        self.scanner = Scanner(open(file=Parser.input_address, mode='r'))
        self.look_ahead = None
        self.has_error = False
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
                output_tree = make_anytree(parse_tree)

                for pre, fill, node in RenderTree(output_tree):
                    self.output_file.write("%s%s\n" % (pre, node.name))

                self.close_files()
                break

    def close_files(self):
        self.scanner.close_files()
        if not self.has_error:
            self.error_file.write('There is no syntax error.')
        self.error_file.close()
        self.output_file.close()

    def report_error(self, type, name):
        self.has_error = True
        self.error_file.write(f'#{self.scanner.line_number} : syntax error, {type} {name}\n')


def terminal_matches(lookahead, terminal):  # todo
    type, value = lookahead
    if type == 'ID' or type == 'NUM':
        return type == terminal
    elif type == 'KEYWORD' or type == 'SYMBOL':
        return value == terminal
    elif terminal == '$':
        return value is None and type is None
    return False


def get_lookahead_string_as_tuple(look_ahead):
    if terminal_matches(look_ahead, '$'):
        return '$'
    type, value = look_ahead
    return f'({type}, {value})'


def get_lookahead_string(lookahead):
    type, value = lookahead
    if type == 'KEYWORD' or type == 'SYMBOL':
        return value
    elif type == 'ID' or type == 'NUM':
        return type
    else:
        return False


def make_anytree(tree, parent=None):
    if parent is None:
        root = Node(tree.name)
    else:
        root = Node(tree.name, parent=parent)
    for subtree in tree.subtrees:
        make_anytree(subtree, root)
    return root


class TransitionDiagram:
    grammar_address = 'c-minus_001.txt'

    def __init__(self, parser):
        self.saved_actions = []
        grammar_file = open(file=TransitionDiagram.grammar_address, mode='r')
        self.grammar = grammar_file.read().splitlines()
        self.non_terminals = self.create_non_terminals()
        self.terminals = []
        self.start_symbols = self.create_transition_diagram()
        self.state = self.start_symbols[0]
        self.parser = parser
        self.code_generator = CodeGenerator()
        self.saved_states = []
        self.saved_states.append(self.state.neighbors[0][1])
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

            final_state = State(-2, self.non_terminals[non_terminal], True)

            start_symbols[non_terminal] = start_state  # Add start state to output
            _, right_hand_sides = rule.split('->')

            for rhs in right_hand_sides.split('|'):

                semantic_action = None
                first_ntt_name, *other_ntt_name = rhs.split()
                ntt = self.find_ntt(first_ntt_name)

                if isinstance(ntt, str):
                    semantic_action = ntt
                    first_ntt_name, *other_ntt_name = rhs.split()[1:]
                    ntt = self.find_ntt(first_ntt_name)

                last_action = None
                if len(other_ntt_name) > 0:
                    last_action = self.find_ntt(other_ntt_name[-1])
                    if isinstance(last_action, str):
                        other_ntt_name.pop()
                    else:
                        last_action = None

                if len(other_ntt_name) > 0:
                    depth_two_state = State(number=state_number, start_non_terminal=self.non_terminals[non_terminal])
                    start_state.add_neighbor(depth_two_state, ntt,
                                             semantic_action=semantic_action)  # first states after start state
                    semantic_action = None

                    state_number += 1

                    temporary_state = depth_two_state  # to make path neighbors

                    for other_name in other_ntt_name[0:-1]:

                        next_ntt = self.find_ntt(other_name)

                        if isinstance(next_ntt, str):
                            semantic_action = next_ntt
                            continue

                        next_state = State(state_number, self.non_terminals[non_terminal])

                        state_number += 1

                        temporary_state.add_neighbor(next_state, next_ntt, semantic_action=semantic_action)
                        temporary_state = next_state
                        semantic_action = None

                    # add final state to last path state neighborhood
                    temporary_state.add_neighbor(final_state, self.find_ntt(other_ntt_name[-1]),
                                                 semantic_action=semantic_action, after_action=last_action)
                else:
                    start_state.add_neighbor(final_state, ntt, semantic_action=semantic_action,
                                             after_action=last_action)

            final_state.number = state_number
            state_number += 1

        return start_symbols

    def output_transition_diagram(self):
        for non_terminal, start_symbol in self.start_symbols.items():
            print(non_terminal)
            print(f'{start_symbol.number}, {start_symbol.is_final}')

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
        if name.startswith('#'):
            return name[1:]

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

    def add_to_saved_trees(self, subtree, new=False):
        if new:
            self.saved_trees.insert(0, subtree)
        else:
            self.saved_trees[0].add_subtree(subtree)

    def handle_transition(self, neighbor, ntt, look_ahead, semantic_action, after_action):
        if semantic_action is not None:
            self.code_gen(semantic_action)
        if ntt.is_terminal:
            if ntt.name == 'epsilon':
                self.add_to_saved_trees(Tree('epsilon'))
                self.goto(neighbor)
            elif terminal_matches(look_ahead, ntt.name):
                self.add_to_saved_trees(Tree(get_lookahead_string_as_tuple(self.parser.look_ahead)))
                self.parser.get_next_token()
                self.goto(neighbor)
            else:
                self.parser.report_error('missing', ntt.name)
                self.goto(neighbor)
            if after_action is not None:
                self.code_gen(after_action)
        else:
            new_state = self.start_symbols[ntt.number]
            self.goto(new_state)
            self.saved_states.append(neighbor)
            self.add_to_saved_trees(Tree(ntt.name), new=True)
            self.saved_actions.append(after_action)


    def find_tree(self, name):
        for idx, tree in enumerate(self.saved_trees):
            if tree.name == name:
                return idx, tree

    def do_transition(self, look_ahead):
        # return from non terminal
        if self.state.is_final:
            # return if parsing has ended
            if self.state.number == 1:
                if look_ahead != (None, None):
                    self.parser.report_error('illegal', get_lookahead_string(look_ahead))
                    self.parser.get_next_token()
                    return
                self.add_to_saved_trees(Tree('$'))
                return self.saved_trees.pop(0)
            # completing tree
            self.add_to_saved_trees(self.saved_trees.pop(0))
            self.state = self.saved_states.pop()
            after_action = self.saved_actions.pop()
            if after_action is not None:
                self.code_gen(after_action)
            return
        if isinstance(self.state, StartState):
            for ntt, neighbor, condition, semantic_action, after_action in self.state.neighbors:
                if any(map(lambda x: terminal_matches(look_ahead, x), condition)):
                    self.handle_transition(neighbor, ntt, look_ahead, semantic_action, after_action)
                    return

            if get_lookahead_string(look_ahead) in self.state.start_non_terminal.follow:
                self.parser.report_error('missing', self.state.start_non_terminal.name)
                self.state = self.saved_states.pop()  # return from non terminal
                self.saved_trees.pop(0)
            else:
                if look_ahead == (None, None):
                    self.parser.report_error('Unexpected', 'EOF')
                    self.saved_trees.pop(0)
                    return self.create_tree()
                self.parser.report_error('illegal', get_lookahead_string(look_ahead))
                self.parser.get_next_token()
        else:
            ntt, neighbor, semantic_action, after_action = self.state.neighbors
            self.handle_transition(neighbor, ntt, look_ahead, semantic_action, after_action)

    def goto(self, neighbor):
        self.state = neighbor

    def all_arcs_terminal(self):
        for ntt, neighbor, condition in self.state.neighbors:
            if not ntt.is_terminal or ntt.name == 'epsilon' or ntt.name == '$':
                return False
        return True

    def get_closest_to_final(self):
        return self.state.neighbors[0]  # todo

    def create_tree(self):
        while True:
            if len(self.saved_trees) == 1:
                return self.saved_trees.pop(0)
            self.add_to_saved_trees(self.saved_trees.pop(0))

    def code_gen(self, semantic_action):
        self.code_generator.code_gen(semantic_action, self.parser.look_ahead[1])


class State:
    def __init__(self, number, start_non_terminal, is_final=False, neighbors=None):
        self.number = number
        self.is_final = is_final
        self.neighbors = neighbors
        self.start_non_terminal = start_non_terminal

    def add_neighbor(self, neighbor, input, semantic_action, after_action=None):  # input is an NTT
        self.neighbors = input, neighbor, semantic_action, after_action


class StartState(State):

    def __init__(self, number, start_non_terminal, is_final=False, neighbors=None):
        super().__init__(number, start_non_terminal, is_final, neighbors)
        self.neighbors = neighbors if neighbors is not None else []

    def add_neighbor(self, neighbor, input, semantic_action=None, after_action=None):
        self.neighbors.append((input, neighbor, semantic_action, after_action))

    def create_condition_on_neighbors(self):

        new_neighbors = []
        for input, neighbor, semantic_action, after_action in self.neighbors:
            condition = set()
            cur = neighbor
            ntt = input
            # first
            while True:
                if cur.is_final:
                    condition.update(ntt.first)
                    break
                first = set(ntt.first).difference(['epsilon'])
                condition.update(first)
                if len(first) == len(ntt.first):
                    break
                ntt, cur, _, _ = cur.neighbors
            # follow
            if 'epsilon' in condition:
                condition.update(self.start_non_terminal.follow)
            new_neighbors.append((input, neighbor, list(condition), semantic_action, after_action))
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
    def __init__(self, name):
        self.name = name
        self.subtrees = []

    def add_subtree(self, tree):
        self.subtrees.append(tree)
