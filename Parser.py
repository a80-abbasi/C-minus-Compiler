# A:  0---B--->1
# 0 and 1: State
# B: NTT (NonTerminal or Terminal! change it if you want)

class TransitionDiagram:

    grammar_address = 'c-minus_001'

    def __init__(self):
        start_symbols = self.create_transition_diagram()
        grammar_file = open(file=TransitionDiagram.grammar_address, mode='r')
        self.non_terminals = self.create_non_terminals()
        self.grammar = grammar_file.read().splitlines()
        self.state = start_symbols[0]

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


    # def do_transition(self, look_ahead):
    #     for ntt, neighbor in self.state.neighbors.items():
    #         if self.should_do_with_first(self, ntt, look_ahead)
    #             self.state = neighbor
    #             return
    #     if
    #
    # def should_do_with_first(self, cur_state, ntt, look_ahead):
    #     if look_ahead in ntt.first:
    #         return True
    #     if 'epsilon' in ntt.first:  # todo: epsilon
    #         for t, neigh in cur_state.neighbors[ntt].items():
    #             if self.should_do_with_first(cur_state.neighbors[ntt], t, look_ahead):
    #                 return True
    #     return False


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


