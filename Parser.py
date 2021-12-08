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
        grammar_file = open(file=TransitionDiagram.grammar_address, mode='r')
        self.start_symbols = self.create_transition_diagram()
        self.non_terminals = self.create_non_terminals()
        self.terminals = []
        self.grammar = grammar_file.read().splitlines()
        self.state = self.start_symbols[0]
        self.parser = parser
        self.saved_state = None

    def create_transition_diagram(self):  # todo
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

    def handle_transition(self, neighbor, ntt, look_ahead):
        if ntt.is_terminal:
            if terminal_matches(look_ahead, ntt.name):
                self.parser.get_next_token()
                self.goto(neighbor)
            else:
                pass  # todo: error
        else:
            new_state = self.start_symbols[ntt.number]
            self.goto(new_state)
            self.saved_state = neighbor

    def do_transition(self, look_ahead):
        if self.state.is_final:
            self.state = self.saved_state
            return  # todo: we can not return - todo: ending parsing
        if isinstance(self.state, StartState):
            for ntt, neighbor, condition in self.state.neighbors:
                if look_ahead in condition:
                    self.handle_transition(neighbor, ntt, look_ahead)
                    return
            # todo: error based on follow
        else:
            ntt, neighbor = self.state.neighbors
            self.handle_transition(neighbor, ntt, look_ahead)

    def goto(self, neighbor):
        self.state = neighbor


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
