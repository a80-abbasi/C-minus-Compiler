# A:  0---B--->1
# 0 and 1: State
# B: NTT (NonTerminal or Terminal! change it if you want)
from scanner import Scanner


class Parser:
    input_adress = 'input'

    def __init__(self):
        self.td = TransitionDiagram(self)
        self.scanner = Scanner(Parser.input_adress)
        self.look_ahead = self.scanner.get_next_token()

    def get_next_token(self):
        self.look_ahead = self.scanner.get_next_token()


def terminal_matches(la, t):  # todo
    return la == t


class TransitionDiagram:
    grammar_address = 'c-minus_001'

    def __init__(self, parser):
        self.start_symbols = self.create_transition_diagram()
        grammar_file = open(file=TransitionDiagram.grammar_address, mode='r')
        self.non_terminals = self.create_non_terminals()
        self.grammar = grammar_file.read().splitlines()
        self.state = self.start_symbols[0]
        self.parser = parser
        self.saved_state = None

    def create_transition_diagram(self):  # todo
        start_symbols = {}
        state_number = 0
        for non_terminal, rule in enumerate(self.grammar):
            start_state = StartState(state_number, self.non_terminals[non_terminal])
            start_symbols[non_terminal] = start_state

        return None

    def create_non_terminals(self):
        non_terminals = []
        for num, rule in enumerate(self.grammar):
            non_terminal_name = rule.split('->')[0].strip()
            non_terminal = NTT(number=num, is_terminal=False, name=non_terminal_name)
            non_terminals.append(non_terminal)
        return non_terminals

    def handle_transition(self, neighbor, ntt, look_ahead):
        if ntt.is_terminal:
            if terminal_matches(look_ahead, ntt.name):
                self.parser.get_next_token()
                self.goto(neighbor)
            else:
                pass
        else:
            new_state = self.start_symbols[ntt.number]
            self.goto(new_state)
            self.saved_state = neighbor


    def do_transition(self, look_ahead):
        if self.state.is_final:
            self.state = self.saved_state
            return  # todo: we can not return - what
        if isinstance(self, StartState):
            for ntt, neighbor, condition in self.neighbors:
                if look_ahead in condition:
                    self.handle_transition(neighbor, ntt, look_ahead)
        else:
            pass

    def goto(self, neighbor):
        self.state = neighbor


class State:
    def __init__(self, number, is_final=False, neighbors=None):
        self.number = number
        self.is_final = is_final
        self.neighbors = neighbors

    def add_neighbor(self, neighbor, input):  # input is an NTT
        self.neighbors = input, neighbor


class StartState(State):

    def __init__(self, number, start_terminal, is_final=False, neighbors=None):
        super().__init__(number, is_final, neighbors)
        self.start_terminal = start_terminal
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
            if 'epsilon' in condition:
                condition.extend(self.start_terminal.follow)
            new_neighbors.append((input, neighbor, condition))
        self.neighbors = new_neighbors


class NTT:
    def __init__(self, number, is_terminal=False, name=None):
        self.is_terminal = is_terminal
        self.name = name
        self.number = number
        self.first = self.set_first()
        self.follow = self.set_follow()

    def set_first(self):
        pass

    def set_follow(self):
        pass
